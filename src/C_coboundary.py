"""Generate symbolic coboundary coefficients for odd maps on C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path


Expression = dict[str, dict[str, Fraction]]


def _add_term(
    expression: Expression, output: str, parameter: str, coeff: Fraction
) -> None:
    terms = expression.setdefault(output, {})
    terms[parameter] = terms.get(parameter, Fraction(0)) + coeff
    if not terms[parameter]:
        del terms[parameter]
    if not terms:
        del expression[output]


def _format_coefficient(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def generate_coboundary_schema(n: int, data_dir: Path = Path("data")) -> dict:
    if n < 1:
        raise ValueError("n must be a positive integer")
    path = data_dir / f"C_{n}_structure.json"
    structure = json.loads(path.read_text(encoding="utf-8"))
    even = structure["basis"]["even"]
    odd = structure["basis"]["odd"]
    labels = odd + even
    parity = structure["parity"]

    brackets: dict[tuple[str, str], dict[str, Fraction]] = {}
    for item in structure["structure_constants"]:
        x, y, z = item["X"], item["Y"], item["Z"]
        coeff = Fraction(item["coeff"])
        brackets.setdefault((x, y), {})[z] = coeff
        if x != y:
            sign = -1 if parity[x] * parity[y] % 2 == 0 else 1
            reverse = brackets.setdefault((y, x), {})
            reverse[z] = reverse.get(z, Fraction(0)) + sign * coeff
            if not reverse[z]:
                del reverse[z]

    f_parameters: dict[str, str] = {}
    f_targets: dict[str, list[tuple[str, str]]] = {}
    for source in labels:
        target_labels = odd if parity[source] == 0 else even
        f_targets[source] = []
        for target in target_labels:
            parameter = f"phi_{target}__from__{source}"
            f_parameters[parameter] = target
            f_targets[source].append((target, parameter))

    coboundary_records = []
    for x, y in combinations_with_replacement(labels, 2):
        result: Expression = {}

        first_sign = -1 if parity[x] else 1
        for target, parameter in f_targets[y]:
            for output, coeff in brackets.get((x, target), {}).items():
                _add_term(result, output, parameter, first_sign * coeff)

        exponent = ((parity[x] + 1) * parity[y]) % 2
        second_sign = 1 if exponent else -1
        for target, parameter in f_targets[x]:
            for output, coeff in brackets.get((y, target), {}).items():
                _add_term(result, output, parameter, second_sign * coeff)

        for intermediate, bracket_coeff in brackets.get((x, y), {}).items():
            for target, parameter in f_targets[intermediate]:
                _add_term(result, target, parameter, -bracket_coeff)

        for output in labels:
            terms = result.get(output)
            if not terms:
                continue
            coboundary_records.append(
                {
                    "X": x,
                    "Y": y,
                    "Z": output,
                    "terms": [
                        {"phi_parameter": parameter, "coeff": _format_coefficient(coeff)}
                        for parameter, coeff in sorted(terms.items())
                    ],
                    "sign_rule": "graded",
                }
            )

    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "basis": structure["basis"],
        "parity": structure["parity"],
        "odd_linear_map": {
            "parity": 1,
            "definition": "f(Z_source) = sum_target phi_target_from_source * Z_target",
            "coefficient_parity": 0,
            "parameters": [
                {
                    "name": parameter,
                    "source": source,
                    "target": target,
                }
                for source in labels
                for target, parameter in f_targets[source]
            ],
        },
        "coboundary_coefficients": coboundary_records,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": structure["metadata"]["generation_date"],
            "references": [
                "docs/math/C_coboundary_definition.md",
                f"data/C_{n}_structure.json",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    for n in args.ranks:
        schema = generate_coboundary_schema(n, args.data_dir)
        output = args.data_dir / f"C_{n}_coboundary.json"
        output.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
