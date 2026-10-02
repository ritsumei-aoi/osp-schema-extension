#!/usr/bin/env python3
"""Generate coboundary coefficients for a generic odd map on C(n+1)."""

from __future__ import annotations

import json
from datetime import date
from fractions import Fraction
from pathlib import Path


def _parameter(output: str, input_name: str) -> str:
    return f"phi_{output}_from_{input_name}"


def _add(*terms: dict[tuple[str, str], Fraction]) -> dict[tuple[str, str], Fraction]:
    result: dict[tuple[str, str], Fraction] = {}
    for term in terms:
        for key, coeff in term.items():
            result[key] = result.get(key, Fraction()) + coeff
    return {key: coeff for key, coeff in result.items() if coeff}


def _scale(
    term: dict[tuple[str, str], Fraction], coeff: Fraction
) -> dict[tuple[str, str], Fraction]:
    return {key: value * coeff for key, value in term.items() if value * coeff}


def generate_coboundary_schema(gamma_path: Path, structure_path: Path) -> dict:
    gamma = json.loads(gamma_path.read_text(encoding="utf-8"))
    structure = json.loads(structure_path.read_text(encoding="utf-8"))
    if gamma["algebra"]["n"] != structure["algebra"]["n"]:
        raise ValueError("Schema 1 and Schema 2 ranks do not match")
    n = structure["algebra"]["n"]
    even = structure["basis"]["even"]
    odd = structure["basis"]["odd"]
    basis = even + odd
    parity = structure["parity"]
    indices = {name: index for index, name in enumerate(basis)}
    constants: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in structure["structure_constants"]:
        constants.setdefault((entry["X"], entry["Y"]), {})[entry["Z"]] = Fraction(
            entry["coeff"]
        )

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        if indices[x] <= indices[y]:
            return constants.get((x, y), {})
        sign = -1 if parity[x] * parity[y] else 1
        return {
            z: -sign * coeff
            for z, coeff in constants.get((y, x), {}).items()
        }

    def apply_f(inputs: dict[str, Fraction]) -> dict[tuple[str, str], Fraction]:
        result: dict[tuple[str, str], Fraction] = {}
        for input_name, input_coeff in inputs.items():
            targets = odd if parity[input_name] == 0 else even
            for output_name in targets:
                key = (output_name, _parameter(output_name, input_name))
                result[key] = result.get(key, Fraction()) + input_coeff
        return {key: coeff for key, coeff in result.items() if coeff}

    def bracket_with_f(
        x: str, input_name: str
    ) -> dict[tuple[str, str], Fraction]:
        result: dict[tuple[str, str], Fraction] = {}
        targets = odd if parity[input_name] == 0 else even
        for target in targets:
            parameter = _parameter(target, input_name)
            for output, coeff in bracket(x, target).items():
                key = (output, parameter)
                result[key] = result.get(key, Fraction()) + coeff
        return {key: coeff for key, coeff in result.items() if coeff}

    parameters = [
        {
            "label": _parameter(output, input_name),
            "output": output,
            "input": input_name,
        }
        for input_name in basis
        for output in (odd if parity[input_name] == 0 else even)
    ]
    coboundary_coefficients = []
    for i, x in enumerate(basis):
        for y in basis[i:]:
            px, py = parity[x], parity[y]
            first = _scale(
                bracket_with_f(x, y),
                Fraction(-1 if px else 1),
            )
            second_sign = -1 if ((px + 1) * py) % 2 else 1
            second = _scale(
                bracket_with_f(y, x),
                Fraction(-second_sign),
            )
            third = _scale(apply_f(bracket(x, y)), Fraction(-1))
            result = _add(first, second, third)
            for (z, parameter), coeff in result.items():
                expected_parity = (px + py + 1) % 2
                if parity[z] != expected_parity:
                    raise ValueError(
                        f"Parity mismatch in coboundary ({x}, {y}) -> {z}"
                    )
                coboundary_coefficients.append({
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "parameter": parameter,
                    "coeff": str(coeff.numerator) if coeff.denominator == 1
                    else f"{coeff.numerator}/{coeff.denominator}",
                })

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": structure["algebra"]["cartan_type"],
            "schema1_file": structure_path.name,
            "schema2_file": gamma_path.name,
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": structure["basis"]["ordering_convention"],
        },
        "linear_map": {
            "parity": 1,
            "description": "Generic odd linear map f: g -> g, reversing generator parity",
            "parameter_count": len(parameters),
            "parameters": parameters,
        },
        "coboundary": {
            "formula": (
                "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] "
                "- (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
            ),
            "coefficient_convention": (
                "Each record is one coefficient of a linear parameter phi "
                "in the basis expansion of delta f(X,Y)"
            ),
            "coboundary_coefficients": coboundary_coefficients,
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": date.today().isoformat(),
            "references": ["docs/math/C_coboundary_definition.md"],
        },
    }


def write_coboundary_schemas(
    data_dir: Path | str = "data",
    ranks: tuple[int, ...] = (1, 2, 3),
) -> None:
    data_dir = Path(data_dir)
    for n in ranks:
        result = generate_coboundary_schema(
            data_dir / f"C_{n}_gamma.json",
            data_dir / f"C_{n}_structure.json",
        )
        path = data_dir / f"C_{n}_coboundary.json"
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write_coboundary_schemas()
