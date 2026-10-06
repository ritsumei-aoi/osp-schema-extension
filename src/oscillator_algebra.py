"""Normal-ordering engine for the oscillator superalgebra U(A) used by C(n+1) = osp(2|2n).

Generators: kappa (odd, central, kappa^2 = 0), a_1_p, a_1_m (odd, CAR),
b_k_p, b_k_m (even, CCR), k = 1..n.  K is identified with the scalar 1.

Deformation (optional): [b_j^s, a_1^sigma] = - gb_{sigma,j,s} kappa, where the gb are
treated as symbolic scalar coefficients.

Elements are dicts  word(tuple of labels) -> Poly,  where a Poly is a dict
monomial(tuple of sorted gb labels) -> Fraction.  Words are kept in standard
(normal) order: kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_m.
"""
from fractions import Fraction

# ---------------------------------------------------------------- Poly helpers


def poly_const(c):
    c = Fraction(c)
    return {(): c} if c else {}


def poly_add_into(target, p, scale=Fraction(1)):
    for mono, c in p.items():
        v = target.get(mono, Fraction(0)) + c * scale
        if v:
            target[mono] = v
        else:
            target.pop(mono, None)
    return target


def poly_mul(p, q):
    out = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            mono = tuple(sorted(m1 + m2))
            v = out.get(mono, Fraction(0)) + c1 * c2
            if v:
                out[mono] = v
            else:
                out.pop(mono, None)
    return out


def poly_to_json(p):
    """Poly -> {label or "1": "rational"}."""
    return {("*".join(m) if m else "1"): str(c) for m, c in sorted(p.items())}


# -------------------------------------------------------------- Element helpers


def elem_add_into(target, e, scale=None):
    """target += scale * e  (scale is a Poly or None for 1)."""
    for w, p in e.items():
        q = p if scale is None else poly_mul(p, scale)
        cur = target.get(w)
        if cur is None:
            cur = {}
        poly_add_into(cur, q)
        if cur:
            target[w] = cur
        else:
            target.pop(w, None)
    return target


def elem_scale(e, c):
    c = Fraction(c)
    return {w: {m: v * c for m, v in p.items()} for w, p in e.items()} if c else {}


# ------------------------------------------------------------------- Algebra


def gb_label(sigma, j, s):
    """gb_{a_1^sigma, b_j^s}; sigma, s in {'p','m'}."""
    return f"gb_a1{sigma}_b{j}{s}"


class OscillatorAlgebra:
    def __init__(self, n, deformed=False):
        self.n = n
        self.deformed = deformed
        self.symbols = ["kappa", "a_1_p", "a_1_m"]
        for k in range(1, n + 1):
            self.symbols += [f"b_{k}_p", f"b_{k}_m"]
        self.rank = {s: i for i, s in enumerate(self.symbols)}
        self.parity = {s: (1 if s in ("kappa", "a_1_p", "a_1_m") else 0) for s in self.symbols}
        self._memo = {}

    # -- word utilities
    def word_parity(self, word):
        return sum(self.parity[x] for x in word) % 2

    def _swap(self, x, y):
        """For adjacent x y that is out of order (or nilpotent square), return
        (sign, extra) with  x y = sign * (y x) + extra,  extra a list of (word, Poly).
        Return None if x y is already in order.  sign None means 'x y = extra'."""
        rx, ry = self.rank[x], self.rank[y]
        if x == y and self.parity[x] == 1:  # kappa^2 = a^2 = 0
            return (None, [])
        if rx <= ry:
            return None
        # now y must move left of x
        if y == "kappa":  # x kappa = (-1)^{p(x)} kappa x
            return (Fraction(-1) if self.parity[x] else Fraction(1), [])
        if x == "a_1_m" and y == "a_1_p":  # a^- a^+ = - a^+ a^- + 1
            return (Fraction(-1), [((), poly_const(1))])
        if x.startswith("b_") and y.startswith("a_"):
            # b_j^s a^sigma = a^sigma b_j^s - gb_{sigma,j,s} kappa
            extra = []
            if self.deformed:
                _, j, s = x.split("_")
                sigma = y.split("_")[2]
                extra.append((("kappa",), {(gb_label(sigma, int(j), s),): Fraction(-1)}))
            return (Fraction(1), extra)
        if x.startswith("b_") and y.startswith("b_"):
            jx, jy = x.split("_")[1], y.split("_")[1]
            if jx == jy:  # b^- b^+ = b^+ b^- + 1
                return (Fraction(1), [((), poly_const(1))])
            return (Fraction(1), [])
        raise ValueError(f"no rule for {x} {y}")

    def normal(self, word):
        """Normal-order a word; returns an element."""
        word = tuple(word)
        if word in self._memo:
            return self._memo[word]
        result = None
        for i in range(len(word) - 1):
            rule = self._swap(word[i], word[i + 1])
            if rule is None:
                continue
            sign, extra = rule
            pre, post = word[:i], word[i + 2:]
            result = {}
            if sign is not None:
                elem_add_into(result, self.normal(pre + (word[i + 1], word[i]) + post),
                              poly_const(sign))
            for w, p in extra:
                elem_add_into(result, self.normal(pre + w + post), p)
            break
        if result is None:
            result = {word: poly_const(1)}
        self._memo[word] = result
        return result

    # -- products and brackets
    def mul(self, A, B):
        out = {}
        for wa, pa in A.items():
            for wb, pb in B.items():
                elem_add_into(out, self.normal(wa + wb), poly_mul(pa, pb))
        return out

    def elem_parity(self, A):
        ps = {self.word_parity(w) for w in A}
        if len(ps) > 1:
            raise ValueError("inhomogeneous element")
        return ps.pop() if ps else 0

    def bracket(self, A, B, pA=None, pB=None):
        """Super-bracket [A,B} = AB - (-1)^{p(A)p(B)} BA."""
        pA = self.elem_parity(A) if pA is None else pA
        pB = self.elem_parity(B) if pB is None else pB
        out = self.mul(A, B)
        elem_add_into(out, self.mul(B, A), poly_const(-1 if pA * pB % 2 == 0 else 1))
        return out

    @staticmethod
    def split_kappa(A):
        """Split A = A0 + kappa * A1 (kappa is leftmost in normal order)."""
        a0, a1 = {}, {}
        for w, p in A.items():
            if w and w[0] == "kappa":
                a1[w[1:]] = p
            else:
                a0[w] = p
        return a0, a1


def element_from_terms(terms):
    """[(words list, coeff)] -> element (assumed already normal ordered)."""
    out = {}
    for words, c in terms:
        elem_add_into(out, {tuple(words): poly_const(c)})
    return out
