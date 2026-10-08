"""Exact Weyl-Clifford (oscillator) algebra engine for C(n+1) = osp(2|2n).

Elements are finite linear combinations of normal-ordered words with
``fractions.Fraction`` coefficients.  Symbols:

* ``gb_*``   : deformation parameters (even, central, commute with everything)
* ``kappa``  : odd central element, kappa^2 = 0, anticommutes with odd symbols
* ``a_1_p``, ``a_1_m`` : standard fermionic pair, {a_1_m, a_1_p} = 1, a^2 = 0
* ``b_k_p``, ``b_k_m`` : bosonic oscillators, [b_k_m, b_k_p] = 1

Normal (PBW) order of symbols:
``gb_* < kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m``.
The empty word is the unit ``1`` (identified with the even central element ``K``).

Deformation (docs/math/C_inhomogeneous_definition.md):
``[b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa``.  It is switched on by
constructing the algebra with ``deformed=True``; the parameter names are
``gb_a1{sigma}_b{j}{s}`` (e.g. ``gb_a1p_b1m``).
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict, Iterable, List, Tuple

Word = Tuple[str, ...]


def gb_name(sigma: str, j: int, s: str) -> str:
    """Name of the deformation parameter gb_{a_1^sigma, b_j^s}; sigma, s in {'p','m'}."""
    return f"gb_a1{sigma}_b{j}{s}"


class OscillatorAlgebra:
    """Symbol table + normal-ordering rules for the (possibly deformed) algebra."""

    def __init__(self, n: int, deformed: bool = False):
        self.n = n
        self.deformed = deformed
        self.order: Dict[str, int] = {}
        self.parity: Dict[str, int] = {}
        self.kind: Dict[str, str] = {}
        self.params: List[str] = []
        idx = 0
        if deformed:
            for sigma in ("p", "m"):
                for j in range(1, n + 1):
                    for s in ("p", "m"):
                        name = gb_name(sigma, j, s)
                        self.params.append(name)
                        self._add(name, idx, 0, "param")
                        idx += 1
        self._add("kappa", idx, 1, "kappa")
        idx += 1
        self._add("a_1_p", idx, 1, "a")
        idx += 1
        self._add("a_1_m", idx, 1, "a")
        idx += 1
        self.bosons: List[str] = []
        for k in range(1, n + 1):
            for s in ("p", "m"):
                name = f"b_{k}_{s}"
                self.bosons.append(name)
                self._add(name, idx, 0, "b")
                idx += 1
        self.fermions = ["a_1_p", "a_1_m"]
        self.oscillators = self.fermions + self.bosons

    def _add(self, name: str, idx: int, parity: int, kind: str) -> None:
        self.order[name] = idx
        self.parity[name] = parity
        self.kind[name] = kind

    # -- elementary relations -------------------------------------------------
    def _commutator_term(self, x: str, y: str) -> "Element":
        """Return the element C with  x y = (-1)^{p(x)p(y)} y x + C  (x later than y in order)."""
        kx, ky = self.kind[x], self.kind[y]
        if kx == "a" and ky == "a":  # x = a_1_m, y = a_1_p : {a_m, a_p} = 1
            return Element.scalar(self, 1)
        if kx == "b" and ky == "b":
            # x = b_k_m, y = b_k_p : [b_m, b_p] = 1  (only same k)
            _, kx_idx, sx = x.split("_")
            _, ky_idx, sy = y.split("_")
            if kx_idx == ky_idx and sx == "m" and sy == "p":
                return Element.scalar(self, 1)
            return Element(self)
        if kx == "b" and ky == "a" and self.deformed:
            # [b_j^s, a_1^sigma] = - gb_{sigma, j, s} kappa
            _, j, s = x.split("_")
            sigma = y.split("_")[2]
            return Element(self, {(gb_name(sigma, int(j), s), "kappa"): Fraction(-1)})
        return Element(self)

    def word_parity(self, word: Word) -> int:
        return sum(self.parity[s] for s in word) % 2

    def normal_order(self, word: Word, coeff: Fraction) -> "Element":
        """Rewrite coeff * word in normal order (iterative rewriting)."""
        result = Element(self)
        stack: List[Tuple[Word, Fraction]] = [(word, coeff)]
        order, parity, kind = self.order, self.parity, self.kind
        while stack:
            w, c = stack.pop()
            if c == 0:
                continue
            pos = -1
            for i in range(len(w) - 1):
                x, y = w[i], w[i + 1]
                if order[x] > order[y]:
                    pos = i
                    break
                if x == y and (kind[x] in ("a", "kappa")):
                    pos = i  # fermionic square / kappa^2 = 0
                    break
            if pos < 0:
                result._add_term(w, c)
                continue
            x, y = w[pos], w[pos + 1]
            if x == y:  # nilpotent square
                continue
            sign = -1 if (parity[x] and parity[y]) else 1
            stack.append((w[:pos] + (y, x) + w[pos + 2:], c * sign))
            comm = self._commutator_term(x, y)
            for cw, cc in comm.terms.items():
                stack.append((w[:pos] + cw + w[pos + 2:], c * cc))
        return result


class Element:
    """Linear combination of normal-ordered words."""

    __slots__ = ("alg", "terms")

    def __init__(self, alg: OscillatorAlgebra, terms: Dict[Word, Fraction] | None = None):
        self.alg = alg
        self.terms: Dict[Word, Fraction] = {}
        if terms:
            for w, c in terms.items():
                self._add_term(w, Fraction(c))

    # -- constructors ----------------------------------------------------------
    @classmethod
    def scalar(cls, alg: OscillatorAlgebra, c) -> "Element":
        return cls(alg, {(): Fraction(c)})

    @classmethod
    def word(cls, alg: OscillatorAlgebra, *symbols: str, coeff=1) -> "Element":
        """Build coeff * (product of symbols), normal ordered."""
        return alg.normal_order(tuple(symbols), Fraction(coeff))

    def _add_term(self, w: Word, c: Fraction) -> None:
        if c == 0:
            return
        new = self.terms.get(w, Fraction(0)) + c
        if new == 0:
            self.terms.pop(w, None)
        else:
            self.terms[w] = new

    # -- arithmetic ------------------------------------------------------------
    def copy(self) -> "Element":
        return Element(self.alg, dict(self.terms))

    def __add__(self, other: "Element") -> "Element":
        out = self.copy()
        for w, c in other.terms.items():
            out._add_term(w, c)
        return out

    def __sub__(self, other: "Element") -> "Element":
        out = self.copy()
        for w, c in other.terms.items():
            out._add_term(w, -c)
        return out

    def __neg__(self) -> "Element":
        return Element(self.alg, {w: -c for w, c in self.terms.items()})

    def scale(self, c) -> "Element":
        c = Fraction(c)
        return Element(self.alg, {w: cc * c for w, cc in self.terms.items()})

    def __mul__(self, other: "Element") -> "Element":
        out = Element(self.alg)
        for w1, c1 in self.terms.items():
            for w2, c2 in other.terms.items():
                prod = self.alg.normal_order(w1 + w2, c1 * c2)
                for w, c in prod.terms.items():
                    out._add_term(w, c)
        return out

    def is_zero(self) -> bool:
        return not self.terms

    def __eq__(self, other) -> bool:
        return isinstance(other, Element) and self.terms == other.terms

    def parity(self) -> int:
        """Parity of a homogeneous element (raises if inhomogeneous)."""
        ps = {self.alg.word_parity(w) for w in self.terms}
        if len(ps) > 1:
            raise ValueError("inhomogeneous element")
        return ps.pop() if ps else 0

    def __repr__(self) -> str:
        if not self.terms:
            return "0"
        return " + ".join(f"({c})*{'*'.join(w) if w else '1'}" for w, c in sorted(self.terms.items()))

    # -- structure of the extension -------------------------------------------
    def split_kappa(self) -> Tuple["Element", Dict[str, "Element"]]:
        """Split X = X0 + kappa * sum_p p * X_p  (p = gb parameter, '' = no parameter).

        Returns (X0, {param: X_p}).  Words containing two gb parameters or kappa^2
        cannot occur in results of brackets of quadratics (kappa^2 = 0), but any
        word with a kappa is assigned to the key given by its (unique) parameter.
        """
        x0 = Element(self.alg)
        kparts: Dict[str, Element] = {}
        for w, c in self.terms.items():
            params = tuple(s for s in w if self.alg.kind[s] == "param")
            rest = tuple(s for s in w if self.alg.kind[s] not in ("param", "kappa"))
            has_kappa = "kappa" in w
            if not has_kappa:
                if params:
                    raise ValueError(f"unexpected parameter without kappa in word {w}")
                x0._add_term(rest, c)
            else:
                if len(params) > 1:
                    raise ValueError(f"word with several parameters: {w}")
                key = params[0] if params else ""
                kparts.setdefault(key, Element(self.alg))._add_term(rest, c)
        return x0, kparts


def graded_commutator(x: Element, y: Element) -> Element:
    """[x, y} = x y - (-1)^{p(x) p(y)} y x for homogeneous x, y."""
    sign = -1 if (x.parity() and y.parity()) else 1
    return (x * y) - (y * x).scale(sign)


# ---------------------------------------------------------------------------
# Exact linear decomposition into a given spanning set
# ---------------------------------------------------------------------------
class Decomposer:
    """Express elements as linear combinations of a fixed list of (independent) elements."""

    def __init__(self, columns: List[Tuple[str, Element]]):
        self.labels = [lab for lab, _ in columns]
        self.cols = [el for _, el in columns]
        words = sorted({w for el in self.cols for w in el.terms})
        self.row_index = {w: i for i, w in enumerate(words)}
        d = len(self.cols)
        m = len(words)
        # matrix M (m x d)
        M = [[Fraction(0)] * d for _ in range(m)]
        for j, el in enumerate(self.cols):
            for w, c in el.terms.items():
                M[self.row_index[w]][j] = c
        # find d pivot rows by elimination on a copy
        A = [row[:] for row in M]
        pivot_rows: List[int] = []
        used = [False] * m
        for j in range(d):
            piv = None
            for i in range(m):
                if not used[i] and A[i][j] != 0:
                    piv = i
                    break
            if piv is None:
                raise ValueError(f"columns are linearly dependent (column {self.labels[j]})")
            used[piv] = True
            pivot_rows.append(piv)
            for i in range(m):
                if i != piv and A[i][j] != 0:
                    f = A[i][j] / A[piv][j]
                    A[i] = [a - f * b for a, b in zip(A[i], A[piv])]
        self.M = M
        self.pivot_rows = pivot_rows
        S = [[M[i][j] for j in range(d)] for i in pivot_rows]
        self.S_inv = _invert(S)

    def decompose(self, el: Element) -> Dict[str, Fraction]:
        """Return {label: coeff}; raises ValueError if el is not in the span."""
        d = len(self.cols)
        v = [Fraction(0)] * len(self.row_index)
        for w, c in el.terms.items():
            if w not in self.row_index:
                raise ValueError(f"word {w} not in span of columns")
            v[self.row_index[w]] = c
        vs = [v[i] for i in self.pivot_rows]
        coeffs = [sum(self.S_inv[j][k] * vs[k] for k in range(d)) for j in range(d)]
        # verify
        for i, row in enumerate(self.M):
            if sum(row[j] * coeffs[j] for j in range(d)) != v[i]:
                raise ValueError("element not in span of columns")
        return {self.labels[j]: coeffs[j] for j in range(d) if coeffs[j] != 0}


def _invert(S: List[List[Fraction]]) -> List[List[Fraction]]:
    d = len(S)
    A = [row[:] + [Fraction(int(i == j)) for j in range(d)] for i, row in enumerate(S)]
    for j in range(d):
        piv = next(i for i in range(j, d) if A[i][j] != 0)
        A[j], A[piv] = A[piv], A[j]
        pv = A[j][j]
        A[j] = [a / pv for a in A[j]]
        for i in range(d):
            if i != j and A[i][j] != 0:
                f = A[i][j]
                A[i] = [a - f * b for a, b in zip(A[i], A[j])]
    return [row[d:] for row in A]


def frac_str(c: Fraction) -> str:
    c = Fraction(c)
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"
