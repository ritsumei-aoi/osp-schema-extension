#!/usr/bin/env python3
"""Generate exact Schema 4 coboundary data for C(n+1) = osp(2|2n)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any


COBOUNDARY_FORMULA = (
    "(-1)^p(X) [X, f(Y)] - (-1)^((p(X)+1)p(Y)) [Y, f(X)] - f([X,Y])"
)


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def _parameter_name(output: str, input_name: str) -> str:
    return f"phi_{output}_from_{input_name}"


def _format_expression(
    terms: dict[str, Fraction], parameter_order: dict[str, int]
) -> str:
    ordered = sorted(
        ((name, coefficient) for name, coefficient in terms.items() if coefficient),
        key=lambda item: parameter_order[item[0]],
    )
    expression = ""
    for name, coefficient in ordered:
        magnitude = abs(coefficient)
        if magnitude == 1:
            term = name
        else:
            term = f"{_fraction_string(magnitude)}*{name}"
        if not expression:
            expression = f"-{term}" if coefficient < 0 else term
        else:
            expression += f" - {term}" if coefficient < 0 else f" + {term}"
    return expression


def _validate_schema1(
    n: int, schema1: dict[str, Any]
) -> tuple[list[str], dict[str, int], dict[tuple[str, str], dict[str, Fraction]]]:
    algebra = schema1.get("algebra")
    if not isinstance(algebra, dict) or algebra.get("n") != n:
        raise ValueError(f"Schema 1 algebra rank does not match n={n}")
    if schema1.get("schema_version") != "5.0":
        raise ValueError("Schema 1 schema_version must be '5.0'")

    basis = schema1.get("basis")
    parity = schema1.get("parity")
    if not isinstance(basis, dict) or not isinstance(parity, dict):
        raise ValueError("Schema 1 must contain basis and parity objects")
    even = basis.get("even")
    odd = basis.get("odd")
    if (
        not isinstance(even, list)
        or not isinstance(odd, list)
        or not all(isinstance(name, str) for name in even + odd)
    ):
        raise ValueError("Schema 1 basis.even and basis.odd must be string lists")
    names = odd + even
    if len(set(names)) != len(names) or set(parity) != set(names):
        raise ValueError("Schema 1 basis labels and parity map are inconsistent")
    if any(type(parity[name]) is not int or parity[name] not in (0, 1) for name in names):
        raise ValueError("Schema 1 parities must be integer 0 or 1")
    if any(parity[name] != 0 for name in even) or any(
        parity[name] != 1 for name in odd
    ):
        raise ValueError("Schema 1 basis lists disagree with generator parity")

    constants = schema1.get("structure_constants")
    if not isinstance(constants, list):
        raise ValueError("Schema 1 must contain a structure_constants list")
    name_set = set(names)
    brackets: dict[tuple[str, str], dict[str, Fraction]] = defaultdict(dict)
    for index, entry in enumerate(constants):
        if (
            not isinstance(entry, dict)
            or not all(key in entry for key in ("X", "Y", "Z", "coeff"))
            or any(entry[key] not in name_set for key in ("X", "Y", "Z"))
            or not isinstance(entry["coeff"], str)
            or entry.get("sign_rule") != "graded"
        ):
            raise ValueError(f"Schema 1 structure_constants[{index}] is malformed")
        try:
            coefficient = Fraction(entry["coeff"])
        except (ValueError, ZeroDivisionError) as error:
            raise ValueError(
                f"Schema 1 structure_constants[{index}] has an invalid coefficient"
            ) from error
        if not coefficient:
            raise ValueError(
                f"Schema 1 structure_constants[{index}] must be nonzero"
            )
        if parity[entry["Z"]] != (parity[entry["X"]] + parity[entry["Y"]]) % 2:
            raise ValueError(
                f"Schema 1 structure_constants[{index}] violates parity"
            )
        pair = (entry["X"], entry["Y"])
        vector = brackets[pair]
        vector[entry["Z"]] = vector.get(entry["Z"], Fraction()) + coefficient
        if not vector[entry["Z"]]:
            del vector[entry["Z"]]
    return names, parity, dict(brackets)


def build_coboundary_schema(
    n: int,
    schema1: dict[str, Any],
    generation_date: str | None = None,
) -> dict[str, Any]:
    """Build Schema 4 for the full unrestricted odd map on Schema 1."""
    if n not in (1, 2, 3):
        raise ValueError(f"Unsupported bosonic rank n={n}; expected 1, 2, or 3")
    names, parity, brackets = _validate_schema1(n, schema1)
    index = {name: position for position, name in enumerate(names)}

    map_coefficients = [
        {
            "output": output,
            "input": input_name,
            "parameter": _parameter_name(output, input_name),
        }
        for output in names
        for input_name in names
        if parity[output] != parity[input_name]
    ]
    parameter_order = {
        entry["parameter"]: position
        for position, entry in enumerate(map_coefficients)
    }
    parameter_for = {
        (entry["output"], entry["input"]): entry["parameter"]
        for entry in map_coefficients
    }

    coefficients: dict[tuple[str, str, str], dict[str, Fraction]] = defaultdict(
        lambda: defaultdict(Fraction)
    )

    def add(
        triple: tuple[str, str, str],
        parameter: str,
        coefficient: Fraction,
    ) -> None:
        if coefficient:
            coefficients[triple][parameter] += coefficient

    for x in names:
        px = parity[x]
        for y in names:
            py = parity[y]
            first_sign = Fraction(-1 if px else 1)
            second_sign = Fraction(-1 if ((px + 1) * py) % 2 == 0 else 1)

            for output in names:
                if parity[output] == py:
                    continue
                parameter = parameter_for[(output, y)]
                for z, bracket_coeff in brackets.get((x, output), {}).items():
                    add((x, y, z), parameter, first_sign * bracket_coeff)

            for output in names:
                if parity[output] == px:
                    continue
                parameter = parameter_for[(output, x)]
                for z, bracket_coeff in brackets.get((y, output), {}).items():
                    add((x, y, z), parameter, second_sign * bracket_coeff)

            for intermediate, bracket_coeff in brackets.get((x, y), {}).items():
                for output in names:
                    if parity[output] == parity[intermediate]:
                        continue
                    parameter = parameter_for[(output, intermediate)]
                    add((x, y, output), parameter, -bracket_coeff)

    coboundary_structure = []
    for (x, y, z), terms in sorted(
        coefficients.items(),
        key=lambda item: (
            index[item[0][0]],
            index[item[0][1]],
            index[item[0][2]],
        ),
    ):
        expression = _format_expression(terms, parameter_order)
        if expression:
            coboundary_structure.append(
                {
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "coeff": expression,
                    "sign_rule": "graded",
                }
            )

    expected_parameter_count = (
        2
        * len(schema1["basis"]["even"])
        * len(schema1["basis"]["odd"])
    )
    if len(map_coefficients) != expected_parameter_count:
        raise ValueError("Odd map coefficient count is inconsistent with basis")

    return {
        "schema_version": schema1["schema_version"],
        "schema_layer": 4,
        "algebra": schema1["algebra"],
        "source_schema": f"C_{n}_structure.json",
        "odd_linear_map": {
            "parity": 1,
            "coefficient_parity": 0,
            "definition": (
                "f(input) = sum_output phi_output_from_input * output, "
                "over all outputs of parity opposite to input"
            ),
            "same_parity_coefficients": "zero",
            "scaling_convention": (
                "No separate global scale; scaling is absorbed into the "
                "independent symbolic coefficients"
            ),
            "parameter_order": [
                entry["parameter"] for entry in map_coefficients
            ],
            "coefficients": map_coefficients,
        },
        "coboundary": {
            "formula": COBOUNDARY_FORMULA,
            "coefficient_format": (
                "Exact rational linear combinations of the even phi parameters; "
                "terms are ordered by odd_linear_map.parameter_order"
            ),
            "structure": coboundary_structure,
        },
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                f"C_{n}_structure.json",
                "C_coboundary_definition.md",
                "Approved unrestricted odd-map parameterization",
            ],
        },
    }


def write_coboundary_schema(
    n: int,
    output_dir: Path,
    source_dir: Path | None = None,
) -> Path:
    source_dir = source_dir or output_dir
    source_path = source_dir / f"C_{n}_structure.json"
    if not source_path.is_file():
        raise FileNotFoundError(f"Schema 1 source file not found: {source_path}")
    schema1 = json.loads(source_path.read_text(encoding="utf-8"))
    result = build_coboundary_schema(n, schema1)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"C_{n}_coboundary.json"
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate C(n+1) Schema 4 coboundary JSON files."
    )
    parser.add_argument(
        "n",
        nargs="*",
        type=int,
        choices=(1, 2, 3),
        default=None,
        help="bosonic rank(s) to generate; defaults to 1, 2, and 3",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data",
        help="directory for generated JSON files",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=None,
        help="directory containing Schema 1 source files",
    )
    args = parser.parse_args()
    for n in args.n or (1, 2, 3):
        print(write_coboundary_schema(n, args.output_dir, args.source_dir))


if __name__ == "__main__":
    main()
