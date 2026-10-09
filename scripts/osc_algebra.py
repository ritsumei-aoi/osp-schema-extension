"""
Exact normal-ordering engine for the deformed oscillator (Weyl-Clifford) algebra

    U(A_gb) / (K - 1),      A_gb = V + C K + C kappa,

used to realise C(n+1) = osp(2|2n) and its inhomogeneous deformation
(see docs/math/C_inhomogeneous_definition.md).

Generators (integer ids, which also fix the normal order):
    0            : kappa  (odd, central, kappa^2 = 0)
    1            : a^+    (odd)          2 : a^-  (odd)      {a^-, a^+} = 1
    3 + 2(j-1)   : b_j^+  (even)   4 + 2(j-1) : b_j^-  (even)   [b_j^-, b_j^+] = 1

Deformed relations (gb_{sigma,j,s} are complex scalars):
    [b_j^s, a^sigma] = - gb_{sigma,j,s} * kappa .

Coefficients live in the polynomial ring Q[gb_0, ..., gb_{4n-1}]; they are stored
as dicts {monomial(tuple of sorted gb indices): Fraction}.  Because every gb comes
with one factor of kappa and kappa^2 = 0, only degree <= 1 monomials ever occur
(this is asserted by the callers).

A polynomial of U(A_gb) is a dict {word(tuple of generator ids): coefficient}.
All words stored in a polynomial are in normal order.
"""
from fractions import Fraction
from functools import lru_cache

# --------------------------------------------------------------------------
# coefficient ring helpers  (sparse polynomials in the gb parameters)
# --------------------------------------------------------------------------
ONE = {(): Fraction(1)}


def c_add(x, y, scale=Fraction(1)):
    out = dict(x)
    for k, v in y.items():
        nv = out.get(k, Fraction(0)) + scale * v
        if nv == 0:
            out.pop(k, None)
        else:
            out[k] = nv
    return out


def c_mul(x, y):
    out = {}
    for k1, v1 in x.items():
        for k2, v2 in y.items():
            k = tuple(sorted(k1 + k2))
            nv = out.get(k, Fraction(0)) + v1 * v2
            if nv == 0:
                out.pop(k, None)
            else:
                out[k] = nv
    return out


def c_scale(x, s):
    if s == 0:
        return {}
    return {k: v * s for k, v in x.items()}


# --------------------------------------------------------------------------
# polynomial helpers
# --------------------------------------------------------------------------
def p_add(P, Q, scale=Fraction(1)):
    out = {w: dict(c) for w, c in P.items()}
    for w, c in Q.items():
        nc = c_add(out.get(w, {}), c, scale)
        if nc:
            out[w] = nc
        else:
            out.pop(w, None)
    return out


def p_scale(P, s):
    if s == 0:
        return {}
    return {w: c_scale(c, s) for w, c in P.items()}


def p_cscale(P, coef):
    """multiply polynomial by a coefficient-ring element"""
    out = {}
    for w, c in P.items():
        nc = c_mul(c, coef)
        if nc:
            out[w] = nc
    return out


class OscAlgebra:
    def __init__(self, n):
        self.n = n
        self.ngen = 3 + 2 * n
        # gb parameter indexing: p = index of (sigma, j, s) in this list
        self.gb_labels = []
        for sigma in ("+", "-"):
            for j in range(1, n + 1):
                for s in ("+", "-"):
                    self.gb_labels.append((sigma, j, s))
        self.gb_index = {lab: p for p, lab in enumerate(self.gb_labels)}
        self._normal_cache = {}

    # ---- generator bookkeeping -------------------------------------------
    @staticmethod
    def kappa():
        return 0

    @staticmethod
    def a(sigma):
        return 1 if sigma == "+" else 2

    @staticmethod
    def b(j, s):
        return 3 + 2 * (j - 1) + (0 if s == "+" else 1)

    def gen_label(self, g):
        if g == 0:
            return "kappa"
        if g == 1:
            return "a+"
        if g == 2:
            return "a-"
        j = (g - 3) // 2 + 1
        s = "+" if (g - 3) % 2 == 0 else "-"
        return f"b{j}{s}"

    @staticmethod
    def parity(g):
        return 1 if g in (0, 1, 2) else 0

    def word_parity(self, word):
        return sum(self.parity(g) for g in word) % 2

    def is_b(self, g):
        return g >= 3

    def b_data(self, g):
        j = (g - 3) // 2 + 1
        s = "+" if (g - 3) % 2 == 0 else "-"
        return j, s

    # ---- defining supercommutators of generators ---------------------------
    def supercomm_gen(self, x, y):
        """[x, y] (supercommutator) for generators x > y, as a polynomial."""
        if x == 0 or y == 0:
            return {}  # kappa is central
        if x == 2 and y == 1:  # {a-, a+} = 1
            return {(): dict(ONE)}
        if self.is_b(x) and y in (1, 2):  # [b_j^s, a^sigma] = -gb kappa
            j, s = self.b_data(x)
            sigma = "+" if y == 1 else "-"
            p = self.gb_index[(sigma, j, s)]
            return {(0,): {(p,): Fraction(-1)}}
        if self.is_b(x) and self.is_b(y):
            jx, sx = self.b_data(x)
            jy, sy = self.b_data(y)
            if jx == jy and sx == "-" and sy == "+":  # [b^-, b^+] = 1
                return {(): dict(ONE)}
            return {}
        raise ValueError((x, y))

    # ---- normal ordering ----------------------------------------------------
    def normal_word(self, word):
        """Normal order a word; returns polynomial (dict word -> coefficient)."""
        if word in self._normal_cache:
            return self._normal_cache[word]
        res = self._normal_word(word)
        self._normal_cache[word] = res
        return res

    def _normal_word(self, word):
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            if x == y:
                if self.parity(x) == 1:
                    return {}  # odd generators square to zero (kappa^2=a^2=0)
                continue
            if x > y:
                sign = -1 if (self.parity(x) == 1 and self.parity(y) == 1) else 1
                # x y = sign * y x + [x, y]
                swapped = word[:i] + (y, x) + word[i + 2:]
                result = p_scale(self.normal_word(swapped), Fraction(sign))
                for cw, cc in self.supercomm_gen(x, y).items():
                    neww = word[:i] + cw + word[i + 2:]
                    result = p_add(result, p_cscale(self.normal_word(neww), cc))
                return result
        return {word: dict(ONE)}

    def normal(self, P):
        out = {}
        for w, c in P.items():
            out = p_add(out, p_cscale(self.normal_word(w), c))
        return out

    # ---- algebra operations ---------------------------------------------------
    def mul(self, P, Q):
        out = {}
        for w1, c1 in P.items():
            for w2, c2 in Q.items():
                out = p_add(out, p_cscale(self.normal_word(w1 + w2), c_mul(c1, c2)))
        return out

    def poly_parity(self, P):
        pars = {self.word_parity(w) for w in P}
        if len(pars) != 1:
            raise ValueError("inhomogeneous polynomial: %r" % (pars,))
        return pars.pop()

    def supercomm(self, P, Q):
        """[P, Q] = P Q - (-1)^{p(P) p(Q)} Q P for homogeneous P, Q."""
        sign = -1 if (self.poly_parity(P) == 1 and self.poly_parity(Q) == 1) else 1
        return p_add(self.mul(P, Q), self.mul(Q, P), Fraction(-sign))

    # ---- pretty printing ------------------------------------------------------
    def coef_str(self, c):
        parts = []
        for k, v in sorted(c.items()):
            mon = "*".join("gb(%s,%d,%s)" % self.gb_labels[p] for p in k)
            parts.append(f"{v}" + (f"*{mon}" if mon else ""))
        return " + ".join(parts) if parts else "0"

    def poly_str(self, P):
        if not P:
            return "0"
        terms = []
        for w, c in sorted(P.items(), key=lambda t: (len(t[0]), t[0])):
            ws = " ".join(self.gen_label(g) for g in w) or "1"
            terms.append(f"({self.coef_str(c)}) {ws}")
        return " + ".join(terms)
