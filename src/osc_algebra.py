"""
Oscillator algebra engine for C(n+1) = osp(2|2n).

Elements of the universal enveloping algebra U(A) of the oscillator extension
A = V + C K + C kappa are represented as dicts {word: coeff}, where a word is a
tuple of oscillator labels in *normal order* and coeff is a sympy expression
(rational numbers, possibly linear in the deformation symbols gb_*).

Normal order (handover/notation.md §2):
    kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m

Relations:
    {a_1_m, a_1_p} = 1,  (a_1_±)^2 = 0
    [b_k_m, b_l_p] = δ_kl,  [b_k_±, b_l_±] = 0
    [b_k_s, a_1_σ] = -gb_{σ,k,s} kappa      (gb = 0 : undeformed)
    kappa odd central: kappa a = -a kappa, kappa b = b kappa, kappa^2 = 0
    K = 1 (the empty word).
"""
from __future__ import annotations

import sympy
from sympy import Rational, Symbol, Integer, expand

ZERO = Integer(0)
ONE = Integer(1)


def gb_label(sigma: str, k: int, s: str) -> str:
    """Label of the deformation parameter gb_{sigma,k,s}, e.g. gb_a1p_b1m."""
    return f"gb_a1{sigma}_b{k}{s}"


def gb_symbols(n: int) -> dict:
    """All 4n deformation symbols, keyed by (sigma, k, s)."""
    return {(sig, k, s): Symbol(gb_label(sig, k, s))
            for sig in "pm" for k in range(1, n + 1) for s in "pm"}


class OscAlgebra:
    """Normal-ordering engine for U(A) modulo kappa^2."""

    def __init__(self, n: int, gb: dict | None = None):
        self.n = n
        self.letters = ["kappa", "a_1_p", "a_1_m"] + [
            f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"]
        self.index = {l: i for i, l in enumerate(self.letters)}
        self.parity = {l: (1 if l in ("kappa", "a_1_p", "a_1_m") else 0)
                       for l in self.letters}
        # gb[(sigma, k, s)] -> sympy expression (default 0)
        self.gb = dict(gb) if gb else {}

    # ------------------------------------------------------------------ words
    def word_parity(self, word) -> int:
        return sum(self.parity[l] for l in word) % 2

    def _swap_rule(self, x: str, y: str):
        """Return (sign, extra) such that  x y = sign * y x + extra,
        for letters x, y with index[x] > index[y]. extra is a dict word->coeff."""
        px, py = self.parity[x], self.parity[y]
        sign = -1 if (px and py) else 1
        extra = {}
        if y == "kappa":
            return sign, extra                      # kappa central
        if x == "a_1_m" and y == "a_1_p":
            extra[()] = ONE                         # a_m a_p = -a_p a_m + 1
            return sign, extra
        if x.startswith("b_") and y.startswith("b_"):
            _, kx, sx = x.split("_")
            _, ky, sy = y.split("_")
            if kx == ky and sx == "m" and sy == "p":
                extra[()] = ONE                     # b_m b_p = b_p b_m + 1
            return sign, extra
        if x.startswith("b_") and y.startswith("a_"):
            _, k, s = x.split("_")
            sigma = y.split("_")[2]
            g = self.gb.get((sigma, int(k), s), ZERO)
            if g != 0:
                extra[("kappa",)] = -g              # b a = a b - gb kappa
            return sign, extra
        raise ValueError(f"unexpected pair {x} {y}")

    def normal_form(self, word, coeff=ONE) -> dict:
        """Normal-order a single word. Returns {word: coeff}."""
        result = {}
        stack = [(tuple(word), coeff)]
        while stack:
            w, c = stack.pop()
            if c == 0:
                continue
            # find first inversion
            pos = None
            for i in range(len(w) - 1):
                if self.index[w[i]] > self.index[w[i + 1]]:
                    pos = i
                    break
                if w[i] == w[i + 1] and self.parity[w[i]] == 1:
                    c = ZERO       # kappa^2 = 0, (a^±)^2 = 0
                    break
            if c == 0:
                continue
            if pos is None:
                result[w] = result.get(w, ZERO) + c
                continue
            x, y = w[pos], w[pos + 1]
            sign, extra = self._swap_rule(x, y)
            stack.append((w[:pos] + (y, x) + w[pos + 2:], sign * c))
            for ew, ec in extra.items():
                stack.append((w[:pos] + ew + w[pos + 2:], c * ec))
        return {w: expand(c) for w, c in result.items() if expand(c) != 0}

    # --------------------------------------------------------------- elements
    @staticmethod
    def add(p: dict, q: dict, scale=ONE) -> dict:
        r = dict(p)
        for w, c in q.items():
            r[w] = r.get(w, ZERO) + scale * c
        return {w: expand(c) for w, c in r.items() if expand(c) != 0}

    def mul(self, p: dict, q: dict) -> dict:
        r = {}
        for w1, c1 in p.items():
            for w2, c2 in q.items():
                for w, c in self.normal_form(w1 + w2, c1 * c2).items():
                    r[w] = r.get(w, ZERO) + c
        return {w: expand(c) for w, c in r.items() if expand(c) != 0}

    def element_parity(self, p: dict) -> int:
        ps = {self.word_parity(w) for w in p}
        if len(ps) > 1:
            raise ValueError("inhomogeneous element")
        return ps.pop() if ps else 0

    def bracket(self, p: dict, q: dict) -> dict:
        """Graded bracket [p, q} = p q - (-1)^{|p||q|} q p."""
        sign = -1 if (self.element_parity(p) and self.element_parity(q)) else 1
        return self.add(self.mul(p, q), self.mul(q, p), -sign)

    def substitute(self, p: dict, mapping: dict) -> dict:
        """Replace each letter l by the element mapping[l] (default: itself)
        and renormalize. Used for the oscillator shift b -> b + kappa c."""
        r = {}
        for w, c in p.items():
            term = {(): c}
            for l in w:
                term = self.mul(term, mapping.get(l, {(l,): ONE}))
            r = self.add(r, term)
        return r

    @staticmethod
    def split_kappa(p: dict):
        """Split p = p0 + kappa * p1 into (p0, p1) with kappa stripped."""
        p0, p1 = {}, {}
        for w, c in p.items():
            if w and w[0] == "kappa":
                p1[w[1:]] = c
            else:
                p0[w] = c
        return p0, p1


def word_str(word) -> str:
    return " ".join(word) if word else "1"
