"""Exact oscillator (Weyl-Clifford) algebra engine for C(n+1) = osp(2|2n).

The engine normal-orders words in the universal enveloping algebra U(A) of
    A = V + C K + C kappa,   V = span{a_1^+, a_1^-, b_1^+, b_1^-, ..., b_n^+, b_n^-}
with the relations (handover/notation.md §1 and §4)

    {a_1^-, a_1^+} = 1,   (a_1^±)^2 = 0,
    [b_k^-, b_l^+] = δ_kl, [b_k^±, b_l^±] = 0,
    [b_k^s, a_1^σ] = - gb_{a_1^σ, b_k^s} * kappa      (deformed case; 0 if undeformed),
    kappa^2 = 0,  x*kappa = (-1)^{p(x)} kappa*x,  K = 1.

Coefficients are exact: Fractions, or sparse polynomials (class Poly) in the formal
symbols gb_* with Fraction coefficients.  Because kappa^2 = 0, every coefficient that
arises is at most linear in the gb symbols.

Word ordering (PBW order of oscillator symbols):
    kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

Word = Tuple[str, ...]

# --------------------------------------------------------------------------- Poly


class Poly:
    """Sparse polynomial in commuting symbols with Fraction coefficients.

    Stored as {monomial: Fraction}, monomial = sorted tuple of symbol names
    (() is the constant monomial)."""

    __slots__ = ("terms",)

    def __init__(self, terms: Optional[Dict[Tuple[str, ...], Fraction]] = None):
        self.terms: Dict[Tuple[str, ...], Fraction] = {}
        if terms:
            for m, c in terms.items():
                c = Fraction(c)
                if c != 0:
                    self.terms[tuple(m)] = c

    # constructors ---------------------------------------------------------
    @staticmethod
    def const(c) -> "Poly":
        return Poly({(): Fraction(c)})

    @staticmethod
    def symbol(name: str, c=1) -> "Poly":
        return Poly({(name,): Fraction(c)})

    @staticmethod
    def zero() -> "Poly":
        return Poly()

    # predicates -----------------------------------------------------------
    def is_zero(self) -> bool:
        return not self.terms

    def is_const(self) -> bool:
        return all(m == () for m in self.terms)

    def const_value(self) -> Fraction:
        if not self.is_const():
            raise ValueError(f"Poly {self} is not constant")
        return self.terms.get((), Fraction(0))

    # arithmetic -----------------------------------------------------------
    def __add__(self, other: "Poly") -> "Poly":
        t = dict(self.terms)
        for m, c in other.terms.items():
            t[m] = t.get(m, Fraction(0)) + c
        return Poly(t)

    def __neg__(self) -> "Poly":
        return Poly({m: -c for m, c in self.terms.items()})

    def __sub__(self, other: "Poly") -> "Poly":
        return self + (-other)

    def __mul__(self, other) -> "Poly":
        if not isinstance(other, Poly):
            other = Poly.const(other)
        t: Dict[Tuple[str, ...], Fraction] = {}
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                m = tuple(sorted(m1 + m2))
                t[m] = t.get(m, Fraction(0)) + c1 * c2
        return Poly(t)

    __rmul__ = __mul__

    def scale(self, c) -> "Poly":
        c = Fraction(c)
        return Poly({m: c * v for m, v in self.terms.items()})

    def __eq__(self, other) -> bool:
        if not isinstance(other, Poly):
            other = Poly.const(other)
        return self.terms == other.terms

    def __hash__(self):
        return hash(tuple(sorted(self.terms.items())))

    # utilities ------------------------------------------------------------
    def symbols(self) -> List[str]:
        s = set()
        for m in self.terms:
            s.update(m)
        return sorted(s)

    def degree(self) -> int:
        return max((len(m) for m in self.terms), default=-1)

    def substitute(self, values: Dict[str, Fraction]) -> "Poly":
        out = Poly()
        for m, c in self.terms.items():
            coeff = Fraction(c)
            rest: List[str] = []
            for s in m:
                if s in values:
                    coeff *= Fraction(values[s])
                else:
                    rest.append(s)
            out = out + Poly({tuple(sorted(rest)): coeff})
        return out

    def linear_terms(self) -> List[Tuple[str, Fraction]]:
        """Return [(symbol, coeff)] for a polynomial that is linear homogeneous."""
        out = []
        for m, c in sorted(self.terms.items()):
            if len(m) != 1:
                raise ValueError(f"Poly {self} is not linear homogeneous")
            out.append((m[0], c))
        return out

    def __repr__(self) -> str:
        if not self.terms:
            return "0"
        parts = []
        for m, c in sorted(self.terms.items()):
            mono = "*".join(m)
            if mono == "":
                parts.append(str(c))
            elif c == 1:
                parts.append(mono)
            elif c == -1:
                parts.append("-" + mono)
            else:
                parts.append(f"{c}*{mono}")
        return " + ".join(parts).replace("+ -", "- ")


# --------------------------------------------------------------------------- Element

Element = Dict[Word, Poly]


def el_add(x: Element, y: Element) -> Element:
    out: Element = dict(x)
    for w, c in y.items():
        s = out[w] + c if w in out else c
        if s.is_zero():
            out.pop(w, None)
        else:
            out[w] = s
    return out


def el_scale(x: Element, c) -> Element:
    if isinstance(c, Poly):
        out = {w: v * c for w, v in x.items()}
    else:
        out = {w: v.scale(c) for w, v in x.items()}
    return {w: v for w, v in out.items() if not v.is_zero()}


def el_neg(x: Element) -> Element:
    return el_scale(x, -1)


def el_sub(x: Element, y: Element) -> Element:
    return el_add(x, el_neg(y))


def el_is_zero(x: Element) -> bool:
    return all(v.is_zero() for v in x.values())


def el_substitute(x: Element, values: Dict[str, Fraction]) -> Element:
    out = {w: v.substitute(values) for w, v in x.items()}
    return {w: v for w, v in out.items() if not v.is_zero()}


def el_from_words(terms: Iterable[Tuple[Sequence[str], object]]) -> Element:
    out: Element = {}
    for words, coeff in terms:
        c = coeff if isinstance(coeff, Poly) else Poly.const(Fraction(coeff))
        out = el_add(out, {tuple(words): c})
    return out


# --------------------------------------------------------------------------- Algebra


class OscillatorAlgebra:
    """U(A) for C(n+1) with optional kappa-deformation.

    deformation: None (undeformed), "symbolic" (gb_* symbols), or a dict
    {gb_label: Fraction} (numeric deformation).
    """

    KAPPA = "kappa"

    def __init__(self, n: int, deformation=None):
        if n < 1:
            raise ValueError("n must be >= 1")
        self.n = n
        self.symbols: List[str] = [self.KAPPA, "a_1_p", "a_1_m"]
        for k in range(1, n + 1):
            self.symbols += [f"b_{k}_p", f"b_{k}_m"]
        self.index = {s: i for i, s in enumerate(self.symbols)}
        self.parity = {s: (1 if (s == self.KAPPA or s.startswith("a_")) else 0) for s in self.symbols}
        self.deformation = deformation
        self._cache: Dict[Word, Element] = {}

    # ---- labels ------------------------------------------------------------
    @staticmethod
    def gb_label(sigma: str, k: int, s: str) -> str:
        """gb_{a_1^sigma, b_k^s}; sigma, s in {'p','m'}."""
        return f"gb_a1{sigma}_b{k}{s}"

    def gb_labels(self) -> List[str]:
        return [self.gb_label(sig, k, s) for sig in "pm" for k in range(1, self.n + 1) for s in "pm"]

    def gb_value(self, sigma: str, k: int, s: str) -> Poly:
        lab = self.gb_label(sigma, k, s)
        if self.deformation is None:
            return Poly.zero()
        if self.deformation == "symbolic":
            return Poly.symbol(lab)
        return Poly.const(Fraction(self.deformation.get(lab, 0)))

    # ---- elementary relations ---------------------------------------------
    def _swap_bracket(self, x: str, y: str) -> Element:
        """Graded bracket [x, y} of two oscillator symbols with index(x) > index(y)
        (i.e. the pair is out of normal order). Returns an Element."""
        if x == self.KAPPA or y == self.KAPPA:
            return {}
        xa, ya = x.startswith("a_"), y.startswith("a_")
        if xa and ya:
            # x = a_1_m, y = a_1_p (only out-of-order fermion pair): {a^-, a^+} = 1
            return {(): Poly.const(1)}
        if (not xa) and (not ya):
            # bosons: out of order means x = b_k_m, y = b_k_p with same k, or different k
            kx, sx = x.split("_")[1], x.split("_")[2]
            ky, sy = y.split("_")[1], y.split("_")[2]
            if kx == ky and sx == "m" and sy == "p":
                return {(): Poly.const(1)}       # [b_k^-, b_k^+] = 1
            return {}
        # mixed: x = b_k^s (boson, higher index), y = a_1^sigma (fermion)
        if (not xa) and ya:
            k, s = x.split("_")[1], x.split("_")[2]
            sigma = y.split("_")[2]
            g = self.gb_value(sigma, int(k), s)
            if g.is_zero():
                return {}
            return {(self.KAPPA,): -g}         # [b_k^s, a_1^sigma] = - gb * kappa
        raise AssertionError(f"unexpected swap {x},{y}")

    # ---- normal ordering ---------------------------------------------------
    def normal_order(self, word: Word) -> Element:
        word = tuple(word)
        if word in self._cache:
            return self._cache[word]
        res = self._normal_order(word)
        self._cache[word] = res
        return res

    def _normal_order(self, word: Word) -> Element:
        for i in range(len(word) - 1):
            x, y = word[i], word[i + 1]
            ix, iy = self.index[x], self.index[y]
            if ix == iy and self.parity[x] == 1:
                return {}                                  # x*x = 0 for odd symbols
            if ix > iy:
                sign = -1 if (self.parity[x] == 1 and self.parity[y] == 1) else 1
                head, tail = word[:i], word[i + 2:]
                swapped = self.normal_order(head + (y, x) + tail)
                out = el_scale(swapped, sign)
                br = self._swap_bracket(x, y)
                for w, c in br.items():
                    sub = self.normal_order(head + w + tail)
                    out = el_add(out, el_scale(sub, c))
                return out
        return {word: Poly.const(1)}

    # ---- element arithmetic ----------------------------------------------
    def mul(self, x: Element, y: Element) -> Element:
        out: Element = {}
        for w1, c1 in x.items():
            for w2, c2 in y.items():
                prod = self.normal_order(w1 + w2)
                out = el_add(out, el_scale(prod, c1 * c2))
        return out

    @staticmethod
    def word_parity(word: Word, parity: Dict[str, int]) -> int:
        return sum(parity[s] for s in word) % 2

    def element_parity(self, x: Element) -> Optional[int]:
        ps = {self.word_parity(w, self.parity) for w in x}
        if not ps:
            return None
        if len(ps) > 1:
            raise ValueError("inhomogeneous element")
        return ps.pop()

    def bracket(self, x: Element, y: Element, px: int, py: int) -> Element:
        """Graded bracket [x, y} = x y - (-1)^{px py} y x."""
        xy = self.mul(x, y)
        yx = self.mul(y, x)
        sign = -1 if (px == 1 and py == 1) else 1
        return el_sub(xy, el_scale(yx, sign))

    # ---- kappa splitting ---------------------------------------------------
    def split_kappa(self, x: Element) -> Tuple[Element, Element]:
        """Return (kappa^0 part, kappa^1 part with the leading kappa removed)."""
        zero: Element = {}
        one: Element = {}
        for w, c in x.items():
            if w and w[0] == self.KAPPA:
                one[w[1:]] = c
            elif self.KAPPA in w:
                raise AssertionError("kappa not normal-ordered to the front")
            else:
                zero[w] = c
        return zero, one


# --------------------------------------------------------------------------- Linear decomposition


class LinearDecomposer:
    """Exact decomposition of Elements in a given list of Elements (basis) + constant K."""

    def __init__(self, labels: Sequence[str], elements: Sequence[Element], allow_K: bool = True):
        self.labels = list(labels)
        self.allow_K = allow_K
        cols: List[Element] = list(elements)
        if allow_K:
            self.labels.append("K")
            cols.append({(): Poly.const(1)})
        words = sorted({w for e in cols for w in e}, key=lambda w: (len(w), w))
        self.words = words
        self.widx = {w: i for i, w in enumerate(words)}
        m, k = len(words), len(cols)
        # matrix B (m x k) of Fractions
        B = [[Fraction(0)] * k for _ in range(m)]
        for j, e in enumerate(cols):
            for w, c in e.items():
                B[self.widx[w]][j] = c.const_value()
        self.B = B
        # Gaussian elimination to find pivot rows and the inverse of the square pivot submatrix
        pivots: List[int] = []
        rows_used: List[int] = []
        M = [row[:] for row in B]
        r = 0
        for j in range(k):
            piv = None
            for i in range(m):
                if i in rows_used:
                    continue
                if M[i][j] != 0:
                    piv = i
                    break
            if piv is None:
                raise ValueError(f"basis element {self.labels[j]} is linearly dependent")
            rows_used.append(piv)
            pivots.append(j)
            pv = M[piv][j]
            M[piv] = [v / pv for v in M[piv]]
            for i in range(m):
                if i != piv and M[i][j] != 0:
                    f = M[i][j]
                    M[i] = [a - f * b for a, b in zip(M[i], M[piv])]
            r += 1
        self.rows_used = rows_used
        # inverse of square submatrix S = B[rows_used][:, :]
        S = [[B[i][j] for j in range(k)] for i in rows_used]
        self.Sinv = _invert(S)

    def decompose(self, x: Element) -> Dict[str, Poly]:
        """Decompose x = sum_j c_j * basis_j (+ c_K * K).  Coefficients are Poly
        (symbolic) in general; raises if x is not in the span."""
        # split by monomial
        monos: Dict[Tuple[str, ...], List[Fraction]] = {}
        for w, c in x.items():
            if w not in self.widx:
                raise ValueError(f"word {w} not in span of basis")
            for m, v in c.terms.items():
                vec = monos.setdefault(m, [Fraction(0)] * len(self.words))
                vec[self.widx[w]] += v
        out: Dict[str, Poly] = {}
        k = len(self.labels)
        for m, vec in monos.items():
            sub = [vec[i] for i in self.rows_used]
            coeffs = [sum(self.Sinv[j][i] * sub[i] for i in range(k)) for j in range(k)]
            # residual check
            for i, w in enumerate(self.words):
                val = sum(self.B[i][j] * coeffs[j] for j in range(k))
                if val != vec[i]:
                    raise ValueError(f"element not in span (residual at word {w})")
            for j, c in enumerate(coeffs):
                if c != 0:
                    lab = self.labels[j]
                    out[lab] = out.get(lab, Poly()) + Poly({m: c})
        return {lab: p for lab, p in out.items() if not p.is_zero()}


def _invert(S: List[List[Fraction]]) -> List[List[Fraction]]:
    k = len(S)
    A = [row[:] + [Fraction(int(i == j)) for j in range(k)] for i, row in enumerate(S)]
    for c in range(k):
        piv = next(i for i in range(c, k) if A[i][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        pv = A[c][c]
        A[c] = [v / pv for v in A[c]]
        for i in range(k):
            if i != c and A[i][c] != 0:
                f = A[i][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[c])]
    return [row[k:] for row in A]


# --------------------------------------------------------------------------- helpers


def frac_str(c: Fraction) -> str:
    c = Fraction(c)
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"


def poly_terms_json(p: Poly) -> List[Dict[str, str]]:
    """Linear-form JSON representation: [{"gb": symbol, "coeff": "r"}] ; a constant
    monomial is represented with "gb": "1"."""
    out = []
    for m, c in sorted(p.terms.items()):
        if len(m) > 1:
            raise ValueError("non-linear term in gamma")
        out.append({"gb": m[0] if m else "1", "coeff": frac_str(c)})
    return out
