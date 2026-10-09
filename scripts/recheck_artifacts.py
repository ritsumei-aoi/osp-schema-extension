"""
Engine-independent re-verification from the JSON artifacts only.

Reads artifacts/cn1_n{n}.json and, using nothing but the structure constants C,
the gamma data G, the maps f and the functionals lambda stored there, checks

  (a) super-Jacobi identity of C (so C really defines a Lie superalgebra);
  (b) dimension (2n^2+n+1 | 4n) and that ad(N), ad(Hs_j) reproduce the stored weights;
  (c) the 2-cocycle identity for gamma_gb (kappa-part of the Jacobi identity of the
      deformed bracket on ghat + kappa*ghat) for each gb direction;
  (d) gamma_gb(Z_i,Z_j) = (delta f_gb)(Z_i,Z_j) + lambda_gb([Z_i,Z_j]_0) * 1   (exact);
  (e) delta(ad_Z) = 0 for every odd basis element Z;
  (f) from-scratch solvability: the linear system  delta(phi) = gamma_gb|_g  is consistent
      (augmented rank == rank, computed mod a large prime) -- an independent existence check
      that does not use the closed form f;
  (g) no nonzero gb makes all scalar parts of gamma vanish (rank of scalar map = 4n).

Run:  python3 scripts/recheck_artifacts.py
"""
import json, os, sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "artifacts")


def load(n):
    with open(os.path.join(ART, f"cn1_n{n}.json")) as fh:
        return json.load(fh)


def vadd(u, v, s=F(1)):
    out = dict(u)
    for k, x in v.items():
        nv = out.get(k, F(0)) + s * x
        if nv == 0:
            out.pop(k, None)
        else:
            out[k] = nv
    return out


class Alg:
    def __init__(self, art):
        self.n = art["n"]
        self.m = art["dim_even"] + art["dim_odd"]
        self.par = [Z["parity"] for Z in art["basis"]][: self.m]
        self.weight = [Z["weight"] for Z in art["basis"]][: self.m]
        self.labels = [Z["label"] for Z in art["basis"]]
        self.C = {}
        for i, j, k, v in art["structure_constants"]["data"]:
            self.C.setdefault((i, j), {})[k] = F(v)
        self.P = len(art["gb_parameters"])
        self.G = [dict() for _ in range(self.P)]
        for p, i, j, k, v in art["gamma"]["data"]:
            self.G[p].setdefault((i, j), {})[k] = F(v)
        self.f = [dict() for _ in range(self.P)]
        for p, i, j, v in art["f"]["data"]:
            self.f[p].setdefault(j, {})[i] = F(v)
        self.lam = [dict() for _ in range(self.P)]
        for p, k, v in art["lambda_"]["data"]:
            self.lam[p][k] = F(v)
        self.inner = []
        for d in art["inner_odd_derivations"]["data"]:
            f = {}
            for i, j, v in d["map"]:
                f.setdefault(j, {})[i] = F(v)
            self.inner.append((d["Z"], f))

    def br(self, u, v):
        out = {}
        for i, x in u.items():
            if i == self.m:
                continue
            for j, y in v.items():
                if j == self.m:
                    continue
                row = self.C.get((i, j))
                if row:
                    out = vadd(out, row, x * y)
        return out

    def parity_of(self, u):
        ps = {self.par[i] if i < self.m else 0 for i in u}
        assert len(ps) <= 1
        return ps.pop() if ps else 0

    def delta(self, f):
        m, par = self.m, self.par
        out = {}
        for i in range(m):
            for j in range(m):
                t = self.br({i: F(1)}, f.get(j, {}))
                t = {k: (-1 if par[i] else 1) * v for k, v in t.items()}
                s2 = F(-1) * (-1 if ((par[i] + 1) * par[j]) % 2 else 1)
                t = vadd(t, self.br({j: F(1)}, f.get(i, {})), s2)
                for k, c in self.C.get((i, j), {}).items():
                    t = vadd(t, f.get(k, {}), -c)
                if t:
                    out[(i, j)] = t
        return out

    # deformed bracket on ghat + kappa ghat for gb = e_p
    def dbr(self, p, u, v):
        u0, u1 = u
        v0, v1 = v
        out0 = self.br(u0, v0)
        out1 = {}
        for i, x in u0.items():
            for j, y in v0.items():
                g = self.G[p].get((i, j))
                if g:
                    out1 = vadd(out1, g, x * y)
        out1 = vadd(out1, self.br(u1, v0))
        out1 = vadd(out1, self.br(u0, v1), F(-1) if self.parity_of(u0) == 1 else F(1))
        return out0, out1


def check_jacobi(A):
    m, par = A.m, A.par
    for i in range(m):
        for j in range(m):
            for k in range(m):
                t1 = A.br({i: F(1)}, A.C.get((j, k), {}))
                t2 = A.br(A.C.get((i, j), {}), {k: F(1)})
                t3 = A.br({j: F(1)}, A.C.get((i, k), {}))
                s = F(-1) if (par[i] and par[j]) else F(1)
                if vadd(vadd(t1, t2, F(-1)), t3, -s):
                    return False
    return True


def check_weights(A):
    cartan = [0] + [1 + j for j in range(A.n)]
    for k in range(A.m):
        for c, h in enumerate(cartan):
            row = A.C.get((h, k), {})
            w = A.weight[k][c]
            if row != ({k: F(w)} if w else {}):
                return False
    return True


def check_cocycle(A):
    m, par = A.m, A.par
    for p in range(A.P):
        for i in range(m):
            for j in range(m):
                for k in range(m):
                    Zi, Zj, Zk = ({i: F(1)}, {}), ({j: F(1)}, {}), ({k: F(1)}, {})
                    t1 = A.dbr(p, Zi, A.dbr(p, Zj, Zk))
                    t2 = A.dbr(p, A.dbr(p, Zi, Zj), Zk)
                    t3 = A.dbr(p, Zj, A.dbr(p, Zi, Zk))
                    s = F(-1) if (par[i] and par[j]) else F(1)
                    if vadd(vadd(t1[1], t2[1], F(-1)), t3[1], -s) or vadd(vadd(t1[0], t2[0], F(-1)), t3[0], -s):
                        return False
    return True


def check_gamma_equals_delta_f_plus_lambda(A):
    m = A.m
    for p in range(A.P):
        df = A.delta(A.f[p])
        for i in range(m):
            for j in range(m):
                g = A.G[p].get((i, j), {})
                gpart = {k: v for k, v in g.items() if k != m}
                if vadd(gpart, df.get((i, j), {}), F(-1)):
                    return False
                lam_br = sum((A.lam[p].get(k, F(0)) * c for k, c in A.C.get((i, j), {}).items()), F(0))
                if g.get(m, F(0)) != lam_br:
                    return False
    return True


def check_inner_in_kernel(A):
    return all(not A.delta(f) for _, f in A.inner) and len(A.inner) == 4 * A.n


def rank_mod_p(rows, ncols, prime):
    import numpy as np
    M = np.zeros((len(rows), ncols), dtype=np.int64)
    for r, d in enumerate(rows):
        for c, v in d.items():
            M[r, c] = (v.numerator % prime) * pow(v.denominator % prime, prime - 2, prime) % prime
    rank, rowpos = 0, 0
    for col in range(ncols):
        if rowpos >= M.shape[0]:
            break
        nz = np.nonzero(M[rowpos:, col])[0]
        if len(nz) == 0:
            continue
        piv = rowpos + nz[0]
        M[[rowpos, piv]] = M[[piv, rowpos]]
        inv = pow(int(M[rowpos, col]), prime - 2, prime)
        M[rowpos] = (M[rowpos] * inv) % prime
        others = np.nonzero(M[:, col])[0]
        others = others[others != rowpos]
        if len(others):
            M[others] = (M[others] - np.outer(M[others, col], M[rowpos])) % prime
        rowpos += 1
        rank += 1
    return rank


def check_solvable_from_scratch(A, prime=1000000007):
    """Build delta as a matrix over the unknowns phi_{ij} (p_i != p_j) and check that
    every gamma_p|_g lies in its column space (augmented rank == rank, mod prime)."""
    m, par = A.m, A.par
    unk = [(i, j) for j in range(m) for i in range(m) if par[i] != par[j]]
    uidx = {u: a for a, u in enumerate(unk)}
    N = len(unk)
    rows, rhs = [], [[] for _ in range(A.P)]
    for i in range(m):
        for j in range(i, m):
            comps = {}

            def add(k, u, val):
                if val == 0:
                    return
                d = comps.setdefault(k, {})
                nv = d.get(uidx[u], F(0)) + val
                if nv == 0:
                    d.pop(uidx[u], None)
                else:
                    d[uidx[u]] = nv
            s1 = F(-1) if par[i] else F(1)
            s2 = F(-1) * (-1 if ((par[i] + 1) * par[j]) % 2 else 1)
            for l in range(m):
                if par[l] != par[j]:
                    for k, c in A.C.get((i, l), {}).items():
                        add(k, (l, j), s1 * c)
                if par[l] != par[i]:
                    for k, c in A.C.get((j, l), {}).items():
                        add(k, (l, i), s2 * c)
            for k, c in A.C.get((i, j), {}).items():
                for l in range(m):
                    if par[l] != par[k]:
                        add(l, (l, k), -c)
            # keep every component k (even if the row is zero) so rhs aligns
            for k in range(m):
                rows.append(comps.get(k, {}))
                for p in range(A.P):
                    rhs[p].append(A.G[p].get((i, j), {}).get(k, F(0)))
    r0 = rank_mod_p(rows, N, prime)
    ok = True
    for p in range(A.P):
        aug = []
        for r, b in zip(rows, rhs[p]):
            row = dict(r)
            if b:
                row[N] = b
            aug.append(row)
        ok &= (rank_mod_p(aug, N + 1, prime) == r0)
    return ok, r0, N


def check_scalar_rank(A):
    piv, rank = {}, 0
    for p in range(A.P):
        v = {i * A.m + j: g[A.m] for (i, j), g in A.G[p].items() if A.m in g}
        while v:
            c = min(v)
            if c in piv:
                v = vadd(v, piv[c], -v[c] / piv[c][c])
            else:
                piv[c] = v
                rank += 1
                break
    return rank == A.P


if __name__ == "__main__":
    allok = True
    for n in (1, 2, 3):
        A = Alg(load(n))
        res = {
            "dimension": (A.m == 2 * n * n + 5 * n + 1 and sum(A.par) == 4 * n),
            "jacobi": check_jacobi(A),
            "weights": check_weights(A),
            "cocycle": check_cocycle(A),
            "gamma = delta f + lambda([.,.])": check_gamma_equals_delta_f_plus_lambda(A),
            "inner odd derivations in ker delta": check_inner_in_kernel(A),
        }
        solv, r0, N = check_solvable_from_scratch(A)
        res["from-scratch solvable (mod p)"] = solv
        res["rank delta / unknowns"] = f"{r0}/{N} (kernel {N - r0} = 4n: {N - r0 == 4*n})"
        res["scalar residual rank = 4n"] = check_scalar_rank(A)
        print(f"n = {n}:")
        for k, v in res.items():
            print(f"   {k}: {v}")
        allok &= all(v is True for k, v in res.items() if k != "rank delta / unknowns")
    print("ALL RECHECKS PASS" if allok else "RECHECK FAILURE")
    sys.exit(0 if allok else 1)
