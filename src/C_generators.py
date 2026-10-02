"""Build C(n+1) oscillator bases and their Schema 1 structure constants."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import TypeAlias

from sympy import Matrix, Rational

Word: TypeAlias = tuple[str, ...]
Polynomial: TypeAlias = dict[Word, Rational]

FERMION_PLUS = "a_1_p"
FERMION_MINUS = "a_1_m"
_BOSON_PATTERN = re.compile(r"^b_(\d+)_(p|m)$")


def _oscillator_key(label: str) -> tuple[int, ...]:
    if label == FERMION_PLUS:
        return (0, 0)
    if label == FERMION_MINUS:
        return (0, 1)

    match = _BOSON_PATTERN.fullmatch(label)
    if match is None:
        raise ValueError(f"Unknown oscillator label: {label}")
    index = int(match.group(1))
    sign = match.group(2)
    return (1, 0 if sign == "p" else 1, index)


def _add_scaled(
    destination: dict[Word, Rational],
    source: dict[Word, Rational],
    scale: Rational,
) -> None:
    for word, coefficient in source.items():
        total = destination.get(word, Rational(0)) + scale * coefficient
        if total:
            destination[word] = total
        else:
            destination.pop(word, None)


def _cached_normal_order(
    word: Word,
) -> tuple[tuple[Word, Rational], ...]:
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]

        if left in (FERMION_PLUS, FERMION_MINUS) and right in (
            FERMION_PLUS,
            FERMION_MINUS,
        ):
            if left == right:
                return ()
            if left == FERMION_MINUS and right == FERMION_PLUS:
                result: dict[Word, Rational] = {}
                prefix, suffix = word[:index], word[index + 2 :]
                _add_scaled(result, dict(_cached_normal_order(prefix + suffix)), Rational(1))
                _add_scaled(
                    result,
                    dict(
                        _cached_normal_order(
                            prefix + (FERMION_PLUS, FERMION_MINUS) + suffix
                        )
                    ),
                    Rational(-1),
                )
                return tuple(sorted(result.items(), key=lambda item: _word_sort_key(item[0])))

        left_match = _BOSON_PATTERN.fullmatch(left)
        right_match = _BOSON_PATTERN.fullmatch(right)
        if left_match and right_match:
            left_index = int(left_match.group(1))
            left_sign = left_match.group(2)
            right_index = int(right_match.group(1))
            right_sign = right_match.group(2)

            if left_sign == "m" and right_sign == "p":
                result = {}
                prefix, suffix = word[:index], word[index + 2 :]
                if left_index == right_index:
                    _add_scaled(
                        result,
                        dict(_cached_normal_order(prefix + suffix)),
                        Rational(1),
                    )
                _add_scaled(
                    result,
                    dict(_cached_normal_order(prefix + (right, left) + suffix)),
                    Rational(1),
                )
                return tuple(sorted(result.items(), key=lambda item: _word_sort_key(item[0])))

        if _oscillator_key(left) > _oscillator_key(right):
            reordered = word[:index] + (right, left) + word[index + 2 :]
            return _cached_normal_order(reordered)

    return ((word, Rational(1)),)


def _word_sort_key(word: Word) -> tuple[tuple[int, ...], ...]:
    return tuple(_oscillator_key(letter) for letter in word)


def normal_order_word(word: Word) -> Polynomial:
    """Return the exact normal-ordered expansion of an oscillator word."""
    return dict(_cached_normal_order(tuple(word)))


def normal_order_polynomial(polynomial: Polynomial) -> Polynomial:
    """Normalize and combine all words in an oscillator polynomial."""
    result: Polynomial = {}
    for word, coefficient in polynomial.items():
        for normalized_word, factor in _cached_normal_order(tuple(word)):
            total = result.get(normalized_word, Rational(0)) + coefficient * factor
            if total:
                result[normalized_word] = total
            else:
                result.pop(normalized_word, None)
    return result


def _multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            product_coefficient = left_coefficient * right_coefficient
            for word, factor in _cached_normal_order(left_word + right_word):
                total = result.get(word, Rational(0)) + product_coefficient * factor
                if total:
                    result[word] = total
                else:
                    result.pop(word, None)
    return result


def graded_bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
) -> Polynomial:
    """Compute XY - (-1)^(p(X)p(Y)) YX with exact oscillator arithmetic."""
    if left_parity not in (0, 1) or right_parity not in (0, 1):
        raise ValueError("Parities must be 0 or 1")
    sign = -1 if left_parity * right_parity else 1
    result = _multiply(left, right)
    _add_scaled(result, _multiply(right, left), Rational(-sign))
    return result


def build_basis(n: int) -> tuple[list[str], list[str], dict[str, int]]:
    """Build the even and odd basis labels in the approved display order."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")

    even = [f"H_{index}" for index in range(1, n + 2)]
    even.extend(f"E_2del{index}_p" for index in range(1, n + 1))
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    even.extend(f"E_del{i}_del{j}_pp" for i, j in pairs)
    even.extend(f"E_2del{index}_m" for index in range(1, n + 1))
    even.extend(f"E_del{i}_del{j}_mm" for i, j in pairs)
    for suffix in ("pm", "mp"):
        even.extend(f"E_del{i}_del{j}_{suffix}" for i, j in pairs)

    odd = [
        label
        for index in range(1, n + 1)
        for label in (
            f"E_eps1_del{index}_pp",
            f"E_eps1_del{index}_pm",
        )
    ]
    odd.extend(
        label
        for index in range(1, n + 1)
        for label in (
            f"E_eps1_del{index}_mp",
            f"E_eps1_del{index}_mm",
        )
    )
    parity = {label: 0 for label in even}
    parity.update({label: 1 for label in odd})
    return even, odd, parity


def _single_term(word: Word, coefficient: Rational = Rational(1)) -> Polynomial:
    return {word: coefficient} if coefficient else {}


def build_realizations(n: int) -> dict[str, Polynomial]:
    """Build exact oscillator polynomials for every C(n+1) basis generator."""
    even, odd, _ = build_basis(n)
    realizations: dict[str, Polynomial] = {}

    realizations["H_1"] = {
        (FERMION_PLUS, FERMION_MINUS): Rational(1),
        ("b_1_p", "b_1_m"): Rational(1),
    }
    for index in range(2, n + 1):
        realizations[f"H_{index}"] = {
            (f"b_{index - 1}_p", f"b_{index - 1}_m"): Rational(1),
            (f"b_{index}_p", f"b_{index}_m"): Rational(-1),
        }
    realizations[f"H_{n + 1}"] = {
        (f"b_{n}_p", f"b_{n}_m"): Rational(-1),
        (): Rational(-1, 2),
    }

    for index in range(1, n + 1):
        realizations[f"E_2del{index}_p"] = _single_term(
            (f"b_{index}_p", f"b_{index}_p"), Rational(1, 2)
        )
        realizations[f"E_2del{index}_m"] = _single_term(
            (f"b_{index}_m", f"b_{index}_m"), Rational(1, 2)
        )

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            realizations[f"E_del{i}_del{j}_pp"] = _single_term(
                (f"b_{i}_p", f"b_{j}_p")
            )
            realizations[f"E_del{i}_del{j}_pm"] = _single_term(
                (f"b_{i}_p", f"b_{j}_m")
            )
            realizations[f"E_del{i}_del{j}_mp"] = _single_term(
                (f"b_{i}_m", f"b_{j}_p")
            )
            realizations[f"E_del{i}_del{j}_mm"] = _single_term(
                (f"b_{i}_m", f"b_{j}_m")
            )

    for index in range(1, n + 1):
        realizations[f"E_eps1_del{index}_pp"] = _single_term(
            (FERMION_PLUS, f"b_{index}_p")
        )
        realizations[f"E_eps1_del{index}_pm"] = _single_term(
            (FERMION_PLUS, f"b_{index}_m")
        )
        realizations[f"E_eps1_del{index}_mp"] = _single_term(
            (FERMION_MINUS, f"b_{index}_p")
        )
        realizations[f"E_eps1_del{index}_mm"] = _single_term(
            (FERMION_MINUS, f"b_{index}_m")
        )

    expected = set(even) | set(odd)
    if set(realizations) != expected:
        raise RuntimeError("Generator realizations do not match the basis labels")
    return {label: normal_order_polynomial(realizations[label]) for label in expected}


def _basis_order(n: int) -> tuple[list[str], list[str], dict[str, int]]:
    even, odd, parity = build_basis(n)
    return odd + even, even, parity


def _coordinates_in_basis(
    polynomial: Polynomial,
    labels: list[str],
    realizations: dict[str, Polynomial],
    monomials: list[Word],
    realization_matrix: Matrix,
    pivot_rows: list[int],
    pivot_inverse: Matrix,
) -> dict[str, Rational]:
    unknown = set(polynomial) - set(monomials)
    if unknown:
        raise ValueError(f"Bracket contains monomials outside the basis span: {unknown}")

    vector = Matrix([polynomial.get(word, Rational(0)) for word in monomials])
    coordinates = pivot_inverse * Matrix([vector[row] for row in pivot_rows])
    if realization_matrix * coordinates != vector:
        raise ValueError("Bracket is not in the linear span of the basis realizations")
    return {
        label: Rational(coordinates[index])
        for index, label in enumerate(labels)
        if coordinates[index]
    }


def compute_structure_constants(n: int) -> list[dict[str, str]]:
    """Compute all nonzero ordered-pair graded brackets in basis order."""
    labels, _, parity = _basis_order(n)
    realizations = build_realizations(n)
    monomials = sorted(
        {word for polynomial in realizations.values() for word in polynomial},
        key=_word_sort_key,
    )
    realization_matrix = Matrix(
        [
            [realizations[label].get(word, Rational(0)) for label in labels]
            for word in monomials
        ]
    )
    if realization_matrix.rank() != len(labels):
        raise ValueError("Generator realizations are linearly dependent")

    _, pivot_columns = realization_matrix.T.rref()
    pivot_rows = list(pivot_columns)
    square_matrix = realization_matrix.extract(
        pivot_rows, list(range(len(labels)))
    )
    pivot_inverse = square_matrix.inv()

    constants: list[dict[str, str]] = []
    for x in labels:
        for y in labels:
            bracket = graded_bracket(
                realizations[x], realizations[y], parity[x], parity[y]
            )
            if not bracket:
                continue
            coordinates = _coordinates_in_basis(
                bracket,
                labels,
                realizations,
                monomials,
                realization_matrix,
                pivot_rows,
                pivot_inverse,
            )
            for z in labels:
                coefficient = coordinates.get(z)
                if coefficient:
                    constants.append(
                        {
                            "X": x,
                            "Y": y,
                            "Z": z,
                            "coeff": str(coefficient),
                            "sign_rule": "graded",
                        }
                    )
    return constants


def _word_list(word: Word) -> list[str]:
    return list(word)


def _standard_form(polynomial: Polynomial) -> list[dict[str, object]]:
    return [
        {"words": _word_list(word), "coeff": str(coefficient)}
        for word, coefficient in sorted(
            polynomial.items(), key=lambda item: _word_sort_key(item[0])
        )
    ]


def _frappat_forms(n: int) -> dict[str, str]:
    forms = {
        "H_1": "a_1^+ a_1^- + b_1^+ b_1^-",
        f"H_{n + 1}": f"-b_{n}^+ b_{n}^- - 1/2",
    }
    for index in range(2, n + 1):
        forms[f"H_{index}"] = (
            f"b_{index - 1}^+ b_{index - 1}^- - b_{index}^+ b_{index}^-"
        )
    for index in range(1, n + 1):
        forms[f"E_2del{index}_p"] = f"1/2 (b_{index}^+)^2"
        forms[f"E_2del{index}_m"] = f"1/2 (b_{index}^-)^2"
        forms[f"E_eps1_del{index}_pp"] = f"a_1^+ b_{index}^+"
        forms[f"E_eps1_del{index}_pm"] = f"a_1^+ b_{index}^-"
        forms[f"E_eps1_del{index}_mp"] = f"a_1^- b_{index}^+"
        forms[f"E_eps1_del{index}_mm"] = f"a_1^- b_{index}^-"
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            forms[f"E_del{i}_del{j}_pp"] = f"b_{i}^+ b_{j}^+"
            forms[f"E_del{i}_del{j}_pm"] = f"b_{i}^+ b_{j}^-"
            forms[f"E_del{i}_del{j}_mp"] = f"b_{i}^- b_{j}^+"
            forms[f"E_del{i}_del{j}_mm"] = f"b_{i}^- b_{j}^-"
    return forms


def build_schema(n: int) -> dict[str, object]:
    """Assemble one complete in-memory Schema 1 document."""
    even, odd, parity = build_basis(n)
    realizations = build_realizations(n)
    labels = odd + even
    realization_forms = _frappat_forms(n)

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n)",
            },
            "dimension_formula": {
                "even": "2n^2 + n + 1",
                "odd": "4n",
                "total": "2n^2 + 5n + 1",
            },
            "dimension": {
                "total": 2 * n * n + 5 * n + 1,
                "even": 2 * n * n + n + 1,
                "odd": 4 * n,
            },
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": [FERMION_PLUS, FERMION_MINUS],
                "parity": 1,
                "description": "One standard fermionic CAR pair a_1^+, a_1^-.",
            },
            "bosons": {
                "rank": n,
                "count": 2 * n,
                "labels": [
                    label
                    for index in range(1, n + 1)
                    for label in (f"b_{index}_p", f"b_{index}_m")
                ],
                "parity": 0,
                "description": "Bosonic oscillator pairs b_i^+, b_i^- for i=1,...,n.",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for a_1^+, a_1^-.",
                "relations": {
                    "same_type": "{a_1^+, a_1^+} = {a_1^-, a_1^-} = 0",
                    "conjugate_pair": "{a_1^-, a_1^+} = 1",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for b_i^+, b_i^-.",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0",
            },
        },
        "central_elements": {
            "kappa": {
                "label": "κ",
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "κ^2 = 0",
                "in_basis": False,
            },
            "K": {
                "label": "K",
                "parity": 0,
                "central": True,
                "relation": "K = 1",
                "in_basis": False,
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: κ < [odd] < [even]; K = 1 is excluded.",
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(
                [FERMION_PLUS, FERMION_MINUS]
                + [
                    label
                    for index in range(1, n + 1)
                    for label in (f"b_{index}_p", f"b_{index}_m")
                ]
            ),
            "realizations": {
                label: {
                    "standard_form": _standard_form(realizations[label]),
                    "frappat_form": realization_forms[label],
                    "parity": parity[label],
                }
                for label in labels
            },
        },
        "structure_constants": compute_structure_constants(n),
        "metadata": {
            "generated_by": "build_C_structure_constants.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "C(n+1) oscillator realization, docs/math/Cn1_definition.md",
            ],
        },
    }


def write_schema(n: int, output_dir: str | Path = "data") -> Path:
    """Write one C(n+1) Schema 1 document and return its path."""
    schema = build_schema(n)
    path = Path(output_dir) / f"C_{n}_structure.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "n",
        nargs="+",
        type=int,
        help="Bosonic rank(s) to generate, e.g. 1 2 3",
    )
    parser.add_argument("--output-dir", default="data")
    args = parser.parse_args()
    for rank in args.n:
        print(write_schema(rank, args.output_dir))


if __name__ == "__main__":
    main()
