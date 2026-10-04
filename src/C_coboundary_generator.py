#!/usr/bin/env python3
"""Generate generic odd-map coboundaries for C(n+1) Schema 1 data."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _parameter(output: str, input_label: str) -> str:
    return f"phi_{output}_from_{input_label}"


def build_coboundary_schema(structure: dict) -> dict:
    algebra = structure["algebra"]
    basis = structure["basis"]["odd"] + structure["basis"]["even"]
    parity = structure["parity"]
    positions = {label: index for index, label in enumerate(basis)}
    canonical: dict[tuple[str, str], dict[str, Fraction]] = {}
    for record in structure["structure_constants"]:
        pair = (record["X"], record["Y"])
        canonical.setdefault(pair, {})[record["Z"]] = Fraction(record["coeff"])

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        if positions[x] <= positions[y]:
            return canonical.get((x, y), {})
        sign = -1 if parity[x] * parity[y] == 0 else 1
        return {
            output: sign * coefficient
            for output, coefficient in canonical.get((y, x), {}).items()
        }

    f_map = [
        {
            "input": input_label,
            "output": output_label,
            "parameter": _parameter(output_label, input_label),
        }
        for input_label in basis
        for output_label in basis
        if parity[input_label] != parity[output_label]
    ]
    map_parameter = {
        (item["output"], item["input"]): item["parameter"] for item in f_map
    }

    def odd_f_terms(input_label: str) -> list[tuple[str, str]]:
        return [
            (output, map_parameter[(output, input_label)])
            for output in basis
            if parity[output] != parity[input_label]
        ]

    records = []
    for left_index, x in enumerate(basis):
        for y in basis[left_index:]:
            result: dict[tuple[str, str], Fraction] = {}

            def add(output: str, parameter: str, coefficient: Fraction) -> None:
                key = (output, parameter)
                value = result.get(key, Fraction(0)) + coefficient
                if value:
                    result[key] = value
                else:
                    result.pop(key, None)

            # First term: (-1)^p(X) [X, f(Y)].
            first_sign = Fraction(-1 if parity[x] else 1)
            for f_output, parameter in odd_f_terms(y):
                for output, coefficient in bracket(x, f_output).items():
                    add(output, parameter, first_sign * coefficient)

            # Second term: -(-1)^((p(X)+1)p(Y)) [Y, f(X)].
            second_exponent = ((parity[x] + 1) * parity[y]) % 2
            second_sign = Fraction(-1 if second_exponent == 0 else 1)
            for f_output, parameter in odd_f_terms(x):
                for output, coefficient in bracket(y, f_output).items():
                    add(output, parameter, second_sign * coefficient)

            # Third term: -f([X,Y]).
            for intermediate, bracket_coefficient in bracket(x, y).items():
                for output, parameter in odd_f_terms(intermediate):
                    add(output, parameter, -bracket_coefficient)

            by_output: dict[str, list[dict[str, str]]] = {}
            for (output, parameter), coefficient in sorted(
                result.items(),
                key=lambda item: (
                    positions[item[0][0]],
                    item[0][1],
                ),
            ):
                by_output.setdefault(output, []).append(
                    {"parameter": parameter, "coeff": _fraction_text(coefficient)}
                )
            for output, coefficients in by_output.items():
                records.append(
                    {
                        "X": x,
                        "Y": y,
                        "Z": output,
                        "coefficients": coefficients,
                        "sign_rule": "graded",
                    }
                )

    n = algebra["n"]
    return {
        "schema_version": "5.0",
        "algebra": algebra,
        "source_schema1": f"C_{n}_structure.json",
        "basis": structure["basis"],
        "parity": parity,
        "linear_map_f": {
            "parity": 1,
            "definition": "f(Z_j) = sum_i phi_{i,j} Z_i with p(Z_i) = p(Z_j) + 1",
            "parameters": f_map,
        },
        "coboundary_convention": "delta_f(X,Y) = (-1)^p(X)[X,f(Y)] - (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])",
        "coboundary_coefficients": records,
        "metadata": {
            "generated_by": "src/C_coboundary_generator.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_coboundary_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    for n in args.n:
        source = args.data_dir / f"C_{n}_structure.json"
        structure = json.loads(source.read_text(encoding="utf-8"))
        result = build_coboundary_schema(structure)
        output = args.data_dir / f"C_{n}_coboundary.json"
        output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
