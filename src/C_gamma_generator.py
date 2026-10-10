"""Generate Schema 2 inhomogeneous gamma data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path

import sympy as sp

if __package__:
    from .C_generators import (
        Polynomial,
        _coordinates,
        _make_basis,
        _sympy_matrix,
        normal_order_word,
    )
else:
    from C_generators import (
        Polynomial,
        _coordinates,
        _make_basis,
        _sympy_matrix,
        normal_order_word,
    )


GammaPolynomial = dict[tuple[str, ...], sp.Expr]


def _gb_label(fermion: str, boson: str) -> str:
    fermion_sign = "p" if fermion == "a_1_p" else "m"
    _, boson_index, boson_sign = boson.split("_")
    return f"gb_a1_{fermion_sign}_b{boson_index}_{boson_sign}"


def _word_parity(word: tuple[str, ...]) -> int:
    return sum(label in ("a_1_p", "a_1_m") for label in word) % 2


def _merge_fraction(
    target: Polynomial, source: Polynomial, scale: Fraction = Fraction(1)
) -> None:
    for word, coefficient in source.items():
        target[word] = target.get(word, Fraction(0)) + scale * coefficient
        if not target[word]:
            del target[word]


def _merge_gamma(
    target: GammaPolynomial,
    source: GammaPolynomial,
    scale: Fraction = Fraction(1),
) -> None:
    for word, coefficient in source.items():
        value = sp.expand(target.get(word, sp.Integer(0)) + scale * coefficient)
        if value:
            target[word] = value
        else:
            target.pop(word, None)


def _normal_order_deformed_word(
    word: tuple[str, ...],
    n: int,
    oscillator_order: tuple[str, ...],
    gb_symbols: dict[str, sp.Symbol],
) -> tuple[Polynomial, GammaPolynomial]:
    """Return the undeformed part and the coefficient of leftmost kappa."""
    positions = {label: index for index, label in enumerate(oscillator_order)}

    def reduce(current: tuple[str, ...]) -> tuple[Polynomial, GammaPolynomial]:
        for index in range(len(current) - 1):
            left, right = current[index : index + 2]
            prefix, suffix = current[:index], current[index + 2 :]

            if left == right and left in ("a_1_p", "a_1_m"):
                return {}, {}
            if positions[left] <= positions[right]:
                continue

            if left.startswith("b_") and right in ("a_1_p", "a_1_m"):
                base, gamma = reduce(prefix + (right, left) + suffix)
                boson = left
                parameter = gb_symbols[_gb_label(right, boson)]
                contraction = normal_order_word(prefix + suffix, n)
                sign = -1 if _word_parity(prefix) else 1
                _merge_gamma(
                    gamma,
                    {
                        reduced_word: -sign * parameter * coefficient
                        for reduced_word, coefficient in contraction.items()
                    },
                )
                return base, gamma

            if (left, right) == ("a_1_m", "a_1_p"):
                base: Polynomial = {}
                gamma: GammaPolynomial = {}
                contracted_base, contracted_gamma = reduce(prefix + suffix)
                _merge_fraction(base, contracted_base)
                _merge_gamma(gamma, contracted_gamma)
                swapped_base, swapped_gamma = reduce(
                    prefix + ("a_1_p", "a_1_m") + suffix
                )
                _merge_fraction(base, swapped_base, Fraction(-1))
                _merge_gamma(gamma, swapped_gamma, Fraction(-1))
                return base, gamma

            if (
                left.startswith("b_")
                and right.startswith("b_")
                and left.split("_")[1] == right.split("_")[1]
                and left.endswith("_m")
                and right.endswith("_p")
            ):
                base = {}
                gamma = {}
                contracted_base, contracted_gamma = reduce(prefix + suffix)
                _merge_fraction(base, contracted_base)
                _merge_gamma(gamma, contracted_gamma)
                swapped_base, swapped_gamma = reduce(
                    prefix + (right, left) + suffix
                )
                _merge_fraction(base, swapped_base)
                _merge_gamma(gamma, swapped_gamma)
                return base, gamma

            return reduce(prefix + (right, left) + suffix)

        return {current: Fraction(1)}, {}

    return reduce(word)


def _multiply_deformed(
    left: Polynomial,
    right: Polynomial,
    n: int,
    oscillator_order: tuple[str, ...],
    gb_symbols: dict[str, sp.Symbol],
) -> tuple[Polynomial, GammaPolynomial]:
    base: Polynomial = {}
    gamma: GammaPolynomial = {}
    for left_word, left_coefficient in left.items():
        for right_word, right_coefficient in right.items():
            word_base, word_gamma = _normal_order_deformed_word(
                left_word + right_word, n, oscillator_order, gb_symbols
            )
            scale = left_coefficient * right_coefficient
            _merge_fraction(base, word_base, scale)
            _merge_gamma(gamma, word_gamma, scale)
    return base, gamma


def _deformed_bracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
    n: int,
    oscillator_order: tuple[str, ...],
    gb_symbols: dict[str, sp.Symbol],
) -> tuple[Polynomial, GammaPolynomial]:
    left_right_base, left_right_gamma = _multiply_deformed(
        left, right, n, oscillator_order, gb_symbols
    )
    right_left_base, right_left_gamma = _multiply_deformed(
        right, left, n, oscillator_order, gb_symbols
    )
    sign = -1 if left_parity * right_parity % 2 else 1
    _merge_fraction(left_right_base, right_left_base, Fraction(-sign))
    _merge_gamma(left_right_gamma, right_left_gamma, Fraction(-sign))
    return left_right_base, left_right_gamma


def _gamma_coordinates(
    gamma: GammaPolynomial,
    ordered_labels: list[str],
    reducer_data,
    gb_symbols: dict[str, sp.Symbol],
) -> dict[str, sp.Expr]:
    parameters = tuple(gb_symbols.values())
    by_parameter: dict[sp.Symbol, Polynomial] = {symbol: {} for symbol in parameters}

    for word, expression in gamma.items():
        polynomial = sp.Poly(sp.expand(expression), *parameters)
        for powers, coefficient in polynomial.terms():
            degree = sum(powers)
            if degree != 1:
                raise ValueError(
                    f"Expected a linear gb term, found {expression} for {word}"
                )
            symbol = next(
                symbol
                for symbol, power in zip(polynomial.gens, powers)
                if power
            )
            value = Fraction(int(coefficient.p), int(coefficient.q))
            by_parameter[symbol][word] = (
                by_parameter[symbol].get(word, Fraction(0)) + value
            )

    result: dict[str, sp.Expr] = {}
    for symbol, oscillator_polynomial in by_parameter.items():
        if not oscillator_polynomial:
            continue
        coordinates = _coordinates(
            oscillator_polynomial, ordered_labels, reducer_data
        )
        for label, coefficient in zip(ordered_labels, coordinates):
            if coefficient:
                result[label] = sp.expand(
                    result.get(label, sp.Integer(0)) + coefficient * symbol
                )
    return {label: coefficient for label, coefficient in result.items() if coefficient}


def build_gamma_schema(
    n: int,
    structure_data: dict,
    generation_date: str | None = None,
) -> dict:
    if n < 1:
        raise ValueError("n must be a positive integer")
    if structure_data["algebra"]["family"] != "C" or structure_data["algebra"]["n"] != n:
        raise ValueError("Schema 1 family/rank does not match requested C(n+1) rank")

    ordered_labels, parity, generators = _make_basis(n)
    structure_labels = (
        structure_data["basis"]["even"] + structure_data["basis"]["odd"]
    )
    if set(structure_labels) != set(ordered_labels):
        raise ValueError("Schema 1 basis does not match the C(n+1) generator basis")
    if structure_data["parity"] != parity:
        raise ValueError("Schema 1 parity map does not match generated C(n+1) parity")
    gamma_labels = ["K", *ordered_labels]
    gamma_generators = {"K": {(): Fraction(1)}, **generators}
    gamma_parity = {"K": 0, **parity}

    oscillator_order = (
        "a_1_p",
        "a_1_m",
        *(label for k in range(1, n + 1) for label in (f"b_{k}_p", f"b_{k}_m")),
    )
    row_labels = ["a_1_p", "a_1_m"]
    column_labels = [
        label
        for k in range(1, n + 1)
        for label in (f"b_{k}_p", f"b_{k}_m")
    ]
    gb_symbols = {
        _gb_label(fermion, boson): sp.Symbol(_gb_label(fermion, boson))
        for fermion in row_labels
        for boson in column_labels
    }
    structure_reducer_data = _sympy_matrix(generators, ordered_labels)
    gamma_reducer_data = _sympy_matrix(gamma_generators, gamma_labels)

    structure_brackets: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in structure_data["structure_constants"]:
        structure_brackets.setdefault((entry["X"], entry["Y"]), {})[
            entry["Z"]
        ] = Fraction(entry["coeff"])

    gamma_entries: list[dict] = []
    gamma_brackets: dict[tuple[str, str], dict[str, sp.Expr]] = {}
    for left in ordered_labels:
        for right in ordered_labels:
            base, gamma = _deformed_bracket(
                generators[left],
                generators[right],
                parity[left],
                parity[right],
                n,
                oscillator_order,
                gb_symbols,
            )
            base_coordinates = _coordinates(
                base, ordered_labels, structure_reducer_data
            )
            base_bracket = {
                label: coefficient
                for label, coefficient in zip(ordered_labels, base_coordinates)
                if coefficient
            }
            if base_bracket != structure_brackets.get((left, right), {}):
                raise ValueError(
                    f"Undeformed bracket disagrees with Schema 1 for ({left}, {right})"
                )

            coordinates = _gamma_coordinates(
                gamma, gamma_labels, gamma_reducer_data, gb_symbols
            )
            expected_parity = (parity[left] + parity[right] + 1) % 2
            if any(
                gamma_parity[label] != expected_parity
                for label in coordinates
            ):
                raise ValueError(
                    f"Gamma output parity mismatch for ({left}, {right})"
                )
            gamma_brackets[(left, right)] = coordinates
            for result, coefficient in coordinates.items():
                gamma_entries.append(
                    {
                        "X": left,
                        "Y": right,
                        "Z": result,
                        "coeff": str(coefficient),
                        "sign_rule": "graded",
                    }
                )

    for left in ordered_labels:
        for right in ordered_labels:
            factor = 1 if parity[left] * parity[right] % 2 else -1
            expected = {
                label: sp.expand(factor * coefficient)
                for label, coefficient in gamma_brackets[(right, left)].items()
                if factor * coefficient
            }
            if gamma_brackets[(left, right)] != expected:
                raise ValueError(
                    f"Gamma coefficients violate graded skew-symmetry for ({left}, {right})"
                )

    matrix_entries = [
        [
            gb_symbols[_gb_label(fermion, boson)].name
            for boson in column_labels
        ]
        for fermion in row_labels
    ]
    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "source_structure_file": f"C_{n}_structure.json",
        "inhomogeneous_deformation": {
            "type": "gb",
            "gb_matrix": {
                "shape": [2, 2 * n],
                "row_labels": row_labels,
                "column_labels": column_labels,
                "entries": matrix_entries,
                "parameter_parity": 0,
            },
            "kappa": {"parity": 1, "nilpotent": True},
            "mixed_oscillator_relations": {
                "convention": (
                    "[b_j^s, a_1^σ] = -gb_{σ,j,s} * κ; "
                    "κ is placed on the right in this relation"
                ),
                "parameter_parity": 0,
                "relations": [
                    {
                        "X": boson,
                        "Y": fermion,
                        "parameter": _gb_label(fermion, boson),
                        "rhs": f"-{_gb_label(fermion, boson)} * κ",
                    }
                    for fermion in row_labels
                    for boson in column_labels
                ],
            },
            "gamma_coefficients": gamma_entries,
        },
        "metadata": {
            "generated_by": "src/C_gamma_generator.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/C_inhomogeneous_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def write_gamma_schemas(
    data_dir: Path, ranks: tuple[int, ...] = (1, 2, 3)
) -> list[Path]:
    written = []
    for n in ranks:
        structure_path = data_dir / f"C_{n}_structure.json"
        structure_data = json.loads(structure_path.read_text(encoding="utf-8"))
        gamma_data = build_gamma_schema(n, structure_data)
        path = data_dir / f"C_{n}_gamma.json"
        path.write_text(
            json.dumps(gamma_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    arguments = parser.parse_args()
    for path in write_gamma_schemas(arguments.data_dir, tuple(arguments.ranks)):
        print(path)


if __name__ == "__main__":
    main()
