"""Oscillator superalgebra engine for C(n+1) = osp(2|2n).

Elements of the (deformed) oscillator algebra ``A`` are represented as
dictionaries mapping a *normal-ordered word* -- a tuple of letters -- to a
sympy coefficient.

Letters and their normal-ordering index (``handover/notation.md`` 4.3)::

    kappa = 0,  a_1_p = 1,  a_1_m = 2,  b_k_p = 2k+1,  b_k_m = 2k+2

Relations (``docs/math/Cn1_definition.md`` 2, ``docs/math/C_inhomogeneous_definition.md``)::

    {a_1^-, a_1^+} = 1        (a_1^+-)^2 = 0
    [b_k^-, b_l^+] = delta_kl
    [b_k^s, a_1^sigma] = - gb[sigma, k, s] * kappa      (0 when undeformed)
    kappa is odd, supercentral, kappa^2 = 0

The Lie superalgebra C(n+1) sits inside ``A`` as the span of the quadratic
words listed in ``handover/notation.md`` 2.
"""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

import sympy as sp

Word = Tuple[str, ...]
Element = Dict[Word, sp.Expr]

KAPPA = "kappa"
FERM = ("a_1_p", "a_1_m")


# --------------------------------------------------------------------------
# letters
# --------------------------------------------------------------------------
def boson(k: int, sign: str) -> str:
    """Bosonic letter ``b_k_p`` / ``b_k_m`` (k is 1-based)."""
    return f"b_{k}_{sign}"


def letter_index(letter: str) -> int:
    if letter == KAPPA:
        return 0
    if letter == "a_1_p":
        return 1
    if letter == "a_1_m":
        return 2
    _, k, s = letter.split("_")
    return 2 * int(k) + (1 if s == "p" else 2)


def letter_parity(letter: str) -> int:
    return 1 if letter == KAPPA or letter in FERM else 0


def word_parity(word: Word) -> int:
    return sum(letter_parity(x) for x in word) % 2


ODD_LETTERS = frozenset({KAPPA, "a_1_p", "a_1_m"})


# --------------------------------------------------------------------------
# element arithmetic
# --------------------------------------------------------------------------
def add_into(target: Element, word: Word, coeff: sp.Expr) -> None:
    if coeff == 0:
        return
    new = target.get(word, sp.Integer(0)) + coeff
    new = sp.expand(new)
    if new == 0:
        target.pop(word, None)
    else:
        target[word] = new


def elt_add(*elements: Element) -> Element:
    out: Element = {}
    for e in elements:
        for w, c in e.items():
            add_into(out, w, c)
    return out


def elt_scale(e: Element, factor) -> Element:
    out: Element = {}
    for w, c in e.items():
        add_into(out, w, sp.expand(factor * c))
    return out


def elt_sub(a: Element, b: Element) -> Element:
    return elt_add(a, elt_scale(b, -1))


def elt_is_zero(e: Element) -> bool:
    return all(sp.simplify(c) == 0 for c in e.values())


# --------------------------------------------------------------------------
# the algebra
# --------------------------------------------------------------------------
class OscAlgebra:
    """Normal-ordering engine for the (optionally gb-deformed) oscillator algebra.

    Parameters
    ----------
    n:
        bosonic rank.
    gb:
        mapping ``(sigma, k, s) -> coefficient`` with ``sigma, s in {'p','m'}``
        and ``k`` 1-based, giving ``[b_k^s, a_1^sigma] = -gb * kappa``.
        ``None`` means the undeformed algebra.
    """

    def __init__(self, n: int, gb: Dict[Tuple[str, int, str], sp.Expr] | None = None):
        self.n = n
        self.gb = dict(gb) if gb else {}
        self._memo: Dict[Word, Element] = {}

    # -- contraction [x, y} for a single out-of-order adjacent pair ----------
    def _contraction(self, x: str, y: str) -> Element:
        # kappa supercommutes with everything
        if x == KAPPA or y == KAPPA:
            return {}
        # {a_1^-, a_1^+} = 1
        if x == "a_1_m" and y == "a_1_p":
            return {(): sp.Integer(1)}
        # [b_k^-, b_k^+] = 1
        if x.startswith("b_") and y.startswith("b_"):
            _, kx, sx = x.split("_")
            _, ky, sy = y.split("_")
            if kx == ky and sx == "m" and sy == "p":
                return {(): sp.Integer(1)}
            return {}
        # [b_k^s, a_1^sigma] = - gb[sigma, k, s] * kappa
        if x.startswith("b_") and y in FERM:
            _, k, s = x.split("_")
            sigma = "p" if y == "a_1_p" else "m"
            g = self.gb.get((sigma, int(k), s), sp.Integer(0))
            if g == 0:
                return {}
            return {(KAPPA,): sp.expand(-g)}
        return {}

    # -- normal ordering ----------------------------------------------------
    def normalize(self, word: Word) -> Element:
        """Rewrite ``word`` as a linear combination of normal-ordered words."""
        if word in self._memo:
            return dict(self._memo[word])

        # find first descent
        pos = -1
        for i in range(len(word) - 1):
            if letter_index(word[i]) > letter_index(word[i + 1]):
                pos = i
                break

        if pos == -1:
            # already sorted: kill repeated odd letters (kappa^2 = (a^+-)^2 = 0)
            for i in range(len(word) - 1):
                if word[i] == word[i + 1] and word[i] in ODD_LETTERS:
                    self._memo[word] = {}
                    return {}
            result: Element = {word: sp.Integer(1)}
            self._memo[word] = dict(result)
            return result

        x, y = word[pos], word[pos + 1]
        pre, post = word[:pos], word[pos + 2:]
        sign = -1 if (letter_parity(x) and letter_parity(y)) else 1

        out: Element = {}
        for w, c in self.normalize(pre + (y, x) + post).items():
            add_into(out, w, sign * c)
        for cw, cc in self._contraction(x, y).items():
            for w, c in self.normalize(pre + cw + post).items():
                add_into(out, w, cc * c)

        self._memo[word] = dict(out)
        return out

    # -- products and brackets ---------------------------------------------
    def mul(self, a: Element, b: Element) -> Element:
        out: Element = {}
        for wa, ca in a.items():
            for wb, cb in b.items():
                for w, c in self.normalize(wa + wb).items():
                    add_into(out, w, ca * cb * c)
        return out

    def bracket(self, a: Element, b: Element, pa: int, pb: int) -> Element:
        """Graded bracket ``[a, b} = a b - (-1)^{pa pb} b a``."""
        sign = -1 if (pa and pb) else 1
        return elt_sub(self.mul(a, b), elt_scale(self.mul(b, a), sign))


# --------------------------------------------------------------------------
# basis of C(n+1)
# --------------------------------------------------------------------------
def _pairs(n: int) -> Iterable[Tuple[int, int]]:
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            yield i, j


def build_basis(n: int):
    """Return ``(odd_labels, even_labels, realization, parity, roots)``.

    ``realization[label]`` is an :data:`Element` (normal-ordered already).
    Ordering follows Option A of ``handover/notation.md`` 4.2.
    """
    realization: Dict[str, Element] = {}
    parity: Dict[str, int] = {}
    roots: Dict[str, str] = {}

    # ---- odd block: E_eps1_del{k}_{pp,pm,mp,mm} --------------------------
    odd: list[str] = []
    suffix_to_osc = {
        "pp": ("a_1_p", "p", "eps + del{k}"),
        "pm": ("a_1_p", "m", "eps - del{k}"),
        "mp": ("a_1_m", "p", "-eps + del{k}"),
        "mm": ("a_1_m", "m", "-eps - del{k}"),
    }
    for k in range(1, n + 1):
        for suf in ("pp", "pm", "mp", "mm"):
            a_letter, bsign, root = suffix_to_osc[suf]
            label = f"E_eps1_del{k}_{suf}"
            odd.append(label)
            realization[label] = {(a_letter, boson(k, bsign)): sp.Integer(1)}
            parity[label] = 1
            roots[label] = root.format(k=k)

    # ---- even block ------------------------------------------------------
    even: list[str] = []

    def add_even(label: str, elt: Element, root: str) -> None:
        even.append(label)
        realization[label] = elt
        parity[label] = 0
        roots[label] = root

    # Cartan (symmetrized; see I01 Response 3)
    add_even("H_eps1", {("a_1_p", "a_1_m"): sp.Integer(1), (): sp.Rational(-1, 2)},
             "0 (so(2) Cartan)")
    for k in range(1, n + 1):
        add_even(f"H_del{k}",
                 {(boson(k, "p"), boson(k, "m")): sp.Integer(1), (): sp.Rational(1, 2)},
                 "0 (sp(2n) Cartan)")

    for k in range(1, n + 1):
        add_even(f"E_2del{k}_p", {(boson(k, "p"), boson(k, "p")): sp.Integer(1)},
                 f"2*del{k}")
    for i, j in _pairs(n):
        add_even(f"E_del{i}_del{j}_pp", {(boson(i, "p"), boson(j, "p")): sp.Integer(1)},
                 f"del{i} + del{j}")
    for k in range(1, n + 1):
        add_even(f"E_2del{k}_m", {(boson(k, "m"), boson(k, "m")): sp.Integer(1)},
                 f"-2*del{k}")
    for i, j in _pairs(n):
        add_even(f"E_del{i}_del{j}_mm", {(boson(i, "m"), boson(j, "m")): sp.Integer(1)},
                 f"-del{i} - del{j}")
    for i, j in _pairs(n):
        add_even(f"E_del{i}_del{j}_pm", {(boson(i, "p"), boson(j, "m")): sp.Integer(1)},
                 f"del{i} - del{j}")
    for i, j in _pairs(n):
        add_even(f"E_del{i}_del{j}_mp", {(boson(i, "m"), boson(j, "p")): sp.Integer(1)},
                 f"-del{i} + del{j}")

    return odd, even, realization, parity, roots


class CAlgebra:
    """C(n+1) with its PBW basis, decomposition map and bracket."""

    def __init__(self, n: int, gb=None):
        self.n = n
        self.osc = OscAlgebra(n, gb)
        self.odd, self.even, self.realization, self.parity, self.roots = build_basis(n)
        self.pbw_order = self.odd + self.even
        self.index = {lab: i for i, lab in enumerate(self.pbw_order)}

        # signature word -> label (each basis element has a unique leading word)
        self.signature: Dict[Word, str] = {}
        for lab, elt in self.realization.items():
            sig = max((w for w in elt if w), key=lambda w: (len(w), w))
            assert sig not in self.signature, f"signature clash on {sig}"
            self.signature[sig] = lab

    # -- decomposition ------------------------------------------------------
    def decompose(self, elt: Element) -> Dict[str, sp.Expr]:
        """Write ``elt`` in the basis; the key ``'K'`` collects the scalar part.

        Raises ``ValueError`` if ``elt`` leaves the span of basis + K.
        """
        coeffs: Dict[str, sp.Expr] = {}
        for w, c in elt.items():
            if w == ():
                continue
            if w not in self.signature:
                raise ValueError(f"word {w} is outside span(C(n+1)) + K")
            coeffs[self.signature[w]] = sp.expand(c)

        residual = dict(elt)
        for lab, c in coeffs.items():
            residual = elt_sub(residual, elt_scale(self.realization[lab], c))
        residual = {w: sp.expand(c) for w, c in residual.items() if sp.expand(c) != 0}
        if set(residual) - {()}:
            raise ValueError(f"non-scalar residual {residual}")
        kc = sp.expand(residual.get((), sp.Integer(0)))
        if kc != 0:
            coeffs["K"] = kc
        return {k: v for k, v in coeffs.items() if sp.expand(v) != 0}

    def decompose_kappa(self, elt: Element) -> Dict[str, sp.Expr]:
        """Strip a leading ``kappa`` and decompose the remainder.

        ``elt`` must have every word starting with ``kappa``; returns the
        decomposition of ``g`` where ``elt = kappa * g``.
        """
        stripped: Element = {}
        for w, c in elt.items():
            if not w or w[0] != KAPPA:
                raise ValueError(f"word {w} has no leading kappa")
            add_into(stripped, w[1:], c)
        return self.decompose(stripped)

    def split_kappa(self, elt: Element) -> Tuple[Element, Element]:
        """Split into (kappa-free part, kappa part)."""
        free: Element = {}
        kap: Element = {}
        for w, c in elt.items():
            (kap if (w and w[0] == KAPPA) else free)[w] = c
        return free, kap

    # -- bracket ------------------------------------------------------------
    def bracket_labels(self, x: str, y: str) -> Element:
        return self.osc.bracket(self.realization[x], self.realization[y],
                                self.parity[x], self.parity[y])

    def bracket_coeffs(self, x: str, y: str) -> Dict[str, sp.Expr]:
        free, _ = self.split_kappa(self.bracket_labels(x, y))
        return self.decompose(free)

    # -- convenience --------------------------------------------------------
    @property
    def dim_even(self) -> int:
        return len(self.even)

    @property
    def dim_odd(self) -> int:
        return len(self.odd)

    def elt_from_coeffs(self, coeffs: Dict[str, sp.Expr]) -> Element:
        out: Element = {}
        for lab, c in coeffs.items():
            if lab == "K":
                add_into(out, (), c)
            else:
                out = elt_add(out, elt_scale(self.realization[lab], c))
        return out


def gb_symbols(n: int):
    """Symbolic gb parameters, keyed ``(sigma, k, s)``; also returns the label map."""
    gb: Dict[Tuple[str, int, str], sp.Symbol] = {}
    labels: Dict[Tuple[str, int, str], str] = {}
    for sigma in ("p", "m"):
        for k in range(1, n + 1):
            for s in ("p", "m"):
                name = f"gb_a1{sigma.upper()}_b{k}{s.upper()}"
                gb[(sigma, k, s)] = sp.Symbol(name, commutative=True)
                labels[(sigma, k, s)] = name
    return gb, labels
