"""Generate symbolic odd-map coboundary data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


def _bracket_table(structure: dict[str, Any]) -> tuple[list[str], dict[str, int], dict]:
    labels = structure["basis"]["odd"] + structure["basis"]["even"]
    position = {label: index for index, label in enumerate(labels)}
    parity = structure["parity"]
    table: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in structure["structure_constants"]:
        table.setdefault((entry["X"], entry["Y"]), {})[entry["Z"]] = Fraction(entry["coeff"])

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        if position[x] <= position[y]:
            return table.get((x, y), {})
        sign = Fraction(1 if parity[x] and parity[y] else -1)
        return {
            z: sign * coeff
            for z, coeff in table.get((y, x), {}).items()
        }

    return labels, parity, bracket


def _parameter(target: str, source: str) -> str:
    return f"phi__{target}__{source}"


def _add_term(
    coefficients: dict[tuple[str, str, str], dict[str, Fraction]],
    key: tuple[str, str, str],
    parameter: str,
    coefficient: Fraction,
) -> None:
    if not coefficient:
        return
    terms = coefficients.setdefault(key, {})
    terms[parameter] = terms.get(parameter, Fraction(0)) + coefficient
    if not terms[parameter]:
        del terms[parameter]
    if not terms:
        del coefficients[key]


def build_coboundary_schema(
    structure: dict[str, Any], generation_date: str = "2026-10-04"
) -> dict[str, Any]:
    labels, parity, bracket = _bracket_table(structure)
    allowed_targets = {
        source: [target for target in labels if parity[target] == 1 - parity[source]]
        for source in labels
    }
    coefficients: dict[tuple[str, str, str], dict[str, Fraction]] = {}
    for x in labels:
        px = parity[x]
        for y in labels:
            py = parity[y]
            for target in allowed_targets[y]:
                scale = Fraction(-1 if px else 1)
                for z, coeff in bracket(x, target).items():
                    _add_term(
                        coefficients,
                        (x, y, z),
                        _parameter(target, y),
                        scale * coeff,
                    )
            second_scale = Fraction(-1 if (px + 1) * py % 2 else 1)
            for target in allowed_targets[x]:
                for z, coeff in bracket(y, target).items():
                    _add_term(
                        coefficients,
                        (x, y, z),
                        _parameter(target, x),
                        -second_scale * coeff,
                    )
            for middle, bracket_coeff in bracket(x, y).items():
                for target in allowed_targets[middle]:
                    _add_term(
                        coefficients,
                        (x, y, target),
                        _parameter(target, middle),
                        -bracket_coeff,
                    )

    f_parameters = [
        {
            "parameter": _parameter(target, source),
            "target": target,
            "source": source,
        }
        for source in labels
        for target in allowed_targets[source]
    ]
    coboundary_coefficients = [
        {
            "X": x,
            "Y": y,
            "Z": z,
            "terms": [
                {"parameter": parameter, "coeff": str(coeff)}
                for parameter, coeff in sorted(terms.items())
            ],
        }
        for (x, y, z), terms in sorted(
            coefficients.items(),
            key=lambda item: (
                labels.index(item[0][0]),
                labels.index(item[0][1]),
                labels.index(item[0][2]),
            ),
        )
    ]
    n = structure["algebra"]["n"]
    return {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": structure["algebra"],
        "base_structure_file": f"C_{n}_structure.json",
        "odd_linear_map": {
            "parity": 1,
            "rule": "f(Z_j) = sum_i phi_{i,j} Z_i with parity(Z_i) = 1 - parity(Z_j).",
            "parameter_count": len(f_parameters),
            "parameters": f_parameters,
        },
        "coboundary_definition": {
            "formula": (
                "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] "
                "- (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
            ),
            "sign_rule": "graded",
            "coefficient_convention": (
                "Each term coeff * parameter contributes to the stated Z coefficient."
            ),
        },
        "coboundary_coefficients": coboundary_coefficients,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": generation_date,
            "references": [
                "docs/math/C_coboundary_definition.md",
                f"data/C_{n}_structure.json",
            ],
        },
    }


def validate_against_structure(
    coboundary: dict[str, Any], structure: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    labels = set(structure["basis"]["even"] + structure["basis"]["odd"])
    parity = structure["parity"]
    f_parameters = {
        entry["parameter"]: (entry["target"], entry["source"])
        for entry in coboundary["odd_linear_map"]["parameters"]
    }
    expected_count = 2 * len(structure["basis"]["even"]) * len(structure["basis"]["odd"])
    if coboundary["odd_linear_map"]["parameter_count"] != expected_count:
        errors.append("Odd-map parameter count does not match the parity decomposition.")
    if len(f_parameters) != expected_count:
        errors.append("Odd-map parameter labels are not unique.")
    for target, source in f_parameters.values():
        if target not in labels or source not in labels:
            errors.append(f"Odd map references an unknown basis label: {target}, {source}.")
        elif parity[target] + parity[source] != 1:
            errors.append(f"Odd map does not reverse parity: {target} <- {source}.")
    for entry in coboundary["coboundary_coefficients"]:
        if any(entry[label] not in labels for label in ("X", "Y", "Z")):
            errors.append(f"Coboundary term references an unknown basis label: {entry}.")
        for term in entry["terms"]:
            if term["parameter"] not in f_parameters:
                errors.append(f"Coboundary term uses an unknown phi parameter: {term}.")
            if not Fraction(term["coeff"]):
                errors.append(f"Coboundary term has an explicit zero coefficient: {term}.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    failed = False
    for n in args.ranks:
        structure = json.loads(
            (args.data_dir / f"C_{n}_structure.json").read_text(encoding="utf-8")
        )
        coboundary = build_coboundary_schema(structure)
        errors = validate_against_structure(coboundary, structure)
        if errors:
            for error in errors:
                print(f"FAIL C_{n}_coboundary.json: {error}")
            failed = True
            continue
        output = args.data_dir / f"C_{n}_coboundary.json"
        output.write_text(
            json.dumps(coboundary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(
            f"PASS {output}: phi_parameters={coboundary['odd_linear_map']['parameter_count']}, "
            f"delta_terms={len(coboundary['coboundary_coefficients'])}"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
