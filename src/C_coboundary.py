#!/usr/bin/env python3
"""Generate symbolic coboundary structures for general odd maps on C(n+1)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any

if __package__:
    from .C_generators import build_basis
else:
    from C_generators import build_basis

BracketKey = tuple[str, str]
OutputKey = tuple[str, str, str]
LinearExpression = dict[str, Fraction]


def _parameter_symbol(output_label: str, input_label: str) -> str:
    return f"phi_{output_label}__from__{input_label}"


def _add_scaled(
    target: LinearExpression,
    parameter: str,
    coefficient: Fraction,
) -> None:
    total = target.get(parameter, Fraction()) + coefficient
    if total:
        target[parameter] = total
    else:
        target.pop(parameter, None)


def _format_expression(
    terms: LinearExpression,
    parameter_order: list[str],
) -> str:
    formatted: list[str] = []
    for parameter in parameter_order:
        coefficient = terms.get(parameter, Fraction())
        if not coefficient:
            continue
        magnitude = abs(coefficient)
        body = parameter if magnitude == 1 else f"{magnitude}*{parameter}"
        if not formatted:
            formatted.append(body if coefficient > 0 else f"-{body}")
        else:
            formatted.append(f" + {body}" if coefficient > 0 else f" - {body}")
    return "".join(formatted)


def _load_schema1(
    schema1: dict[str, Any],
) -> tuple[int, list[str], dict[str, int], dict[BracketKey, dict[str, Fraction]]]:
    try:
        algebra = schema1["algebra"]
        n = algebra["n"]
        if algebra["family"] != "C" or algebra["m"] != 1:
            raise ValueError("Schema 1 input must describe C(n+1) with m=1")
        if schema1["schema_version"] != "5.0":
            raise ValueError("Schema 1 input must use schema_version 5.0")
        basis = build_basis(n)
        if schema1["basis"]["even"] != basis.even:
            raise ValueError("Schema 1 even basis does not match C(n+1)")
        if schema1["basis"]["odd"] != basis.odd:
            raise ValueError("Schema 1 odd basis does not match C(n+1)")
        parity = schema1["parity"]
    except (KeyError, TypeError) as error:
        raise ValueError(f"Malformed Schema 1 input: {error}") from error

    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("Schema rank n must be a positive integer")
    if parity != basis.parity:
        raise ValueError("Schema 1 parity map does not match the C(n+1) basis")

    labels = basis.pbw_order
    label_set = set(labels)
    records = schema1.get("structure_constants")
    if not isinstance(records, list):
        raise ValueError("Schema 1 structure_constants must be an array")
    brackets: dict[BracketKey, dict[str, Fraction]] = defaultdict(dict)
    for record in records:
        try:
            x, y, z = record["X"], record["Y"], record["Z"]
            coefficient = Fraction(record["coeff"])
            if record["sign_rule"] != "graded":
                raise ValueError("Structure-constant record must use graded signs")
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            raise ValueError(f"Malformed Schema 1 structure record: {record}") from error
        if x not in label_set or y not in label_set or z not in label_set:
            raise ValueError(f"Schema 1 structure record uses an unknown label: {record}")
        if not coefficient:
            raise ValueError(f"Schema 1 structure record must be nonzero: {record}")
        if z in brackets[(x, y)]:
            raise ValueError(f"Duplicate Schema 1 structure record: {record}")
        brackets[(x, y)][z] = coefficient

    return n, labels, parity, brackets


def build_odd_linear_map(
    labels: list[str],
    parity: dict[str, int],
) -> tuple[list[dict[str, str]], dict[str, list[tuple[str, str]]]]:
    """Return all independent coefficients of a general odd endomorphism."""
    coefficients: list[dict[str, str]] = []
    outputs_by_input: dict[str, list[tuple[str, str]]] = {}
    for input_label in labels:
        outputs: list[tuple[str, str]] = []
        for output_label in labels:
            if parity[output_label] == parity[input_label]:
                continue
            symbol = _parameter_symbol(output_label, input_label)
            coefficients.append({
                "input": input_label,
                "output": output_label,
                "symbol": symbol,
            })
            outputs.append((output_label, symbol))
        outputs_by_input[input_label] = outputs
    return coefficients, outputs_by_input


def compute_coboundary_structure(
    labels: list[str],
    parity: dict[str, int],
    brackets: dict[BracketKey, dict[str, Fraction]],
    outputs_by_input: dict[str, list[tuple[str, str]]],
) -> list[dict[str, str]]:
    """Apply the approved odd-map coboundary formula using exact arithmetic."""
    expressions: dict[OutputKey, LinearExpression] = defaultdict(dict)

    for x in labels:
        px = parity[x]
        for y in labels:
            py = parity[y]

            first_scale = Fraction(-1 if px else 1)
            second_exponent = (px + 1) * py
            second_scale = Fraction(-1 if second_exponent % 2 == 0 else 1)

            for intermediate, parameter in outputs_by_input[y]:
                for z, coefficient in brackets.get((x, intermediate), {}).items():
                    _add_scaled(
                        expressions[(x, y, z)],
                        parameter,
                        first_scale * coefficient,
                    )

            for intermediate, parameter in outputs_by_input[x]:
                for z, coefficient in brackets.get((y, intermediate), {}).items():
                    _add_scaled(
                        expressions[(x, y, z)],
                        parameter,
                        second_scale * coefficient,
                    )

            for intermediate, bracket_coefficient in brackets.get((x, y), {}).items():
                for z, parameter in outputs_by_input[intermediate]:
                    _add_scaled(
                        expressions[(x, y, z)],
                        parameter,
                        -bracket_coefficient,
                    )

    parameter_order = [
        symbol
        for input_label in labels
        for _, symbol in outputs_by_input[input_label]
    ]
    records: list[dict[str, str]] = []
    for x in labels:
        for y in labels:
            for z in labels:
                coefficient = _format_expression(
                    expressions.get((x, y, z), {}),
                    parameter_order,
                )
                if coefficient:
                    records.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coeff": coefficient,
                        "sign_rule": "graded",
                    })
    return records


def generate_coboundary_schema(
    schema1: dict[str, Any],
    generation_date: str | None = None,
) -> dict[str, Any]:
    """Generate Schema 4 for the general unscaled odd map."""
    n, labels, parity, brackets = _load_schema1(schema1)
    coefficients, outputs_by_input = build_odd_linear_map(labels, parity)
    coboundary_structure = compute_coboundary_structure(
        labels,
        parity,
        brackets,
        outputs_by_input,
    )
    return {
        "schema_version": schema1["schema_version"],
        "algebra": schema1["algebra"],
        "odd_linear_map": {
            "parity": 1,
            "formula": (
                "f(Z_j) = sum_{i: parity(Z_i)=parity(Z_j)+1 mod 2} "
                "phi_{i,j} * Z_i"
            ),
            "scaling_convention": (
                "Independent unconstrained formal scalar coefficients; "
                "no overall normalization."
            ),
            "coefficient_count": len(coefficients),
            "coefficients": coefficients,
        },
        "coboundary_formula": (
            "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] "
            "- (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
        ),
        "coboundary_structure": coboundary_structure,
        "metadata": {
            "generated_by": "C_coboundary.py",
            "schema1_file": f"C_{n}_structure.json",
            "generation_date": generation_date or date.today().isoformat(),
        },
    }


def write_coboundary_schema(
    schema1: dict[str, Any],
    output_dir: str | Path,
    generation_date: str | None = None,
) -> Path:
    """Write `C_{n}_coboundary.json`."""
    n = schema1["algebra"]["n"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    destination = output_path / f"C_{n}_coboundary.json"
    serialized = json.dumps(
        generate_coboundary_schema(schema1, generation_date),
        ensure_ascii=False,
        indent=2,
    )
    destination.write_text(serialized + "\n", encoding="utf-8")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate C(n+1) coboundary data for a general odd map."
    )
    parser.add_argument(
        "--ranks",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Bosonic ranks to generate (default: 1 2 3).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory containing C_n_structure.json inputs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
        help="Directory for C_n_coboundary.json outputs.",
    )
    args = parser.parse_args(argv)

    for n in args.ranks:
        source = args.data_dir / f"C_{n}_structure.json"
        try:
            schema1 = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            parser.error(f"could not load Schema 1 file {source}: {error}")
        destination = write_coboundary_schema(schema1, args.output_dir)
        print(f"Wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
