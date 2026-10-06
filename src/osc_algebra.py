"""Exact oscillator algebra for C(n+1) = osp(2|2n).

Normal-ordered Weyl-Clifford algebra with one standard fermionic pair
(a_1^+, a_1^-) and n bosonic pairs (b_k^+, b_k^-), plus an optional odd
nilpotent central element kappa (kappa^2 = 0) used for the inhomogeneous
deformation  [b_j^s, a_1^sigma] = -gb[sigma, j, s] * kappa.

Element = dict {monomial: Fraction};  monomial = (k, fp, fm, bos) with
  k    in {0,1}   power of kappa (kappa always written on the LEFT),
  fp, fm in {0,1} exponents of a_1^+, a_1^-  (normal order a^+ a^-),
  bos  tuple (p_1, q_1, ..., p_n, q_n) exponents of b_k^+, b_k^-
       (normal order: all b^+ left of b^-).
Fermions and bosons commute; kappa commutes with b and anticommutes with a.
Everything beyond first order in kappa is dropped (kappa^2 = 0).
"""
from fractions import Fraction
from math import comb, factorial

# ---- fermion table: product of normal-ordered monomials a+^fp a-^fm ----------
# Faithful 2x2 matrix model: a+ = E10, a- = E01  ({a-, a+} = 1).
_F = {}


def _fermion_table():
    import itertools

    def mat(fp, fm):
        ap = ((0, 0), (1, 0))
        am = ((0, 1), (0, 0))
        m = ((1, 0), (0, 1))
        for _ in range(fp):
            m = _mm(m, ap)
        for _ in range(fm):
            m = _mm(m, am)
        return m

    for (p1, m1), (p2, m2) in itertools.product(itertools.product((0, 1), repeat=2), repeat=2):
        m = _mm(mat(p1, m1), mat(p2, m2))
        c1, cp, cm = m[0][0], m[1][0], m[0][1]
        cpm = m[1][1] - c1
        res = {}
        for key, c in (((0, 0), c1), ((1, 0), cp), ((0, 1), cm), ((1, 1), cpm)):
            if c:
                res[key] = Fraction(c)
        _F[((p1, m1), (p2, m2))] = res


def _mm(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)) for i in range(2))


_fermion_table()


def _boson_mode_product(p1, q1, p2, q2):
    """(b+)^p1 (b-)^q1 * (b+)^p2 (b-)^q2 -> {(p,q): coeff}, [b-,b+]=1."""
    out = {}
    for k in range(min(q1, p2) + 1):
        out[(p1 + p2 - k, q1 + q2 - k)] = Fraction(factorial(k) * comb(q1, k) * comb(p2, k))
    return out


def _boson_product(B1, B2, n):
    res = {(): Fraction(1)}
    for j in range(n):
        modes = _boson_mode_product(B1[2 * j], B1[2 * j + 1], B2[2 * j], B2[2 * j + 1])
        new = {}
        for pre, c in res.items():
            for pq, c2 in modes.items():
                new[pre + pq] = new.get(pre + pq, 0) + c * c2
        res = new
    return res


def add_to(acc, mono, c):
    if c:
        v = acc.get(mono, 0) + c
        if v:
            acc[mono] = v
        else:
            acc.pop(mono, None)


def mono_product(m1, m2, n, gb=None):
    """Product of two monomials. gb: dict {(sigma, j, s): Fraction}, sigma/s in {'p','m'}, j=1..n."""
    k1, fp1, fm1, B1 = m1
    k2, fp2, fm2, B2 = m2
    out = {}
    if k1 + k2 > 1:
        return out
    # kappa moved left of the second factor's partner: kappa M2 passes A1 (deg fp1+fm1)
    if k2:
        sign0 = -1 if (fp1 + fm1) % 2 else 1
    else:
        sign0 = 1
    k = k1 + k2
    bprod = _boson_product(B1, B2, n)
    for fkey, fc in _F[((fp1, fm1), (fp2, fm2))].items():
        for bk, bc in bprod.items():
            add_to(out, (k, fkey[0], fkey[1], bk), sign0 * fc * bc)
    # first order contraction  b a -> -gb kappa
    if gb and k == 0:
        letters = []
        if fp2:
            letters.append('p')
        if fm2:
            letters.append('m')
        degA1 = fp1 + fm1
        for t, sig in enumerate(letters):  # t = 0-based position
            rem = [l for i, l in enumerate(letters) if i != t]
            rp, rm = (1 if 'p' in rem else 0), (1 if 'm' in rem else 0)
            sign = -1 if (degA1 + t) % 2 else 1
            for j in range(n):
                for s, idx in (('p', 2 * j), ('m', 2 * j + 1)):
                    e = B1[idx]
                    g = gb.get((sig, j + 1, s), 0)
                    if not e or not g:
                        continue
                    B1r = list(B1)
                    B1r[idx] -= 1
                    bprod2 = _boson_product(tuple(B1r), B2, n)
                    for fkey, fc in _F[((fp1, fm1), (rp, rm))].items():
                        for bk, bc in bprod2.items():
                            add_to(out, (1, fkey[0], fkey[1], bk), sign * (-g) * e * fc * bc)
    return out


def mul(X, Y, n, gb=None):
    out = {}
    for m1, c1 in X.items():
        for m2, c2 in Y.items():
            for m, c in mono_product(m1, m2, n, gb).items():
                add_to(out, m, c1 * c2 * c)
    return out


def parity_of(X):
    """Parity of a homogeneous element (fermion degree mod 2 + kappa power)."""
    ps = {(k + fp + fm) % 2 for (k, fp, fm, _), _c in X.items()}
    if len(ps) > 1:
        raise ValueError("inhomogeneous parity")
    return ps.pop() if ps else 0


def lincomb(X, Y, a=1, b=1):
    out = {}
    for m, c in X.items():
        add_to(out, m, a * c)
    for m, c in Y.items():
        add_to(out, m, b * c)
    return out


def scale(X, c):
    return {m: v * c for m, v in X.items() if v * c}


def bracket(X, Y, n, px, py, gb=None):
    """Graded bracket [X,Y} = XY - (-1)^{px py} YX."""
    s = -1 if (px * py) % 2 else 1
    return lincomb(mul(X, Y, n, gb), mul(Y, X, n, gb), 1, -s)
