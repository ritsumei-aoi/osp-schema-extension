"""Build Schema 1 structure data for C(n+1) = osp(2|2n).

This module is a draft generator. Calling it as a script writes JSON files;
the unit tests use ``build_schema`` directly and do not write generated data.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Iterable


Word = tuple[str, ...]
Polynomial = dict[Word, Fraction]
_FERMIONS = {"a_1_p", "a_1_m"}


def oscillator_order(n: int) -> tuple[str, ...]:
    if n < 1:
        raise ValueError("n must be a positive integer")
    return ("a_1_p", "a_1_m") + tuple(
        label for k in range(1, n + 1) for label in (f"b_{k}_p", f"b_{k}_m")
    )


def normal_order_word(word: Word, n: int) -> Polynomial:
    """Reduce a word using the CAR, CCR, and boson-fermion commutativity."""
    order = {label: index for index, label in enumerate(oscillator_order(n))}

    def reduce(current: Word) -> Polynomial:
        for index in range(len(current) - 1):
            left, right = current[index : index + 2]
            prefix, suffix = current[:index], current[index + 2 :]

            if left == right and left in _FERMIONS:
                return {}

            if order[left] <= order[right]:
                continue

            if (left, right) == ("a_1_m", "a_1_p"):
                terms = (
                    (prefix + suffix, Fraction(1)),
                    (prefix + ("a_1_p", "a_1_m") + suffix, Fraction(-1)),
                )
            elif (
                left.startswith("b_")
                and right.startswith("b_")
                and left.split("_")[1] == right.split("_")[1]
                and left.endswith("_m")
                and right.endswith("_p")
            ):
                terms = (
                    (prefix + suffix, Fraction(1)),
                    (prefix + (right, left) + suffix, Fraction(1)),
                )
            else:
                terms = ((prefix + (right, left) + suffix, Fraction(1)),)

            result: Polynomial = {}
            for replacement, coefficient in terms:
                for reduced_word, reduced_coefficient in reduce(replacement).items():
                    result[reduced_word] = (
                        result.get(reduced_word, Fraction(0))
                        + coefficient * reduced_coefficient
                    )
            return {key: value for key, value in result.items() if value}

        return {current: Fraction(1)}

    return reduce(word)


def _add(
    left: Polynomial, right: Polynomial, right_scale: Fraction = Fraction(1)
) -> Polynomial:
    result = left.copy()
    for word, coefficient in right.items():
        result[word] = result.get(word, Fraction(0)) + right_scale * coefficient
        if not result[word]:
            del result[word]
    return result


def _multiply(left: Polynomial, right: Polynomial, n: int) -> Polynomial:
    result: Polynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            for word, coefficient in normal_order_word(left_word + right_word, n).items():
                result[word] = (
                    result.get(word, Fraction(0))
                    + left_coefficient * right_coefficient * coefficient
                )
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def _bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
    n: int,
) -> Polynomial:
    sign = -1 if left_parity * right_parity % 2 else 1
    return _add(
        _multiply(left, right, n),
        _multiply(right, left, n),
        Fraction(-sign),
    )


def _single_word(*labels: str, coefficient: Fraction = Fraction(1)) -> Polynomial:
    return {tuple(labels): coefficient}


def _linear_combination(*terms: tuple[Word, Fraction]) -> Polynomial:
    result: Polynomial = {}
    for word, coefficient in terms:
        result[word] = result.get(word, Fraction(0)) + coefficient
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def _odd_label(k: int, signs: str) -> str:
    return f"E_eps1_del{k}_{signs}"


def _pair_label(i: int, j: int, signs: str) -> str:
    return f"E_del{i}_del{j}_{signs}"


def _make_basis(n: int) -> tuple[list[str], dict[str, int], dict[str, Polynomial]]:
    if n < 1:
        raise ValueError("n must be a positive integer")

    negative_odd = [
        _odd_label(k, signs)
        for k in range(1, n + 1)
        for signs in ("mm", "mp")
    ]
    negative_pair_even = [
        _pair_label(i, j, signs)
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
        for signs in ("mm", "mp")
    ]
    negative_long_even = [f"E_2del{k}_m" for k in range(1, n + 1)]
    cartan = [f"H_{k}" for k in range(1, n + 2)]
    positive_pair_even = [
        _pair_label(i, j, signs)
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
        for signs in ("pp", "pm")
    ]
    positive_long_even = [f"E_2del{k}_p" for k in range(1, n + 1)]
    positive_odd = [
        _odd_label(k, signs)
        for k in range(1, n + 1)
        for signs in ("pp", "pm")
    ]

    ordered_labels = (
        negative_odd
        + negative_pair_even
        + negative_long_even
        + cartan
        + positive_pair_even
        + positive_long_even
        + positive_odd
    )
    parity = {label: int(label.startswith("E_eps1_")) for label in ordered_labels}
    generators: dict[str, Polynomial] = {}

    generators["H_1"] = _linear_combination(
        (("a_1_p", "a_1_m"), Fraction(1)),
        (("b_1_p", "b_1_m"), Fraction(1)),
    )
    for k in range(2, n + 1):
        generators[f"H_{k}"] = _linear_combination(
            ((f"b_{k - 1}_p", f"b_{k - 1}_m"), Fraction(1)),
            ((f"b_{k}_p", f"b_{k}_m"), Fraction(-1)),
        )
    generators[f"H_{n + 1}"] = _linear_combination(
        ((f"b_{n}_p", f"b_{n}_m"), Fraction(-1)),
        ((), Fraction(-1, 2)),
    )

    for k in range(1, n + 1):
        generators[f"E_2del{k}_p"] = _single_word(
            f"b_{k}_p", f"b_{k}_p", coefficient=Fraction(1, 2)
        )
        generators[f"E_2del{k}_m"] = _single_word(
            f"b_{k}_m", f"b_{k}_m", coefficient=Fraction(1, 2)
        )
        for signs, fermion, boson_sign in (
            ("pp", "a_1_p", "p"),
            ("pm", "a_1_p", "m"),
            ("mp", "a_1_m", "p"),
            ("mm", "a_1_m", "m"),
        ):
            generators[_odd_label(k, signs)] = _single_word(
                fermion, f"b_{k}_{boson_sign}"
            )

    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for signs, i_sign, j_sign in (
                ("pp", "p", "p"),
                ("pm", "p", "m"),
                ("mp", "m", "p"),
                ("mm", "m", "m"),
            ):
                generators[_pair_label(i, j, signs)] = _single_word(
                    f"b_{i}_{i_sign}", f"b_{j}_{j_sign}"
                )

    if set(ordered_labels) != set(generators):
        raise RuntimeError("PBW basis ordering does not match generator realizations")
    return ordered_labels, parity, generators


def _sympy_matrix(generators: dict[str, Polynomial], ordered_labels: list[str]):
    try:
        from sympy import Matrix, Rational
    except ImportError as error:
        raise RuntimeError("SymPy is required to solve for structure constants") from error

    monomials = sorted(
        {word for label in ordered_labels for word in generators[label]},
        key=lambda word: (len(word), word),
    )
    row = {word: index for index, word in enumerate(monomials)}
    matrix = Matrix(
        [
            [
                Rational(
                    generators[label].get(word, Fraction(0)).numerator,
                    generators[label].get(word, Fraction(0)).denominator,
                )
                for label in ordered_labels
            ]
            for word in monomials
        ]
    )
    if matrix.rank() != len(ordered_labels):
        raise ValueError("C(n+1) oscillator generators are linearly dependent")

    _, independent_rows = matrix.T.rref()
    square = matrix[list(independent_rows), :]
    inverse = square.inv()
    return Matrix, Rational, monomials, row, matrix, inverse, independent_rows


def _coordinates(
    polynomial: Polynomial,
    ordered_labels: list[str],
    reducer_data,
) -> list[Fraction]:
    Matrix, Rational, monomials, row, matrix, inverse, independent_rows = reducer_data
    unknown_words = set(polynomial) - set(monomials)
    if unknown_words:
        raise ValueError(f"Bracket is outside the generator span: {unknown_words!r}")

    target = Matrix(
        [
            Rational(
                polynomial.get(word, Fraction(0)).numerator,
                polynomial.get(word, Fraction(0)).denominator,
            )
            for word in monomials
        ]
    )
    coordinates = inverse * target[list(independent_rows), :]
    if matrix * coordinates != target:
        raise ValueError("Bracket does not close in the C(n+1) generator span")
    return [
        Fraction(int(value.p), int(value.q))
        for value in coordinates
    ]


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _realization_form(label: str, n: int) -> str:
    cartan_match = re.fullmatch(r"H_(\d+)", label)
    if cartan_match:
        k = int(cartan_match.group(1))
        if k == 1:
            return "a_1^+ a_1^- + b_1^+ b_1^-"
        if k == n + 1:
            return f"-b_{n}^+ b_{n}^- - 1/2"
        return f"b_{k - 1}^+ b_{k - 1}^- - b_{k}^+ b_{k}^-"

    long_match = re.fullmatch(r"E_2del(\d+)_([pm])", label)
    if long_match:
        k = int(long_match.group(1))
        sign = "+" if long_match.group(2) == "p" else "-"
        return f"1/2 (b_{k}^{sign})^2"

    pair_match = re.fullmatch(r"E_del(\d+)_del(\d+)_([pm])([pm])", label)
    if pair_match:
        i, j = int(pair_match.group(1)), int(pair_match.group(2))
        first = "+" if pair_match.group(3) == "p" else "-"
        second = "+" if pair_match.group(4) == "p" else "-"
        return f"b_{i}^{first} b_{j}^{second}"

    odd_match = re.fullmatch(r"E_eps1_del(\d+)_([pm])([pm])", label)
    if odd_match:
        k = int(odd_match.group(1))
        fermion = "+" if odd_match.group(2) == "p" else "-"
        boson = "+" if odd_match.group(3) == "p" else "-"
        return f"a_1^{fermion} b_{k}^{boson}"

    raise ValueError(f"Unknown generator label: {label}")


def _standard_form(polynomial: Polynomial, order: tuple[str, ...]) -> list[dict]:
    variable_order = {label: index for index, label in enumerate(order)}
    terms = sorted(
        polynomial.items(),
        key=lambda item: tuple(variable_order[label] for label in item[0]),
    )
    return [
        {"words": list(word), "coeff": _fraction_string(coefficient)}
        for word, coefficient in terms
    ]


def _build_structure_constants(
    n: int,
    ordered_labels: list[str],
    parity: dict[str, int],
    generators: dict[str, Polynomial],
) -> list[dict]:
    reducer_data = _sympy_matrix(generators, ordered_labels)
    constants: list[dict] = []
    for left_index, left_label in enumerate(ordered_labels):
        for right_label in ordered_labels:
            bracket = _bracket(
                generators[left_label],
                generators[right_label],
                parity[left_label],
                parity[right_label],
                n,
            )
            if not bracket:
                continue
            coordinates = _coordinates(bracket, ordered_labels, reducer_data)
            for result_label, coefficient in zip(ordered_labels, coordinates):
                if coefficient:
                    constants.append(
                        {
                            "X": left_label,
                            "Y": right_label,
                            "Z": result_label,
                            "coeff": _fraction_string(coefficient),
                            "sign_rule": "graded",
                        }
                    )
    return constants


def build_schema(n: int, generation_date: str | None = None) -> dict:
    """Build one complete Schema 1 object in memory without writing a file."""
    if n < 1:
        raise ValueError("n must be a positive integer")

    ordered_labels, parity, generators = _make_basis(n)
    even = [label for label in ordered_labels if parity[label] == 0]
    odd = [label for label in ordered_labels if parity[label] == 1]
    oscillator_labels = oscillator_order(n)

    realizations = {
        label: {
            "standard_form": _standard_form(generators[label], oscillator_labels),
            "frappat_form": _realization_form(label, n),
            "parity": parity[label],
        }
        for label in ordered_labels
    }
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "family_formula": "osp(2m|2n) with m=1",
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
                "labels": ["a_1_p", "a_1_m"],
                "parity": 1,
                "description": "Standard fermionic creation and annihilation pair",
            },
            "bosons": {
                "n": n,
                "count": 2 * n,
                "labels": [
                    label
                    for k in range(1, n + 1)
                    for label in (f"b_{k}_p", f"b_{k}_m")
                ],
                "description": "Bosonic oscillators b_i^± with i=1,...,n",
            },
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations for a_1^±",
                "relations": {
                    "conjugate_pair": "{a_1_m, a_1_p} = 1",
                    "same_type": "{a_1^±, a_1^±} = 0",
                },
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_ij",
                },
            },
            "mixed_commutators": {
                "boson_fermion": "[b_j^s, a_1^σ] = 0 in the undeformed algebra"
            },
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "central": True,
                "nilpotent": True,
                "relation": "κ^2 = 0",
            },
            "K": {
                "parity": 0,
                "central": True,
                "role": "identity",
                "realization": "1",
                "in_basis": False,
            },
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": (
                "PBW: negative root vectors < H_1,...,H_{n+1} < positive "
                "root vectors; within-block order is defined in "
                "docs/json_schema_specification.md"
            ),
        },
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": ", ".join(oscillator_labels),
            "realizations": realizations,
        },
        "structure_constants": _build_structure_constants(
            n, ordered_labels, parity, generators
        ),
        "metadata": {
            "generated_by": "src/C_generators.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)",
            ],
        },
    }


def write_schemas(output_dir: Path, ranks: Iterable[int] = (1, 2, 3)) -> list[Path]:
    """Write the generated schemas; this is not run by the test suite."""
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for n in ranks:
        path = output_dir / f"C_{n}_structure.json"
        path.write_text(
            json.dumps(build_schema(n), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    arguments = parser.parse_args()
    for path in write_schemas(arguments.output_dir, arguments.ranks):
        print(path)


if __name__ == "__main__":
    main()
