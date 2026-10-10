"""Generate Schema 4 odd-map coboundary data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import sympy as sp

if __package__:
    from .C_generators import _make_basis
else:
    from C_generators import _make_basis


def _phi_label(output: str, input_label: str) -> str:
    return f"phi__{output}__from__{input_label}"


def _coefficient_map(structure_data: dict) -> dict[tuple[str, str], dict[str, sp.Expr]]:
    brackets: dict[tuple[str, str], dict[str, sp.Expr]] = {}
    for entry in structure_data["structure_constants"]:
        pair = (entry["X"], entry["Y"])
        output = entry["Z"]
        bracket = brackets.setdefault(pair, {})
        if output in bracket:
            raise ValueError(f"Duplicate Schema 1 structure constant for {pair}, {output}")
        bracket[output] = sp.Rational(entry["coeff"])
    return brackets


def _add_term(
    target: dict[str, sp.Expr], output: str, coefficient: sp.Expr
) -> None:
    value = sp.expand(target.get(output, sp.Integer(0)) + coefficient)
    if value:
        target[output] = value
    else:
        target.pop(output, None)


def _coboundary_pair(
    left: str,
    right: str,
    parity: dict[str, int],
    map_parameters: dict[str, list[tuple[str, sp.Symbol]]],
    brackets: dict[tuple[str, str], dict[str, sp.Expr]],
) -> dict[str, sp.Expr]:
    result: dict[str, sp.Expr] = {}
    left_parity = parity[left]
    right_parity = parity[right]

    first_sign = -1 if left_parity else 1
    for image, parameter in map_parameters[right]:
        for output, coefficient in brackets.get((left, image), {}).items():
            _add_term(result, output, first_sign * coefficient * parameter)

    second_factor = -(
        -1
        if ((left_parity + 1) * right_parity) % 2
        else 1
    )
    for image, parameter in map_parameters[left]:
        for output, coefficient in brackets.get((right, image), {}).items():
            _add_term(result, output, second_factor * coefficient * parameter)

    for intermediate, coefficient in brackets.get((left, right), {}).items():
        for output, parameter in map_parameters[intermediate]:
            _add_term(result, output, -coefficient * parameter)

    return result


def build_coboundary_schema(
    n: int,
    structure_data: dict,
    generation_date: str | None = None,
) -> dict:
    if n < 1:
        raise ValueError("n must be a positive integer")
    if structure_data["algebra"]["family"] != "C" or structure_data["algebra"]["n"] != n:
        raise ValueError("Schema 1 family/rank does not match requested C(n+1) rank")

    ordered_labels, parity, _ = _make_basis(n)
    if structure_data["parity"] != parity:
        raise ValueError("Schema 1 parity map does not match generated C(n+1) parity")
    if set(structure_data["basis"]["even"] + structure_data["basis"]["odd"]) != set(
        ordered_labels
    ):
        raise ValueError("Schema 1 basis does not match the generated C(n+1) basis")

    map_parameters: dict[str, list[tuple[str, sp.Symbol]]] = {}
    parameter_records = []
    for input_label in ordered_labels:
        parameters = []
        for output_label in ordered_labels:
            if parity[input_label] == parity[output_label]:
                continue
            symbol_name = _phi_label(output_label, input_label)
            symbol = sp.Symbol(symbol_name)
            parameters.append((output_label, symbol))
            parameter_records.append(
                {
                    "input": input_label,
                    "output": output_label,
                    "symbol": symbol_name,
                    "input_parity": parity[input_label],
                    "output_parity": parity[output_label],
                }
            )
        map_parameters[input_label] = parameters

    brackets = _coefficient_map(structure_data)
    coboundary_coefficients = []
    for left in ordered_labels:
        for right in ordered_labels:
            coefficients = _coboundary_pair(
                left, right, parity, map_parameters, brackets
            )
            expected_parity = (parity[left] + parity[right] + 1) % 2
            for output, coefficient in coefficients.items():
                if parity[output] != expected_parity:
                    raise ValueError(
                        f"Coboundary output parity mismatch for "
                        f"({left}, {right}, {output})"
                    )
                coboundary_coefficients.append(
                    {
                        "X": left,
                        "Y": right,
                        "Z": output,
                        "coeff": str(coefficient),
                        "sign_rule": "graded",
                    }
                )

    coefficients_by_pair: dict[tuple[str, str], dict[str, sp.Expr]] = {}
    for entry in coboundary_coefficients:
        coefficients_by_pair.setdefault((entry["X"], entry["Y"]), {})[
            entry["Z"]
        ] = sp.sympify(entry["coeff"])
    for left in ordered_labels:
        for right in ordered_labels:
            factor = 1 if parity[left] * parity[right] % 2 else -1
            expected = {
                output: sp.expand(factor * coefficient)
                for output, coefficient in coefficients_by_pair.get(
                    (right, left), {}
                ).items()
                if factor * coefficient
            }
            if coefficients_by_pair.get((left, right), {}) != expected:
                raise ValueError(
                    f"Coboundary violates graded skew-symmetry for ({left}, {right})"
                )

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "source_structure_file": f"C_{n}_structure.json",
        "odd_linear_map": {
            "definition": "f(Z_j) = sum_{i: parity(Z_i) != parity(Z_j)} phi_ij Z_i",
            "coefficient_parity": 0,
            "global_scale": "absorbed_into_phi_ij",
            "parameters": parameter_records,
        },
        "coboundary_coefficients": coboundary_coefficients,
        "metadata": {
            "generated_by": "src/C_coboundary_generator.py",
            "generation_date": generation_date or date.today().isoformat(),
            "references": [
                "docs/math/C_coboundary_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def write_coboundary_schemas(
    data_dir: Path, ranks: tuple[int, ...] = (1, 2, 3)
) -> list[Path]:
    written = []
    for n in ranks:
        structure_data = json.loads(
            (data_dir / f"C_{n}_structure.json").read_text(encoding="utf-8")
        )
        coboundary = build_coboundary_schema(n, structure_data)
        path = data_dir / f"C_{n}_coboundary.json"
        path.write_text(
            json.dumps(coboundary, indent=2, ensure_ascii=False) + "\n",
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
    for path in write_coboundary_schemas(arguments.data_dir, tuple(arguments.ranks)):
        print(path)


if __name__ == "__main__":
    main()
