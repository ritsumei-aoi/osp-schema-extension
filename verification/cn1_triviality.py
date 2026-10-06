"""
Verification of triviality of the inhomogeneous (gb) deformation of C(n+1)=osp(2|2n).

Model: U(A) with A = V + C K + C kappa, K=1, kappa odd central (kappa^2=0).
g = span of super-Weyl-symmetrised quadratics sym(xy), x,y in V.
Brackets are computed by a generic normal-ordering engine (no ansatz):
  [X_i,X_j] = sum_k c_ij^k X_k + kappa * sum_k gamma_ij^k X_k.
Triviality: gamma = delta f for an odd f (formula of C_coboundary_definition.md),
decided by exact linear algebra (rank over F_p, p = 2^31-1; all entries are dyadic rationals).
"""
import itertools, json, sys
from fractions import Fraction as Fr

P = 2**31 - 1


def build_letters(n):
    L = [("a", "+", 0), ("a", "-", 0)]
    for j in range(1, n + 1):
        L += [("b", "+", j), ("b", "-", j)]
    return L


class Algebra:
    def __init__(self, n, gb):
        """gb: dict (sigma, j, s) -> number, [b_j^s, a^sigma] = -gb * kappa."""
        self.n = n
        self.letters = ["k"] + build_letters(n)  # kappa first in the order
        self.idx = {l: i for i, l in enumerate(self.letters)}
        self.gb = gb

    def par(self, l):
        return 1 if (l == "k" or l[0] == "a") else 0

    def omega(self, x, y):
        """[x,y] for letters in V as (K-scalar, kappa-scalar)."""
        if x == "k" or y == "k":
            return (Fr(0), Fr(0))
        if x[0] == "a" and y[0] == "a":
            return (Fr(1) if x[1] != y[1] else Fr(0), Fr(0))  # {a-,a+}=1
        if x[0] == "b" and y[0] == "b":
            if x[2] != y[2] or x[1] == y[1]:
                return (Fr(0), Fr(0))
            return (Fr(1) if (x[1], y[1]) == ("-", "+") else Fr(-1), Fr(0))
        if x[0] == "b":  # [b_j^s, a^sigma] = -gb kappa
            return (Fr(0), -Fr(self.gb.get((y[1], x[2], x[1]), 0)))
        return (Fr(0), Fr(self.gb.get((x[1], y[2], y[1]), 0)))  # [a,b] = -[b,a]

    def normal(self, elt):
        """Canonical form: letters sorted, kappa first, kappa^2 = 0, odd x^2 = [x,x]/2."""
        out = {}
        stack = list(elt.items())
        while stack:
            w, c = stack.pop()
            if c == 0:
                continue
            dead = False
            reduced = False
            for i in range(len(w) - 1):
                x, y = w[i], w[i + 1]
                ix, iy = self.idx[x], self.idx[y]
                if ix < iy:
                    continue
                pre, suf = w[:i], w[i + 2:]
                if ix == iy:
                    if self.par(x) == 0:
                        continue
                    reduced = True
                    if x == "k":
                        dead = True
                        break
                    k0, k1 = self.omega(x, x)  # x x = 1/2 [x,x]
                    if k0:
                        stack.append((pre + suf, c * Fr(1, 2) * k0))
                    if k1:
                        stack.append((("k",) + pre + suf,
                                      c * Fr(1, 2) * k1 * (-1) ** sum(self.par(t) for t in pre)))
                    break
                reduced = True
                sgn = (-1) ** (self.par(x) * self.par(y))
                stack.append((pre + (y, x) + suf, c * sgn))
                if "k" not in (x, y):
                    k0, k1 = self.omega(x, y)
                    if k0:
                        stack.append((pre + suf, c * k0))
                    if k1:
                        stack.append((("k",) + pre + suf,
                                      c * k1 * (-1) ** sum(self.par(t) for t in pre)))
                break
            if dead:
                continue
            if not reduced:
                out[w] = out.get(w, 0) + c
        return {w: c for w, c in out.items() if c != 0}

    def mul(self, A, B):
        r = {}
        for w1, c1 in A.items():
            for w2, c2 in B.items():
                r[w1 + w2] = r.get(w1 + w2, 0) + c1 * c2
        return self.normal(r)

    def add(self, A, B, cb=1):
        r = dict(A)
        for w, c in B.items():
            r[w] = r.get(w, 0) + cb * c
        return {w: c for w, c in r.items() if c != 0}

    def sym(self, x, y):
        e = {(x, y): Fr(1, 2)}
        e[(y, x)] = e.get((y, x), 0) + Fr(1, 2) * (-1) ** (self.par(x) * self.par(y))
        return self.normal(e)

    def bracket(self, A, B, pA, pB):
        return self.add(self.mul(A, B), self.mul(B, A), -(-1) ** (pA * pB))


def g_basis(n):
    B = []
    for x, y in itertools.combinations_with_replacement(build_letters(n), 2):
        if x[0] == "a" and y[0] == "a" and x[1] == y[1]:
            continue
        B.append((x, y))
    return B


def structure(n, gb):
    """Return basis, parity, {(i,j): (K-part {k:val}, kappa-part {k:val})}."""
    alg = Algebra(n, gb)
    basis = g_basis(n)
    N = len(basis)
    par = [(alg.par(x) + alg.par(y)) % 2 for x, y in basis]
    elts = [alg.sym(x, y) for x, y in basis]
    pos = {}
    for i, (x, y) in enumerate(basis):
        pos[(x, y)] = i
        pos[(y, x)] = i

    def expand(elt):
        """Canonical words -> coordinates in sym-basis; ordered xy = sym(xy) + [x,y]/2.
        Raises if constants / non-quadratic terms survive (closure check)."""
        K, kap = {}, {}
        const = 0   # K-scalar
        constk = 0  # kappa * scalar
        for w, c in elt.items():
            has_k = bool(w) and w[0] == "k"
            ww = w[1:] if has_k else w
            tgt = kap if has_k else K
            if len(ww) == 2:
                x, y = ww
                i = pos[(x, y)]
                tgt[i] = tgt.get(i, 0) + c
                if x != y:
                    k0, k1 = alg.omega(x, y)
                    if has_k:
                        constk += c * Fr(1, 2) * k0
                    else:
                        const += c * Fr(1, 2) * k0
                        constk += c * Fr(1, 2) * k1
            elif len(ww) == 0:
                if has_k:
                    constk += c
                else:
                    const += c
            else:
                raise ValueError(f"non-quadratic term {w}")
        if const != 0 or constk != 0:
            raise ValueError(f"constant leftover {const},{constk}")
        return ({k: v for k, v in K.items() if v}, {k: v for k, v in kap.items() if v})

    S = {}
    for i in range(N):
        for j in range(N):
            br = alg.bracket(elts[i], elts[j], par[i], par[j])
            K, kap = expand(br)
            if K or kap:
                S[(i, j)] = (K, kap)
    return basis, par, S


def label(b):
    f = lambda l: f"{l[0]}{l[2] if l[0] == 'b' else 1}^{l[1]}"
    return f"{f(b[0])}*{f(b[1])}"


def modrank(vecs):
    """Rank over F_P of a list of sparse vectors (dict col->Fraction)."""
    def red(v):
        v = Fr(v)
        return (v.numerator * pow(v.denominator, -1, P)) % P
    piv, r = {}, 0
    for row in vecs:
        v = {c: red(x) for c, x in row.items()}
        v = {c: x for c, x in v.items() if x}
        while v:
            c = min(v)
            if c in piv:
                f = v[c]
                for cc, xx in piv[c].items():
                    nv = (v.get(cc, 0) - f * xx) % P
                    if nv:
                        v[cc] = nv
                    else:
                        v.pop(cc, None)
            else:
                inv = pow(v[c], -1, P)
                piv[c] = {cc: xx * inv % P for cc, xx in v.items()}
                r += 1
                break
    return r


def delta_columns(N, par, c0):
    """delta as a linear map phi -> delta f. Returns (unknowns, rows{(i,j,k):{u:coef}})."""
    unk = [(k, m) for k in range(N) for m in range(N) if par[k] != par[m]]
    uidx = {u: t for t, u in enumerate(unk)}
    br = lambda i, j: c0.get((i, j), {})
    rows = {}

    def addrow(key, u, v):
        if v:
            d = rows.setdefault(key, {})
            d[u] = d.get(u, 0) + v

    for i in range(N):
        for j in range(N):
            pi, pj = par[i], par[j]
            s1 = (-1) ** pi
            s2 = (-1) ** ((pi + 1) * pj)
            for m in range(N):  # (-1)^{p(X)} [X, f(Y)]
                if par[m] != pj:
                    for k, v in br(i, m).items():
                        addrow((i, j, k), uidx[(m, j)], s1 * v)
            for m in range(N):  # -(-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                if par[m] != pi:
                    for k, v in br(j, m).items():
                        addrow((i, j, k), uidx[(m, i)], -s2 * v)
            for l, v in br(i, j).items():  # - f([X,Y])
                for k in range(N):
                    if par[k] != par[l]:
                        addrow((i, j, k), uidx[(k, l)], -v)
    return unk, rows


def analyse(n):
    names = [(s, j, t) for j in range(1, n + 1) for s in "+-" for t in "+-"]
    basis, par, S0 = structure(n, {})
    N = len(basis)
    gam = {}
    for nm in names:
        _, _, S = structure(n, {nm: 1})
        d = {}
        for (i, j), (K, kap) in S.items():
            assert K == S0.get((i, j), ({}, {}))[0], "K-part must be gb independent"
            for k, v in kap.items():
                d[(i, j, k)] = v
        gam[nm] = d
    c0 = {ij: K for ij, (K, kap) in S0.items()}
    unk, rows = delta_columns(N, par, c0)
    keys = sorted(set(rows) | {k for g in gam.values() for k in g})
    kidx = {k: t for t, k in enumerate(keys)}
    cols_delta = [dict() for _ in unk]
    for key, d in rows.items():
        for u, v in d.items():
            cols_delta[u][kidx[key]] = v
    cols_gam = [{kidx[k]: v for k, v in gam[nm].items()} for nm in names]
    r_delta = modrank(cols_delta)
    r_gam = modrank(cols_gam)
    r_both = modrank(cols_delta + cols_gam)
    inter = r_delta + r_gam - r_both
    res = dict(n=n, dim_even=par.count(0), dim_odd=sum(par), N=N, n_gb=len(names),
               n_unknown_phi=len(unk), rank_delta=r_delta, rank_gamma=r_gam,
               rank_joint=r_both, dim_trivial_gb_subspace=inter,
               all_gb_trivial=(inter == r_gam == len(names)))
    ctx = dict(basis=basis, par=par, c0=c0, gam=gam, names=names, unk=unk,
               rows=rows, keys=keys, kidx=kidx)
    return res, ctx


if __name__ == "__main__":
    for n in [int(a) for a in sys.argv[1:]] or [1, 2]:
        res, _ = analyse(n)
        print(json.dumps(res), flush=True)
