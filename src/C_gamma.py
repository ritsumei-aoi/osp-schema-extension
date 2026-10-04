"""Generate first-order inhomogeneous deformation data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

if __package__:
    from .C_generators import _linear_coordinates, build_generators
else:
    from C_generators import _linear_coordinates, build_generators


def _normalize_deformed(
    word: tuple[str, ...], n: int, parameter: str | None = None
) -> dict[tuple[tuple[str, ...], str | None], Fraction]:
    order = {
        "a_1_p": 0,
        "a_1_m": 1,
        **{f"b_{i}_p": i + 1 for i in range(1, n + 1)},
        **{f"b_{i}_m": n + i + 1 for i in range(1, n + 1)},
    }
    for index in range(len(word) - 1):
        left, right = word[index : index + 2]
        if left == right and left in ("a_1_p", "a_1_m"):
            return {}
        if order[left] <= order[right]:
            continue

        prefix, suffix = word[:index], word[index + 2 :]
        if left == "a_1_m" and right == "a_1_p":
            contracted = _normalize_deformed(prefix + suffix, n, parameter)
            swapped = _normalize_deformed(prefix + (right, left) + suffix, n, parameter)
            return _add_deformed(contracted, swapped, Fraction(1), Fraction(-1))

        if left.startswith("b_") and left.endswith("_m") and right.startswith("b_") and right.endswith("_p"):
            left_mode = int(left.split("_")[1])
            right_mode = int(right.split("_")[1])
            contracted = (
                _normalize_deformed(prefix + suffix, n, parameter)
                if left_mode == right_mode
                else {}
            )
            swapped = _normalize_deformed(prefix + (right, left) + suffix, n, parameter)
            return _add_deformed(contracted, swapped)

        if left.startswith("b_") and right.startswith("a_"):
            swapped = _normalize_deformed(prefix + (right, left) + suffix, n, parameter)
            if parameter is not None:
                return swapped
            name = f"gb_{right.replace('_', '')}_{left.replace('_', '')}"
            contracted = _normalize_deformed(prefix + suffix, n, name)
            return _add_deformed(swapped, contracted, Fraction(1), Fraction(-1))

        return _normalize_deformed(prefix + (right, left) + suffix, n, parameter)
    return {(word, parameter): Fraction(1)}


def _add_deformed(
    left: dict[tuple[tuple[str, ...], str | None], Fraction],
    right: dict[tuple[tuple[str, ...], str | None], Fraction],
    left_scale: Fraction = Fraction(1),
    right_scale: Fraction = Fraction(1),
) -> dict[tuple[tuple[str, ...], str | None], Fraction]:
    result = {term: left_scale * coefficient for term, coefficient in left.items()}
    for term, coefficient in right.items():
        result[term] = result.get(term, Fraction(0)) + right_scale * coefficient
    return {term: coeff for term, coeff in result.items() if coeff}


def _multiply_deformed(
    left: dict[tuple[tuple[str, ...], str | None], Fraction],
    right: dict[tuple[tuple[str, ...], str | None], Fraction],
    n: int,
) -> dict[tuple[tuple[str, ...], str | None], Fraction]:
    result: dict[tuple[tuple[str, ...], str | None], Fraction] = {}
    for (left_word, left_parameter), left_coeff in left.items():
        for (right_word, right_parameter), right_coeff in right.items():
            if left_parameter and right_parameter:
                continue
            parameter = left_parameter or right_parameter
            normalized = _normalize_deformed(left_word + right_word, n, parameter)
            for term, coeff in normalized.items():
                result[term] = result.get(term, Fraction(0)) + left_coeff * right_coeff * coeff
    return {term: coeff for term, coeff in result.items() if coeff}


def _deformed_bracket(
    x: dict[tuple[tuple[str, ...], str | None], Fraction],
    y: dict[tuple[tuple[str, ...], str | None], Fraction],
    px: int,
    py: int,
    n: int,
) -> dict[tuple[tuple[str, ...], str | None], Fraction]:
    xy = _multiply_deformed(x, y, n)
    yx = _multiply_deformed(y, x, n)
    sign = Fraction(-1 if not (px and py) else 1)
    result = dict(xy)
    for term, coeff in yx.items():
        result[term] = result.get(term, Fraction(0)) + sign * coeff
    return {term: coeff for term, coeff in result.items() if coeff}


def build_gamma_schema(n: int, generation_date: str = "2026-10-04") -> dict[str, Any]:
    even, odd, realizations, parity = build_generators(n)
    labels = odd + even
    output_labels = labels + ["K"]
    plain_basis = [realizations[label] for label in labels] + [{(): Fraction(1)}]
    deformed_basis = [
        {(word, None): coeff for word, coeff in realizations[label].items()}
        for label in labels
    ]
    gamma: list[dict[str, str]] = []
    for i, x in enumerate(labels):
        for j in range(i, len(labels)):
            y = labels[j]
            result = _deformed_bracket(
                deformed_basis[i], deformed_basis[j], parity[x], parity[y], n
            )
            parameters = sorted(
                {parameter for _, parameter in result if parameter is not None}
            )
            for parameter in parameters:
                vector = {
                    word: coeff
                    for (word, found_parameter), coeff in result.items()
                    if found_parameter == parameter
                }
                coordinates = _linear_coordinates(plain_basis, vector)
                for z, coeff in zip(output_labels, coordinates):
                    if coeff:
                        gamma.append({
                            "X": x,
                            "Y": y,
                            "Z": z,
                            "parameter": parameter,
                            "coeff": str(coeff),
                            "sign_rule": "graded",
                        })

    fermion_labels = ["a_1_p", "a_1_m"]
    boson_labels = [
        label
        for k in range(1, n + 1)
        for label in (f"b_{k}_p", f"b_{k}_m")
    ]
    parameter_labels = [
        f"gb_{fermion.replace('_', '')}_{boson.replace('_', '')}"
        for fermion in fermion_labels
        for boson in boson_labels
    ]
    exchange_relations = []
    for fermion in fermion_labels:
        for boson in boson_labels:
            parameter = f"gb_{fermion.replace('_', '')}_{boson.replace('_', '')}"
            exchange_relations.append({
                "X": boson,
                "Y": fermion,
                "relation": f"[{boson}, {fermion}] = -{parameter} * kappa",
                "parameter": parameter,
            })

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "base_structure_file": f"C_{n}_structure.json",
        },
        "gb_matrix": {
            "shape": [2, 2 * n],
            "row_labels": fermion_labels,
            "column_labels": boson_labels,
            "parameters": [
                [
                    f"gb_{fermion.replace('_', '')}_{boson.replace('_', '')}"
                    for boson in boson_labels
                ]
                for fermion in fermion_labels
            ],
            "parameter_parity": 1,
            "parameter_count": 4 * n,
        },
        "inhomogeneous_deformation": {
            "bracket_formula": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
            "oscillator_exchange_relations": exchange_relations,
            "gamma_coefficients": gamma,
            "coefficient_convention": (
                "gamma(X,Y) is the sum of coeff * gb_parameter * Z over records."
            ),
            "parity_note": (
                "The source assigns odd parity to both gb and kappa, yet their "
                "mixed oscillator commutator has odd parity. Coefficients are "
                "therefore retained formally and parity-discrepant terms are "
                "reported rather than silently altered."
            ),
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": generation_date,
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                f"data/C_{n}_structure.json",
            ],
            "assumptions": [
                "The specified mixed exchange relation is expanded to first order in gb*kappa.",
                "The documented odd gb and odd kappa are retained as formal labels; their product is treated as the central even deformation coefficient in the oscillator rewrite.",
                "Scalar identity terms that are not in the Lie basis are represented by K=1, as recorded among the Schema 1 central elements.",
                "The source parity assignments for gb and kappa conflict with the mixed oscillator commutator's parity; no parity reinterpretation is made in this formal coefficient extraction.",
            ],
        },
    }


def validate_against_structure(gamma_schema: dict[str, Any], structure: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    n = gamma_schema["algebra"]["n"]
    if structure["schema_version"] != gamma_schema["schema_version"]:
        errors.append("Gamma and structure schema versions do not match.")
    if structure["algebra"]["n"] != n:
        errors.append("Gamma and structure ranks do not match.")
    if "K" not in structure["central_elements"]:
        errors.append("Schema 1 does not declare the required central identity K.")
    basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
    basis.add("K")
    if gamma_schema["algebra"]["base_structure_file"] != f"C_{n}_structure.json":
        errors.append("Gamma file references the wrong Schema 1 filename.")
    if gamma_schema["gb_matrix"]["shape"] != [2, 2 * n]:
        errors.append("gb_matrix has an incorrect shape.")
    if gamma_schema["gb_matrix"]["parameter_count"] != 4 * n:
        errors.append("gb_matrix has an incorrect parameter count.")
    if len(gamma_schema["gb_matrix"]["parameters"]) != 2 or any(
        len(row) != 2 * n for row in gamma_schema["gb_matrix"]["parameters"]
    ):
        errors.append("gb_matrix parameter rows do not match the declared shape.")
    parity = structure["parity"]
    for entry in gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]:
        if any(entry[label] not in basis for label in ("X", "Y", "Z")):
            errors.append(f"Gamma coefficient refers to an unknown basis label: {entry}.")
            continue
        if entry["parameter"] not in {
            parameter
            for row in gamma_schema["gb_matrix"]["parameters"]
            for parameter in row
        }:
            errors.append(f"Gamma coefficient uses an unknown gb parameter: {entry}.")
    expected_parameters = {
        f"gb_{fermion.replace('_', '')}_{boson.replace('_', '')}"
        for fermion in gamma_schema["gb_matrix"]["row_labels"]
        for boson in gamma_schema["gb_matrix"]["column_labels"]
    }
    actual_parameters = {
        parameter
        for row in gamma_schema["gb_matrix"]["parameters"]
        for parameter in row
    }
    if actual_parameters != expected_parameters:
        errors.append("gb_matrix does not enumerate every fermion/boson pair exactly.")
    if len(gamma_schema["inhomogeneous_deformation"]["oscillator_exchange_relations"]) != 4 * n:
        errors.append("Mixed oscillator exchange relation count is incorrect.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    failed = False
    for n in args.ranks:
        gamma_schema = build_gamma_schema(n)
        structure_path = args.output_dir / f"C_{n}_structure.json"
        structure = json.loads(structure_path.read_text(encoding="utf-8"))
        errors = validate_against_structure(gamma_schema, structure)
        if errors:
            for error in errors:
                print(f"FAIL C_{n}_gamma.json: {error}")
            failed = True
            continue
        output = args.output_dir / f"C_{n}_gamma.json"
        output.write_text(
            json.dumps(gamma_schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            f"PASS {output}: parameters={gamma_schema['gb_matrix']['parameter_count']}, "
            f"gamma_terms={len(gamma_schema['inhomogeneous_deformation']['gamma_coefficients'])}, "
            f"parity_exceptions={_parity_exception_count(gamma_schema, structure)}"
        )
    return 1 if failed else 0


def _parity_exception_count(gamma_schema: dict[str, Any], structure: dict[str, Any]) -> int:
    parity = structure["parity"]
    return sum(
        1
        for entry in gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]
        if entry["Z"] != "K"
        and parity[entry["Z"]] != (parity[entry["X"]] + parity[entry["Y"]]) % 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
