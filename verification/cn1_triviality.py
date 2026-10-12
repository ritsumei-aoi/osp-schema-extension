"""Triviality of the inhomogeneous (gb) deformation of C(n+1) = osp(2|2n).

Everything is computed from first principles in the universal enveloping
algebra U(A) of the Heisenberg-type superalgebra

    A = span{a^+, a^-, b_j^+, b_j^-} + C K + C kappa      (K even, kappa odd central)

with K set to 1, and the (deformed) brackets of generators

    [b_j^-, b_l^+] = delta_{jl},   {a^-, a^+} = 1,
    [b_j^s, a^sigma] = -gb_{sigma,j,s} kappa,  [a^sigma, b_j^s] = +gb_{sigma,j,s} kappa,

all other brackets of generators being zero (in particular kappa^2 = 0).

Pipeline (for each n and each basis convention):
  1. PBW normal ordering in U(A) with exact rational coefficients that are
     polynomials in the gb parameters.
  2. Realize g = C(n+1) as quadratic elements; compute the deformed bracket
     [Z_a, Z_b] = sum_k C_ab^k Z_k + kappa * sum_k gamma_ab^k Z_k + (scalars in C1 + C kappa).
     The scalar part is central in U(A) and is discarded ("up to scalar").
  3. Check closure, gb-independence of C, the 2-cocycle condition for gamma.
  4. Solve gamma = delta f for an odd linear map f (exact sparse elimination),
     for each of the 4n elementary gb directions, and report the rank /
     kernel of delta on odd 1-cochains.
  5. Independently verify the closed-form f obtained from the oscillator
     redefinition  a^sigma -> a^sigma + kappa * lambda_sigma(b).
  6. Dump everything as JSON.
"""

from __future__ import annotations

import itertools
import json
import os
import sys
from fractions import Fraction
from functools import lru_cache

# ---------------------------------------------------------------------------
# Exact polynomial coefficients in the gb parameters
# A coefficient is a dict {monomial: Fraction}, monomial = sorted tuple of gb indices.
# ---------------------------------------------------------------------------


def c_const(x):
    x = Fraction(x)
    return {(): x} if x else {}


def c_add(p, q, s=1):
    r = dict(p)
    for m, v in q.items():
        r[m] = r.get(m, 0) + s * v
        if r[m] == 0:
            del r[m]
    return r


def c_mul(p, q):
    r = {}
    for m1, v1 in p.items():
        for m2, v2 in q.items():
            m = tuple(sorted(m1 + m2))
            r[m] = r.get(m, 0) + v1 * v2
            if r[m] == 0:
                del r[m]
    return r


def c_scale(p, s):
    s = Fraction(s)
    return {m: v * s for m, v in p.items()} if s else {}


# ---------------------------------------------------------------------------
# U(A) with K = 1
# ---------------------------------------------------------------------------


class Model:
    def __init__(self, n, gb_values=None):
        """gb_values: None -> symbolic gb (index m <-> gb label);
        otherwise a dict label -> Fraction (numerical specialisation)."""
        self.n = n
        self.gens = ["k", "ap", "am"] + [f"b{j}{s}" for j in range(1, n + 1) for s in "pm"]
        self.order = {g: i for i, g in enumerate(self.gens)}
        self.parity = {g: (1 if g in ("k", "ap", "am") else 0) for g in self.gens}
        # gb labels: (sigma, j, s) with sigma, s in {'+','-'}
        self.gb_labels = [(sg, j, s) for sg in "+-" for j in range(1, n + 1) for s in "+-"]
        self.gb_index = {lab: i for i, lab in enumerate(self.gb_labels)}
        self.gb_values = gb_values

    def gb(self, sigma, j, s):
        lab = (sigma, j, s)
        if self.gb_values is None:
            return {(self.gb_index[lab],): Fraction(1)}
        return c_const(self.gb_values.get(lab, 0))

    # bracket of two generators -> element (dict word -> coeff), central
    def gen_bracket(self, u, v):
        if u == "k" or v == "k":
            return {}
        if u in ("ap", "am") and v in ("ap", "am"):
            return {(): c_const(1)} if u != v else {}
        if u[0] == "b" and v[0] == "b":
            ju, su, jv, sv = int(u[1:-1]), u[-1], int(v[1:-1]), v[-1]
            if ju != jv or su == sv:
                return {}
            return {(): c_const(1 if su == "m" else -1)}
        # mixed b / a
        if u[0] == "b":
            j, s, sigma = int(u[1:-1]), u[-1], v[1]
            g = self.gb("+" if sigma == "p" else "-", j, "+" if s == "p" else "-")
            return {("k",): c_scale(g, -1)} if g else {}
        j, s, sigma = int(v[1:-1]), v[-1], u[1]
        g = self.gb("+" if sigma == "p" else "-", j, "+" if s == "p" else "-")
        return {("k",): g} if g else {}

    @lru_cache(maxsize=None)
    def normal_order(self, word):
        """Return normal-ordered form of a word as tuple of (word, coeff-items)."""
        w = list(word)
        for i in range(len(w) - 1):
            u, v = w[i], w[i + 1]
            if u == v and self.parity[u] == 1:
                # u u = (1/2)[u,u]; all such brackets vanish here
                return ()
            if self.order[u] > self.order[v]:
                sign = -1 if (self.parity[u] and self.parity[v]) else 1
                res = {}
                swapped = tuple(w[:i] + [v, u] + w[i + 2 :])
                _acc(res, self.normal_order(swapped), c_const(sign))
                for cw, cc in self.gen_bracket(u, v).items():
                    new = tuple(w[:i]) + cw + tuple(w[i + 2 :])
                    _acc(res, self.normal_order(new), cc)
                return tuple((k, tuple(sorted(v.items()))) for k, v in res.items() if v)
        return ((tuple(w), ((((), Fraction(1)),))),)

    # elements: dict word -> coeff
    def elem(self, *words_coeffs):
        e = {}
        for word, c in words_coeffs:
            _acc(e, self.normal_order(tuple(word)), c_const(c))
        return e

    def mul(self, x, y):
        res = {}
        for w1, c1 in x.items():
            for w2, c2 in y.items():
                _acc(res, self.normal_order(w1 + w2), c_mul(c1, c2))
        return res

    def sbracket(self, x, px, y, py):
        s = -1 if (px and py) else 1
        return e_add(self.mul(x, y), self.mul(y, x), -s)


def _acc(res, nf, coeff):
    if not coeff:
        return
    for w, citems in nf:
        c = c_mul(dict(citems), coeff)
        if c:
            res[w] = c_add(res.get(w, {}), c)
            if not res[w]:
                del res[w]


def e_add(x, y, s=1):
    r = dict(x)
    for w, c in y.items():
        r[w] = c_add(r.get(w, {}), c, s)
        if not r[w]:
            del r[w]
    return r


def e_scale(x, coeff):
    r = {}
    for w, c in x.items():
        cc = c_mul(c, coeff)
        if cc:
            r[w] = cc
    return r


# ---------------------------------------------------------------------------
# Bases of g = C(n+1) inside U(A)
# ---------------------------------------------------------------------------


def bname(g):
    if g == "ap":
        return "a+"
    if g == "am":
        return "a-"
    return f"b{g[1:-1]}{'+' if g[-1] == 'p' else '-'}"


def basis_symmetrized(M):
    """Super-symmetrized quadratics S(xy) = (xy + (-1)^{p(x)p(y)} yx)/2."""
    n = M.n
    bgens = [f"b{j}{s}" for j in range(1, n + 1) for s in "pm"]
    B = []
    for i, x in enumerate(bgens):
        for y in bgens[i:]:
            B.append((f"S({bname(x)}{bname(y)})", M.elem(((x, y), Fraction(1, 2)), ((y, x), Fraction(1, 2))), 0))
    B.append(("S(a+a-)", M.elem((("ap", "am"), Fraction(1, 2)), (("am", "ap"), Fraction(-1, 2))), 0))
    for a in ("ap", "am"):
        for y in bgens:
            B.append((f"S({bname(a)}{bname(y)})", M.elem(((a, y), Fraction(1, 2)), ((y, a), Fraction(1, 2))), 1))
    return B


def basis_cn1(M):
    """Literal generators of docs/math/Cn1_definition.md (products, with the -1/2 shift)."""
    n = M.n
    bp = lambda k: f"b{k}p"
    bm = lambda k: f"b{k}m"
    B = []
    # Cartan
    B.append(("H1", M.elem((("ap", "am"), 1), ((bp(1), bm(1)), 1)), 0))
    for k in range(2, n + 1):
        B.append((f"H{k}", M.elem(((bp(k - 1), bm(k - 1)), 1), ((bp(k), bm(k)), -1)), 0))
    B.append((f"H{n+1}", M.elem(((bp(n), bm(n)), -1), ((), Fraction(-1, 2))), 0))
    # sp(2n) root vectors
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                B.append((f"E(d{k}-d{l})", M.elem(((bp(k), bm(l)), 1)), 0))
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            B.append((f"E(d{k}+d{l})", M.elem(((bp(k), bp(l)), 1)), 0))
            B.append((f"E(-d{k}-d{l})", M.elem(((bm(k), bm(l)), 1)), 0))
    for k in range(1, n + 1):
        B.append((f"E(2d{k})", M.elem(((bp(k), bp(k)), 1)), 0))
        B.append((f"E(-2d{k})", M.elem(((bm(k), bm(k)), 1)), 0))
    # odd root vectors E_{+-eps +- d_l} = a^{+-} b_l^{+-}
    for a, es in (("ap", "eps"), ("am", "-eps")):
        for l in range(1, n + 1):
            B.append((f"E({es}+d{l})", M.elem(((a, bp(l)), 1)), 1))
            B.append((f"E({es}-d{l})", M.elem(((a, bm(l)), 1)), 1))
    return B


# ---------------------------------------------------------------------------
# Decomposition of an element of U(A) into  sum c_i Z_i + kappa sum d_i Z_i + scalars
# ---------------------------------------------------------------------------


class Decomposer:
    def __init__(self, M, B):
        self.M, self.B = M, B
        self.N = len(B)
        # leading (kappa-free, degree-2) part of each basis element, gb-independent
        self.qwords = sorted({w for (_, e, _) in B for w in e if len(w) == 2 and "k" not in w})
        mat = []
        for (_, e, _) in B:
            row = []
            for w in self.qwords:
                c = e.get(w, {})
                assert set(c) <= {()}, "leading part must be gb-independent"
                row.append(c.get((), Fraction(0)))
            mat.append(row)
        # invert the N x N (square) leading matrix: qwords count must equal N
        assert len(self.qwords) == self.N, (len(self.qwords), self.N)
        self.inv = mat_inverse([list(r) for r in zip(*mat)])  # columns = basis elements

    def coords(self, e_words):
        """e_words: dict qword -> coeff (polynomial). Return list of coefficients (polys)."""
        vec = [e_words.get(w, {}) for w in self.qwords]
        out = []
        for i in range(self.N):
            acc = {}
            for j, v in enumerate(vec):
                if v and self.inv[i][j]:
                    acc = c_add(acc, c_scale(v, self.inv[i][j]))
            out.append(acc)
        return out

    def decompose(self, x):
        M = self.M
        lead = {w: c for w, c in x.items() if len(w) == 2 and w[0] != "k"}
        c = self.coords(lead)
        r = dict(x)
        for i, ci in enumerate(c):
            if ci:
                r = e_add(r, e_scale(self.B[i][1], ci), -1)
        kpart = {w[1:]: cc for w, cc in r.items() if len(w) == 3 and w[0] == "k"}
        d = self.coords(kpart)
        kappa = {("k",): c_const(1)}
        for i, di in enumerate(d):
            if di:
                r = e_add(r, e_scale(M.mul(kappa, self.B[i][1]), di), -1)
        # what remains must be central scalars: words () or ("k",); anything else
        # is reported as a closure failure (returned, not asserted)
        bad = sorted(w for w in r if w not in ((), ("k",)))
        central = {w: cc for w, cc in r.items() if w in ((), ("k",))}
        return c, d, central, bad


def mat_inverse(A):
    n = len(A)
    M = [list(map(Fraction, row)) + [Fraction(int(i == j)) for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col] != 0)
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [v / pv for v in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [a - f * b for a, b in zip(M[r], M[col])]
    return [row[n:] for row in M]


# ---------------------------------------------------------------------------
# Sparse exact linear algebra
# ---------------------------------------------------------------------------


def sparse_solve(rows, nvars, nrhs):
    """rows: list of (dict var->Fraction, [rhs_0..rhs_{nrhs-1}]).
    Returns (rank, consistent flags per rhs, particular solutions per rhs (dict), pivots)."""
    pivots = {}  # var -> (row dict, rhs list), row normalised with coeff 1 at var
    inconsistent = [False] * nrhs
    for coeffs, rhs in rows:
        coeffs = dict(coeffs)
        rhs = list(rhs)
        # reduce against existing pivots
        changed = True
        while True:
            hit = next((v for v in coeffs if v in pivots), None)
            if hit is None:
                break
            f = coeffs[hit]
            prow, prhs = pivots[hit]
            for v, a in prow.items():
                nv = coeffs.get(v, 0) - f * a
                if nv:
                    coeffs[v] = nv
                else:
                    coeffs.pop(v, None)
            rhs = [r - f * pr for r, pr in zip(rhs, prhs)]
        if not coeffs:
            for t in range(nrhs):
                if rhs[t] != 0:
                    inconsistent[t] = True
            continue
        v0 = min(coeffs)
        a0 = coeffs[v0]
        coeffs = {v: a / a0 for v, a in coeffs.items()}
        rhs = [r / a0 for r in rhs]
        # eliminate v0 from existing pivot rows (keep fully reduced)
        for pv, (prow, prhs) in pivots.items():
            if v0 in prow:
                f = prow[v0]
                for v, a in coeffs.items():
                    nv = prow.get(v, 0) - f * a
                    if nv:
                        prow[v] = nv
                    else:
                        prow.pop(v, None)
                pivots[pv] = (prow, [r - f * x for r, x in zip(prhs, rhs)])
        pivots[v0] = (coeffs, rhs)
    sols = []
    for t in range(nrhs):
        sol = {}
        for pv, (prow, prhs) in pivots.items():
            if prhs[t] != 0:
                sol[pv] = prhs[t]  # free variables set to 0
        sols.append(sol)
    return len(pivots), [not x for x in inconsistent], sols


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------


def poly_to_str(p, labels):
    if not p:
        return "0"
    terms = []
    for m, v in sorted(p.items()):
        mon = "*".join(f"gb[{labels[i][0]},{labels[i][1]},{labels[i][2]}]" for i in m)
        terms.append(f"({v})" + (f"*{mon}" if mon else ""))
    return " + ".join(terms)


def linear_part(p, m):
    return p.get((m,), Fraction(0))


def analyse(n, basis_kind):
    M = Model(n)
    B = basis_symmetrized(M) if basis_kind == "symmetrized" else basis_cn1(M)
    N = len(B)
    par = [b[2] for b in B]
    names = [b[0] for b in B]
    D = Decomposer(M, B)
    G = len(M.gb_labels)

    C = [[None] * N for _ in range(N)]  # structure constants (Fractions)
    GAM = [[None] * N for _ in range(N)]  # gamma coefficients (polys)
    SCAL = [[None] * N for _ in range(N)]  # discarded central scalars
    closure_failures = 0  # pairs whose bracket leaves non-central words outside g + kappa*g
    gb_dependent_C = 0  # pairs whose undeformed coefficients depend on gb
    nonlinear_gamma = 0  # pairs whose kappa-coefficients are not homogeneous linear in gb
    for a in range(N):
        for b in range(N):
            br = M.sbracket(B[a][1], par[a], B[b][1], par[b])
            c, d, r, bad = D.decompose(br)
            if bad:
                closure_failures += 1
            if any(set(ci) - {()} for ci in c):
                gb_dependent_C += 1
            C[a][b] = [ci.get((), Fraction(0)) for ci in c]
            if any(len(m) != 1 for di in d for m in di):
                nonlinear_gamma += 1
            GAM[a][b] = d
            SCAL[a][b] = r

    # C must equal the bracket computed with gb = 0 (and gamma must vanish there)
    M0 = Model(n, gb_values={})
    B0 = basis_symmetrized(M0) if basis_kind == "symmetrized" else basis_cn1(M0)
    D0 = Decomposer(M0, B0)
    mismatch_gb0 = 0
    for a in range(N):
        for b in range(N):
            c0, d0, _, bad0 = D0.decompose(M0.sbracket(B0[a][1], par[a], B0[b][1], par[b]))
            if bad0 or [x.get((), 0) for x in c0] != C[a][b] or any(d0):
                mismatch_gb0 += 1
    closure_ok = closure_failures == 0
    undeformed_ok = gb_dependent_C == 0 and mismatch_gb0 == 0
    linear_ok = nonlinear_gamma == 0

    # dimension checks
    n_even = sum(1 for p in par if p == 0)
    n_odd = N - n_even
    assert (n_even, n_odd) == (2 * n * n + n + 1, 4 * n)

    # super Jacobi for C (sanity of the undeformed algebra)
    def br_vec(u, pu, v, pv):  # u,v coordinate vectors (dict idx->Fraction), homogeneous
        out = {}
        for i, x in u.items():
            for j, y in v.items():
                for k, z in enumerate(C[i][j]):
                    if z:
                        out[k] = out.get(k, 0) + x * y * z
        return {k: v for k, v in out.items() if v}

    jac_ok = True
    for a, b, c in itertools.product(range(N), repeat=3):
        pa, pb, pc = par[a], par[b], par[c]
        t1 = br_vec({a: 1}, pa, br_vec({b: 1}, pb, {c: 1}, pc), (pb + pc) % 2)
        t2 = br_vec(br_vec({a: 1}, pa, {b: 1}, pb), (pa + pb) % 2, {c: 1}, pc)
        t3 = br_vec({b: 1}, pb, br_vec({a: 1}, pa, {c: 1}, pc), (pa + pc) % 2)
        s = (-1) ** (pa * pb)
        for k in set(t1) | set(t2) | set(t3):
            if t1.get(k, 0) - t2.get(k, 0) - s * t3.get(k, 0) != 0:
                jac_ok = False
    # gamma matrices per elementary gb direction
    gam_m = [[[[linear_part(GAM[a][b][k], m) for k in range(N)] for b in range(N)] for a in range(N)] for m in range(G)]

    # 2-cocycle condition for gamma: super-Jacobi of [ , ]_0 + kappa*gamma on L = g + kappa g
    # at first order in kappa (kappa odd, central, kappa^2 = 0).
    cocycle_ok = True
    for m in range(G):
        g = gam_m[m]
        # Jacobi at first order in kappa for basis triples, with
        # [X,Y]_t = [X,Y] + kappa*gamma(X,Y), kappa odd central:
        # [X,[Y,Z]_t]_t = [X,[Y,Z]] + kappa*( gamma(X,[Y,Z]) + (-1)^{p(X)} [X, gamma(Y,Z)] )
        def first(a, bvec):  # [Z_a, kappa*V]_t first-order coefficient vector (V in coords)
            out = {}
            for j, y in bvec.items():
                for k, z in enumerate(C[a][j]):
                    if z:
                        out[k] = out.get(k, 0) + (-1) ** par[a] * y * z
            return out

        def gam_left(a, bvec):  # gamma(Z_a, V)
            out = {}
            for j, y in bvec.items():
                for k, z in enumerate(g[a][j]):
                    if z:
                        out[k] = out.get(k, 0) + y * z
            return out

        def gam_right(avec, c):  # gamma(U, Z_c)
            out = {}
            for i, x in avec.items():
                for k, z in enumerate(g[i][c]):
                    if z:
                        out[k] = out.get(k, 0) + x * z
            return out

        def kappa_left(avec, c):  # [kappa*U, Z_c] = kappa*[U, Z_c]
            out = {}
            for i, x in avec.items():
                for k, z in enumerate(C[i][c]):
                    if z:
                        out[k] = out.get(k, 0) + x * z
            return out

        for a, b, c in itertools.product(range(N), repeat=3):
            pa, pb = par[a], par[b]
            bc = {k: v for k, v in enumerate(C[b][c]) if v}
            ab = {k: v for k, v in enumerate(C[a][b]) if v}
            ac = {k: v for k, v in enumerate(C[a][c]) if v}
            gbc = {k: v for k, v in enumerate(g[b][c]) if v}
            gab = {k: v for k, v in enumerate(g[a][b]) if v}
            gac = {k: v for k, v in enumerate(g[a][c]) if v}
            t1 = _vadd(gam_left(a, bc), first(a, gbc))
            t2 = _vadd(gam_right(ab, c), kappa_left(gab, c))
            # [Z_b, [Z_a, Z_c]_t]_t
            t3 = _vadd(gam_left(b, ac), first(b, gac))
            s = (-1) ** (pa * pb)
            for k in set(t1) | set(t2) | set(t3):
                if t1.get(k, 0) - t2.get(k, 0) - s * t3.get(k, 0) != 0:
                    cocycle_ok = False
                    break
            if not cocycle_ok:
                break

    # ---- Solve gamma = delta f for odd f -----------------------------------
    # unknowns phi[i][j] (f(Z_j) = sum_i phi_ij Z_i), only par[i] != par[j]
    var_index = {}
    for j in range(N):
        for i in range(N):
            if par[i] != par[j]:
                var_index[(i, j)] = len(var_index)
    rows_keys = []
    for a in range(N):
        for b in range(N):
            pa, pb = par[a], par[b]
            eqs = {}  # k -> dict var->coef
            # (-1)^{pa} [Z_a, f Z_b] = (-1)^{pa} sum_i phi_ib C[a][i]
            for i in range(N):
                if par[i] == pb:
                    continue
                v = var_index[(i, b)]
                for k, z in enumerate(C[a][i]):
                    if z:
                        eqs.setdefault(k, {})
                        eqs[k][v] = eqs[k].get(v, 0) + (-1) ** pa * z
            # -(-1)^{(pa+1)pb} [Z_b, f Z_a]
            sgn = -((-1) ** ((pa + 1) * pb))
            for i in range(N):
                if par[i] == pa:
                    continue
                v = var_index[(i, a)]
                for k, z in enumerate(C[b][i]):
                    if z:
                        eqs.setdefault(k, {})
                        eqs[k][v] = eqs[k].get(v, 0) + sgn * z
            # - f([Z_a,Z_b]) = - sum_m C[a][b][m] sum_k phi_km Z_k
            for mm, z in enumerate(C[a][b]):
                if z:
                    for k in range(N):
                        if par[k] != par[mm]:
                            v = var_index[(k, mm)]
                            eqs.setdefault(k, {})
                            eqs[k][v] = eqs[k].get(v, 0) - z
            for k in range(N):
                coeffs = {v: x for v, x in eqs.get(k, {}).items() if x}
                rhs = [gam_m[m][a][b][k] for m in range(G)]
                rows_keys.append((coeffs, rhs, (a, b, k)))
    nvars = len(var_index)
    # negative controls: elementary odd, super-antisymmetric cochains
    #   eta(Z_a,Z_b) = Z_k, eta(Z_b,Z_a) = -(-1)^{p_a p_b} Z_k   (p_k = p_a + p_b + 1)
    import random

    rng = random.Random(20261006 + n)
    controls = []
    while len(controls) < 5:
        a, b, k = rng.randrange(N), rng.randrange(N), rng.randrange(N)
        if a != b and par[k] == (par[a] + par[b] + 1) % 2:
            controls.append((a, b, k))
    ctrl_rhs = {}
    for t, (a, b, k) in enumerate(controls):
        ctrl_rhs[(a, b, k, t)] = Fraction(1)
        ctrl_rhs[(b, a, k, t)] = -Fraction((-1) ** (par[a] * par[b]))
    rows_ext = []
    used = set()
    for coeffs, rhs, key in rows_keys:
        extra = [ctrl_rhs.get(key + (t,), Fraction(0)) for t in range(len(controls))]
        rows_ext.append((coeffs, rhs + extra))
        used.add(key)
    for (a, b, k, t), v in ctrl_rhs.items():
        if (a, b, k) not in used:  # equation with no unknowns but nonzero rhs
            extra = [Fraction(0)] * len(controls)
            extra[t] = v
            rows_ext.append(({}, [Fraction(0)] * G + extra))
    rank, consistent_all, sols = sparse_solve(rows_ext, nvars, G + len(controls))
    consistent, ctrl_consistent = consistent_all[:G], consistent_all[G:]
    rows = rows_ext
    inv_var = {v: ij for ij, v in var_index.items()}

    # ---- Closed-form f from the oscillator redefinition ---------------------
    # a^sigma = atilde^sigma - kappa*lambda_sigma,
    # lambda_sigma = sum_j ( gb_{sigma,j,-} b_j^+ - gb_{sigma,j,+} b_j^- ).
    # Z_i(a,b) = Z_i(atilde,b) + kappa*H_i ;  f = h where H_i = sum_j h_ji Z_j (+ scalars).
    # (Z~_i := Z_i - kappa*H_i obey the undeformed brackets, whence gamma = delta h.)
    closed_ok = []
    closed_f = []
    for m in range(G):
        sg, j0, s0 = M.gb_labels[m]
        vals = {M.gb_labels[m]: Fraction(1)}
        Mm = Model(n, gb_values=vals)
        Bm = basis_symmetrized(Mm) if basis_kind == "symmetrized" else basis_cn1(Mm)
        Dm = Decomposer(Mm, Bm)
        lam = {}
        for sigma in "+-":
            terms = []
            for j in range(1, n + 1):
                gm = vals.get((sigma, j, "-"), 0)
                gp = vals.get((sigma, j, "+"), 0)
                if gm:
                    terms.append(((f"b{j}p",), gm))
                if gp:
                    terms.append(((f"b{j}m",), -gp))
            lam[sigma] = Mm.elem(*terms) if terms else {}
        kap = {("k",): c_const(1)}
        # build the tilde-generator substitution: a^sigma -> a^sigma + kappa*lambda_sigma gives atilde
        # The kappa-linear part of Z_i(a) - Z_i(atilde) is obtained by substituting
        # a = atilde - kappa*lambda in the defining word expression of Z_i.
        fmat = [[Fraction(0)] * N for _ in range(N)]
        defs = basis_definitions(n, basis_kind)
        for i, terms in enumerate(defs):
            # Z_i(a) - Z_i(atilde) where atilde = a + kappa*lambda : first-order difference
            diff = {}
            for word, coef in terms:
                # replace each a-letter in turn by (-kappa*lambda) [first order]
                for pos, letter in enumerate(word):
                    if letter in ("ap", "am"):
                        sigma = "+" if letter == "ap" else "-"
                        left = Mm.elem((word[:pos], 1))
                        right = Mm.elem((word[pos + 1 :], 1))
                        mid = e_scale(Mm.mul(kap, lam[sigma]), c_const(-1))
                        diff = e_add(diff, e_scale(Mm.mul(Mm.mul(left, mid), right), c_const(coef)))
            # Z_i(a) = Z_i(atilde) + diff, diff = kappa*H_i
            if diff:
                kp = {w[1:]: cc for w, cc in diff.items() if len(w) == 3 and w[0] == "k"}
                h = Dm.coords(kp)
                for jj in range(N):
                    fmat[jj][i] = h[jj].get((), Fraction(0))
        closed_f.append(fmat)
        # verify gamma = delta f with this f
        ok = True
        for a in range(N):
            for b in range(N):
                pa, pb = par[a], par[b]
                lhs = [Fraction(0)] * N
                for i in range(N):
                    if fmat[i][b]:
                        for k, z in enumerate(C[a][i]):
                            lhs[k] += (-1) ** pa * fmat[i][b] * z
                    if fmat[i][a]:
                        for k, z in enumerate(C[b][i]):
                            lhs[k] -= (-1) ** ((pa + 1) * pb) * fmat[i][a] * z
                for mm, z in enumerate(C[a][b]):
                    if z:
                        for k in range(N):
                            lhs[k] -= z * fmat[k][mm]
                if lhs != gam_m[m][a][b]:
                    ok = False
        closed_ok.append(ok)

    # injectivity of gb -> gamma (are distinct gb giving distinct cochains?)
    gvecs = []
    for m in range(G):
        vec = {}
        for a in range(N):
            for b in range(N):
                for k in range(N):
                    if gam_m[m][a][b][k]:
                        vec[(a, b, k)] = gam_m[m][a][b][k]
        gvecs.append(vec)
    keys = sorted(set().union(*[set(v) for v in gvecs]))
    kidx = {k: i for i, k in enumerate(keys)}
    rank_gb, _, _ = sparse_solve([({kidx[k]: x for k, x in v.items()}, []) for v in gvecs], len(keys), 0)

    nonzero_scalars = sum(1 for a in range(N) for b in range(N) if SCAL[a][b])
    kappa_scalars = sum(1 for a in range(N) for b in range(N) if ("k",) in SCAL[a][b])

    result = {
        "n": n,
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "basis_kind": basis_kind,
        "dim_even": n_even,
        "dim_odd": n_odd,
        "basis": [{"index": i, "name": names[i], "parity": par[i]} for i in range(N)],
        "gb_labels": [f"gb[{s},{j},{t}]" for (s, j, t) in M.gb_labels],
        "structure_constants": {
            f"{a},{b}": {str(k): str(z) for k, z in enumerate(C[a][b]) if z} for a in range(N) for b in range(N) if any(C[a][b])
        },
        "gamma": {
            f"{a},{b}": {str(k): poly_to_str(GAM[a][b][k], M.gb_labels) for k in range(N) if GAM[a][b][k]}
            for a in range(N)
            for b in range(N)
            if any(GAM[a][b])
        },
        "discarded_central_scalars": {
            f"{a},{b}": {("1" if w == () else "kappa"): poly_to_str(c, M.gb_labels) for w, c in SCAL[a][b].items()}
            for a in range(N)
            for b in range(N)
            if SCAL[a][b]
        },
        "checks": {
            "closure_mod_center": closure_ok,
            "pairs_failing_closure": closure_failures,
            "undeformed_part_gb_independent": undeformed_ok,
            "pairs_with_gb_dependent_undeformed_part": gb_dependent_C,
            "pairs_mismatching_gb0_computation": mismatch_gb0,
            "gamma_linear_in_gb": linear_ok,
            "pairs_with_nonlinear_gamma": nonlinear_gamma,
            "super_jacobi_undeformed": jac_ok,
            "gamma_2cocycle_condition": cocycle_ok,
            "rank_gb_to_gamma": rank_gb,
            "gb_to_gamma_injective": rank_gb == G,
            "pairs_with_nonzero_discarded_scalars": nonzero_scalars,
            "pairs_with_kappa_scalar": kappa_scalars,
        },
        "coboundary_system": {
            "num_odd_unknowns_phi": nvars,
            "num_equations": len(rows),
            "rank_delta_on_odd_1cochains": rank,
            "dim_kernel_delta_odd": nvars - rank,
            "negative_controls": [
                {"cochain": f"eta(Z_{a},Z_{b}) = Z_{k} (super-antisymmetrized)", "is_coboundary": ctrl_consistent[t]}
                for t, (a, b, k) in enumerate(controls)
            ],
            "solvable_for_each_elementary_gb": {f"gb[{s},{j},{t}]": consistent[m] for m, (s, j, t) in enumerate(M.gb_labels)},
            "particular_solution_phi_per_gb": {
                f"gb[{s},{j},{t}]": {f"{inv_var[v][0]},{inv_var[v][1]}": str(x) for v, x in sorted(sols[m].items())}
                for m, (s, j, t) in enumerate(M.gb_labels)
            },
        },
        "closed_form_f": {
            "description": "f = h, where Z_i(a,b) = Z_i(atilde,b) + kappa*sum_j h_ji Z_j (+scalar), "
            "atilde^sigma = a^sigma + kappa*lambda_sigma, lambda_sigma = sum_j (gb_{sigma,j,-} b_j^+ - gb_{sigma,j,+} b_j^-)",
            "verified_gamma_equals_delta_f": {f"gb[{s},{j},{t}]": closed_ok[m] for m, (s, j, t) in enumerate(M.gb_labels)},
            "phi_per_gb": {
                f"gb[{s},{j},{t}]": {f"{i},{jj}": str(closed_f[m][i][jj]) for i in range(N) for jj in range(N) if closed_f[m][i][jj]}
                for m, (s, j, t) in enumerate(M.gb_labels)
            },
        },
    }
    return result


def _vadd(x, y):
    r = dict(x)
    for k, v in y.items():
        r[k] = r.get(k, 0) + v
    return r


def basis_definitions(n, kind):
    """Word-level definitions (list of (word tuple, coeff)) matching basis_* order."""
    bgens = [f"b{j}{s}" for j in range(1, n + 1) for s in "pm"]
    defs = []
    if kind == "symmetrized":
        for i, x in enumerate(bgens):
            for y in bgens[i:]:
                defs.append([((x, y), Fraction(1, 2)), ((y, x), Fraction(1, 2))])
        defs.append([(("ap", "am"), Fraction(1, 2)), (("am", "ap"), Fraction(-1, 2))])
        for a in ("ap", "am"):
            for y in bgens:
                defs.append([((a, y), Fraction(1, 2)), ((y, a), Fraction(1, 2))])
        return defs
    bp = lambda k: f"b{k}p"
    bm = lambda k: f"b{k}m"
    defs.append([(("ap", "am"), 1), ((bp(1), bm(1)), 1)])
    for k in range(2, n + 1):
        defs.append([((bp(k - 1), bm(k - 1)), 1), ((bp(k), bm(k)), -1)])
    defs.append([((bp(n), bm(n)), -1), ((), Fraction(-1, 2))])
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                defs.append([((bp(k), bm(l)), 1)])
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            defs.append([((bp(k), bp(l)), 1)])
            defs.append([((bm(k), bm(l)), 1)])
    for k in range(1, n + 1):
        defs.append([((bp(k), bp(k)), 1)])
        defs.append([((bm(k), bm(k)), 1)])
    for a in ("ap", "am"):
        for l in range(1, n + 1):
            defs.append([((a, bp(l)), 1)])
            defs.append([((a, bm(l)), 1)])
    return defs


def main():
    ns = [int(x) for x in sys.argv[1:]] or [1, 2, 3]
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
    os.makedirs(outdir, exist_ok=True)
    summary = {}
    for n in ns:
        for kind in ("symmetrized", "cn1"):
            res = analyse(n, kind)
            path = os.path.join(outdir, f"cn1_n{n}_{kind}.json")
            with open(path, "w") as fh:
                json.dump(res, fh, indent=1)
            cs = res["coboundary_system"]
            summary[f"n={n},{kind}"] = {
                "dims": f"{res['dim_even']}|{res['dim_odd']}",
                **res["checks"],
                "rank_delta_odd": cs["rank_delta_on_odd_1cochains"],
                "dim_ker_delta_odd": cs["dim_kernel_delta_odd"],
                "all_gb_directions_trivial": all(cs["solvable_for_each_elementary_gb"].values()),
                "closed_form_f_verified": all(res["closed_form_f"]["verified_gamma_equals_delta_f"].values()),
                "negative_controls_rejected": sum(not c["is_coboundary"] for c in cs["negative_controls"]),
            }
            print(json.dumps({f"n={n},{kind}": summary[f"n={n},{kind}"]}, indent=1), flush=True)
    with open(os.path.join(outdir, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)


if __name__ == "__main__":
    main()
