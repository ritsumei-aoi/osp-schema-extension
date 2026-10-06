"""Oscillator superalgebra for C(n+1) = osp(2|2n), with optional inhomogeneous deformation.

Letters (oscillators), in normal (PBW) order:
    kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m

Relations (K = 1):
    {a_1^-, a_1^+} = 1,  (a_1^+)^2 = (a_1^-)^2 = 0
    [b_k^-, b_l^+] = delta_{kl},  all other boson brackets 0
    [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa        (deformation; 0 if undeformed)
    kappa odd, supercentral, kappa^2 = 0

Coefficients are `Lin` objects: exact linear combinations (Fraction) of symbols, with
the key "1" for the constant part.  This is enough because every gb (or phi) symbol
comes together with one kappa and kappa^2 = 0, so products of two symbols never survive.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache


# --------------------------------------------------------------------------- Lin
class Lin(dict):
    """Linear combination of symbols with Fraction coefficients; key "1" = constant."""

    @staticmethod
    def const(c) -> "Lin":
        c = Fraction(c)
        return Lin({"1": c}) if c else Lin()

    @staticmethod
    def sym(name: str, c=1) -> "Lin":
        return Lin({name: Fraction(c)})

    def __add__(self, other: "Lin") -> "Lin":
        out = Lin(self)
        for k, v in other.items():
            w = out.get(k, 0) + v
            if w:
                out[k] = w
            else:
                out.pop(k, None)
        return out

    def scale(self, c) -> "Lin":
        c = Fraction(c)
        return Lin({k: v * c for k, v in self.items()}) if c else Lin()

    def __mul__(self, other: "Lin") -> "Lin":
        if "1" in self and len(self) == 1:
            return other.scale(self["1"])
        if "1" in other and len(other) == 1:
            return self.scale(other["1"])
        if not self or not other:
            return Lin()
        raise ValueError("product of two symbolic coefficients (should be killed by kappa^2=0)")

    def __neg__(self) -> "Lin":
        return self.scale(-1)

    def is_zero(self) -> bool:
        return not self

    def to_str(self) -> str:
        """SymPy-compatible string, constant first, symbols sorted."""
        if not self:
            return "0"
        parts = []
        for k in sorted(self, key=lambda s: (s != "1", s)):
            v = self[k]
            if k == "1":
                parts.append(str(v))
            elif v == 1:
                parts.append(k)
            elif v == -1:
                parts.append("-" + k)
            else:
                parts.append(f"{v}*{k}")
        s = " + ".join(parts)
        return s.replace("+ -", "- ")

    def evaluate(self, values: dict) -> Fraction:
        tot = Fraction(0)
        for k, v in self.items():
            tot += v * (1 if k == "1" else Fraction(values[k]))
        return tot


def gb_name(sigma: str, j: int, s: str) -> str:
    """Symbol for gb_{a_1^sigma, b_j^s}; sigma, s in {'p','m'}."""
    return f"gb_{sigma}_{j}_{s}"


# --------------------------------------------------------------------------- algebra
class OscAlgebra:
    """Clifford-Weyl superalgebra with one fermion pair, n boson pairs and odd central kappa."""

    def __init__(self, n: int, deformed: bool = False):
        self.n = n
        self.deformed = deformed
        self.letters = ["kappa", "a_1_p", "a_1_m"]
        for k in range(1, n + 1):
            self.letters += [f"b_{k}_p", f"b_{k}_m"]
        self.order = {x: i for i, x in enumerate(self.letters)}
        self.parity = {x: (1 if x in ("kappa", "a_1_p", "a_1_m") else 0) for x in self.letters}
        self._nf = lru_cache(maxsize=None)(self._normal_form_word)

    # -- the bracket of two letters x > y (in order), used when swapping x y -> +- y x + [x, y}
    def _letter_bracket(self, x: str, y: str):
        """Return (word, Lin) for the supercommutator [x, y} or None if it vanishes."""
        if x == "a_1_m" and y == "a_1_p":
            return (), Lin.const(1)
        if x.startswith("b_") and y.startswith("b_"):
            _, kx, sx = x.split("_")
            _, ky, sy = y.split("_")
            if kx == ky and sx == "m" and sy == "p":
                return (), Lin.const(1)
            return None
        if self.deformed and x.startswith("b_") and y.startswith("a_1_"):
            _, j, s = x.split("_")
            sigma = y.split("_")[2]
            return ("kappa",), Lin.sym(gb_name(sigma, int(j), s), -1)
        return None

    def _normal_form_word(self, word: tuple) -> dict:
        """Normal form of a single word (coefficient 1) as {word: Lin}."""
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            if x == y and self.parity[x] == 1:  # a^2 = 0, kappa^2 = 0
                return {}
            if self.order[x] > self.order[y]:
                sign = -1 if (self.parity[x] and self.parity[y]) else 1
                out: dict = {}
                swapped = word[:i] + (y, x) + word[i + 2:]
                _acc(out, self._nf(swapped), Lin.const(sign))
                br = self._letter_bracket(x, y)
                if br is not None:
                    w, c = br
                    _acc(out, self._nf(word[:i] + w + word[i + 2:]), c)
                return out
        return {word: Lin.const(1)}

    # -- elements are dicts {word(tuple): Lin}
    def normal(self, elem: dict) -> dict:
        out: dict = {}
        for w, c in elem.items():
            _acc(out, self._nf(w), c)
        return out

    def mul(self, x: dict, y: dict) -> dict:
        out: dict = {}
        for wx, cx in x.items():
            for wy, cy in y.items():
                c = cx * cy
                if c:
                    _acc(out, self._nf(wx + wy), c)
        return out

    def word_parity(self, w: tuple) -> int:
        return sum(self.parity[x] for x in w) % 2

    def bracket(self, x: dict, y: dict, px: int, py: int) -> dict:
        """Graded bracket [x, y} = xy - (-1)^{px py} yx of homogeneous elements."""
        xy = self.mul(x, y)
        yx = self.mul(y, x)
        sign = -1 if (px and py) else 1
        out = dict(xy)
        for w, c in yx.items():
            _acc_single(out, w, c.scale(-sign))
        return out


def _acc_single(out: dict, w: tuple, c: Lin) -> None:
    if not c:
        return
    v = out.get(w)
    v = c if v is None else v + c
    if v:
        out[w] = v
    else:
        out.pop(w, None)


def _acc(out: dict, src: dict, factor: Lin) -> None:
    for w, c in src.items():
        _acc_single(out, w, c * factor)


def split_kappa(elem: dict):
    """Split a normal-ordered element into (kappa-free part, kappa-coefficient part)."""
    p0, p1 = {}, {}
    for w, c in elem.items():
        if w and w[0] == "kappa":
            p1[w[1:]] = c
        else:
            p0[w] = c
    return p0, p1
