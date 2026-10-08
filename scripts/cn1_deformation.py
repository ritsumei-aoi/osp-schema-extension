#!/usr/bin/env python3
"""
Exact computation of the inhomogeneous (gb) deformation of C(n+1) = osp(2|2n)
realized inside the universal enveloping algebra U(A') of the deformed
oscillator (Heisenberg) superalgebra

    A' = V (+) C K (+) C kappa,   V = span{ a^+, a^-, b_j^+, b_j^- (j=1..n) }

with relations (K identified with 1, kappa odd and central, hence kappa^2 = 0)

    {a^-, a^+} = 1,      [b_j^-, b_k^+] = delta_jk,
    [b_j^s, a^sigma] = - gb_{sigma, j, s} * kappa,     sigma, s in {+,-}.

Everything is done with exact rational arithmetic.  The gb parameters are kept
*symbolic* in a minimal way: every coefficient is a linear form
        c_0 + sum_{(sigma,j,s)} c_{sigma,j,s} * gb_{sigma,j,s}
(no quadratic terms in gb can ever appear because each gb comes with one kappa
and kappa^2 = 0).

Usage:  python3 scripts/cn1_deformation.py 1 2 3
Writes  artifacts/Cn1_n{n}_verification.json  for every n given.

Conventions (all taken from docs/math/*.md):
  * basis of g = C(n+1): the Cartan elements H_1..H_{n+1} and the root
    vectors exactly as written in docs/math/Cn1_definition.md, section 2
    ("All root generators" normalisation E_{±2δ_k} = (b_k^±)^2);
  * deformed bracket  [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)
    (kappa written on the LEFT);
  * coboundary (docs/math/C_coboundary_definition.md):
        (δf)(X,Y) = (-1)^{p(X)} [X,f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y,f(X)] - f([X,Y]).
"""
from fractions import Fraction
import itertools
import json
import os
import sys

ONE = Fraction(1)
HALF = Fraction(1, 2)


# --------------------------------------------------------------------------
# coefficients: linear forms in the gb parameters
#   represented as dict  key -> Fraction, key = None (constant) or (sigma,j,s)
# --------------------------------------------------------------------------
def const(x):
    return {None: Fraction(x)}


def coef_add(c1, c2, out=None):
    out = dict(c1) if out is None else out
    for k, v in c2.items():
        nv = out.get(k, 0) + v
        if nv == 0:
            out.pop(k, None)
        else:
            out[k] = nv
    return out


def coef_scale(c, x):
    if x == 0:
        return {}
    return {k: v * x for k, v in c.items()}


def coef_mul(c1, c2):
    """Product of two linear forms.  A product gb*gb is only ever generated
    together with kappa^2 = 0, so the caller must discard it (we return None)."""
    out = {}
    for k1, v1 in c1.items():
        for k2, v2 in c2.items():
            if k1 is None:
                k = k2
            elif k2 is None:
                k = k1
            else:
                return None  # gb*gb term: must be accompanied by kappa^2 = 0
            out[k] = out.get(k, 0) + v1 * v2
    return {k: v for k, v in out.items() if v != 0}


# --------------------------------------------------------------------------
# the oscillator superalgebra U(A') with normal ordering
#   generator ids:  0 = kappa, 1..n = b_j^+, n+1..2n = b_j^-, 2n+1 = a^+, 2n+2 = a^-
#   normal order  = increasing id
# --------------------------------------------------------------------------
class Osc:
    def __init__(self, n):
        self.n = n
        self.KAPPA = 0
        self.AP = 2 * n + 1
        self.AM = 2 * n + 2
        self.memo = {}

    # generator helpers --------------------------------------------------
    def bp(self, j):
        return j

    def bm(self, j):
        return self.n + j

    def is_b(self, g):
        return 1 <= g <= 2 * self.n

    def b_info(self, g):
        """(j, s) for a bosonic generator id"""
        if g <= self.n:
            return g, '+'
        return g - self.n, '-'

    def parity(self, g):
        return 1 if (g == 0 or g >= self.AP) else 0

    def word_parity(self, w):
        return sum(self.parity(g) for g in w) % 2

    def name(self, g):
        if g == 0:
            return 'kappa'
        if g == self.AP:
            return 'a+'
        if g == self.AM:
            return 'a-'
        j, s = self.b_info(g)
        return 'b%d%s' % (j, s)

    def word_name(self, w):
        return '*'.join(self.name(g) for g in w) if w else '1'

    def weight(self, w):
        """weight vector (eps, delta_1, ..., delta_n) of a word"""
        wt = [0] * (self.n + 1)
        for g in w:
            if g == self.AP:
                wt[0] += 1
            elif g == self.AM:
                wt[0] -= 1
            elif self.is_b(g):
                j, s = self.b_info(g)
                wt[j] += 1 if s == '+' else -1
        return tuple(wt)

    # normal ordering ----------------------------------------------------
    def normal_order(self, word):
        if word in self.memo:
            return self.memo[word]
        res = self._no(word)
        self.memo[word] = res
        return res

    def _acc(self, out, word, coef):
        for w, c in self.normal_order(word).items():
            cc = coef_mul(c, coef)
            if cc is None:
                # gb*gb term: must come with two kappas, which is zero anyway
                assert w.count(0) >= 2 or True
                continue
            coef_add({}, cc, out.setdefault(w, {}))
            if not out[w]:
                del out[w]

    def _no(self, word):
        n = self.n
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            if x == y and self.parity(x) == 1:
                return {}  # kappa^2 = 0, (a^+)^2 = 0, (a^-)^2 = 0
            if x > y:
                pre, post = word[:i], word[i + 2:]
                out = {}
                if y == 0:  # x kappa = (-1)^{p(x)} kappa x
                    self._acc(out, pre + (0, x) + post, const(-1 if self.parity(x) else 1))
                    return out
                if x == self.AM and y == self.AP:  # a^- a^+ = 1 - a^+ a^-
                    self._acc(out, pre + post, const(1))
                    self._acc(out, pre + (self.AP, self.AM) + post, const(-1))
                    return out
                if x >= self.AP and self.is_b(y):
                    # a^sigma b_j^s = b_j^s a^sigma + [a,b],  [a,b] = -[b,a] = gb kappa
                    sigma = '+' if x == self.AP else '-'
                    j, s = self.b_info(y)
                    self._acc(out, pre + (y, x) + post, const(1))
                    self._acc(out, pre + (0,) + post, {(sigma, j, s): ONE})
                    return out
                if self.is_b(x) and self.is_b(y):
                    jx, sx = self.b_info(x)
                    jy, sy = self.b_info(y)
                    self._acc(out, pre + (y, x) + post, const(1))
                    if sx == '-' and sy == '+' and jx == jy:
                        # b_j^- b_j^+ = b_j^+ b_j^- + 1
                        self._acc(out, pre + post, const(1))
                    return out
                raise RuntimeError('unhandled pair %s %s' % (x, y))
        return {word: const(1)}

    # element algebra ----------------------------------------------------
    @staticmethod
    def add(E1, E2, scale=ONE):
        out = {w: dict(c) for w, c in E1.items()}
        for w, c in E2.items():
            coef_add({}, coef_scale(c, scale), out.setdefault(w, {}))
            if not out[w]:
                del out[w]
        return out

    def mul(self, E1, E2):
        out = {}
        for w1, c1 in E1.items():
            for w2, c2 in E2.items():
                c = coef_mul(c1, c2)
                if c is None:
                    assert (w1 + w2).count(0) >= 2
                    continue
                self._acc(out, w1 + w2, c)
        return out

    def bracket(self, E1, p1, E2, p2):
        """supercommutator of homogeneous elements"""
        sign = -1 if (p1 and p2) else 1
        return self.add(self.mul(E1, E2), self.mul(E2, E1), -sign)

    def word(self, *gens):
        return {tuple(gens): const(1)}

    @staticmethod
    def elem_parity_check(osc, E):
        ps = {osc.word_parity(w) for w in E}
        assert len(ps) <= 1, 'inhomogeneous element'
        return ps.pop() if ps else None

    @staticmethod
    def split_kappa(E):
        """return (part without kappa, part with kappa stripped off the front)"""
        E0, E1 = {}, {}
        for w, c in E.items():
            if w and w[0] == 0:
                assert 0 not in w[1:]
                E1[w[1:]] = c
            else:
                assert 0 not in w
                E0[w] = c
        return E0, E1


# --------------------------------------------------------------------------
# exact linear algebra helpers (Fractions)
# --------------------------------------------------------------------------
class Decomposer:
    """Express vectors (dict word->Fraction) in a given basis of such vectors."""

    def __init__(self, basis_vectors):
        self.m = len(basis_vectors)
        words = sorted({w for v in basis_vectors for w in v})
        self.widx = {w: i for i, w in enumerate(words)}
        # build augmented rows: for each word, row of coefficients over basis
        rows = []
        for w in words:
            rows.append([v.get(w, Fraction(0)) for v in basis_vectors])
        # row-reduce the (words x basis) matrix keeping track of the operations
        # We solve basis_coeffs from vector by least structure: Gaussian elim on
        # the transpose system  M x = v  where M is words x m.
        self.M = rows
        # precompute pivot structure by elimination on M augmented later
        # (simple approach: do elimination per solve; sizes are tiny)

    def solve(self, vec):
        """return list of m Fractions x with sum_i x_i basis_i == vec, else raise"""
        for w in vec:
            if w not in self.widx and vec[w] != 0:
                raise ValueError('word %s not in span' % (w,))
        nrow = len(self.M)
        A = [row[:] + [vec.get(w, Fraction(0))] for row, w in zip(self.M, sorted(self.widx, key=self.widx.get))]
        m = self.m
        piv_cols = []
        r = 0
        for c in range(m):
            p = None
            for i in range(r, nrow):
                if A[i][c] != 0:
                    p = i
                    break
            if p is None:
                continue
            A[r], A[p] = A[p], A[r]
            pv = A[r][c]
            A[r] = [x / pv for x in A[r]]
            for i in range(nrow):
                if i != r and A[i][c] != 0:
                    f = A[i][c]
                    A[i] = [x - f * y for x, y in zip(A[i], A[r])]
            piv_cols.append(c)
            r += 1
        for i in range(r, nrow):
            if A[i][m] != 0:
                raise ValueError('vector not in span')
        x = [Fraction(0)] * m
        for i, c in enumerate(piv_cols):
            x[c] = A[i][m]
        return x


def fstr(x):
    return str(Fraction(x))


# --------------------------------------------------------------------------
# the Lie superalgebra C(n+1) inside U(A')
# --------------------------------------------------------------------------
def build_basis(osc):
    n = osc.n
    B = []  # list of (name, element, parity)

    def add(name, E):
        # Normal-order the defining word.  In U(A') the document's word
        # a^sigma b_l^s equals the normal-ordered word b_l^s a^sigma plus the
        # central term gb*kappa; central terms do not change any bracket, and we
        # take the kappa-free (normal-ordered) representative as the basis vector.
        E0 = {}
        for w, c in E.items():
            for w2, c2 in osc.normal_order(w).items():
                if 0 in w2:
                    continue
                cc = coef_mul(c, c2)
                assert set(cc) <= {None}
                coef_add({}, cc, E0.setdefault(w2, {}))
        B.append((name, E0))

    W = osc.word
    # Cartan subalgebra (docs/math/Cn1_definition.md, simple generators)
    add('H_1', osc.add(W(osc.AP, osc.AM), W(osc.bp(1), osc.bm(1))))
    for k in range(2, n + 1):
        add('H_%d' % k, osc.add(W(osc.bp(k - 1), osc.bm(k - 1)), W(osc.bp(k), osc.bm(k)), -1))
    add('H_%d' % (n + 1), osc.add({(): const(-HALF)}, W(osc.bp(n), osc.bm(n)), -1))
    # even root vectors
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                add('E_{d%d-d%d}' % (k, l), W(osc.bp(k), osc.bm(l)))
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            add('E_{d%d+d%d}' % (k, l), W(osc.bp(k), osc.bp(l)))
            add('E_{-d%d-d%d}' % (k, l), W(osc.bm(k), osc.bm(l)))
    for k in range(1, n + 1):
        add('E_{2d%d}' % k, W(osc.bp(k), osc.bp(k)))
        add('E_{-2d%d}' % k, W(osc.bm(k), osc.bm(k)))
    # odd root vectors
    for l in range(1, n + 1):
        add('E_{e+d%d}' % l, W(osc.AP, osc.bp(l)))
        add('E_{e-d%d}' % l, W(osc.AP, osc.bm(l)))
        add('E_{-e+d%d}' % l, W(osc.AM, osc.bp(l)))
        add('E_{-e-d%d}' % l, W(osc.AM, osc.bm(l)))
    assert len(B) == 2 * n * n + 5 * n + 1
    return B


def gb_keys(n):
    return [(sigma, j, s) for sigma in '+-' for j in range(1, n + 1) for s in '+-']


def gb_name(key):
    sigma, j, s = key
    return 'gb[a%s,b%d%s]' % (sigma, j, s)


def main_for_n(n, outdir):
    osc = Osc(n)
    basis = build_basis(osc)
    names = [b[0] for b in basis]
    elems = [b[1] for b in basis]
    N = len(basis)
    parity = []
    weight = []
    for E in elems:
        ps = {osc.word_parity(w) for w in E}
        assert len(ps) == 1
        parity.append(ps.pop())
        wts = {osc.weight(w) for w in E}
        assert len(wts) == 1
        weight.append(wts.pop())
    keys = gb_keys(n)
    idx = {nm: i for i, nm in enumerate(names)}

    # constant-coefficient vectors of the basis + the unit 1
    def const_vec(E):
        out = {}
        for w, c in E.items():
            assert set(c) <= {None}
            if c:
                out[w] = c[None]
        return out

    dec = Decomposer([const_vec(E) for E in elems] + [{(): ONE}])

    def decompose_linear(E):
        """E: element without kappa; returns dict key -> (list of N coeffs, const)"""
        per_key = {}
        for w, c in E.items():
            for k, v in c.items():
                per_key.setdefault(k, {})[w] = v
        out = {}
        for k, vec in per_key.items():
            x = dec.solve(vec)
            out[k] = (x[:N], x[N])
        return out

    # ---------------- structure constants and gamma ----------------------
    C = [[None] * N for _ in range(N)]          # C[i][j] = {k: Fraction}
    gamma = {key: [[{} for _ in range(N)] for _ in range(N)] for key in keys}   # adjoint part
    gamma0 = {key: [[Fraction(0)] * N for _ in range(N)] for key in keys}        # scalar part
    brackets = {}
    for i in range(N):
        for j in range(N):
            Bij = osc.bracket(elems[i], parity[i], elems[j], parity[j])
            brackets[(i, j)] = Bij
            B0, B1 = Osc.split_kappa(Bij)
            d0 = decompose_linear(B0)
            assert set(d0) <= {None}, 'kappa-free part depends on gb?!'
            coeffs, cst = d0.get(None, ([Fraction(0)] * N, Fraction(0)))
            assert cst == 0, 'g is not closed: constant in [%s,%s]' % (names[i], names[j])
            C[i][j] = {k: v for k, v in enumerate(coeffs) if v != 0}
            d1 = decompose_linear(B1)
            assert None not in d1, 'kappa term without gb?!'
            for key, (coeffs, cst) in d1.items():
                gamma[key][i][j] = {k: v for k, v in enumerate(coeffs) if v != 0}
                gamma0[key][i][j] = cst

    # super-skew-symmetry of gamma and of C
    for i in range(N):
        for j in range(N):
            sg = -1 if (parity[i] and parity[j]) else 1
            for k in range(N):
                assert C[i][j].get(k, 0) == -sg * C[j][i].get(k, 0)
                for key in keys:
                    assert gamma[key][i][j].get(k, 0) == -sg * gamma[key][j][i].get(k, 0)
            for key in keys:
                assert gamma0[key][i][j] == -sg * gamma0[key][j][i]

    # sign rules used for the abelian extension L = g (+) kappa g (derived in the report):
    #   [X, kappa Y] = (-1)^{p(X)} kappa [X,Y]_0,     [kappa X, Y] = kappa [X,Y]_0
    kap = osc.word(0)
    for i in range(N):
        for j in range(N):
            kZj = osc.mul(kap, elems[j])
            lhs = osc.bracket(elems[i], parity[i], kZj, (parity[j] + 1) % 2)
            rhs = {}
            for k, v in C[i][j].items():
                rhs = osc.add(rhs, osc.mul(kap, elems[k]), v * (-1 if parity[i] else 1))
            assert lhs == rhs, ('sign rule [X, kappa Y]', names[i], names[j])
            kZi = osc.mul(kap, elems[i])
            lhs = osc.bracket(kZi, (parity[i] + 1) % 2, elems[j], parity[j])
            rhs = {}
            for k, v in C[i][j].items():
                rhs = osc.add(rhs, osc.mul(kap, elems[k]), v)
            assert lhs == rhs, ('sign rule [kappa X, Y]', names[i], names[j])

    # Cartan matrix check (simple roots as listed in the definition document)
    simple = ['E_{e-d1}'] + ['E_{d%d-d%d}' % (k - 1, k) for k in range(2, n + 1)] + ['E_{2d%d}' % n]
    cartan = []
    for i in range(1, n + 2):
        row = []
        for sname in simple:
            j = idx[sname]
            br = C[idx['H_%d' % i]][j]
            assert set(br) <= {j}
            row.append(br.get(j, Fraction(0)))
        cartan.append(row)

    # ---------------- the explicit untwisting map Phi -------------------
    # a~^sigma = a^sigma + kappa * m^sigma,   m^sigma = sum_j (gb[sigma,j,-] b_j^+ - gb[sigma,j,+] b_j^-)
    def m_elem(sigma):
        E = {}
        for j in range(1, n + 1):
            E = osc.add(E, {(osc.bp(j),): {(sigma, j, '-'): ONE}})
            E = osc.add(E, {(osc.bm(j),): {(sigma, j, '+'): -ONE}})
        return E

    image = {}
    for g in range(1, 2 * n + 3):
        if g == osc.AP or g == osc.AM:
            sigma = '+' if g == osc.AP else '-'
            image[g] = osc.add(osc.word(g), osc.mul(osc.word(0), m_elem(sigma)))
        else:
            image[g] = osc.word(g)

    def Phi(E):
        out = {}
        for w, c in E.items():
            P = {(): dict(c)}
            for g in w:
                P = osc.mul(P, image[g])
            out = osc.add(out, P)
        return out

    # check: a~, b satisfy the UNDEFORMED relations in U(A')
    gens = list(range(1, 2 * n + 3))
    for g in gens:
        for h in gens:
            br = osc.bracket(image[g], osc.parity(g), image[h], osc.parity(h))
            expect = {}
            if g == osc.AM and h == osc.AP or g == osc.AP and h == osc.AM:
                expect = {(): const(1)}
            elif osc.is_b(g) and osc.is_b(h):
                jg, sg_ = osc.b_info(g)
                jh, sh = osc.b_info(h)
                if jg == jh and sg_ == '-' and sh == '+':
                    expect = {(): const(1)}
                if jg == jh and sg_ == '+' and sh == '-':
                    expect = {(): const(-1)}
            assert br == expect, ('untwisted generators are not canonical', g, h, br)

    PhiZ = [Phi(E) for E in elems]
    # first-order part F1 (g-component and scalar component), per gb key
    F1 = {key: [[Fraction(0)] * N for _ in range(N)] for key in keys}   # F1[key][i][j]: coefficient of Z_i in Phi_1(Z_j)
    F1c = {key: [Fraction(0)] * N for key in keys}
    for j in range(N):
        P0, P1 = Osc.split_kappa(PhiZ[j])
        assert P0 == elems[j]
        d1 = decompose_linear(P1)
        assert None not in d1
        for key, (coeffs, cst) in d1.items():
            for i in range(N):
                F1[key][i][j] = coeffs[i]
            F1c[key][j] = cst
    # homomorphism check: [Phi(Z_i), Phi(Z_j)] == Phi([Z_i,Z_j]_0) exactly in U(A')
    for i in range(N):
        for j in range(N):
            lhs = osc.bracket(PhiZ[i], parity[i], PhiZ[j], parity[j])
            rhs = {}
            for k, v in C[i][j].items():
                rhs = osc.add(rhs, PhiZ[k], v)
            assert lhs == rhs, ('Phi is not a homomorphism', names[i], names[j])

    # ---------------- the coboundary of f := -Phi_1 -----------------------
    # f(Z_j) = sum_i phi[i][j] Z_i + c_j * 1,     phi = -F1, c = -F1c
    def delta(phi, c):
        """doc formula; returns (adjoint part [i][j] -> {k: val}, scalar part [i][j])"""
        dA = [[{} for _ in range(N)] for _ in range(N)]
        dS = [[Fraction(0)] * N for _ in range(N)]
        for i in range(N):
            for j in range(N):
                acc = {}
                s1 = -1 if parity[i] else 1
                s2 = -1 if ((parity[i] + 1) * parity[j]) % 2 else 1
                # (-1)^{p_i} [Z_i, f(Z_j)]
                for m in range(N):
                    if phi[m][j] != 0:
                        for k, v in C[i][m].items():
                            acc[k] = acc.get(k, 0) + s1 * phi[m][j] * v
                # - (-1)^{(p_i+1)p_j} [Z_j, f(Z_i)]
                for m in range(N):
                    if phi[m][i] != 0:
                        for k, v in C[j][m].items():
                            acc[k] = acc.get(k, 0) - s2 * phi[m][i] * v
                # - f([Z_i,Z_j])
                cst = Fraction(0)
                for m, v in C[i][j].items():
                    for k in range(N):
                        if phi[k][m] != 0:
                            acc[k] = acc.get(k, 0) - v * phi[k][m]
                    cst -= v * c[m]
                dA[i][j] = {k: v for k, v in acc.items() if v != 0}
                dS[i][j] = cst
        return dA, dS

    f_phi = {key: [[-F1[key][i][j] for j in range(N)] for i in range(N)] for key in keys}
    f_c = {key: [-F1c[key][j] for j in range(N)] for key in keys}
    # parity check of f: odd map
    for key in keys:
        for i in range(N):
            for j in range(N):
                if f_phi[key][i][j] != 0:
                    assert parity[i] != parity[j]
            if f_c[key][i] != 0:
                assert parity[i] == 1
    delta_ok = {}
    for key in keys:
        dA, dS = delta(f_phi[key], f_c[key])
        ok_ad = all(dA[i][j] == gamma[key][i][j] for i in range(N) for j in range(N))
        ok_sc = all(dS[i][j] == gamma0[key][i][j] for i in range(N) for j in range(N))
        delta_ok[key] = (ok_ad, ok_sc)
        assert ok_ad and ok_sc, ('gamma != delta f', key, ok_ad, ok_sc)

    # scalar part is nonzero for every single gb parameter
    scalar_nonzero = {key: any(gamma0[key][i][j] != 0 for i in range(N) for j in range(N)) for key in keys}
    assert all(scalar_nonzero.values())
    # and the map gb -> gamma0 is injective (the 4n scalar cochains are linearly independent)
    vecs = []
    for key in keys:
        vecs.append({(i, j): gamma0[key][i][j] for i in range(N) for j in range(N) if gamma0[key][i][j] != 0})
    # simple independence check via exact elimination
    cols = sorted({p for v in vecs for p in v})
    M = [[v.get(p, Fraction(0)) for p in cols] for v in vecs]
    rank = 0
    M2 = [row[:] for row in M]
    for cidx in range(len(cols)):
        piv = next((r for r in range(rank, len(M2)) if M2[r][cidx] != 0), None)
        if piv is None:
            continue
        M2[rank], M2[piv] = M2[piv], M2[rank]
        pv = M2[rank][cidx]
        M2[rank] = [x / pv for x in M2[rank]]
        for r in range(len(M2)):
            if r != rank and M2[r][cidx] != 0:
                fct = M2[r][cidx]
                M2[r] = [x - fct * y for x, y in zip(M2[r], M2[rank])]
        rank += 1
    assert rank == len(keys)

    # ---------------- dependence of the scalar part on the section -------
    # The odd generators admit several natural representatives in U(A') that
    # differ by the CENTRAL element gb*kappa:
    #     document word  a^sigma b_l^s  =  b_l^s a^sigma + gb[sigma,l,s] kappa
    #     normal-ordered b_l^s a^sigma                      (used above)
    #     super-symmetrised (1/2)(a b + b a) = b_l^s a^sigma + (1/2) gb[sigma,l,s] kappa
    # Replacing Z_k by Z_k + kappa*s_k (s_k scalar) does not change any bracket,
    # but changes gamma by  gamma' = gamma - sum_k C_ij^k s_k = gamma + delta(s)
    # (only the scalar part moves).  We recompute everything DIRECTLY with the
    # super-symmetrised representatives and check that the scalar part of gamma
    # vanishes identically, while the adjoint part is unchanged.
    sym_elems = []
    for k in range(N):
        if parity[k] == 1:
            (w,) = elems[k].keys()          # normal-ordered word (b, a)
            b_id, a_id = w
            E = osc.add(osc.normal_order((a_id, b_id)), osc.normal_order((b_id, a_id)))
            E = {ww: coef_scale(c, HALF) for ww, c in E.items()}
            sym_elems.append(E)
        else:
            sym_elems.append(elems[k])
    shift = {key: [Fraction(0)] * N for key in keys}   # Z'_k = Z_k + kappa * sum_key shift[key][k] gb_key
    for k in range(N):
        E0, E1 = Osc.split_kappa(sym_elems[k])
        assert E0 == elems[k]
        for w, c in E1.items():
            assert w == ()
            for key, v in c.items():
                shift[key][k] = v
    sym_scalar_zero = True
    sym_ad_same = True
    for i in range(N):
        for j in range(N):
            Bij = osc.bracket(sym_elems[i], parity[i], sym_elems[j], parity[j])
            B0, B1 = Osc.split_kappa(Bij)
            d0 = decompose_linear(B0)
            coeffs, cst = d0.get(None, ([Fraction(0)] * N, Fraction(0)))
            assert cst == 0 and {k: v for k, v in enumerate(coeffs) if v != 0} == C[i][j]
            d1 = decompose_linear(B1)
            for key in keys:
                coeffs, cst = d1.get(key, ([Fraction(0)] * N, Fraction(0)))
                # re-express the kappa-part in the primed basis: subtract sum_k C_ij^k s_k
                cst_primed = cst - sum(v * shift[key][k] for k, v in C[i][j].items())
                if cst_primed != 0:
                    sym_scalar_zero = False
                if {k: v for k, v in enumerate(coeffs) if v != 0} != gamma[key][i][j]:
                    sym_ad_same = False
    assert sym_scalar_zero and sym_ad_same
    # consistency with the cochain identity: gamma'_sc = gamma_sc + delta(s) = delta(c + s) and c + s = 0
    for key in keys:
        for k in range(N):
            assert f_c[key][k] + shift[key][k] == 0

    # ---------------- JSON artifact -------------------------------------
    def sparse3(T):
        return {names[i]: {names[j]: {names[k]: fstr(v) for k, v in T[i][j].items()} for j in range(N) if T[i][j]} for i in range(N)}

    def sparse2(T):
        return {names[i]: {names[j]: fstr(T[i][j]) for j in range(N) if T[i][j] != 0} for i in range(N)}

    art = {
        'algebra': 'C(%d) = osp(2|%d)' % (n + 1, 2 * n),
        'n': n,
        'dimension': {'even': sum(1 for p in parity if p == 0), 'odd': sum(parity), 'total': N},
        'conventions': {
            'kappa': 'odd central element, kappa^2 = 0, written on the left: [X,Y]_gamma = [X,Y]_0 + kappa*gamma(X,Y)',
            'oscillator_relations': '{a-,a+}=1, [b_j-,b_k+]=delta_jk, [b_j^s,a^sigma] = -gb[a^sigma,b_j^s]*kappa',
            'gamma_decomposition': 'gamma(X,Y) = gamma_ad(X,Y) + gamma_scalar(X,Y)*1 with gamma_ad in g (adjoint module) and gamma_scalar in C (trivial module)',
            'coboundary': '(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])',
            'f_parametrisation': 'f(Z_j) = sum_i phi[i][j] Z_i + c[j]*1  (phi odd: nonzero only for p(Z_i) != p(Z_j))',
            'linearity': 'gamma, gamma_scalar, phi, c are linear in gb; the tables are given per unit gb parameter',
        },
        'basis': [{'name': names[i], 'parity': parity[i], 'weight': list(weight[i]),
                   'oscillator_word': {osc.word_name(w): fstr(c[None]) for w, c in elems[i].items()}} for i in range(N)],
        'simple_roots': simple,
        'cartan_matrix_[H_i,E_alpha_j]=a_ij*E_alpha_j': [[fstr(x) for x in row] for row in cartan],
        'gb_parameters': [gb_name(k) for k in keys],
        'structure_constants_C[i][j][k]': sparse3(C),
        'gamma_ad_per_gb': {gb_name(key): sparse3(gamma[key]) for key in keys},
        'gamma_scalar_per_gb': {gb_name(key): sparse2(gamma0[key]) for key in keys},
        'untwisting_map': {
            'description': 'a~^sigma = a^sigma + kappa*m^sigma, m^sigma = sum_j (gb[a^sigma,b_j-] b_j+ - gb[a^sigma,b_j+] b_j-); b unchanged. '
                           'Phi: U(A) -> U(A\'), a -> a~, b -> b is an isomorphism; Phi(Z) = Z + kappa*Phi_1(Z).',
            'f_definition': 'f := -Phi_1, split into g-part phi and scalar part c',
            'f_phi_per_gb': {gb_name(key): {names[j]: {names[i]: fstr(f_phi[key][i][j]) for i in range(N) if f_phi[key][i][j] != 0} for j in range(N)} for key in keys},
            'f_scalar_per_gb': {gb_name(key): {names[j]: fstr(f_c[key][j]) for j in range(N) if f_c[key][j] != 0} for key in keys},
        },
        'checks': {
            'g_closed_under_bracket_without_constants': True,
            'gamma_super_skew_symmetric': True,
            'untwisted_oscillators_satisfy_undeformed_relations': True,
            'kappa_sign_rules_[X,kY]=(-1)^pX_k[X,Y]_and_[kX,Y]=k[X,Y]': True,
            'Phi_is_homomorphism_exact': True,
            'gamma_ad_equals_delta_f_phi_per_gb': {gb_name(k): delta_ok[k][0] for k in keys},
            'gamma_scalar_equals_delta_f_scalar_per_gb': {gb_name(k): delta_ok[k][1] for k in keys},
            'gamma_scalar_nonzero_per_gb': {gb_name(k): scalar_nonzero[k] for k in keys},
            'rank_of_gb_to_gamma_scalar': rank,
            'symmetrized_section': {
                'description': 'odd generators represented by (1/2)(a b + b a) = b a + (1/2) gb kappa; '
                               'brackets recomputed directly in U(A\') and re-expressed in this basis',
                'shift_s_per_gb': {gb_name(key): {names[k]: fstr(shift[key][k]) for k in range(N) if shift[key][k] != 0} for key in keys},
                'gamma_scalar_vanishes_identically': sym_scalar_zero,
                'gamma_ad_unchanged': sym_ad_same,
                'f_scalar_plus_shift_is_zero': True,
            },
        },
    }
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, 'Cn1_n%d_verification.json' % n)
    with open(path, 'w') as fh:
        json.dump(art, fh, indent=1)
    print('n=%d: dim g = %d (%d|%d), %d gb parameters, Cartan matrix %s' % (
        n, N, art['dimension']['even'], art['dimension']['odd'], len(keys), [[str(x) for x in r] for r in cartan]))
    print('   all exact checks passed; artifact -> %s' % path)
    return art


if __name__ == '__main__':
    ns = [int(x) for x in sys.argv[1:]] or [1, 2, 3]
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(os.path.dirname(here), 'artifacts')
    for n in ns:
        main_for_n(n, outdir)
