"""Exact normal-ordered oscillator (Weyl-Clifford) superalgebra for C(n+1) = osp(2|2n).

Generators (PBW / normal order):  kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m

Relations
    {a_1_m, a_1_p} = 1,  (a_1_p)^2 = (a_1_m)^2 = 0          (CAR)
    [b_k_m, b_k_p] = 1,  [b_k_s, b_l_t] = 0 otherwise         (CCR)
    [b_j_s, a_1_sigma] = -gb_{sigma,j,s} * kappa                (deformation; gb = 0 if undeformed)
    kappa odd, kappa^2 = 0, super-central: kappa b = b kappa, kappa a = -a kappa.

Elements are dicts {word: Poly}, where a word is a tuple of generator names in normal order and
Poly is an exact sparse polynomial over Q in the gb symbols.
"""
from __future__ import annotations

from fractions import Fraction


# ---------------------------------------------------------------------------
# Sparse multivariate polynomials over Q
# ---------------------------------------------------------------------------
class Poly:
    """Sparse polynomial over Q.  terms: {monomial: Fraction}; monomial = tuple of (var, exp)."""

    __slots__ = ("terms",)

    def __init__(self, terms=None):
        self.terms = {}
        if terms:
            for m, c in terms.items():
                c = Fraction(c)
                if c != 0:
                    self.terms[m] = c

    # constructors ---------------------------------------------------------
    @staticmethod
    def const(c) -> "Poly":
        return Poly({(): Fraction(c)})

    @staticmethod
    def var(name: str) -> "Poly":
        return Poly({((name, 1),): Fraction(1)})

    @staticmethod
    def _coerce(x) -> "Poly":
        if isinstance(x, Poly):
            return x
        return Poly.const(x)

    # predicates -----------------------------------------------------------
    def __bool__(self):
        return bool(self.terms)

    def is_zero(self) -> bool:
        return not self.terms

    def is_constant(self) -> bool:
        return all(m == () for m in self.terms)

    def constant(self) -> Fraction:
        return self.terms.get((), Fraction(0))

    def degree(self) -> int:
        return max((sum(e for _, e in m) for m in self.terms), default=0)

    def variables(self) -> set:
        return {v for m in self.terms for v, _ in m}

    def __eq__(self, other):
        return self.terms == Poly._coerce(other).terms

    def __ne__(self, other):
        return not self.__eq__(other)

    __hash__ = None

    # arithmetic -----------------------------------------------------------
    def __add__(self, other):
        other = Poly._coerce(other)
        t = dict(self.terms)
        for m, c in other.terms.items():
            t[m] = t.get(m, Fraction(0)) + c
        return Poly(t)

    __radd__ = __add__

    def __neg__(self):
        return Poly({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-Poly._coerce(other))

    def __rsub__(self, other):
        return Poly._coerce(other) - self

    @staticmethod
    def _mul_mono(m1, m2):
        d = dict(m1)
        for v, e in m2:
            d[v] = d.get(v, 0) + e
        return tuple(sorted(d.items()))

    def __mul__(self, other):
        other = Poly._coerce(other)
        t = {}
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                m = Poly._mul_mono(m1, m2)
                t[m] = t.get(m, Fraction(0)) + c1 * c2
        return Poly(t)

    __rmul__ = __mul__

    def subs(self, values: dict) -> "Poly":
        """Substitute variables by rationals (variables absent from `values` are kept)."""
        out = Poly()
        for m, c in self.terms.items():
            coeff = Fraction(c)
            rest = []
            for v, e in m:
                if v in values:
                    coeff *= Fraction(values[v]) ** e
                else:
                    rest.append((v, e))
            out = out + Poly({tuple(rest): coeff})
        return out

    # string / JSON forms --------------------------------------------------
    @staticmethod
    def mono_str(m) -> str:
        if m == ():
            return "1"
        return "*".join(v if e == 1 else f"{v}^{e}" for v, e in m)

    @staticmethod
    def parse_mono(s: str):
        if s in ("", "1"):
            return ()
        d = {}
        for f in s.split("*"):
            if "^" in f:
                v, e = f.split("^")
                d[v] = d.get(v, 0) + int(e)
            else:
                d[f] = d.get(f, 0) + 1
        return tuple(sorted(d.items()))

    def __str__(self) -> str:
        if not self.terms:
            return "0"
        items = sorted(self.terms.items(), key=lambda kv: (len(kv[0]), kv[0]))
        out = ""
        for m, c in items:
            ms = Poly.mono_str(m)
            if m == ():
                body = str(abs(c))
            elif abs(c) == 1:
                body = ms
            else:
                body = f"{abs(c)}*{ms}"
            if out == "":
                out = ("-" if c < 0 else "") + body
            else:
                out += (" - " if c < 0 else " + ") + body
        return out

    __repr__ = __str__

    def to_terms_dict(self) -> dict:
        return {Poly.mono_str(m): str(c) for m, c in sorted(self.terms.items())}

    @staticmethod
    def from_terms_dict(d: dict) -> "Poly":
        return Poly({Poly.parse_mono(k): Fraction(v) for k, v in d.items()})


# ---------------------------------------------------------------------------
# Element helpers (dict word -> Poly)
# ---------------------------------------------------------------------------
def el_add(a: dict, b: dict) -> dict:
    out = dict(a)
    for w, c in b.items():
        s = out.get(w, Poly()) + c
        if s:
            out[w] = s
        elif w in out:
            del out[w]
    return out


def el_scale(a: dict, c) -> dict:
    c = Poly._coerce(c)
    if not c:
        return {}
    return {w: v * c for w, v in a.items() if (v * c)}


def el_is_zero(a: dict) -> bool:
    return all(not c for c in a.values())


# ---------------------------------------------------------------------------
# The algebra
# ---------------------------------------------------------------------------
class OscillatorAlgebra:
    def __init__(self, n: int, deformed: bool = False):
        self.n = n
        self.deformed = deformed
        self.gens = ["kappa", "a_1_p", "a_1_m"]
        for k in range(1, n + 1):
            self.gens += [f"b_{k}_p", f"b_{k}_m"]
        self.index = {g: i for i, g in enumerate(self.gens)}
        self.parity = {g: (1 if (g == "kappa" or g.startswith("a_")) else 0) for g in self.gens}
        self.nilpotent = {"kappa", "a_1_p", "a_1_m"}
        # deformation parameters gb_{sigma, j, s}
        self.gb = {}
        for sigma in "pm":
            for j in range(1, n + 1):
                for s in "pm":
                    self.gb[(sigma, j, s)] = Poly.var(self.gb_label(sigma, j, s)) if deformed else Poly()
        self._cache: dict = {}

    @staticmethod
    def gb_label(sigma: str, j: int, s: str) -> str:
        return f"gb_a1{sigma}_b{j}{s}"

    def gb_labels(self) -> list:
        return [self.gb_label(sigma, j, s) for sigma in "pm" for j in range(1, self.n + 1) for s in "pm"]

    # ---- rewriting rule:  x y = sign * y x + c   for index[x] > index[y] -------------
    def _swap_rule(self, x: str, y: str):
        px, py = self.parity[x], self.parity[y]
        sign = -1 if (px and py) else 1
        c: dict = {}
        if x.startswith("b_") and y.startswith("b_"):
            _, kx, sx = x.split("_")
            _, ky, sy = y.split("_")
            if kx == ky and sx == "m" and sy == "p":          # b_m b_p = b_p b_m + 1
                c = {(): Poly.const(1)}
        elif x == "a_1_m" and y == "a_1_p":                   # a_m a_p = -a_p a_m + 1
            c = {(): Poly.const(1)}
        elif x.startswith("b_") and y in ("a_1_p", "a_1_m"):  # b a = a b - gb kappa
            _, j, s = x.split("_")
            sigma = "p" if y == "a_1_p" else "m"
            g = self.gb[(sigma, int(j), s)]
            if g:
                c = {("kappa",): -g}
        # x vs kappa (kappa super-central): no extra term
        return sign, c

    def normal_order(self, word: tuple) -> dict:
        if word in self._cache:
            return self._cache[word]
        res = None
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            if x == y and x in self.nilpotent:
                res = {}
                break
            if self.index[x] > self.index[y]:
                sign, c = self._swap_rule(x, y)
                res = el_scale(self.normal_order(word[:i] + (y, x) + word[i + 2:]), sign)
                for cw, cc in c.items():
                    res = el_add(res, el_scale(self.normal_order(word[:i] + cw + word[i + 2:]), cc))
                break
        if res is None:
            res = {word: Poly.const(1)}
        self._cache[word] = res
        return res

    def word_parity(self, word: tuple) -> int:
        return sum(self.parity[g] for g in word) % 2

    def mul(self, a: dict, b: dict) -> dict:
        out: dict = {}
        for wa, ca in a.items():
            for wb, cb in b.items():
                out = el_add(out, el_scale(self.normal_order(wa + wb), ca * cb))
        return out

    def bracket(self, a: dict, b: dict, pa: int, pb: int) -> dict:
        """Super-commutator [a, b} = ab - (-1)^{pa pb} ba for homogeneous a, b of parities pa, pb."""
        sign = -1 if (pa and pb) else 1
        return el_add(self.mul(a, b), el_scale(self.mul(b, a), -sign))

    def element_parity(self, a: dict) -> int:
        ps = {self.word_parity(w) for w in a}
        if len(ps) > 1:
            raise ValueError("inhomogeneous element")
        return ps.pop() if ps else 0

    def subs(self, a: dict, values: dict) -> dict:
        out = {}
        for w, c in a.items():
            c2 = c.subs(values)
            if c2:
                out[w] = c2
        return out


def element_to_str(a: dict) -> str:
    if not a:
        return "0"
    parts = []
    for w, c in sorted(a.items(), key=lambda kv: (len(kv[0]), kv[0])):
        ws = " ".join(w) if w else "1"
        cs = str(c)
        if "+" in cs or (" - " in cs):
            cs = f"({cs})"
        parts.append(f"{cs}*{ws}" if ws != "1" else cs)
    return " + ".join(parts)
