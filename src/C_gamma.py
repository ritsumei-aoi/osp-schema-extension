"""Generate first-order gamma data for the C(n+1) oscillator deformation."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable

if __package__:
    from .C_generators import Polynomial, Word, _generator_data, _solve_coordinates
else:
    from C_generators import Polynomial, Word, _generator_data, _solve_coordinates

DeformedTerm = tuple[str | None, Word]
DeformedPolynomial = dict[DeformedTerm, Fraction]


def _token_order(token: str) -> tuple[int, int]:
    if token == "a_1_p":
        return (0, 0)
    if token == "a_1_m":
        return (0, 1)
    _, index, sign = token.split("_")
    return (int(index), 0 if sign == "p" else 1)


def _fermion(token: str) -> bool:
    return token.startswith("a_")


def _gb_parameter(fermion: str, boson: str) -> str:
    return f"gb_{fermion}_{boson}"


def _mixed_pair(left: str, right: str) -> bool:
    return left.startswith("b_") and right.startswith("a_")


def _pair_parameter(left: str, right: str) -> str:
    return _gb_parameter(right, left)


@lru_cache(maxsize=None)
def _normal_order_word(
    word: Word,
    active_parameter: str | None = None,
) -> tuple[tuple[DeformedTerm, Fraction], ...]:
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        prefix, suffix = word[:index], word[index + 2 :]

        if _fermion(left) and left == right:
            return ()

        if _token_order(left) <= _token_order(right):
            continue

        swapped = prefix + (right, left) + suffix
        if active_parameter is None and _mixed_pair(left, right):
            result: defaultdict[DeformedTerm, Fraction] = defaultdict(Fraction)
            for key, coefficient in _normal_order_word(swapped):
                result[key] += coefficient
            parameter = _pair_parameter(left, right)
            for key, coefficient in _normal_order_word(
                prefix + suffix, parameter
            ):
                result[key] += coefficient
            return tuple((key, coefficient) for key, coefficient in result.items() if coefficient)

        if (
            left == "a_1_m"
            and right == "a_1_p"
        ) or (
            left.startswith("b_")
            and right.startswith("b_")
            and left.split("_")[1] == right.split("_")[1]
            and left.endswith("_m")
            and right.endswith("_p")
        ):
            result = defaultdict(Fraction)
            for key, coefficient in _normal_order_word(prefix + suffix, active_parameter):
                result[key] += coefficient
            swap_sign = Fraction(-1) if _fermion(left) else Fraction(1)
            for key, coefficient in _normal_order_word(swapped, active_parameter):
                result[key] += swap_sign * coefficient
            return tuple((key, coefficient) for key, coefficient in result.items() if coefficient)

        return _normal_order_word(swapped, active_parameter)

    return (((active_parameter, word), Fraction(1)),)


def _deformed_polynomial(
    terms: Iterable[tuple[Word, Fraction | int]],
) -> DeformedPolynomial:
    result: defaultdict[DeformedTerm, Fraction] = defaultdict(Fraction)
    for word, coefficient in terms:
        for key, factor in _normal_order_word(tuple(word)):
            result[key] += Fraction(coefficient) * factor
    return {key: value for key, value in result.items() if value}


def _multiply(left: Polynomial, right: Polynomial) -> DeformedPolynomial:
    terms = []
    for left_word, left_coeff in left.items():
        for right_word, right_coeff in right.items():
            terms.append((left_word + right_word, left_coeff * right_coeff))
    return _deformed_polynomial(terms)


def _add(
    left: DeformedPolynomial,
    right: DeformedPolynomial,
    scale: Fraction = Fraction(1),
) -> DeformedPolynomial:
    result = defaultdict(Fraction, left)
    for key, coefficient in right.items():
        result[key] += scale * coefficient
    return {key: value for key, value in result.items() if value}


def _deformed_superbracket(
    left: Polynomial,
    right: Polynomial,
    left_parity: int,
    right_parity: int,
) -> DeformedPolynomial:
    sign = -1 if left_parity * right_parity % 2 else 1
    return _add(_multiply(left, right), _multiply(right, left), Fraction(-sign))


def _gamma_matrix(n: int) -> tuple[list[str], list[str], list[list[str]], list[dict]]:
    fermions = ["a_1_p", "a_1_m"]
    bosons = [
        label
        for k in range(1, n + 1)
        for label in (f"b_{k}_p", f"b_{k}_m")
    ]
    parameters = [
        {
            "label": _gb_parameter(fermion, boson),
            "fermion": fermion,
            "boson": boson,
            "parity": 1,
        }
        for fermion in fermions
        for boson in bosons
    ]
    matrix = [
        [_gb_parameter(fermion, boson) for boson in bosons]
        for fermion in fermions
    ]
    return fermions, bosons, matrix, parameters


def build_gamma(n: int, structure: dict | None = None) -> dict:
    full_order, parity, realizations = _generator_data(n)
    expected_even = [label for label in full_order if parity[label] == 0]
    expected_odd = [label for label in full_order if parity[label] == 1]
    if structure is None:
        structure = {
            "algebra": {
                "family": "C",
                "m": 1,
                "n": n,
                "cartan_type": f"C({n + 1})",
                "dimension": {
                    "total": 2 * n * n + 5 * n + 1,
                    "even": 2 * n * n + n + 1,
                    "odd": 4 * n,
                },
            },
            "basis": {
                "even": expected_even,
                "odd": expected_odd,
            },
            "parity": parity,
        }
    elif structure["algebra"]["n"] != n:
        raise ValueError("Schema 1 rank does not match requested gamma rank")
    elif (
        structure["algebra"]["family"] != "C"
        or structure["algebra"]["m"] != 1
        or structure["basis"]["even"] != expected_even
        or structure["basis"]["odd"] != expected_odd
        or structure["parity"] != parity
    ):
        raise ValueError("Schema 1 family, basis, or parity does not match C(n+1)")

    fermions, bosons, matrix, parameters = _gamma_matrix(n)
    gamma_basis = full_order + ["K"]
    gamma_realizations = {
        **realizations,
        "K": {(): Fraction(1)},
    }
    parameter_labels = {item["label"] for item in parameters}
    gamma_coefficients = []
    for i, left_label in enumerate(full_order):
        for right_label in full_order[i:]:
            bracket = _deformed_superbracket(
                realizations[left_label],
                realizations[right_label],
                parity[left_label],
                parity[right_label],
            )
            by_parameter: defaultdict[str, dict[Word, Fraction]] = defaultdict(dict)
            for (parameter, word), coefficient in bracket.items():
                if parameter is not None:
                    by_parameter[parameter][word] = coefficient
            for parameter in sorted(by_parameter):
                if parameter not in parameter_labels:
                    raise ValueError(f"unknown deformation parameter {parameter}")
                coordinates = _solve_coordinates(
                    gamma_basis, gamma_realizations, by_parameter[parameter]
                )
                for result_label, coefficient in coordinates.items():
                    gamma_coefficients.append(
                        {
                            "X": left_label,
                            "Y": right_label,
                            "gb_parameter": parameter,
                            "Z": result_label,
                            "coeff": str(coefficient),
                            "sign_rule": "graded",
                        }
                    )

    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "gb_matrix": {
            "shape": [2, 2 * n],
            "row_labels": fermions,
            "column_labels": bosons,
            "entries": matrix,
            "parameters": parameters,
        },
        "inhomogeneous_deformation": {
            "description": (
                "First-order deformation of mixed fermion-boson oscillator "
                "commutators; kappa is factored on the left"
            ),
            "oscillator_relations": [
                {
                    "fermion": item["fermion"],
                    "boson": item["boson"],
                    "relation": (
                        f"[{item['boson']}, {item['fermion']}] = "
                        f"-{item['label']} * kappa"
                    ),
                    "gb_parameter": item["label"],
                }
                for item in parameters
            ],
            "gamma_coefficients": gamma_coefficients,
            "coefficient_convention": (
                "Entries encode gamma in [X,Y]_gamma=[X,Y]_0+kappa*gamma(X,Y); "
                "since gb and kappa are both declared odd, -gb*kappa is rewritten "
                "as +kappa*gb; terms containing kappa^2 are zero."
            ),
        },
        "consistency": {
            "source_structure_file": f"C_{n}_structure.json",
            "basis_matches_schema_1": True,
            "parity_matches_schema_1": True,
            "parity_status": "formal_only",
            "parity_warning": (
                "The reference assigns odd parity to both gb parameters and kappa, "
                "so their product is even although the mixed oscillator commutator "
                "is odd. Gamma coefficients are generated formally from the stated "
                "exchange relation; this parity conflict remains unresolved."
            ),
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/json_schema_specification.md",
                f"data/C_{n}_structure.json",
            ],
        },
    }


def generate(data_directory: Path, ranks: Iterable[int] = (1, 2, 3)) -> list[Path]:
    generated = []
    for n in ranks:
        structure_path = data_directory / f"C_{n}_structure.json"
        structure = json.loads(structure_path.read_text(encoding="utf-8"))
        schema = build_gamma(n, structure)
        path = data_directory / f"C_{n}_gamma.json"
        path.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        generated.append(path)
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for path in generate(args.data_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
