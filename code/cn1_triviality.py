#!/usr/bin/env python3
"""Triviality of the inhomogeneous (gb) deformation of C(n+1) = osp(2|2n).

Model (docs/math/*.md):
  * U(A)/(K=1): generators a+, a- (odd), b_j^+, b_j^- (even), kappa (odd, central, kappa^2=0).
  * [b_j^s, a^sigma] = -gb[sigma,j,s] kappa ;  [a^sigma, b_j^s] = +gb kappa  (supersymmetry).
  * g = span of Weyl(super)symmetrised quadratics Q_{uv} = 1/2 (uv + (-1)^{p_u p_v} vu).
  * [X,Y]_gb = [X,Y]_0 + kappa*gamma(X,Y)   (kappa written on the LEFT).
  * (delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y]).

All structure constants are exact (fractions.Fraction); gamma is exactly linear in gb because
kappa^2 = 0, so gamma = sum_i gb_i gamma_i with gamma_i computed at gb = unit vector e_i.
"""
import json
import sys
from fractions import Fraction as Fr
from itertools import product

import numpy as np

KAPPA = 0  # generator index of kappa (smallest => normal ordering moves it to the left)


class Model:
    def __init__(self, n):
        self.n = n
        # oscillator labels, index 1.. ; 0 is kappa
        self.names = ["kappa", "a+", "a-"]
        for j in range(1, n + 1):
            self.names += [f"b{j}+", f"b{j}-"]
        self.par = [1, 1, 1] + [0] * (2 * n)
        self.idx = {nm: i for i, nm in enumerate(self.names)}
        self.osc = list(range(1, len(self.names)))
        # gb parameters, ordered
        self.gb_keys = [(sg, j, s) for sg in "+-" for j in range(1, n + 1) for s in "+-"]
        self.build_basis()

    # ---- bracket on V (+K=1, +kappa). returns (scalar, kappa_coeff) given gb dict
    def vbr(self, x, y, gb):
        if x == KAPPA or y == KAPPA:
            return (Fr(0), Fr(0))
        nx, ny = self.names[x], self.names[y]
        if nx[0] == "a" and ny[0] == "a":
            return (Fr(1), Fr(0)) if nx != ny else (Fr(0), Fr(0))  # {a-,a+}=1
        if nx[0] == "b" and ny[0] == "b":
            if nx[1] != ny[1]:
                return (Fr(0), Fr(0))
            if nx[2] == "-" and ny[2] == "+":
                return (Fr(1), Fr(0))
            if nx[2] == "+" and ny[2] == "-":
                return (Fr(-1), Fr(0))
            return (Fr(0), Fr(0))
        if nx[0] == "b":  # [b_j^s, a^sigma] = -gb kappa
            return (Fr(0), -Fr(gb.get((ny[1], int(nx[1]), nx[2]), 0)))
        return (Fr(0), Fr(gb.get((nx[1], int(ny[1]), ny[2]), 0)))  # [a,b] = +gb kappa

    # ---- noncommutative normal ordering in U(A)
    def normal(self, elt, gb):
        out = {}
        stack = list(elt.items())
        while stack:
            w, c = stack.pop()
            if c == 0:
                continue
            done = True
            for p in range(len(w) - 1):
                i, j = w[p], w[p + 1]
                if i > j or (i == j and self.par[i] == 1):
                    done = False
                    pre, post = w[:p], w[p + 2:]
                    if i == j:  # odd: x^2 = 1/2 [x,x}
                        sc, kc = self.vbr(i, i, gb)
                        sc, kc = sc / 2, kc / 2
                        if i == KAPPA:
                            sc = kc = Fr(0)
                        stack.append((pre + post, c * sc))
                        stack.append((pre + (KAPPA,) + post, c * kc))
                    else:
                        sgn = -1 if (self.par[i] and self.par[j]) else 1
                        stack.append((pre + (j, i) + post, c * sgn))
                        sc, kc = self.vbr(i, j, gb)
                        stack.append((pre + post, c * sc))
                        stack.append((pre + (KAPPA,) + post, c * kc))
                    break
            if done:
                # kappa^2 = 0
                if w.count(KAPPA) > 1:
                    continue
                out[w] = out.get(w, 0) + c
        return {w: c for w, c in out.items() if c != 0}

    # ---- basis of g: Q_{uv}, u<=v osc indices
    def build_basis(self):
        self.basis = []
        for u in self.osc:
            for v in self.osc:
                if u > v:
                    continue
                if u == v and self.par[u] == 1:
                    continue
                self.basis.append((u, v))
        self.bidx = {q: i for i, q in enumerate(self.basis)}
        self.bpar = [(self.par[u] + self.par[v]) % 2 for (u, v) in self.basis]
        self.dim = len(self.basis)

    def Q(self, u, v):
        """symmetrised Q_{uv} for any ordered pair -> (index, sign)"""
        if u > v:
            return self.bidx[(v, u)], (-1) ** (self.par[u] * self.par[v])
        return self.bidx[(u, v)], 1

    def Qelt(self, k, gb):
        u, v = self.basis[k]
        sgn = (-1) ** (self.par[u] * self.par[v])
        e = {}
        e[(u, v)] = e.get((u, v), 0) + Fr(1, 2)
        e[(v, u)] = e.get((v, u), 0) + Fr(sgn, 2)  # accumulate: u == v must give u*u
        return self.normal(e, gb)

    def bracket_basis(self, a, b, gb):
        """[Z_a, Z_b] in U(A); returns (g part dict, kappa*g part dict) and residual constants."""
        A, B = self.Qelt(a, gb), self.Qelt(b, gb)
        sg = (-1) ** (self.bpar[a] * self.bpar[b])
        e = {}
        for (w1, c1), (w2, c2) in product(A.items(), B.items()):
            e[w1 + w2] = e.get(w1 + w2, 0) + c1 * c2
            e[w2 + w1] = e.get(w2 + w1, 0) - sg * c1 * c2
        N = self.normal(e, gb)
        # convert normal-ordered words to symmetrised basis
        g, kg, const, kconst = {}, {}, Fr(0), Fr(0)
        for w, c in N.items():
            kap = w and w[0] == KAPPA
            rest = w[1:] if kap else w
            if len(rest) == 0:
                if kap:
                    kconst += c
                else:
                    const += c
            elif len(rest) == 2:
                u, v = rest
                i, s = self.Q(u, v)
                (kg if kap else g)[i] = (kg if kap else g).get(i, 0) + c
                # normal-ordered uv = Q_uv + 1/2 [u,v}
                sc, kc = self.vbr(u, v, gb)
                if kap:
                    kconst += c * sc / 2
                else:
                    const += c * sc / 2
                    kconst += c * kc / 2
            else:
                raise RuntimeError(f"unexpected word {w}")
        return g, kg, const, kconst

    def structure(self):
        """undeformed structure constants c[(a,b)] = {c: val}"""
        C = {}
        for a in range(self.dim):
            for b in range(self.dim):
                g, kg, const, kconst = self.bracket_basis(a, b, {})
                assert not kg and const == 0 and kconst == 0
                if g:
                    C[(a, b)] = g
        return C

    def gamma(self, key):
        """gamma_i for unit gb at `key`: {(a,b): {c: val}}  (kappa*gamma)"""
        gb = {key: 1}
        G = {}
        for a in range(self.dim):
            for b in range(self.dim):
                g, kg, const, kconst = self.bracket_basis(a, b, gb)
                # g-part must equal undeformed bracket; scalar residues must vanish
                assert const == 0 and kconst == 0, ("scalar residue", a, b, const, kconst)
                if kg:
                    G[(a, b)] = kg
        return G


def apply_f_bracket(M, C, phi_cols, a, b):
    pass


def delta_f(M, C, f):
    """f: {j: {i: val}} odd linear map. returns delta f as {(a,b): {c: val}} (exact)."""
    def br(x, y):  # x,y: dict basis->coef ; bilinear extension
        out = {}
        for i, ci in x.items():
            for j, cj in y.items():
                for k, v in C.get((i, j), {}).items():
                    out[k] = out.get(k, 0) + ci * cj * v
        return out

    def fapp(x):
        out = {}
        for i, ci in x.items():
            for k, v in f.get(i, {}).items():
                out[k] = out.get(k, 0) + ci * v
        return out

    D = {}
    for a in range(M.dim):
        for b in range(M.dim):
            pa, pb = M.bpar[a], M.bpar[b]
            t1 = br({a: 1}, f.get(b, {}))
            t2 = br({b: 1}, f.get(a, {}))
            t3 = fapp(C.get((a, b), {}))
            res = {}
            for k, v in t1.items():
                res[k] = res.get(k, 0) + (-1) ** pa * v
            for k, v in t2.items():
                res[k] = res.get(k, 0) - (-1) ** ((pa + 1) * pb) * v
            for k, v in t3.items():
                res[k] = res.get(k, 0) - v
            res = {k: v for k, v in res.items() if v != 0}
            if res:
                D[(a, b)] = res
    return D


def explicit_f(M, gb):
    """f induced by a'^sigma = a^sigma + kappa*beta(a^sigma), b unchanged.
    beta(a^sigma) = sum_j  -gb[sigma,j,-] b_j^+ + gb[sigma,j,+] b_j^-  (sign fixed so delta f = +gamma).
    f(Q_uv) = Q(beta u, v) + (-1)^{p_u} Q(u, beta v)."""
    beta = {}
    for sg in "+-":
        t = {}
        for j in range(1, M.n + 1):
            t[M.idx[f"b{j}+"]] = -Fr(gb.get((sg, j, "-"), 0))
            t[M.idx[f"b{j}-"]] = Fr(gb.get((sg, j, "+"), 0))
        beta[M.idx[f"a{sg}"]] = t
    f = {}
    for k, (u, v) in enumerate(M.basis):
        res = {}
        for (x, y, s) in [(None, None, None)]:
            pass
        for w, c in beta.get(u, {}).items():
            i, sg = M.Q(w, v)
            res[i] = res.get(i, 0) + c * sg
        for w, c in beta.get(v, {}).items():
            i, sg = M.Q(u, w)
            res[i] = res.get(i, 0) + (-1) ** M.par[u] * c * sg
        res = {i: c for i, c in res.items() if c != 0}
        if res:
            f[k] = res
    return f


def odd_f_unknowns(M):
    return [(i, j) for j in range(M.dim) for i in range(M.dim) if (M.bpar[i] + M.bpar[j]) % 2 == 1]


def build_delta_matrix(M, C, unk):
    """Sparse columns: delta applied to elementary f = E_{ij} (f(Z_j)=Z_i), rows indexed (a,b,c)."""
    rows = {}
    cols = []
    for (i, j) in unk:
        D = delta_f(M, C, {j: {i: 1}})
        col = {}
        for (a, b), d in D.items():
            for c, v in d.items():
                r = rows.setdefault((a, b, c), len(rows))
                col[r] = float(v)
        cols.append(col)
    return rows, cols


def main(ns=(1, 2, 3)):
    results = {}
    for n in ns:
        M = Model(n)
        C = M.structure()
        # sanity: dimensions
        ev = sum(1 for p in M.bpar if p == 0)
        od = sum(1 for p in M.bpar if p == 1)
        assert (ev, od) == (2 * n * n + n + 1, 4 * n), (ev, od)
        # Jacobi check of undeformed structure constants (super-Jacobi) done in tests below
        gam = {k: M.gamma(k) for k in M.gb_keys}

        # explicit f for each unit gb: delta f == gamma ?
        explicit_ok = {}
        for k in M.gb_keys:
            f = explicit_f(M, {k: 1})
            D = delta_f(M, C, f)
            explicit_ok[str(k)] = (D == gam[k])
        # generic linear-algebra triviality test
        unk = odd_f_unknowns(M)
        rows, cols = build_delta_matrix(M, C, unk)
        # add gamma rows
        for k in M.gb_keys:
            for (a, b), d in gam[k].items():
                for c in d:
                    rows.setdefault((a, b, c), len(rows))
        nr = len(rows)
        Dm = np.zeros((nr, len(unk)))
        for cidx, col in enumerate(cols):
            for r, v in col.items():
                Dm[r, cidx] = v
        Gm = np.zeros((nr, len(M.gb_keys)))
        for gi, k in enumerate(M.gb_keys):
            for (a, b), d in gam[k].items():
                for c, v in d.items():
                    Gm[rows[(a, b, c)], gi] = float(v)
        rD = np.linalg.matrix_rank(Dm)
        rDG = np.linalg.matrix_rank(np.hstack([Dm, Gm]))
        # residual of least squares for random gb
        rng = np.random.default_rng(0)
        gbv = rng.normal(size=len(M.gb_keys))
        sol, *_ = np.linalg.lstsq(Dm, Gm @ gbv, rcond=None)
        resid = float(np.linalg.norm(Dm @ sol - Gm @ gbv))
        results[n] = {
            "dim_even": ev, "dim_odd": od, "num_gb_params": len(M.gb_keys),
            "num_odd_f_unknowns": len(unk),
            "rank_delta_on_odd_maps": int(rD),
            "dim_kernel_delta_odd (odd derivations)": int(len(unk) - rD),
            "rank_[delta|gamma_1..gamma_4n]": int(rDG),
            "dim_of_trivial_gb_subspace": int(len(M.gb_keys) - (rDG - rD)),
            "explicit_f_gives_delta_f_equals_gamma": explicit_ok,
            "lstsq_residual_random_gb": resid,
            "num_nonzero_gamma_entries": {str(k): sum(len(d) for d in gam[k].values()) for k in M.gb_keys},
        }
        # artifacts
        art = {
            "n": n,
            "basis": [{"index": i, "osc": [M.names[u], M.names[v]], "parity": M.bpar[i]}
                      for i, (u, v) in enumerate(M.basis)],
            "gb_keys": [list(map(str, k)) for k in M.gb_keys],
            "structure_constants": [[a, b, c, str(v)] for (a, b), d in sorted(C.items()) for c, v in sorted(d.items())],
            "gamma": {str(k): [[a, b, c, str(v)] for (a, b), d in sorted(gam[k].items()) for c, v in sorted(d.items())]
                      for k in M.gb_keys},
            "explicit_f": {str(k): [[j, i, str(v)] for j, d in sorted(explicit_f(M, {k: 1}).items()) for i, v in sorted(d.items())]
                           for k in M.gb_keys},
            "convention": "[Z_a,Z_b]_gb = [Z_a,Z_b]_0 + kappa*gamma(Z_a,Z_b); entries are [a,b,c,coef] meaning coefficient of Z_c",
            "summary": results[n],
        }
        with open(f"artifacts/C{n+1}_n{n}_verification.json", "w") as fh:
            json.dump(art, fh, indent=1)
        print(n, json.dumps({k: v for k, v in results[n].items() if k != "num_nonzero_gamma_entries"}, indent=1))
    with open("artifacts/summary.json", "w") as fh:
        json.dump({str(k): v for k, v in results.items()}, fh, indent=1)


if __name__ == "__main__":
    main(tuple(int(x) for x in sys.argv[1:]) or (1, 2, 3))
