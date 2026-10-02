#!/usr/bin/env python3
"""Generate symbolic odd-map coboundary data for C(n+1)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path

if __package__:
    from .C_generators import ROOT, build_basis
else:
    from C_generators import ROOT, build_basis

DATA_DIR = ROOT / "data"


def _load_brackets(structure: dict[str, object], labels: list[str]) -> dict[tuple[str, str], dict[str, Fraction]]:
    positions = {label: index for index, label in enumerate(labels)}
    brackets: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in structure["structure_constants"]:
        pair = (entry["X"], entry["Y"])
        brackets.setdefault(pair, {})[entry["Z"]] = Fraction(entry["coeff"])

    def bracket(x: str, y: str) -> dict[str, Fraction]:
        if positions[x] <= positions[y]:
            return brackets.get((x, y), {})
        sign = -1 if structure["parity"][x] * structure["parity"][y] else 1
        return {z: -sign * coeff for z, coeff in brackets.get((y, x), {}).items()}

    return {(x, y): bracket(x, y) for x in labels for y in labels}


def build_coboundary_schema(n: int, structure_path: Path | None = None) -> dict[str, object]:
    if n < 1:
        raise ValueError("n must be at least 1")
    source_path = structure_path or DATA_DIR / f"C_{n}_structure.json"
    with source_path.open(encoding="utf-8") as stream:
        structure = json.load(stream)
    even, odd = build_basis(n)
    labels = even + odd
    if structure["algebra"]["family"] != "C" or structure["algebra"]["n"] != n:
        raise ValueError(f"{source_path} does not match C-family rank {n}")
    if structure["basis"]["even"] != even or structure["basis"]["odd"] != odd:
        raise ValueError(f"{source_path} basis does not match the expected C(n+1) basis")

    parity = structure["parity"]
    brackets = _load_brackets(structure, labels)
    opposite_targets = {
        source: (odd if parity[source] == 0 else even)
        for source in labels
    }
    f_coefficients = {
        source: [
            {"target": target, "parameter": f"phi_{target}_from_{source}"}
            for target in opposite_targets[source]
        ]
        for source in labels
    }
    coefficient_terms: list[dict[str, object]] = []

    for x_index, x in enumerate(labels):
        for y in labels[x_index:]:
            px, py = parity[x], parity[y]
            result: defaultdict[str, defaultdict[str, Fraction]] = defaultdict(
                lambda: defaultdict(Fraction)
            )

            sign_first = Fraction(-1 if px else 1)
            for target in opposite_targets[y]:
                parameter = f"phi_{target}_from_{y}"
                for z, coeff in brackets[(x, target)].items():
                    result[z][parameter] += sign_first * coeff

            sign_second = Fraction(-1 if ((px + 1) * py) % 2 == 0 else 1)
            for target in opposite_targets[x]:
                parameter = f"phi_{target}_from_{x}"
                for z, coeff in brackets[(y, target)].items():
                    result[z][parameter] += sign_second * coeff

            for middle, coeff in brackets[(x, y)].items():
                for target in opposite_targets[middle]:
                    parameter = f"phi_{target}_from_{middle}"
                    result[target][parameter] -= coeff

            for z, expression in result.items():
                terms = [
                    {"parameter": parameter, "coeff": str(coeff)}
                    for parameter, coeff in sorted(expression.items())
                    if coeff
                ]
                if terms:
                    coefficient_terms.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coefficients": terms,
                    })

    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "source_schema": source_path.name,
        "odd_linear_map": {
            "parity": 1,
            "description": "General parity-reversing linear map f: g -> g",
            "coefficients": f_coefficients,
        },
        "coboundary_definition": {
            "formula": (
                "(δf)(X,Y) = (-1)^p(X)[X,f(Y)] "
                "- (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
            ),
            "coboundary_coefficients": coefficient_terms,
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


def generate(n: int, output_dir: Path = DATA_DIR) -> Path:
    schema = build_coboundary_schema(n)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"C_{n}_coboundary.json"
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--output-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    for rank in args.n:
        print(generate(rank, args.output_dir))


if __name__ == "__main__":
    main()
