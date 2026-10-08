"""
Exact oscillator (Weyl-Clifford) algebra with an odd nilpotent supercentral element kappa
and optional inhomogeneous deformation parameters gb.

Generators (letters):
    kappa            odd, kappa^2 = 0, kappa x = (-1)^{p(x)} x kappa
    a_1_p, a_1_m     odd,  {a_1_m, a_1_p} = 1, (a_1_±)^2 = 0
    b_k_p, b_k_m     even, [b_k_m, b_k_p] = 1
Deformation:
    [b_k_s, a_1_sigma] = - gb_a_1_{sigma}_b_{k}_{s} * kappa

Coefficients are `LinPoly`: polynomials in the gb symbols with Fraction coefficients
(only degree <= 1 ever appears because kappa^2 = 0).

Elements are dicts {word(tuple of letters): LinPoly} kept in normal order:
    kappa < a_1_p < a_1_m < b_1_p < b_1_m < ... < b_n_p < b_n_m
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict, Iterable, List, Tuple

Word = Tuple[str, ...]


# --------------------------------------------------------------------------- #
# Linear-polynomial coefficients
# --------------------------------------------------------------------------- #
class LinPoly:
    """Polynomial in symbolic parameters with Fraction coefficients.

    Stored as {monomial: Fraction}, monomial = sorted tuple of symbol names.
    """

    __slots__ = ("terms",)

    def __init__(self, terms=None):
        if terms is None:
            self.terms: Dict[Tuple[str, ...], Fraction] = {}
        elif isinstance(terms, LinPoly):
            self.terms = dict(terms.terms)
        elif isinstance(terms, dict):
            self.terms = {k: Fraction(v) for k, v in terms.items() if v != 0}
        else:  # scalar
            c = Fraction(terms)
            self.terms = {(): c} if c != 0 else {}

    @staticmethod
    def symbol(name: str) -> "LinPoly":
        return LinPoly({(name,): Fraction(1)})

    @staticmethod
    def scalar(c) -> "LinPoly":
        return LinPoly(Fraction(c))

    def copy(self) -> "LinPoly":
        return LinPoly(dict(self.terms))

    def is_zero(self) -> bool:
        return not self.terms

    def is_scalar(self) -> bool:
        return all(k == () for k in self.terms)

    def scalar_value(self) -> Fraction:
        if not self.is_scalar():
            raise ValueError(f"not a scalar: {self}")
        return self.terms.get((), Fraction(0))

    def degree(self) -> int:
        return max((len(k) for k in self.terms), default=0)

    def __add__(self, other):
        other = _lp(other)
        out = dict(self.terms)
        for k, v in other.terms.items():
            nv = out.get(k, Fraction(0)) + v
            if nv == 0:
                out.pop(k, None)
            else:
                out[k] = nv
        return LinPoly(out)

    __radd__ = __add__

    def __neg__(self):
        return LinPoly({k: -v for k, v in self.terms.items()})

    def __sub__(self, other):
        return self + (-_lp(other))

    def __rsub__(self, other):
        return _lp(other) - self

    def __mul__(self, other):
        other = _lp(other)
        out: Dict[Tuple[str, ...], Fraction] = {}
        for k1, v1 in self.terms.items():
            for k2, v2 in other.terms.items():
                k = tuple(sorted(k1 + k2))
                out[k] = out.get(k, Fraction(0)) + v1 * v2
        return LinPoly(out)

    __rmul__ = __mul__

    def __eq__(self, other):
        return self.terms == _lp(other).terms

    def __hash__(self):
        return hash(tuple(sorted(self.terms.items())))

    def substitute(self, values: Dict[str, Fraction]) -> "LinPoly":
        out = LinPoly()
        for k, v in self.terms.items():
            c = Fraction(v)
            rest = []
            for s in k:
                if s in values:
                    c *= Fraction(values[s])
                else:
                    rest.append(s)
            out = out + LinPoly({tuple(rest): c})
        return out

    def symbols(self) -> List[str]:
        return sorted({s for k in self.terms for s in k})

    def to_json(self):
        """Linear form -> {symbol: "rational"}; scalar -> "rational"."""
        if self.is_scalar():
            return str(self.scalar_value())
        if self.degree() > 1:
            raise ValueError("non-linear coefficient cannot be serialised as a linear form")
        out = {}
        if () in self.terms:
            out["1"] = str(self.terms[()])
        for k, v in sorted(self.terms.items()):
            if k:
                out[k[0]] = str(v)
        return out

    def expr(self) -> str:
        if self.is_zero():
            return "0"
        parts = []
        for k, v in sorted(self.terms.items(), key=lambda kv: (len(kv[0]), kv[0])):
            mono = "*".join(k)
            if not k:
                s = str(v)
            elif v == 1:
                s = mono
            elif v == -1:
                s = "-" + mono
            else:
                s = f"{v}*{mono}"
            parts.append(s)
        text = " + ".join(parts)
        return text.replace("+ -", "- ")

    def __repr__(self):
        return self.expr()


def _lp(x) -> LinPoly:
    return x if isinstance(x, LinPoly) else LinPoly(x)


# --------------------------------------------------------------------------- #
# Oscillator algebra
# --------------------------------------------------------------------------- #
class OscillatorAlgebra:
    """Normal-ordering engine for the C(n+1) oscillator algebra with kappa and gb."""

    def __init__(self, n: int, deformed: bool = False):
        self.n = n
        self.deformed = deformed
        self.letters: List[str] = ["kappa", "a_1_p", "a_1_m"]
        for k in range(1, n + 1):
            self.letters += [f"b_{k}_p", f"b_{k}_m"]
        self.order = {x: i for i, x in enumerate(self.letters)}
        self.parity = {x: (0 if x.startswith("b_") else 1) for x in self.letters}
        self.gb_labels: List[str] = []
        for sigma in ("p", "m"):
            for k in range(1, n + 1):
                for s in ("p", "m"):
                    self.gb_labels.append(f"gb_a_1_{sigma}_b_{k}_{s}")

    # -- parity helpers ----------------------------------------------------- #
    def word_parity(self, w: Word) -> int:
        return sum(self.parity[x] for x in w) % 2

    # -- elementary brackets [x, y} for letters -------------------------------#
    def letter_bracket(self, x: str, y: str) -> "Element":
        """Graded bracket [x, y} = xy - (-1)^{p(x)p(y)} yx of two letters (as an Element)."""
        if x == "kappa" or y == "kappa":
            return Element(self)
        if x.startswith("a") and y.startswith("a"):
            if x != y:
                return Element.scalar(self, 1)  # {a_1_m, a_1_p} = 1
            return Element(self)
        if x.startswith("b") and y.startswith("b"):
            kx, sx = x.split("_")[1], x.split("_")[2]
            ky, sy = y.split("_")[1], y.split("_")[2]
            if kx == ky and sx != sy:
                # [b_m, b_p] = 1, [b_p, b_m] = -1
                return Element.scalar(self, 1 if sx == "m" else -1)
            return Element(self)
        # mixed boson/fermion
        if not self.deformed:
            return Element(self)
        if x.startswith("b"):
            b, a, sign = x, y, 1   # [b, a] = -gb kappa
        else:
            b, a, sign = y, x, -1  # [a, b] = -[b, a] (b even)
        k, s = b.split("_")[1], b.split("_")[2]
        sigma = a.split("_")[2]
        gb = LinPoly.symbol(f"gb_a_1_{sigma}_b_{k}_{s}")
        return Element(self, {("kappa",): -sign * gb})

    # -- normal ordering ---------------------------------------------------- #
    def normal_order_word(self, w: Word, coeff: LinPoly) -> Dict[Word, LinPoly]:
        """Return the normally ordered expansion of coeff * w."""
        result: Dict[Word, LinPoly] = {}
        stack: List[Tuple[Word, LinPoly]] = [(tuple(w), coeff)]
        while stack:
            word, c = stack.pop()
            if c.is_zero():
                continue
            # find first out-of-order adjacent pair, or a repeated odd letter
            pos = -1
            for i in range(len(word) - 1):
                x, y = word[i], word[i + 1]
                if self.order[x] > self.order[y]:
                    pos = i
                    break
                if x == y and self.parity[x] == 1:
                    pos = i
                    break
            if pos == -1:
                result[word] = result.get(word, LinPoly()) + c
                continue
            x, y = word[pos], word[pos + 1]
            if x == y and self.parity[x] == 1:
                # x x = (1/2){x,x} = 0 for kappa and for a_1_±
                continue
            sign = -1 if (self.parity[x] == 1 and self.parity[y] == 1) else 1
            # x y = sign * y x + [x, y}
            stack.append((word[:pos] + (y, x) + word[pos + 2:], c * sign))
            br = self.letter_bracket(x, y)
            for bw, bc in br.terms.items():
                stack.append((word[:pos] + bw + word[pos + 2:], c * bc))
        return result


class Element:
    """Element of the oscillator algebra, kept in normal order."""

    __slots__ = ("alg", "terms")

    def __init__(self, alg: OscillatorAlgebra, terms: Dict[Word, LinPoly] | None = None, ordered=False):
        self.alg = alg
        self.terms: Dict[Word, LinPoly] = {}
        if terms:
            for w, c in terms.items():
                c = _lp(c)
                if c.is_zero():
                    continue
                if ordered:
                    self._add_term(w, c)
                else:
                    for nw, nc in alg.normal_order_word(w, c).items():
                        self._add_term(nw, nc)

    def _add_term(self, w: Word, c: LinPoly):
        nc = self.terms.get(w, LinPoly()) + c
        if nc.is_zero():
            self.terms.pop(w, None)
        else:
            self.terms[w] = nc

    @staticmethod
    def scalar(alg, c) -> "Element":
        return Element(alg, {(): LinPoly(c)}, ordered=True)

    @staticmethod
    def word(alg, *letters, coeff=1) -> "Element":
        return Element(alg, {tuple(letters): LinPoly(coeff)})

    def is_zero(self) -> bool:
        return not self.terms

    def __add__(self, other: "Element") -> "Element":
        out = Element(self.alg, dict(self.terms), ordered=True)
        for w, c in other.terms.items():
            out._add_term(w, c)
        return out

    def __neg__(self) -> "Element":
        return Element(self.alg, {w: -c for w, c in self.terms.items()}, ordered=True)

    def __sub__(self, other: "Element") -> "Element":
        return self + (-other)

    def scale(self, c) -> "Element":
        c = _lp(c)
        return Element(self.alg, {w: v * c for w, v in self.terms.items()}, ordered=True)

    def __mul__(self, other: "Element") -> "Element":
        out = Element(self.alg)
        for w1, c1 in self.terms.items():
            for w2, c2 in other.terms.items():
                for nw, nc in self.alg.normal_order_word(w1 + w2, c1 * c2).items():
                    out._add_term(nw, nc)
        return out

    def parity(self) -> int:
        ps = {self.alg.word_parity(w) for w in self.terms}
        if len(ps) > 1:
            raise ValueError("inhomogeneous element")
        return ps.pop() if ps else 0

    def bracket(self, other: "Element") -> "Element":
        """Graded bracket [X, Y} = XY - (-1)^{p(X)p(Y)} YX."""
        sign = -1 if (self.parity() == 1 and other.parity() == 1) else 1
        return self * other - (other * self).scale(sign)

    def split_kappa(self) -> Tuple["Element", "Element"]:
        """Return (part without kappa, coefficient of kappa (kappa stripped from the left))."""
        base, kap = Element(self.alg), Element(self.alg)
        for w, c in self.terms.items():
            if w and w[0] == "kappa":
                kap._add_term(w[1:], c)
            else:
                base._add_term(w, c)
        return base, kap

    def substitute(self, values: Dict[str, Fraction]) -> "Element":
        return Element(self.alg, {w: c.substitute(values) for w, c in self.terms.items()}, ordered=True)

    def __repr__(self):
        if not self.terms:
            return "0"
        return " + ".join(f"({c})*{'.'.join(w) if w else '1'}" for w, c in sorted(self.terms.items()))


# --------------------------------------------------------------------------- #
# Exact rational linear algebra (small systems)
# --------------------------------------------------------------------------- #
def rref(rows: List[List[Fraction]], ncols: int):
    """Reduced row echelon form. Returns (matrix, pivot_columns)."""
    m = [list(r) for r in rows]
    pivots = []
    r = 0
    for c in range(ncols):
        piv = None
        for i in range(r, len(m)):
            if m[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        pv = m[r][c]
        m[r] = [v / pv for v in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [vi - f * vr for vi, vr in zip(m[i], m[r])]
        pivots.append(c)
        r += 1
        if r == len(m):
            break
    return m, pivots


class Decomposer:
    """Decompose elements (of degree <= 2, no kappa) in a given list of basis Elements plus the unit."""

    def __init__(self, alg: OscillatorAlgebra, basis: Dict[str, Element]):
        self.alg = alg
        self.labels = list(basis.keys())
        monos = set()
        for e in basis.values():
            monos.update(e.terms.keys())
        monos.add(())
        self.monos = sorted(monos, key=lambda w: (len(w), [alg.order[x] for x in w]))
        self.mono_index = {w: i for i, w in enumerate(self.monos)}
        # columns: basis elements then the unit; rows: monomials
        ncols = len(self.labels) + 1
        mat = [[Fraction(0)] * ncols for _ in self.monos]
        for j, lab in enumerate(self.labels):
            for w, c in basis[lab].terms.items():
                mat[self.mono_index[w]][j] = c.scalar_value()
        mat[self.mono_index[()]][ncols - 1] = Fraction(1)
        # solve by augmenting with identity: [M | I] -> rref gives left inverse when M has full column rank
        nrows = len(self.monos)
        aug = [row + [Fraction(int(i == k)) for k in range(nrows)] for i, row in enumerate(mat)]
        red, pivots = rref(aug, ncols)
        if pivots != list(range(ncols)):
            raise ValueError("basis elements are linearly dependent")
        self.ncols = ncols
        self.nrows = nrows
        # left inverse L (ncols x nrows): first ncols rows of the right block
        self.left_inv = [red[i][ncols:] for i in range(ncols)]
        # consistency rows: remaining rows of the right block must annihilate any decomposable vector
        self.consistency = [red[i][ncols:] for i in range(ncols, nrows)]

    def decompose(self, elem: Element) -> Tuple[Dict[str, LinPoly], LinPoly]:
        """Return ({label: coeff}, constant_coeff). Raises if elem is not in the span."""
        vec = [LinPoly() for _ in self.monos]
        for w, c in elem.terms.items():
            if w not in self.mono_index:
                raise ValueError(f"monomial {w} is outside the span of the basis")
            vec[self.mono_index[w]] = c
        for row in self.consistency:
            acc = LinPoly()
            for coef, v in zip(row, vec):
                if coef != 0 and not v.is_zero():
                    acc = acc + v * coef
            if not acc.is_zero():
                raise ValueError("element is not in the span of the basis + unit")
        coeffs = {}
        for j in range(self.ncols):
            acc = LinPoly()
            for coef, v in zip(self.left_inv[j], vec):
                if coef != 0 and not v.is_zero():
                    acc = acc + v * coef
            if j < len(self.labels):
                if not acc.is_zero():
                    coeffs[self.labels[j]] = acc
            else:
                const = acc
        return coeffs, const
