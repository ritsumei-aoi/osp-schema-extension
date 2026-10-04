#!/usr/bin/env python3
"""Compute symbolic coboundaries for odd linear maps on C(n+1)."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def _bracket_table(
    structure_schema: dict[str, object], basis: list[str]
) -> dict[tuple[str, str], dict[str, Fraction]]:
    index = {label: position for position, label in enumerate(basis)}
    table: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in structure_schema["structure_constants"]:
        key = entry["X"], entry["Y"]
        table.setdefault(key, {})[entry["Z"]] = Fraction(entry["coeff"])
    return table


def _bracket(
    left: str,
    right: str,
    index: dict[str, int],
    parity: dict[str, int],
    table: dict[tuple[str, str], dict[str, Fraction]],
) -> dict[str, Fraction]:
    if index[left] <= index[right]:
        return table.get((left, right), {})
    sign = -1 if (parity[left] * parity[right]) % 2 == 0 else 1
    return {
        output: sign * coefficient
        for output, coefficient in table.get((right, left), {}).items()
    }


def _add_term(
    coefficients: dict[tuple[str, str], Fraction],
    output: str,
    phi: str,
    coefficient: Fraction,
) -> None:
    key = output, phi
    coefficients[key] = coefficients.get(key, Fraction(0)) + coefficient
    if not coefficients[key]:
        del coefficients[key]


def _coboundary(
    left: str,
    right: str,
    basis: list[str],
    parity: dict[str, int],
    index: dict[str, int],
    brackets: dict[tuple[str, str], dict[str, Fraction]],
) -> dict[tuple[str, str], Fraction]:
    left_parity, right_parity = parity[left], parity[right]
    coefficients: dict[tuple[str, str], Fraction] = {}

    for target in basis:
        if parity[target] == right_parity:
            continue
        phi = f"phi_{target}_{right}"
        sign = Fraction(-1) if left_parity else Fraction(1)
        for output, coefficient in _bracket(left, target, index, parity, brackets).items():
            _add_term(coefficients, output, phi, sign * coefficient)

    second_sign = -1 if ((left_parity + 1) * right_parity) % 2 == 0 else 1
    for target in basis:
        if parity[target] == left_parity:
            continue
        phi = f"phi_{target}_{left}"
        for output, coefficient in _bracket(right, target, index, parity, brackets).items():
            _add_term(coefficients, output, phi, Fraction(second_sign) * coefficient)

    for intermediate, bracket_coefficient in _bracket(
        left, right, index, parity, brackets
    ).items():
        for target in basis:
            if parity[target] == parity[intermediate]:
                continue
            phi = f"phi_{target}_{intermediate}"
            _add_term(
                coefficients,
                target,
                phi,
                -bracket_coefficient,
            )
    return coefficients


def build_coboundary_schema(
    rank: int, structure_schema: dict[str, object]
) -> dict[str, object]:
    if rank < 1:
        raise ValueError("The bosonic rank n must be at least 1")
    if structure_schema["algebra"]["family"] != "C" or structure_schema["algebra"]["n"] != rank:
        raise ValueError(f"Structure schema does not match C rank {rank}")

    basis = list(structure_schema["generator_realization"]["realizations"])
    parity = structure_schema["parity"]
    index = {label: position for position, label in enumerate(basis)}
    brackets = _bracket_table(structure_schema, basis)
    f_map = [
        {
            "source": source,
            "target": target,
            "coefficient": f"phi_{target}_{source}",
        }
        for source in basis
        for target in basis
        if parity[source] != parity[target]
    ]

    coboundary_entries = []
    for left_index, left in enumerate(basis):
        for right in basis[left_index:]:
            terms = _coboundary(left, right, basis, parity, index, brackets)
            grouped: dict[str, list[dict[str, str]]] = {}
            for (output, phi), coefficient in sorted(terms.items()):
                grouped.setdefault(output, []).append(
                    {"phi": phi, "coeff": str(coefficient)}
                )
            for output, phi_terms in grouped.items():
                coboundary_entries.append(
                    {
                        "X": left,
                        "Y": right,
                        "Z": output,
                        "terms": phi_terms,
                        "sign_rule": "graded",
                    }
                )

    return {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": structure_schema["algebra"],
        "source_schema": f"C_{rank}_structure.json",
        "f": {
            "parity": 1,
            "mapping_convention": "f(source) = sum_target phi_target_source * target",
            "coefficient_parity": 0,
            "coefficient_count": len(f_map),
            "map": f_map,
        },
        "coboundary": {
            "formula": (
                "(δf)(X,Y)=(-1)^pX[X,f(Y)]"
                "-(-1)^((pX+1)pY)[Y,f(X)]-f([X,Y])"
            ),
            "entries": coboundary_entries,
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_coboundary_definition.md",
                "docs/json_schema_specification.md",
            ],
        },
    }


def write_coboundary(rank: int, data_dir: Path = DATA_DIR) -> Path:
    structure_path = data_dir / f"C_{rank}_structure.json"
    with structure_path.open(encoding="utf-8") as stream:
        structure_schema = json.load(stream)
    coboundary = build_coboundary_schema(rank, structure_schema)
    output_path = data_dir / f"C_{rank}_coboundary.json"
    output_path.write_text(
        json.dumps(coboundary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    arguments = parser.parse_args()
    for rank in arguments.ranks:
        print(write_coboundary(rank, arguments.data_dir))


if __name__ == "__main__":
    main()
