#!/usr/bin/env python3
"""Generate odd-map coboundary coefficients for C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path


def _fraction_string(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def calculate_coboundary(structure):
    parity = structure["parity"]
    pbw = list(structure["generator_realization"]["realizations"])
    order = {label: index for index, label in enumerate(pbw)}
    raw = {}
    for entry in structure["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        raw.setdefault((x, y), {})[z] = Fraction(entry["coeff"])

    def bracket(x, y):
        if order[x] <= order[y]:
            return dict(raw.get((x, y), {}))
        reverse_factor = (
            -1 if (parity[x] * parity[y]) % 2 == 0 else 1
        )
        return {
            z: reverse_factor * coeff
            for z, coeff in raw.get((y, x), {}).items()
        }

    f_map = {}
    f_parameters = []
    for source in pbw:
        target_parity = 1 - parity[source]
        targets = [
            target for target in pbw if parity[target] == target_parity
        ]
        f_map[source] = {}
        for target in targets:
            parameter = f"phi_{target}_from_{source}"
            f_map[source][target] = parameter
            f_parameters.append({
                "parameter": parameter,
                "input": source,
                "output": target,
                "parity": 0,
            })

    coefficients = {}
    for i, x in enumerate(pbw):
        for y in pbw[i:]:
            expression = {}

            def add(z, parameter, value):
                if not value:
                    return
                expression.setdefault(z, {})
                expression[z][parameter] = (
                    expression[z].get(parameter, Fraction(0)) + value
                )
                if not expression[z][parameter]:
                    del expression[z][parameter]
                if not expression[z]:
                    del expression[z]

            first_sign = -1 if parity[x] else 1
            for output, parameter in f_map[y].items():
                for z, coeff in bracket(x, output).items():
                    add(z, parameter, first_sign * coeff)

            second_exponent = ((parity[x] + 1) * parity[y]) % 2
            second_sign = 1 if second_exponent else -1
            for output, parameter in f_map[x].items():
                for z, coeff in bracket(y, output).items():
                    add(z, parameter, second_sign * coeff)

            for intermediate, coeff in bracket(x, y).items():
                for output, parameter in f_map[intermediate].items():
                    add(output, parameter, -coeff)

            for z, terms in expression.items():
                if terms:
                    coefficients[(x, y, z)] = terms

    entries = []
    for (x, y, z), terms in sorted(
        coefficients.items(),
        key=lambda item: (
            order[item[0][0]],
            order[item[0][1]],
            order[item[0][2]],
        ),
    ):
        entries.append({
            "X": x,
            "Y": y,
            "Z": z,
            "coefficients": [
                {"parameter": parameter, "coeff": _fraction_string(coeff)}
                for parameter, coeff in sorted(terms.items())
            ],
        })
    return f_parameters, entries


def build_coboundary_schema(structure, generation_date=None):
    f_parameters, coefficients = calculate_coboundary(structure)
    n = structure["algebra"]["n"]
    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "source_schema1": f"C_{n}_structure.json",
        "central_elements": structure["central_elements"],
        "coboundary": {
            "linear_map": {
                "parity": 1,
                "description": "Odd linear map f: g -> g, reversing basis parity",
                "coefficients": f_parameters,
            },
            "coboundary_coefficients": coefficients,
            "nonzero_coefficient_count": len(coefficients),
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "docs/math/C_coboundary_definition.md",
                "docs/json_schema_specification.md",
                "docs/math/Cn1_definition.md",
            ],
        },
    }


def generate_files(data_dir="data", ranks=(1, 2, 3)):
    root = Path(data_dir)
    paths = []
    for n in ranks:
        source_path = root / f"C_{n}_structure.json"
        with source_path.open(encoding="utf-8") as stream:
            structure = json.load(stream)
        schema = build_coboundary_schema(structure)
        path = root / f"C_{n}_coboundary.json"
        path.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    args = parser.parse_args()
    for path in generate_files(args.data_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
