#!/usr/bin/env python3
"""
Exact verification engine for the inhomogeneous (gb) deformation of
C(n+1) = osp(2|2n) realised by oscillators, and its triviality.

Everything is computed with exact rational arithmetic (fractions.Fraction).
No external mathematics library is used.

Conventions (from docs/math/*.md)
---------------------------------
Oscillators:  a+ , a-  (odd, {a-,a+} = 1),   b_k+ , b_k-  (even, [b_k-,b_l+] = delta_kl).
Odd central element kappa with kappa^2 = 0 and  x kappa = (-1)^{p(x)} kappa x.
Deformed relation:   [b_j^s , a^sigma] = - gb[sigma,j,s] * kappa          (4n parameters).

Basis of g = C(n+1) (docs/math/Cn1_definition.md):
    H_1 = a+a- + b_1+b_1-,  H_k = b_{k-1}+b_{k-1}- - b_k+b_k- (2<=k<=n),  H_{n+1} = -b_n+b_n- - 1/2,
    E_{+-delta_k +- delta_l} = b_k^{+-} b_l^{+-} (k<l),  E_{+-2delta_k} = (b_k^{+-})^2,
    E_{eps +- delta_l} = a+ b_l^{+-},  E_{-eps +- delta_l} = a- b_l^{+-}.

Deformed bracket:  [Z_i, Z_j]_theta = sum_k c^k_ij Z_k + kappa * ( sum_k gamma^k_ij Z_k + s_ij * 1 ).
The term kappa*s_ij*1 is the "scalar" term of the coboundary document ("up to scalar").

Coboundary (docs/math/C_coboundary_definition.md), f odd:
    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y]).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction
from itertools import product

# ----------------------------------------------------------------------------
# Coefficient ring: polynomials in the gb parameters with rational coefficients.
# Represented as dict { tuple(sorted gb indices) : Fraction }.
# ----------------------------------------------------------------------------

def padd(p, q, scale=Fraction(1)):
    r = dict(p)
    for k, v in q.items():
        nv = r.get(k, Fraction(0)) + scale * v
        if nv == 0:
            r.pop(k, None)
        else:
            r[k] = nv
    return r


def pmul(p, q):
    r = {}
    for k1, v1 in p.items():
        for k2, v2 in q.items():
            k = tuple(sorted(k1 + k2))
            nv = r.get(k, Fraction(0)) + v1 * v2
            if nv == 0:
                r.pop(k, None)
            else:
                r[k] = nv
    return r


def pscale(p, s):
    if s == 0:
        return {}
    return {k: v * s for k, v in p.items()}


ONE = {(): Fraction(1)}

# ----------------------------------------------------------------------------
# Elements of the (deformed) Weyl-Clifford algebra: dict { word(tuple) : poly }
# ----------------------------------------------------------------------------

def eadd(E, F, scale=Fraction(1)):
    R = {w: dict(p) for w, p in E.items()}
    for w, p in F.items():
        np_ = padd(R.get(w, {}), p, scale)
        if np_:
            R[w] = np_
        else:
            R.pop(w, None)
    return R


def escale(E, s):
    if s == 0:
        return {}
    return {w: pscale(p, s) for w, p in E.items()}


def epscale(E, poly):
    R = {}
    for w, p in E.items():
        q = pmul(p, poly)
        if q:
            R[w] = q
    return R


class OscAlgebra:
    """Normal-ordering engine for  U(A_theta)  with A_theta = V + C K + C kappa, K = 1."""

    def __init__(self, n: int, deformed: bool = True):
        self.n = n
        self.deformed = deformed
        # letters: 0 = kappa, 1 = a+, 2 = a-, then b_k+ , b_k-  (k = 1..n)
        self.names = ['kappa', 'a+', 'a-']
        self.parity = [1, 1, 1]
        self.weight = [(0,) * (n + 1), (1,) + (0,) * n, (-1,) + (0,) * n]
        for k in range(1, n + 1):
            for s, sg in (('+', 1), ('-', -1)):
                self.names.append(f'b{k}{s}')
                self.parity.append(0)
                w = [0] * (n + 1)
                w[k] = sg
                self.weight.append(tuple(w))
        self.nletters = len(self.names)
        # gb parameters alpha = (sigma, j, s)
        self.gb = []       # list of (sigma, j, s)
        self.gb_names = []
        for sigma in ('+', '-'):
            for j in range(1, n + 1):
                for s in ('+', '-'):
                    self.gb.append((sigma, j, s))
                    self.gb_names.append(f'gb[a{sigma},b{j}{s}]')
        self.gb_index = {g: i for i, g in enumerate(self.gb)}
        self._cache = {}

    # letter helpers
    def b(self, k, s):
        return 3 + 2 * (k - 1) + (0 if s == '+' else 1)

    def letter_info(self, x):
        """return ('a', sigma) or ('b', k, s) or ('kappa',)"""
        if x == 0:
            return ('kappa',)
        if x == 1:
            return ('a', '+')
        if x == 2:
            return ('a', '-')
        k = (x - 3) // 2 + 1
        s = '+' if (x - 3) % 2 == 0 else '-'
        return ('b', k, s)

    def bracket_letters(self, x, y):
        """super-commutator [x, y] for letters with x > y (as an element)."""
        if y == 0:            # kappa is central
            return {}
        if x == 2 and y == 1:  # {a-, a+} = 1
            return {(): dict(ONE)}
        ix, iy = self.letter_info(x), self.letter_info(y)
        if ix[0] == 'b' and iy[0] == 'b':
            if ix[1] == iy[1] and ix[2] == '-' and iy[2] == '+':   # [b-, b+] = 1
                return {(): dict(ONE)}
            return {}
        if ix[0] == 'b' and iy[0] == 'a':
            if not self.deformed:
                return {}
            alpha = self.gb_index[(iy[1], ix[1], ix[2])]   # (sigma, j, s)
            # [b_j^s, a^sigma] = - gb[sigma,j,s] kappa
            return {(0,): {(alpha,): Fraction(-1)}}
        return {}

    def normal_order(self, word):
        if word in self._cache:
            return self._cache[word]
        res = None
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            if x == y and self.parity[x] == 1:
                res = {}
                break
            if x > y:
                sign = Fraction(-1) if (self.parity[x] and self.parity[y]) else Fraction(1)
                res = escale(self.normal_order(word[:i] + (y, x) + word[i + 2:]), sign)
                br = self.bracket_letters(x, y)
                for bw, bp in br.items():
                    res = eadd(res, epscale(self.normal_order(word[:i] + bw + word[i + 2:]), bp))
                break
        if res is None:
            res = {word: dict(ONE)}
        self._cache[word] = res
        return res

    def mul(self, E, F):
        R = {}
        for w1, p1 in E.items():
            for w2, p2 in F.items():
                R = eadd(R, epscale(self.normal_order(w1 + w2), pmul(p1, p2)))
        return R

    def eparity(self, E):
        ps = set()
        for w in E:
            ps.add(sum(self.parity[x] for x in w) % 2)
        assert len(ps) <= 1, "inhomogeneous element"
        return ps.pop() if ps else 0

    def scomm(self, E, F):
        pE, pF = self.eparity(E), self.eparity(F)
        sign = Fraction(-1) if (pE and pF) else Fraction(1)
        return eadd(self.mul(E, F), self.mul(F, E), -sign)

    def eweight(self, E):
        ws = set()
        for w in E:
            ws.add(tuple(sum(c) for c in zip(*([self.weight[x] for x in w] + [(0,) * (self.n + 1)]))))
        return ws

    # ------------------------------------------------------------------
    # Basis of g = C(n+1)
    # ------------------------------------------------------------------
    def build_basis(self):
        n = self.n
        Z, names, roots = [], [], []
        A, Am = 1, 2
        def mono(*letters, c=Fraction(1)):
            return {tuple(letters): {(): c}}
        def add(name, elem):
            Z.append(elem); names.append(name)
        # Cartan
        H1 = eadd(mono(A, Am), mono(self.b(1, '+'), self.b(1, '-')))
        add('H_1', H1)
        for k in range(2, n + 1):
            add(f'H_{k}', eadd(mono(self.b(k - 1, '+'), self.b(k - 1, '-')),
                               mono(self.b(k, '+'), self.b(k, '-')), Fraction(-1)))
        add(f'H_{n + 1}', eadd(mono(self.b(n, '+'), self.b(n, '-'), c=Fraction(-1)), {(): {(): Fraction(-1, 2)}}))
        # even roots
        for k in range(1, n + 1):
            for l in range(k + 1, n + 1):
                for s in ('+', '-'):
                    for t in ('+', '-'):
                        add(f'E[{s}d{k}{t}d{l}]', mono(self.b(k, s), self.b(l, t)))
            for s in ('+', '-'):
                add(f'E[{s}2d{k}]', mono(self.b(k, s), self.b(k, s)))
        # odd roots
        for sigma, al in (('+', A), ('-', Am)):
            for l in range(1, n + 1):
                for s in ('+', '-'):
                    add(f'E[{sigma}e{s}d{l}]', mono(al, self.b(l, s)))
        self.Z = [self.normal_order_elem(z) for z in Z]
        self.Znames = names
        self.dim = len(Z)
        self.Zparity = [self.eparity(z) for z in self.Z]
        self.Zweight = []
        for z in self.Z:
            ws = self.eweight(z)
            # constants (weight 0) may accompany the Cartan; weight is the unique non-trivial one
            ws.discard((0,) * (n + 1)) if len(ws) > 1 else None
            assert len(ws) == 1, (ws, z)
            self.Zweight.append(ws.pop())
        assert self.dim == 2 * n * n + 5 * n + 1
        self._build_decomposer()
        return self.Z

    def normal_order_elem(self, E):
        R = {}
        for w, p in E.items():
            R = eadd(R, epscale(self.normal_order(w), p))
        return R

    # ------------------------------------------------------------------
    # Decomposition of degree<=2 elements in the basis Z_1..Z_dim, 1
    # ------------------------------------------------------------------
    def _build_decomposer(self):
        monos = set()
        for z in self.Z:
            monos |= set(z.keys())
        monos.add(())
        # all normal ordered quadratic monomials in oscillators (no kappa)
        letters = list(range(1, self.nletters))
        for x in letters:
            for y in letters:
                if y > x or (y == x and self.parity[x] == 0):
                    monos.add((x, y))
        self.monos = sorted(monos)
        self.mono_index = {m: i for i, m in enumerate(self.monos)}
        ncol = self.dim + 1
        nrow = len(self.monos)
        assert nrow == ncol, (nrow, ncol)
        # matrix M[row=mono][col=basis]; column dim = unit 1
        M = [[Fraction(0)] * ncol for _ in range(nrow)]
        for j, z in enumerate(self.Z):
            for w, p in z.items():
                assert set(p.keys()) == {()}
                M[self.mono_index[w]][j] = p[()]
        M[self.mono_index[()]][self.dim] = Fraction(1)
        self.Minv = invert(M)

    def decompose(self, E):
        """E: element with no kappa and no gb -> (vector over Z, scalar).  Exact; asserts span."""
        v = [Fraction(0)] * len(self.monos)
        for w, p in E.items():
            assert w in self.mono_index, f"monomial {w} outside quadratic span"
            assert set(p.keys()) <= {()}
            v[self.mono_index[w]] = p.get((), Fraction(0))
        x = [sum(self.Minv[i][j] * v[j] for j in range(len(v))) for i in range(len(v))]
        vec = {i: x[i] for i in range(self.dim) if x[i] != 0}
        return vec, x[self.dim]

    def split_kappa(self, E):
        """Split element into (kappa^0 part, kappa^1 part with kappa stripped), as dict gbkey -> element."""
        parts0, parts1 = {}, {}
        for w, p in E.items():
            if w and w[0] == 0:
                target, ww = parts1, w[1:]
                assert 0 not in ww
            else:
                target, ww = parts0, w
                assert 0 not in ww
            for key, c in p.items():
                target.setdefault(key, {})
                target[key] = eadd(target[key], {ww: {(): c}})
        return parts0, parts1


def invert(M):
    n = len(M)
    A = [list(row) + [Fraction(int(i == j)) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        piv = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [row[n:] for row in A]


# ----------------------------------------------------------------------------
# Lie-theoretic layer: structure constants, gamma, coboundaries, cohomology
# ----------------------------------------------------------------------------

def vadd(u, v, s=Fraction(1)):
    r = dict(u)
    for k, x in v.items():
        nv = r.get(k, Fraction(0)) + s * x
        if nv == 0:
            r.pop(k, None)
        else:
            r[k] = nv
    return r


def vscale(u, s):
    return {} if s == 0 else {k: x * s for k, x in u.items()}


class Deformation:
    def __init__(self, n):
        self.n = n
        self.alg = OscAlgebra(n, deformed=True)
        self.alg.build_basis()
        A = self.alg
        self.dim, self.par, self.wt = A.dim, A.Zparity, A.Zweight
        self.ngb = len(A.gb)
        self.compute_brackets()

    # bracket of basis vectors as (c, gamma_alpha, s_alpha)
    def compute_brackets(self):
        A, d = self.alg, self.dim
        self.c = [[{} for _ in range(d)] for _ in range(d)]
        self.gamma = [[[{} for _ in range(d)] for _ in range(d)] for _ in range(self.ngb)]
        self.s = [[[Fraction(0)] * d for _ in range(d)] for _ in range(self.ngb)]
        for i in range(d):
            for j in range(d):
                E = A.scomm(A.Z[i], A.Z[j])
                p0, p1 = A.split_kappa(E)
                assert set(p0.keys()) <= {()}, "gb without kappa?!"
                if () in p0:
                    vec, sc = A.decompose(p0[()])
                    assert sc == 0, "undeformed bracket not closed in g"
                    self.c[i][j] = vec
                for key, el in p1.items():
                    assert len(key) == 1, f"nonlinear gb term {key}"
                    vec, sc = A.decompose(el)
                    self.gamma[key[0]][i][j] = vec
                    self.s[key[0]][i][j] = sc

    # ---- helpers -------------------------------------------------------
    def br(self, u, v):
        """bracket of two vectors (dict index->coeff) in g, undeformed."""
        r = {}
        for i, x in u.items():
            for j, y in v.items():
                r = vadd(r, self.c[i][j], x * y)
        return r

    def apply(self, f, u):
        """f: list of vectors f[j] = f(Z_j); apply to vector u."""
        r = {}
        for j, x in u.items():
            r = vadd(r, f[j], x)
        return r

    def gamma_apply(self, g, u, v):
        r = {}
        for i, x in u.items():
            for j, y in v.items():
                r = vadd(r, g[i][j], x * y)
        return r

    def coboundary(self, f, fscalar=None):
        """delta f per docs/math/C_coboundary_definition.md.  Returns (vector part, scalar part)."""
        d = self.dim
        df = [[{} for _ in range(d)] for _ in range(d)]
        dfs = [[Fraction(0)] * d for _ in range(d)]
        for i in range(d):
            for j in range(d):
                pi, pj = self.par[i], self.par[j]
                s1 = Fraction(-1) ** pi
                s2 = -Fraction(-1) ** ((pi + 1) * pj)
                t = vscale(self.br({i: Fraction(1)}, f[j]), s1)
                t = vadd(t, self.br({j: Fraction(1)}, f[i]), s2)
                t = vadd(t, self.apply(f, self.c[i][j]), Fraction(-1))
                df[i][j] = t
                if fscalar is not None:
                    dfs[i][j] = -sum(x * fscalar[k] for k, x in self.c[i][j].items())
        return df, dfs

    def jacobiator_kappa(self, g):
        """kappa-linear part of the super-Jacobiator of [.,.]_0 + kappa g  (zero iff g is a cocycle)."""
        d = self.dim
        bad = 0
        for x in range(d):
            for y in range(d):
                for z in range(d):
                    px, py = self.par[x], self.par[y]
                    X, Y, Zv = {x: Fraction(1)}, {y: Fraction(1)}, {z: Fraction(1)}
                    t = self.gamma_apply(g, self.c[x][y], Zv)
                    t = vadd(t, self.br(g[x][y], Zv))
                    t = vadd(t, self.gamma_apply(g, X, self.c[y][z]), Fraction(-1))
                    t = vadd(t, self.br(X, g[y][z]), -Fraction(-1) ** px)
                    sg = Fraction(-1) ** (px * py)
                    t = vadd(t, self.gamma_apply(g, Y, self.c[x][z]), sg)
                    t = vadd(t, self.br(Y, g[x][z]), sg * Fraction(-1) ** py)
                    if t:
                        bad += 1
        return bad

    def cochain_weight(self, g):
        ws = set()
        for i in range(self.dim):
            for j in range(self.dim):
                for k in g[i][j]:
                    ws.add(tuple(a - b - c for a, b, c in zip(self.wt[k], self.wt[i], self.wt[j])))
        return ws

    def is_super_skew(self, g):
        for i in range(self.dim):
            for j in range(self.dim):
                sg = -Fraction(-1) ** (self.par[i] * self.par[j])
                if vadd(g[j][i], g[i][j], -sg):
                    return False
        return True

    # ---- construction A: isometry Phi = 1 + kappa h on V -----------------
    def f_isometry(self, alpha):
        """f_A for parameter alpha, from h with omega(h x, y) = theta(x,y)/2."""
        A = self.alg
        sigma, j, s = A.gb[alpha]
        a_sig = 1 if sigma == '+' else 2
        a_other = 2 if sigma == '+' else 1
        half = Fraction(1, 2)
        # h(letter) as element (undeformed algebra for products)
        h = {x: {} for x in range(A.nletters)}
        # h(b_j^s) = -(1/2)(gb[-,j,s] a+ + gb[+,j,s] a-): for this alpha only the matching term
        h[A.b(j, s)] = {(a_other,): {(): -half}}
        # h(a^sigma) = (1/2) sum_l (gb[sigma,l,+] b_l- - gb[sigma,l,-] b_l+)
        if s == '+':
            h[a_sig] = {(A.b(j, '-'),): {(): half}}
        else:
            h[a_sig] = {(A.b(j, '+'),): {(): -half}}
        U = OscAlgebra(self.n, deformed=False)
        fZ, fS = [], []
        for z in A.Z:
            R = {}
            for w, p in z.items():
                if len(w) == 0:
                    continue
                assert len(w) == 2
                x, y = w
                term = U.mul(h[x], {(y,): dict(ONE)})
                term = eadd(term, U.mul({(x,): dict(ONE)}, h[y]), Fraction(-1) ** A.parity[x])
                R = eadd(R, term, p[()])
            vec, sc = A.decompose(R)
            fZ.append(vec); fS.append(sc)
        return fZ, fS

    # ---- construction B: Cartan homotopy  f = iota_N gamma / lambda(N) ----
    def f_cartan(self, alpha, Nvec, lam):
        fZ = [vscale(self.gamma_apply(self.gamma[alpha], Nvec, {j: Fraction(1)}), 1 / lam) for j in range(self.dim)]
        fS = [sum(x * self.s[alpha][i][j] for i, x in Nvec.items()) / lam for j in range(self.dim)]
        return fZ, fS


# ---- sparse exact rank ------------------------------------------------------
def sparse_rank(rows):
    """rows: list of dict{col: Fraction}. Returns rank (exact, Gauss elimination)."""
    pivots = {}   # col -> row dict (normalised)
    rank = 0
    for row in rows:
        r = dict(row)
        while r:
            col = min(r)
            if col in pivots:
                prow = pivots[col]
                f = r[col]
                for k, v in prow.items():
                    nv = r.get(k, Fraction(0)) - f * v
                    if nv == 0:
                        r.pop(k, None)
                    else:
                        r[k] = nv
            else:
                pv = r[col]
                pivots[col] = {k: v / pv for k, v in r.items()}
                rank += 1
                break
    return rank


def fr(x):
    return str(x)


def vec_json(v, names):
    return {names[k]: fr(x) for k, x in sorted(v.items())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=1)
    ap.add_argument('--out', default='artifacts')
    ap.add_argument('--cohomology', action='store_true', help='compute dim H^2_odd(g,g) and odd derivations')
    args = ap.parse_args()
    n = args.n
    D = Deformation(n)
    A = D.alg
    d = D.dim
    names = A.Znames
    print(f'n={n}: dim g = {d} = ({d - 4 * n}|{4 * n}), gb parameters: {D.ngb}')

    report = {
        'n': n, 'algebra': f'C({n + 1}) = osp(2|{2 * n})', 'dim': d,
        'dim_even': d - 4 * n, 'dim_odd': 4 * n,
        'basis': [{'index': i, 'name': names[i], 'parity': D.par[i], 'weight': list(D.wt[i]),
                   'oscillator_expression': {' '.join(A.names[x] for x in w) or '1': fr(p[()]) for w, p in A.Z[i].items()}}
                  for i in range(d)],
        'weight_coordinates': ['epsilon'] + [f'delta_{k}' for k in range(1, n + 1)],
        'gb_parameters': [{'index': a, 'name': A.gb_names[a], 'sigma': g[0], 'j': g[1], 's': g[2],
                           'relation': f'[b{g[1]}{g[2]}, a{g[0]}] = -{A.gb_names[a]} kappa'} for a, g in enumerate(A.gb)],
        'structure_constants': [], 'gamma': {}, 'scalar_terms': {}, 'f_isometry': {}, 'f_cartan': {},
        'checks': {},
    }
    for i in range(d):
        for j in range(d):
            for k, x in sorted(D.c[i][j].items()):
                report['structure_constants'].append([names[i], names[j], names[k], fr(x)])

    checks = report['checks']
    # (1) undeformed Jacobi + closure already asserted in compute_brackets; verify Jacobi of c:
    zero_g = [[{} for _ in range(d)] for _ in range(d)]
    # Jacobi for c itself: use jacobiator on gamma=c? simpler: check directly
    jac_bad = 0
    for x in range(d):
        for y in range(d):
            for z in range(d):
                X, Y, Zv = {x: Fraction(1)}, {y: Fraction(1)}, {z: Fraction(1)}
                t = D.br(D.c[x][y], Zv)
                t = vadd(t, D.br(X, D.c[y][z]), Fraction(-1))
                t = vadd(t, D.br(Y, D.c[x][z]), Fraction(-1) ** (D.par[x] * D.par[y]))
                if t:
                    jac_bad += 1
    checks['undeformed_super_jacobi_violations'] = jac_bad
    print('  undeformed super-Jacobi violations:', jac_bad)

    # N = a+a- - 1/2  (weight functional: epsilon(N)=1, delta_k(N)=0)
    Nvec, Nsc = A.decompose({(1, 2): dict(ONE), (): {(): Fraction(-1, 2)}})
    assert Nsc == 0
    report['N_element'] = {'definition': 'a+ a- - 1/2', 'in_basis': vec_json(Nvec, names)}

    all_ok = True
    gamma_rows = []
    for a in range(D.ngb):
        g = D.gamma[a]
        info = {}
        nz = sum(1 for i in range(d) for j in range(d) if g[i][j])
        info['nonzero_entries'] = nz
        info['super_skew'] = D.is_super_skew(g)
        info['cocycle_violations'] = D.jacobiator_kappa(g)
        ws = D.cochain_weight(g)
        info['weight'] = [list(w) for w in ws]
        assert len(ws) == 1, ws
        lam_vec = next(iter(ws))
        lam = Fraction(lam_vec[0])   # lambda(N) = epsilon-coordinate
        info['lambda(N)'] = fr(lam)
        assert lam != 0
        # construction A
        fA, fAs = D.f_isometry(a)
        dfA, dfAs = D.coboundary(fA, fAs)
        okA = all(not vadd(dfA[i][j], g[i][j], Fraction(-1)) for i in range(d) for j in range(d))
        okAs = all(dfAs[i][j] == D.s[a][i][j] for i in range(d) for j in range(d))
        # construction B
        fB, fBs = D.f_cartan(a, Nvec, lam)
        dfB, dfBs = D.coboundary(fB, fBs)
        okB = all(not vadd(dfB[i][j], g[i][j], Fraction(-1)) for i in range(d) for j in range(d))
        okBs = all(dfBs[i][j] == D.s[a][i][j] for i in range(d) for j in range(d))
        info['delta_fA_equals_gamma'] = okA
        info['delta_fA_scalar_part_equals_s'] = okAs
        info['delta_fB_equals_gamma'] = okB
        info['delta_fB_scalar_part_equals_s'] = okBs
        info['fA_parity_odd'] = all(all(D.par[k] != D.par[j] for k in fA[j]) for j in range(d))
        info['fB_parity_odd'] = all(all(D.par[k] != D.par[j] for k in fB[j]) for j in range(d))
        # difference fA - fB must be an odd derivation (cocycle): check delta(fA - fB) = 0
        diff = [vadd(fA[j], fB[j], Fraction(-1)) for j in range(d)]
        ddiff, _ = D.coboundary(diff)
        info['fA_minus_fB_is_derivation'] = all(not ddiff[i][j] for i in range(d) for j in range(d))
        # negative controls: a wrong candidate must fail (guards against a vacuous checker)
        neg = [vscale(fA[j], Fraction(-1)) for j in range(d)]
        dneg, _ = D.coboundary(neg)
        info['negative_control_minus_fA_fails'] = any(vadd(dneg[i][j], g[i][j], Fraction(-1)) for i in range(d) for j in range(d))
        info['negative_control_f_zero_fails'] = nz > 0
        all_ok &= info['negative_control_minus_fA_fails'] and info['negative_control_f_zero_fails']
        all_ok &= okA and okAs and okB and okBs and info['super_skew'] and info['cocycle_violations'] == 0 and nz > 0
        print(f"  {A.gb_names[a]:16s} nz={nz:4d} skew={info['super_skew']} cocycle_viol={info['cocycle_violations']} "
              f"weight={lam_vec} dfA=gamma:{okA} (scalars {okAs})  dfB=gamma:{okB} (scalars {okBs})")
        report['gamma'][A.gb_names[a]] = {f'[{names[i]},{names[j]}]': vec_json(g[i][j], names)
                                          for i in range(d) for j in range(d) if g[i][j]}
        report['scalar_terms'][A.gb_names[a]] = {f'[{names[i]},{names[j]}]': fr(D.s[a][i][j])
                                                 for i in range(d) for j in range(d) if D.s[a][i][j]}
        report['f_isometry'][A.gb_names[a]] = {names[j]: {'g_part': vec_json(fA[j], names), 'scalar': fr(fAs[j])}
                                               for j in range(d) if fA[j] or fAs[j]}
        report['f_cartan'][A.gb_names[a]] = {names[j]: {'g_part': vec_json(fB[j], names), 'scalar': fr(fBs[j])}
                                             for j in range(d) if fB[j] or fBs[j]}
        checks[A.gb_names[a]] = info
        # row for independence
        row = {}
        for i in range(d):
            for j in range(d):
                for k, x in g[i][j].items():
                    row[(i * d + j) * d + k] = x
        gamma_rows.append(row)
    rk = sparse_rank(gamma_rows)
    checks['rank_of_gamma_family'] = rk
    checks['gamma_family_independent'] = (rk == D.ngb)
    print(f'  rank of {{gamma_alpha}} = {rk} (expected {D.ngb})')

    if args.cohomology:
        # odd 1-cochains: f(Z_j) = Z_k with parity(k) != parity(j)
        cols = [(j, k) for j in range(d) for k in range(d) if D.par[j] != D.par[k]]
        rows_by_entry = {}
        for ci, (j, k) in enumerate(cols):
            f = [{} for _ in range(d)]
            f[j] = {k: Fraction(1)}
            df, _ = D.coboundary(f)
            for i in range(d):
                for jj in range(d):
                    for kk, x in df[i][jj].items():
                        rows_by_entry.setdefault((i, jj, kk), {})[ci] = x
        rk1 = sparse_rank(list(rows_by_entry.values()))
        ker1 = len(cols) - rk1
        checks['odd_1_cochains'] = len(cols)
        checks['rank_delta1_odd'] = rk1
        checks['dim_odd_derivations'] = ker1
        checks['dim_g_odd'] = 4 * n
        print(f'  odd 1-cochains {len(cols)}, rank delta^1 = {rk1}, odd derivations = {ker1} (dim g_1 = {4 * n})')
        # weight-zero odd 2-cochains and their cocycle condition
        pairs = [(i, j) for i in range(d) for j in range(i, d) if i < j or D.par[i] == 1]
        basis2 = []
        for (i, j) in pairs:
            for k in range(d):
                if D.par[k] == (D.par[i] + D.par[j] + 1) % 2 and \
                   all(a + b == c for a, b, c in zip(D.wt[i], D.wt[j], D.wt[k])):
                    basis2.append((i, j, k))
        # weight-zero odd 1-cochains (should be none)
        c1w0 = [(j, k) for (j, k) in cols if D.wt[j] == D.wt[k]]
        checks['dim_weight0_odd_1_cochains'] = len(c1w0)
        checks['dim_weight0_odd_2_cochains'] = len(basis2)
        # build J rows via linearity, restricted to weight-zero cochains
        col_index = {}
        for ci, (i, j, k) in enumerate(basis2):
            col_index[(i, j, k)] = (ci, Fraction(1))
            col_index[(j, i, k)] = (ci, -Fraction(-1) ** (D.par[i] * D.par[j]))

        def gcomp(x, y):
            """gamma(Z_x, Z_y) as dict k -> {col: coeff}"""
            out = {}
            for k in range(d):
                if (x, y, k) in col_index:
                    ci, sg = col_index[(x, y, k)]
                    out[k] = {ci: sg}
            return out

        rows = {}
        def addrow(x, y, z, k, col, val):
            if val:
                key = (x, y, z, k)
                rows.setdefault(key, {})
                rows[key][col] = rows[key].get(col, Fraction(0)) + val
        for x in range(d):
            for y in range(d):
                for z in range(d):
                    px, py = D.par[x], D.par[y]
                    sg = Fraction(-1) ** (px * py)
                    # gamma(c(x,y), z)
                    for m, cm in D.c[x][y].items():
                        for k, cols_ in gcomp(m, z).items():
                            for col, v in cols_.items():
                                addrow(x, y, z, k, col, cm * v)
                    # c(gamma(x,y), z)
                    for k, cols_ in gcomp(x, y).items():
                        for col, v in cols_.items():
                            for kk, w in D.c[k][z].items():
                                addrow(x, y, z, kk, col, v * w)
                    # - gamma(x, c(y,z))
                    for m, cm in D.c[y][z].items():
                        for k, cols_ in gcomp(x, m).items():
                            for col, v in cols_.items():
                                addrow(x, y, z, k, col, -cm * v)
                    # - (-1)^px c(x, gamma(y,z))
                    for k, cols_ in gcomp(y, z).items():
                        for col, v in cols_.items():
                            for kk, w in D.c[x][k].items():
                                addrow(x, y, z, kk, col, -Fraction(-1) ** px * v * w)
                    # + sg gamma(y, c(x,z))
                    for m, cm in D.c[x][z].items():
                        for k, cols_ in gcomp(y, m).items():
                            for col, v in cols_.items():
                                addrow(x, y, z, k, col, sg * cm * v)
                    # + sg (-1)^py c(y, gamma(x,z))
                    for k, cols_ in gcomp(x, z).items():
                        for col, v in cols_.items():
                            for kk, w in D.c[y][k].items():
                                addrow(x, y, z, kk, col, sg * Fraction(-1) ** py * v * w)
        rows_list = [{c: v for c, v in r.items() if v != 0} for r in rows.values()]
        rows_list = [r for r in rows_list if r]
        rkJ = sparse_rank(rows_list)
        z2 = len(basis2) - rkJ
        checks['rank_delta2_on_weight0_odd_2_cochains'] = rkJ
        checks['dim_weight0_odd_2_cocycles'] = z2
        checks['dim_H2_odd(g,g)'] = z2 - 0   # no weight-zero odd 1-cochains => no coboundaries of weight 0
        print(f'  weight-0 odd 2-cochains {len(basis2)}, rank delta^2 = {rkJ}, dim Z^2_0 = {z2}, '
              f'weight-0 odd 1-cochains = {len(c1w0)}  =>  dim H^2_odd(g,g) = {z2}')

    checks['ALL_TRIVIALITY_CHECKS_PASSED'] = all_ok
    report['conclusion'] = ('For every value of the 4n parameters gb the cocycle gamma_gb is a coboundary: '
                            'gamma_gb = delta f_gb with f_gb given explicitly (f_isometry and f_cartan). '
                            'The scalar terms s_ij are accounted for by allowing f to take values in g + C*1.')
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f'C{n + 1}_deformation_n{n}.json')
    with open(path, 'w') as fh:
        json.dump(report, fh, indent=1)
    print('  ALL TRIVIALITY CHECKS PASSED:', all_ok, '->', path)
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
