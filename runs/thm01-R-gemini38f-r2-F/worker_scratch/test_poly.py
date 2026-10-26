from fractions import Fraction
from collections import defaultdict
import itertools

class Monomial:
    """
    Represents (a_1^+)^{f_p} (a_1^-)^{f_m} * prod_{k=1}^n (b_k^+)^{bp[k-1]} (b_k^-)^{bm[k-1]}
    f_p, f_m in {0, 1}
    bp, bm are tuples of length n of non-negative ints
    """
    def __init__(self, fp, fm, bp, bm):
        self.fp = fp
        self.fm = fm
        self.bp = tuple(bp)
        self.bm = tuple(bm)
        self.n = len(self.bp)

    @property
    def parity(self):
        return (self.fp + self.fm) % 2

    def __eq__(self, other):
        return (self.fp, self.fm, self.bp, self.bm) == (other.fp, other.fm, other.bp, other.bm)

    def __hash__(self):
        return hash((self.fp, self.fm, self.bp, self.bm))

    def __repr__(self):
        parts = []
        if self.fp: parts.append("a_1_p")
        if self.fm: parts.append("a_1_m")
        for k in range(self.n):
            if self.bp[k]: parts.append(f"b_{k+1}_p^{self.bp[k]}" if self.bp[k] > 1 else f"b_{k+1}_p")
            if self.bm[k]: parts.append(f"b_{k+1}_m^{self.bm[k]}" if self.bm[k] > 1 else f"b_{k+1}_m")
        return " * ".join(parts) if parts else "1"

class Poly:
    def __init__(self, terms=None, n=1):
        self.n = n
        self.terms = defaultdict(Fraction)
        if terms:
            for m, c in terms.items():
                c = Fraction(c)
                if c != 0:
                    self.terms[m] += c
            # Clean zeros
            self.terms = defaultdict(Fraction, {m: c for m, c in self.terms.items() if c != 0})

    @classmethod
    def from_osc(cls, name, n):
        # name: a_1_p, a_1_m, b_{k}_p, b_{k}_m
        bp = [0]*n
        bm = [0]*n
        fp, fm = 0, 0
        if name == "a_1_p":
            fp = 1
        elif name == "a_1_m":
            fm = 1
        elif name.startswith("b_"):
            parts = name.split("_")
            k = int(parts[1]) - 1
            if parts[2] == "p":
                bp[k] = 1
            else:
                bm[k] = 1
        return cls({Monomial(fp, fm, bp, bm): Fraction(1)}, n=n)

    @classmethod
    def const(cls, val, n):
        m = Monomial(0, 0, (0,)*n, (0,)*n)
        return cls({m: Fraction(val)}, n=n)

    def __add__(self, other):
        res = defaultdict(Fraction, self.terms)
        for m, c in other.terms.items():
            res[m] += c
        return Poly({m: c for m, c in res.items() if c != 0}, n=self.n)

    def __sub__(self, other):
        return self + (other * Fraction(-1))

    def __mul__(self, other):
        if isinstance(other, (int, Fraction)):
            if other == 0:
                return Poly(n=self.n)
            return Poly({m: c * Fraction(other) for m, c in self.terms.items()}, n=self.n)
        elif isinstance(other, Poly):
            res = defaultdict(Fraction)
            for m1, c1 in self.terms.items():
                for m2, c2 in other.terms.items():
                    prod_terms = mul_monomials(m1, m2)
                    for pm, pc in prod_terms:
                        res[pm] += c1 * c2 * pc
            return Poly({m: c for m, c in res.items() if c != 0}, n=self.n)

    def __rmul__(self, other):
        return self.__mul__(other)

def mul_monomials(m1, m2):
    """
    Multiply two monomials m1 * m2 and return list of (Monomial, Fraction).
    Fermions commute with bosons.
    Fermion part:
    (a_1^+)^f1p (a_1^-)^f1m * (a_1^+)^f2p (a_1^-)^f2m
    Using CAR:
    {a_1^-, a_1^+} = 1 => a_1^- a_1^+ = 1 - a_1^+ a_1^-
    (a_1^+)^2 = (a_1^-)^2 = 0.
    """
    # Fermion part
    # Evaluate product of strings of a_p, a_m
    ferm_terms = mul_fermions(m1.fp, m1.fm, m2.fp, m2.fm)
    # Boson part: mode by mode
    # For each mode k: (b_k^+)^u1 (b_k^-)^v1 * (b_k^+)^u2 (b_k^-)^v2
    # We need to normal order: (b^-)^v1 (b^+)^u2
    # Standard formula: (b^-)^v (b^+)^u = sum_{r=0}^{min(u,v)} r! binom(v, r) binom(u, r) (b^+)^{u-r} (b^-)^{v-r}
    boson_modes = []
    for k in range(m1.n):
        u1, v1 = m1.bp[k], m1.bm[k]
        u2, v2 = m2.bp[k], m2.bm[k]
        b_terms = mul_boson_mode(u1, v1, u2, v2)
        boson_modes.append(b_terms)

    # Combine
    # Cartesian product of boson modes
    total_terms = []
    for f_mono, f_coeff in ferm_terms:
        # boson product
        for b_comb in itertools.product(*boson_modes):
            # b_comb is a tuple of ( (u_k, v_k), coeff_k )
            b_coeff = Fraction(1)
            bp = []
            bm = []
            for (uk, vk), ck in b_comb:
                b_coeff *= ck
                bp.append(uk)
                bm.append(vk)
            total_terms.append((Monomial(f_mono[0], f_mono[1], bp, bm), f_coeff * b_coeff))
    return total_terms

def mul_fermions(f1p, f1m, f2p, f2m):
    # returns list of ((fp, fm), coeff)
    # Cases:
    # If f1m == 0:
    # (a_p)^f1p * (a_p)^f2p (a_m)^f2m:
    # if f1p == 1 and f2p == 1: 0
    # else: ((f1p + f2p, f2m), 1)
    if f1m == 0:
        if f1p == 1 and f2p == 1:
            return []
        return [((f1p + f2p, f2m), Fraction(1))]
    # If f1m == 1:
    # (a_p)^f1p a_m (a_p)^f2p (a_m)^f2m
    if f2p == 0:
        # (a_p)^f1p a_m (a_m)^f2m
        if f2m == 1:
            return [] # (a_m)^2 = 0
        return [((f1p, 1), Fraction(1))]
    else:
        # f2p == 1
        # a_m a_p = 1 - a_p a_m
        # (a_p)^f1p (1 - a_p a_m) (a_m)^f2m
        # = (a_p)^f1p (a_m)^f2m - (a_p)^f1p a_p a_m (a_m)^f2m
        # Note: (a_p)^f1p a_p is 0 if f1p == 1
        # and a_m (a_m)^f2m is 0 if f2m == 1
        res = []
        # term 1: (a_p)^f1p (a_m)^f2m
        res.append(((f1p, f2m), Fraction(1)))
        # term 2: - (a_p)^{f1p+1} (a_m)^{f2m+1}
        if f1p == 0 and f2m == 0:
            res.append(((1, 1), Fraction(-1)))
        return res

import math

def mul_boson_mode(u1, v1, u2, v2):
    # (b^+)^u1 (b^-)^v1 (b^+)^u2 (b^-)^v2
    # Normal order (b^-)^v1 (b^+)^u2:
    # = sum_{r=0}^{min(u2, v1)} r! * binom(v1, r) * binom(u2, r) * (b^+)^{u2 - r} (b^-)^{v1 - r}
    # Then overall (b^+)^{u1 + u2 - r} (b^-)^{v1 - r + v2}
    res = []
    max_r = min(u2, v1)
    for r in range(max_r + 1):
        coeff = Fraction(math.factorial(r) * math.comb(v1, r) * math.comb(u2, r))
        res.append(((u1 + u2 - r, v1 - r + v2), coeff))
    return res

print("Monomial and Poly classes defined successfully.")
