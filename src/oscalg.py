"""Normal-ordering engine for the oscillator algebra of C(n+1) = osp(2|2n).

Letters (integers, also the PBW word order):
    0 kappa (odd, central, kappa^2 = 0)
    1 a_1_p, 2 a_1_m                (odd, CAR {a-, a+} = 1)
    3+2(i-1) b_i_p, 4+2(i-1) b_i_m  (even, CCR [b_i-, b_j+] = delta_ij)

Undeformed: bosons commute with fermions.  Deformed (gb given):
    [b_j^s, a^sigma] = b a - a b = -gb[(sigma, j, s)] * kappa,
kappa odd central: kappa x = (-1)^{p(x)} x kappa.
Elements are dicts {word(tuple of ints): Fraction}.
"""
from fractions import Fraction
from functools import lru_cache

KAPPA, AP, AM = 0, 1, 2


def b_letter(i, s):
    return 3 + 2 * (i - 1) + (0 if s == "p" else 1)


def letter_name(x):
    if x == KAPPA:
        return "kappa"
    if x in (AP, AM):
        return "a_1_" + ("p" if x == AP else "m")
    i = (x - 3) // 2 + 1
    return f"b_{i}_" + ("p" if (x - 3) % 2 == 0 else "m")


def letter_parity(x):
    return 1 if x <= AM else 0


def word_parity(w):
    return sum(letter_parity(x) for x in w) % 2


class OscAlgebra:
    def __init__(self, gb=None):
        """gb: dict {(sigma 'p'/'m', j, s 'p'/'m'): number} or None (undeformed)."""
        self.gb = {k: Fraction(v) for k, v in (gb or {}).items()}
        self._cache = {}

    def _gbval(self, sigma, j, s):
        return self.gb.get((sigma, j, s), Fraction(0))

    def normal(self, word):
        """Normal-order a word -> dict word->coeff."""
        word = tuple(word)
        hit = self._cache.get(word)
        if hit is not None:
            return hit
        res = self._normal(word)
        self._cache[word] = res
        return res

    def _normal(self, w):
        for i in range(len(w) - 1):
            x, y = w[i], w[i + 1]
            if x == y and x <= AM:  # kappa^2 = a^2 = 0
                return {}
            if x > y:
                out = {}
                sign = -1 if (letter_parity(x) and letter_parity(y)) else 1
                self._add(out, self.normal(w[:i] + (y, x) + w[i + 2:]), sign)
                # scalar / kappa terms from the commutator
                if x == AM and y == AP:
                    self._add(out, self.normal(w[:i] + w[i + 2:]), 1)
                elif x >= 3 and y >= 3 and x == y + 1 and (y - 3) % 2 == 0:
                    self._add(out, self.normal(w[:i] + w[i + 2:]), 1)
                elif x >= 3 and y in (AP, AM) and self.gb:
                    j = (x - 3) // 2 + 1
                    s = "p" if (x - 3) % 2 == 0 else "m"
                    g = self._gbval("p" if y == AP else "m", j, s)
                    if g:
                        self._add(out, self.normal(w[:i] + (KAPPA,) + w[i + 2:]), -g)
                return out
        return {w: Fraction(1)}

    @staticmethod
    def _add(acc, other, c):
        for k, v in other.items():
            nv = acc.get(k, 0) + c * v
            if nv:
                acc[k] = nv
            elif k in acc:
                del acc[k]

    def mul(self, A, B):
        out = {}
        for wa, ca in A.items():
            for wb, cb in B.items():
                self._add(out, self.normal(wa + wb), ca * cb)
        return out

    def bracket(self, A, pA, B, pB):
        """Graded commutator AB - (-1)^{pA pB} BA."""
        out = {}
        self._add(out, self.mul(A, B), 1)
        self._add(out, self.mul(B, A), -1 if (pA * pB) % 2 == 0 else 1)
        return out


def make_decomposer(vectors):
    """Return decompose(v) -> (coeffs, residual) w.r.t. the given (independent) vectors."""
    reduced = []  # (pivot, vec, transform)
    for idx, v in enumerate(vectors):
        v = dict(v)
        t = {idx: Fraction(1)}
        for piv, rv, rt in reduced:
            c = v.get(piv, 0)
            if c:
                OscAlgebra._add(v, rv, -c)
                OscAlgebra._add(t, rt, -c)
        if not v:
            raise ValueError("basis vectors are linearly dependent")
        piv = min(v)
        c = v[piv]
        v = {k: x / c for k, x in v.items()}
        t = {k: x / c for k, x in t.items()}
        reduced.append((piv, v, t))

    def decompose(vec):
        v = dict(vec)
        coeffs = {}
        for piv, rv, rt in reduced:
            c = v.get(piv, 0)
            if c:
                OscAlgebra._add(v, rv, -c)
                OscAlgebra._add(coeffs, rt, c)
        return coeffs, v

    return decompose
