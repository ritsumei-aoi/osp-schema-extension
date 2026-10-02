#!/usr/bin/env python3
"""Generate generic odd-map coboundaries for C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path


Vector = dict[str, Fraction]
SymbolicVector = dict[str, dict[str, Fraction]]


def _add(left: Vector, right: Vector) -> Vector:
    result = dict(left)
    for label, coefficient in right.items():
        result[label] = result.get(label, Fraction()) + coefficient
    return {label: value for label, value in result.items() if value}


def _scale(vector: Vector, coefficient: Fraction | int) -> Vector:
    return {
        label: coefficient * value
        for label, value in vector.items()
        if coefficient * value
    }


def _add_symbolic(
    left: SymbolicVector, right: SymbolicVector
) -> SymbolicVector:
    result = {label: dict(values) for label, values in left.items()}
    for label, values in right.items():
        target = result.setdefault(label, {})
        for parameter, coefficient in values.items():
            target[parameter] = target.get(parameter, Fraction()) + coefficient
    return {
        label: {parameter: value for parameter, value in values.items() if value}
        for label, values in result.items()
        if any(values.values())
    }


def _scale_symbolic(
    vector: SymbolicVector, coefficient: Fraction | int
) -> SymbolicVector:
    return {
        label: {
            parameter: coefficient * value
            for parameter, value in values.items()
            if coefficient * value
        }
        for label, values in vector.items()
        if any(coefficient * value for value in values.values())
    }


def _format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def _parameter(target: str, source: str) -> str:
    return f"phi_{target}_from_{source}"


def _format_expression(coefficients: dict[str, Fraction]) -> str:
    terms: list[str] = []
    for parameter in sorted(coefficients):
        coefficient = coefficients[parameter]
        if not coefficient:
            continue
        magnitude = abs(coefficient)
        term = parameter if magnitude == 1 else (
            f"{_format_fraction(magnitude)}*{parameter}"
        )
        if not terms:
            terms.append(("-" if coefficient < 0 else "") + term)
        else:
            terms.append(f" {'-' if coefficient < 0 else '+'} {term}")
    return "".join(terms)


def _bracket_table(schema: dict) -> tuple[list[str], dict[str, int], dict]:
    labels = list(schema["generator_realization"]["realizations"])
    parity = schema["parity"]
    positions = {label: index for index, label in enumerate(labels)}
    table: dict[tuple[str, str], Vector] = {}
    for record in schema["structure_constants"]:
        key = (record["X"], record["Y"])
        value = table.setdefault(key, {})
        value[record["Z"]] = value.get(record["Z"], Fraction()) + Fraction(
            record["coeff"]
        )

    def bracket(left: str, right: str) -> Vector:
        if positions[left] <= positions[right]:
            return table.get((left, right), {})
        reverse = table.get((right, left), {})
        sign = 1 if parity[left] and parity[right] else -1
        return _scale(reverse, sign)

    return labels, parity, bracket


def _map_image(source: str, targets: list[str]) -> SymbolicVector:
    return {
        target: {_parameter(target, source): Fraction(1)}
        for target in targets
    }


def _bracket_with_symbolic(
    generator: str, symbolic: SymbolicVector, bracket
) -> SymbolicVector:
    result: SymbolicVector = {}
    for source, coefficients in symbolic.items():
        for target, scalar in bracket(generator, source).items():
            contribution = {
                target: {
                    parameter: scalar * value
                    for parameter, value in coefficients.items()
                }
            }
            result = _add_symbolic(result, contribution)
    return result


def _map_of_vector(
    vector: Vector,
    parity: dict[str, int],
    targets_by_parity: dict[int, list[str]],
) -> SymbolicVector:
    result: SymbolicVector = {}
    for source, coefficient in vector.items():
        for target in targets_by_parity[1 - parity[source]]:
            result = _add_symbolic(
                result,
                {target: {_parameter(target, source): coefficient}},
            )
    return result


def _coboundary(
    x: str,
    y: str,
    parity: dict[str, int],
    targets_by_parity: dict[int, list[str]],
    bracket,
) -> SymbolicVector:
    px, py = parity[x], parity[y]
    fx = _map_image(x, targets_by_parity[1 - px])
    fy = _map_image(y, targets_by_parity[1 - py])

    first = _scale_symbolic(
        _bracket_with_symbolic(x, fy, bracket),
        -1 if px else 1,
    )
    exponent = (px + 1) * py
    second_sign = 1 if exponent % 2 else -1
    second = _scale_symbolic(
        _bracket_with_symbolic(y, fx, bracket),
        second_sign,
    )
    third = _scale_symbolic(
        _map_of_vector(bracket(x, y), parity, targets_by_parity),
        -1,
    )
    return _add_symbolic(_add_symbolic(first, second), third)


def build_coboundary_schema(
    structure_schema: dict, generation_date: str | None = None
) -> dict:
    if structure_schema["algebra"]["family"] != "C":
        raise ValueError("Source structure schema is not a C-family schema")
    rank = structure_schema["algebra"]["n"]
    labels, parity, bracket = _bracket_table(structure_schema)
    targets_by_parity = {
        0: [label for label in labels if parity[label] == 0],
        1: [label for label in labels if parity[label] == 1],
    }

    map_entries = [
        {
            "source": source,
            "target": target,
            "coefficient": _parameter(target, source),
        }
        for source in labels
        for target in targets_by_parity[1 - parity[source]]
    ]
    coboundary_coefficients = []
    for left_index, x in enumerate(labels):
        for y in labels[left_index:]:
            values = _coboundary(
                x, y, parity, targets_by_parity, bracket
            )
            for z in labels:
                coefficients = values.get(z, {})
                expression = _format_expression(coefficients)
                if expression:
                    coboundary_coefficients.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coeff": expression,
                        "sign_rule": "graded",
                    })

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": rank,
            "cartan_type": f"C({rank + 1})",
        },
        "source_schema": f"C_{rank}_structure.json",
        "odd_linear_map": {
            "parity": 1,
            "parameter_parity": 0,
            "entries": map_entries,
        },
        "coboundary": {
            "formula": (
                "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] "
                "- (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
            ),
            "coefficients": coboundary_coefficients,
        },
        "metadata": {
            "generated_by": "src/C_coboundary_generator.py",
            "generation_date": generation_date or date.today().isoformat(),
        },
    }


def validate_coboundary_schema(coboundary: dict, structure: dict) -> None:
    rank = structure["algebra"]["n"]
    if coboundary["source_schema"] != f"C_{rank}_structure.json":
        raise ValueError("Coboundary data references the wrong Schema 1 file")
    basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
    parity = structure["parity"]
    for entry in coboundary["odd_linear_map"]["entries"]:
        if entry["source"] not in basis or entry["target"] not in basis:
            raise ValueError(f"Map entry references a non-basis label: {entry}")
        if parity[entry["source"]] == parity[entry["target"]]:
            raise ValueError(f"Map entry does not reverse parity: {entry}")
    for entry in coboundary["coboundary"]["coefficients"]:
        if not {entry["X"], entry["Y"], entry["Z"]} <= basis:
            raise ValueError(f"Coboundary coefficient references a non-basis label: {entry}")


def write_coboundary_schemas(data_dir: Path, ranks: list[int]) -> list[Path]:
    outputs = []
    for rank in ranks:
        with (data_dir / f"C_{rank}_structure.json").open(encoding="utf-8") as stream:
            structure = json.load(stream)
        coboundary = build_coboundary_schema(structure)
        validate_coboundary_schema(coboundary, structure)
        output = data_dir / f"C_{rank}_coboundary.json"
        output.write_text(json.dumps(coboundary, indent=2) + "\n", encoding="utf-8")
        outputs.append(output)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for path in write_coboundary_schemas(args.data_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
