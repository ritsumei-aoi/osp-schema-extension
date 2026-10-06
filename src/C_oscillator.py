"""Oscillator (Weyl-Clifford) algebra engine for C(n+1) = osp(2|2n).

Generators, in normal-ordering order:
    kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m
kappa is an odd central nilpotent element (kappa^2 = 0, {kappa, a} = 0,
[kappa, b] = 0).  Relations:
    {a_1_m, a_1_p} = 1,  a^2 = 0           (CAR)
    [b_k_m, b_k_p] = 1                      (CCR)
    [b_j^s, a^sigma] = -gb[(sigma, j, s)] * kappa   (deformation; gb = 0 gives g)
Elements are dicts {word(tuple of generator indices): Fraction}.
"""
from fractions import Fraction

KAPPA = 0
A_P, A_M = 1, 2


def b_index(k, s):
    """Generator index of b_k^s (k >= 1, s in 'p','m')."""
    return 3 + 2 * (k - 1) + (0 if s == "p" else 1)


def gen_names(n):
    names = ["kappa", "a_1_p", "a_1_m"]
    for k in range(1, n + 1):
        names += [f"b_{k}_p", f"b_{k}_m"]
    return names


def gen_parity(g):
    return 1 if g in (KAPPA, A_P, A_M) else 0


class OscAlgebra:
    def __init__(self, n, gb=None):
        """gb: dict {(sigma, k, s): value}, sigma/s in 'p','m'; missing = 0."""
        self.n = n
        self.gb = {k: Fraction(v) for k, v in (gb or {}).items()}
        self._cache = {}

    def _gb(self, a, b):
        """gb for the pair of fermion index a and boson index b."""
        sigma = "p" if a == A_P else "m"
        k = (b - 3) // 2 + 1
        s = "p" if (b - 3) % 2 == 0 else "m"
        return self.gb.get((sigma, k, s), Fraction(0))

    def normal(self, word):
        if word in self._cache:
            return self._cache[word]
        res = {}
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            if x == y and gen_parity(x) == 1:
                res = {}
                break
            if x > y:
                px, py = gen_parity(x), gen_parity(y)
                sign = -1 if (px and py) else 1
                swapped = word[:i] + (y, x) + word[i + 2:]
                for w, c in self.normal(swapped).items():
                    res[w] = res.get(w, 0) + sign * c
                if x == A_M and y == A_P:                      # {a-, a+} = 1
                    coeff, mid = Fraction(1), ()
                elif x >= 3 and y >= 3 and x == y + 1 and (y - 3) % 2 == 0:
                    coeff, mid = Fraction(1), ()               # [b-, b+] = 1
                elif x >= 3 and y in (A_P, A_M):               # [b, a] = -gb kappa
                    coeff, mid = -self._gb(y, x), (KAPPA,)
                else:
                    coeff, mid = Fraction(0), ()
                if coeff != 0:
                    new = word[:i] + mid + word[i + 2:]
                    for w, c in self.normal(new).items():
                        res[w] = res.get(w, 0) + coeff * c
                break
        else:
            res = {word: Fraction(1)}
        res = {w: c for w, c in res.items() if c != 0}
        self._cache[word] = res
        return res

    def mul(self, X, Y):
        out = {}
        for w1, c1 in X.items():
            for w2, c2 in Y.items():
                for w, c in self.normal(w1 + w2).items():
                    out[w] = out.get(w, 0) + c1 * c2 * c
        return {w: c for w, c in out.items() if c != 0}

    def bracket(self, X, Y, pX, pY):
        """Supercommutator [X, Y} = XY - (-1)^{pX pY} YX."""
        s = -1 if (pX and pY) else 1
        out = dict(self.mul(X, Y))
        for w, c in self.mul(Y, X).items():
            out[w] = out.get(w, 0) - s * c
        return {w: c for w, c in out.items() if c != 0}
