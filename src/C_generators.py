"""
C_generators.py

Generates Schema 1 (structure constants) JSON for C(n+1) = osp(2|2n)
for n = 1, 2, 3.

Mathematical basis: docs/math/Cn1_definition.md and handover/notation.md.

Oscillator algebra:
  - Fermionic pair: a_1^+, a_1^-  with {a_1^-, a_1^+} = 1, {a_1^s, a_1^s} = 0
  - Bosonic pair:   b_k^+, b_k^-  with [b_i^-, b_j^+] = delta_ij, [b_i^s, b_j^s] = 0
  - Mixed: [a_1^s, b_k^t] = 0

Generators are represented as dictionaries of {(word,): coeff} where word is a
tuple of oscillator labels in PBW order. Bracket is computed symbolically.
"""

from __future__ import annotations
import json
import datetime
import os
from fractions import Fraction
from itertools import product as iproduct


# ---------------------------------------------------------------------------
# Oscillator algebra representation
# ---------------------------------------------------------------------------

# PBW order: a_1_p < a_1_m < b_1_p < b_1_m < b_2_p < b_2_m < ...
# Within fermions: a_1_p=0, a_1_m=1
# Within bosons: b_k_p = 2*(k-1)+2, b_k_m = 2*(k-1)+3

def _osc_order(label: str, n: int) -> int:
    if label == "a_1_p":
        return 0
    if label == "a_1_m":
        return 1
    for k in range(1, n + 1):
        if label == f"b_{k}_p":
            return 2 * k
        if label == f"b_{k}_m":
            return 2 * k + 1
    raise ValueError(f"Unknown oscillator label: {label}")


def _parity_of_osc(label: str) -> int:
    if label in ("a_1_p", "a_1_m"):
        return 1
    return 0


def _parity_of_word(word: tuple) -> int:
    return sum(_parity_of_osc(o) for o in word) % 2


# Element: dict mapping word (tuple of osc labels) -> Fraction coefficient
# Represents a linear combination of oscillator monomials

def _zero() -> dict:
    return {}


def _scalar(c: Fraction) -> dict:
    return {(): c} if c != 0 else {}


def _single(word: tuple, coeff: Fraction) -> dict:
    if coeff == 0:
        return {}
    return {word: coeff}


def _add(a: dict, b: dict) -> dict:
    result = dict(a)
    for word, coeff in b.items():
        result[word] = result.get(word, Fraction(0)) + coeff
    return {w: c for w, c in result.items() if c != 0}


def _scale(a: dict, c: Fraction) -> dict:
    if c == 0:
        return {}
    return {word: coeff * c for word, coeff in a.items()}


def _mul_words(w1: tuple, w2: tuple, n: int) -> dict:
    """
    Multiply two oscillator words using the commutation/anticommutation relations,
    bringing the result to PBW normal form.
    Returns a dict of {word: coeff}.
    """
    # Base case: multiply one oscillator into a word
    return _mul_element(_single(w1, Fraction(1)), _single(w2, Fraction(1)), n)


def _move_osc_left(osc: str, word: tuple, n: int) -> dict:
    """
    Move oscillator `osc` past all elements in `word` to PBW position,
    collecting commutator/anticommutator residuals.
    Returns sum of words in PBW order.
    """
    if not word:
        return _single((osc,), Fraction(1))

    result = {}
    # Try to insert osc before word[0]
    first = word[0]
    rest = word[1:]

    ord_osc = _osc_order(osc, n)
    ord_first = _osc_order(first, n)

    if ord_osc <= ord_first:
        # Already in order
        inner = _move_osc_left(first, rest, n) if rest else _single((first,), Fraction(1))
        # osc * (first * rest) = osc * inner
        for w, c in inner.items():
            new_word = (osc,) + w
            result = _add(result, {new_word: c})
        return result
    else:
        # Need to commute osc past first
        # osc * first = ±first * osc + [osc, first} (residual)
        p_osc = _parity_of_osc(osc)
        p_first = _parity_of_osc(first)

        if p_osc == 0 and p_first == 0:
            # Both bosonic: [b_i^s, b_j^t] = delta(i,j, s conjugate t)
            sign = Fraction(1)
            residual = _commutator_boson_boson(osc, first)
        elif p_osc == 1 and p_first == 1:
            # Both fermionic: {a_1^s, a_1^t} = delta(conj)
            sign = Fraction(-1)  # {A,B} -> A*B = -B*A + {A,B}
            residual = _anticommutator_fermion_fermion(osc, first)
        else:
            # Mixed: boson-fermion commute freely
            sign = Fraction(-1) if (p_osc == 1 and p_first == 1) else Fraction(1)
            # Actually for mixed: [b, a] = 0 and [a, b] = 0 in undeformed algebra
            if p_osc == 1 and p_first == 0:
                sign = Fraction(1)  # a*b = b*a (they commute)
            elif p_osc == 0 and p_first == 1:
                sign = Fraction(1)
            residual = {}

        # first part: ±first * osc * rest
        sign_part1 = sign
        # For fermion-fermion: osc*first = -first*osc + residual (scalar/word)
        # For boson-boson: osc*first = first*osc + residual
        # For mixed: osc*first = first*osc (commute)

        # Move osc past rest
        osc_rest = _move_osc_left(osc, rest, n)
        # first * (osc * rest)
        for w, c in osc_rest.items():
            new_word = (first,) + w
            result = _add(result, {new_word: sign_part1 * c})

        # residual * rest
        for rw, rc in residual.items():
            if rw == ():
                # scalar residual
                # rc * rest
                result = _add(result, {rest: rc})
            else:
                # rw * rest
                combined = rw + rest
                # Need to normalize combined
                normalized = _normalize_word(combined, n)
                result = _add(result, _scale(normalized, rc))

        return result


def _commutator_boson_boson(osc1: str, osc2: str) -> dict:
    """[b_i^s, b_j^t] = delta_ij * delta_{s,-t} (conjugate pair)"""
    # b_i^- * b_i^+ = 1 + b_i^+ * b_i^- => [b_i^-, b_i^+] = 1
    # But here we compute osc1 * osc2 - osc2 * osc1 = [osc1, osc2]
    # For bosons: [b_i^-, b_j^+] = delta_ij, [b_i^+, b_j^-] = -delta_ij
    # Actually we just need the scalar part when we commute
    # If osc1 = b_i_m and osc2 = b_j_p: residual = delta_ij
    # If osc1 = b_i_p and osc2 = b_j_m: residual = -delta_ij
    # Others: 0
    def _boson_index_sign(label):
        # Returns (k, sign) where sign is + for creation, - for annihilation
        for part in label.split("_"):
            pass
        parts = label.split("_")
        k = int(parts[1])
        s = parts[2]  # p or m
        return k, s

    k1, s1 = _boson_index_sign(osc1)
    k2, s2 = _boson_index_sign(osc2)

    if k1 != k2:
        return {}
    if s1 == "m" and s2 == "p":
        return {(): Fraction(1)}
    if s1 == "p" and s2 == "m":
        return {(): Fraction(-1)}
    return {}


def _anticommutator_fermion_fermion(osc1: str, osc2: str) -> dict:
    """{a_1^-, a_1^+} = 1; {a_1^s, a_1^s} = 0"""
    if osc1 == "a_1_m" and osc2 == "a_1_p":
        return {(): Fraction(1)}
    if osc1 == "a_1_p" and osc2 == "a_1_m":
        return {(): Fraction(1)}
    return {}


def _normalize_word(word: tuple, n: int) -> dict:
    """Bring a word to PBW normal form by bubble sort with relation replacement."""
    if len(word) == 0:
        return {(): Fraction(1)}
    if len(word) == 1:
        return {word: Fraction(1)}

    # Check if already in order
    in_order = True
    for i in range(len(word) - 1):
        if _osc_order(word[i], n) > _osc_order(word[i + 1], n):
            in_order = False
            break

    if in_order:
        # In PBW form, adjacent identical fermionic labels give zero (nilpotency)
        for i in range(len(word) - 1):
            if word[i] == word[i + 1] and _parity_of_osc(word[i]) == 1:
                return {}
        return {word: Fraction(1)}

    # Find first inversion
    for i in range(len(word) - 1):
        if _osc_order(word[i], n) > _osc_order(word[i + 1], n):
            osc1, osc2 = word[i], word[i + 1]
            prefix = word[:i]
            suffix = word[i + 2:]

            p1 = _parity_of_osc(osc1)
            p2 = _parity_of_osc(osc2)

            result = {}

            if p1 == 0 and p2 == 0:
                # bosons: osc1*osc2 = osc2*osc1 + [osc1,osc2]
                res = _commutator_boson_boson(osc1, osc2)
                sign = Fraction(1)
            elif p1 == 1 and p2 == 1:
                # fermions: osc1*osc2 = -osc2*osc1 + {osc1,osc2}
                res = _anticommutator_fermion_fermion(osc1, osc2)
                sign = Fraction(-1)
            else:
                # mixed: commute freely
                res = {}
                sign = Fraction(1)

            # swapped term
            swapped = prefix + (osc2, osc1) + suffix
            swapped_normalized = _normalize_word(swapped, n)
            result = _add(result, _scale(swapped_normalized, sign))

            # residual term
            for rw, rc in res.items():
                combined = prefix + rw + suffix
                if combined:
                    combined_normalized = _normalize_word(combined, n)
                    result = _add(result, _scale(combined_normalized, rc))
                else:
                    result = _add(result, {(): rc})

            return result

    return {word: Fraction(1)}


def _mul_element(a: dict, b: dict, n: int) -> dict:
    """Multiply two algebra elements in PBW normal form."""
    result = {}
    for wa, ca in a.items():
        for wb, cb in b.items():
            combined = wa + wb
            normalized = _normalize_word(combined, n)
            result = _add(result, _scale(normalized, ca * cb))
    return result


def _graded_bracket(a: dict, b: dict, pa: int, pb: int, n: int) -> dict:
    """
    Compute graded bracket [a, b} = a*b - (-1)^{pa*pb} * b*a
    where pa, pb are parities of a and b.
    """
    ab = _mul_element(a, b, n)
    ba = _mul_element(b, a, n)
    sign = Fraction((-1) ** (pa * pb))
    return _add(ab, _scale(ba, -sign))


# ---------------------------------------------------------------------------
# Generator construction for C(n+1)
# ---------------------------------------------------------------------------

def build_generators(n: int) -> dict:
    """Build all generators as oscillator-algebra elements for C(n+1)."""
    gens = {}

    # Cartan generators
    # H_1 = a_1^+ a_1^- + b_1^+ b_1^-
    h1 = _add(
        _single(("a_1_p", "a_1_m"), Fraction(1)),
        _single((f"b_1_p", f"b_1_m"), Fraction(1))
    )
    gens["H_1"] = (h1, 0)

    # H_k for k=2..n: b_{k-1}^+ b_{k-1}^- - b_k^+ b_k^-
    for k in range(2, n + 1):
        hk = _add(
            _single((f"b_{k-1}_p", f"b_{k-1}_m"), Fraction(1)),
            _single((f"b_{k}_p", f"b_{k}_m"), Fraction(-1))
        )
        gens[f"H_{k}"] = (hk, 0)

    # H_{n+1} = -b_n^+ b_n^- - 1/2
    # In oscillator algebra, b_n^+ b_n^- is the number operator
    hn1 = _add(
        _single((f"b_{n}_p", f"b_{n}_m"), Fraction(-1)),
        _single((), Fraction(-1, 2))
    )
    gens[f"H_{n+1}"] = (hn1, 0)

    # Even root generators
    for k in range(1, n + 1):
        gens[f"E_2del{k}_p"] = (_single((f"b_{k}_p", f"b_{k}_p"), Fraction(1)), 0)
        gens[f"E_2del{k}_m"] = (_single((f"b_{k}_m", f"b_{k}_m"), Fraction(1)), 0)

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            gens[f"E_del{i}_del{j}_pp"] = (_single((f"b_{i}_p", f"b_{j}_p"), Fraction(1)), 0)
            gens[f"E_del{i}_del{j}_mm"] = (_single((f"b_{i}_m", f"b_{j}_m"), Fraction(1)), 0)
            gens[f"E_del{i}_del{j}_pm"] = (_single((f"b_{i}_p", f"b_{j}_m"), Fraction(1)), 0)
            gens[f"E_del{i}_del{j}_mp"] = (_single((f"b_{i}_m", f"b_{j}_p"), Fraction(1)), 0)

    # Odd root generators (ε-roots)
    for k in range(1, n + 1):
        gens[f"E_eps1_del{k}_pp"] = (_single(("a_1_p", f"b_{k}_p"), Fraction(1)), 1)
        gens[f"E_eps1_del{k}_pm"] = (_single(("a_1_p", f"b_{k}_m"), Fraction(1)), 1)
        gens[f"E_eps1_del{k}_mp"] = (_single(("a_1_m", f"b_{k}_p"), Fraction(1)), 1)
        gens[f"E_eps1_del{k}_mm"] = (_single(("a_1_m", f"b_{k}_m"), Fraction(1)), 1)

    return gens


def build_basis_order(n: int) -> list:
    """Return the basis in PBW order: odd first, then even."""
    odd = []
    for sign in ["pp", "pm", "mp", "mm"]:
        for k in range(1, n + 1):
            odd.append(f"E_eps1_del{k}_{sign}")

    even = []
    for k in range(1, n + 2):
        even.append(f"H_{k}")
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_p")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_pp")
    for k in range(1, n + 1):
        even.append(f"E_2del{k}_m")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mm")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_pm")
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            even.append(f"E_del{i}_del{j}_mp")

    return odd + even


def _element_to_gen(elem: dict, gens: dict, basis: list, tol=Fraction(0)) -> dict:
    """
    Try to express an oscillator element as a linear combination of generators.
    Returns {gen_label: coeff} or None if not expressible.
    """
    result = {}
    remaining = dict(elem)

    for label in basis:
        gen_elem, _ = gens[label]
        # Find the leading word of this generator
        if not gen_elem:
            continue
        # Get coefficient of leading word in remaining
        for word, coeff in gen_elem.items():
            if word in remaining:
                c = remaining[word] / coeff
                if c != 0:
                    result[label] = c
                    # Subtract c * gen from remaining
                    remaining = _add(remaining, _scale(gen_elem, -c))
                break

    # Check if remaining is zero
    remaining = {w: c for w, c in remaining.items() if c != 0}
    if remaining:
        return None  # Not expressible purely in basis
    return result


def _build_decomposition_matrix(gens: dict, basis: list) -> tuple:
    """
    Build the word-to-generator matrix for linear decomposition.
    Returns (words_list, word_to_idx, matrix) where matrix[i][j] = coeff of word_i in gen_j.
    """
    # Collect all words appearing in generators, including scalar ()
    word_set = set()
    word_set.add(())  # scalar term needed for Cartan generators with constants
    for label in basis:
        elem, _ = gens[label]
        for word in elem:
            word_set.add(word)

    words = sorted(word_set, key=lambda w: (len(w), w))
    word_to_idx = {w: i for i, w in enumerate(words)}
    n_words = len(words)
    n_gens = len(basis)

    # Build matrix: A[i][j] = coeff of words[i] in basis[j]
    A = [[Fraction(0)] * n_gens for _ in range(n_words)]
    for j, label in enumerate(basis):
        elem, _ = gens[label]
        for word, coeff in elem.items():
            if word in word_to_idx:
                A[word_to_idx[word]][j] = coeff

    return words, word_to_idx, A


def _solve_decomposition(bracket: dict, words: list, word_to_idx: dict, A: list, basis: list) -> dict:
    """
    Solve: sum_j coeff[j] * gen_j = bracket using Gaussian elimination.
    Returns {gen_label: coeff} or raises ValueError if unsolvable.
    """
    n_words = len(words)
    n_gens = len(basis)

    # Build RHS vector from bracket
    b_vec = [Fraction(0)] * n_words
    for word, coeff in bracket.items():
        if word in word_to_idx:
            b_vec[word_to_idx[word]] = coeff
        # Scalar term (): skip (should not appear in Lie algebra brackets)
        # or add as extra constraint if needed

    # Augmented matrix [A | b] — solve for x such that A*x = b
    # Use subset: only rows with nonzero entries in A or b
    active_rows = [i for i in range(n_words) if any(A[i][j] != 0 for j in range(n_gens)) or b_vec[i] != 0]

    if not active_rows:
        return {}

    # Build reduced system
    nR = len(active_rows)
    aug = [[A[active_rows[i]][j] for j in range(n_gens)] + [b_vec[active_rows[i]]] for i in range(nR)]

    # Gaussian elimination
    pivot_col = {}
    row = 0
    for col in range(n_gens):
        # Find pivot
        pivot_r = None
        for r in range(row, nR):
            if aug[r][col] != 0:
                pivot_r = r
                break
        if pivot_r is None:
            continue
        aug[row], aug[pivot_r] = aug[pivot_r], aug[row]
        pivot_val = aug[row][col]
        aug[row] = [v / pivot_val for v in aug[row]]
        for r in range(nR):
            if r != row and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [aug[r][c] - factor * aug[row][c] for c in range(n_gens + 1)]
        pivot_col[col] = row
        row += 1

    # Check consistency: rows after pivot phase with 0 LHS but nonzero RHS
    for r in range(row, nR):
        if aug[r][-1] != 0:
            return None  # Inconsistent

    # Extract solution
    result = {}
    for col, r in pivot_col.items():
        coeff = aug[r][-1]
        if coeff != 0:
            result[basis[col]] = coeff

    return result


def compute_structure_constants(n: int) -> list:
    """
    Compute all non-zero structure constants [X, Y} = sum_Z f^Z_{XY} Z
    for basis generators X, Y.
    Returns list of {X, Y, Z, coeff, sign_rule} dicts.
    """
    gens = build_generators(n)
    basis = build_basis_order(n)

    # Build decomposition matrix once
    words, word_to_idx, A = _build_decomposition_matrix(gens, basis)

    constants = []

    for X_label in basis:
        for Y_label in basis:
            X_elem, pX = gens[X_label]
            Y_elem, pY = gens[Y_label]

            bracket = _graded_bracket(X_elem, Y_elem, pX, pY, n)
            if not bracket:
                continue

            bracket_filtered = {w: c for w, c in bracket.items() if c != 0}
            if not bracket_filtered:
                continue

            decomp = _solve_decomposition(bracket_filtered, words, word_to_idx, A, basis)
            if decomp is None:
                raise ValueError(f"Cannot decompose bracket [{X_label}, {Y_label}]")

            for Z_label, coeff in decomp.items():
                if coeff != 0:
                    constants.append({
                        "X": X_label,
                        "Y": Y_label,
                        "Z": Z_label,
                        "coeff": str(coeff),
                        "sign_rule": "graded"
                    })

    return constants


def build_schema1(n: int) -> dict:
    """Build Schema 1 JSON for C(n+1) with bosonic rank n."""
    gens = build_generators(n)
    basis = build_basis_order(n)

    odd_basis = [b for b in basis if gens[b][1] == 1]
    even_basis = [b for b in basis if gens[b][1] == 0]

    # Dimension formulas
    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    dim_total = dim_even + dim_odd

    assert len(even_basis) == dim_even, f"Even basis count mismatch: {len(even_basis)} != {dim_even}"
    assert len(odd_basis) == dim_odd, f"Odd basis count mismatch: {len(odd_basis)} != {dim_odd}"

    # Parity dict
    parity = {}
    for label in basis:
        parity[label] = gens[label][1]

    # Generator realizations
    def elem_to_json(elem):
        terms = []
        for word, coeff in sorted(elem.items(), key=lambda x: x[0]):
            terms.append({"words": list(word), "coeff": str(coeff)})
        return terms

    realizations = {}
    for label in basis:
        elem, p = gens[label]
        realizations[label] = {
            "standard_form": elem_to_json(elem),
            "parity": p
        }

    # Boson labels
    boson_labels = []
    for k in range(1, n + 1):
        boson_labels += [f"b_{k}_p", f"b_{k}_m"]

    # Structure constants
    structure_constants = compute_structure_constants(n)

    cartan_type = f"C({n+1})"
    osp_notation = f"osp(2|{2*n})"

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": cartan_type,
            "alternative_notation": {
                "osp": osp_notation,
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": dim_total,
                "even": dim_even,
                "odd": dim_odd,
                "even_formula": "2*n^2 + n + 1",
                "odd_formula": "4*n"
            }
        },
        "central_elements": {
            "K": {
                "label": "K",
                "parity": 0,
                "description": "Even central identity; K=1 in all realizations. Excluded from basis.",
                "property": "K = 1"
            },
            "kappa": {
                "label": "kappa",
                "parity": 1,
                "description": "Odd central nilpotent element; appears in deformed bracket.",
                "property": "kappa^2 = 0"
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic CAR pair a_1^+, a_1^-"
            },
            "bosons": {
                "count": 2 * n,
                "n": n,
                "labels": boson_labels,
                "description": f"Bosonic oscillators b_k^± with k=1,...,{n}"
            }
        },
        "oscillator_relations": {
            "fermionic_anticommutators": {
                "description": "Canonical anticommutation relations for standard fermionic pair",
                "relations": {
                    "anticommutator": "{a_1^-, a_1^+} = 1",
                    "same_sign": "{a_1^s, a_1^s} = 0 for s in {+,-}"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^s, b_j^s] = 0 for all i,j,s",
                    "conjugate_pair": "[b_i^-, b_j^+] = delta_ij"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_k^s, a_1^sigma] = 0 (undeformed algebra)"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: kappa < [odd: E_eps1_del{k}_{pp/pm/mp/mm}] < [even: H_k, E_2del{k}_p/m, E_del{i}_del{j}_{pp/mm/pm/mp}]"
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, " + ", ".join(boson_labels),
            "realizations": realizations
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": [
                "Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras",
                "arXiv:hep-th/9607161"
            ]
        }
    }
    return schema


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C_{n}_structure.json (C({n+1}) = osp(2|{2*n}))...")
        schema = build_schema1(n)
        sc_count = len(schema["structure_constants"])
        print(f"  Basis: {schema['algebra']['dimension']['even']} even + {schema['algebra']['dimension']['odd']} odd")
        print(f"  Structure constants: {sc_count} non-zero entries")
        out_path = os.path.join(data_dir, f"C_{n}_structure.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written to {out_path}")


if __name__ == "__main__":
    main()
