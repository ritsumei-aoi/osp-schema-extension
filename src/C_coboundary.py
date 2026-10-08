#!/usr/bin/env python3
"""Generate symbolic odd-map coboundaries for C(n+1) structure data."""

from __future__ import annotations

import argparse
import json
from datetime import date
from fractions import Fraction
from pathlib import Path


def _fraction_string(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _parameter(target: str, source: str) -> str:
    return f"phi_{target}_from_{source}"


def _bracket_table(structure: dict) -> tuple[list[str], dict[str, int], dict]:
    basis = structure["basis"]
    labels = basis["even"] + basis["odd"]
    parity = structure["parity"]
    entries: dict[tuple[str, str], dict[str, Fraction]] = {}
    for row in structure["structure_constants"]:
        entries.setdefault((row["X"], row["Y"]), {})[row["Z"]] = Fraction(row["coeff"])
    return labels, parity, entries


def _bracket(
    x: str,
    y: str,
    parity: dict[str, int],
    entries: dict[tuple[str, str], dict[str, Fraction]],
) -> dict[str, Fraction]:
    direct = entries.get((x, y))
    if direct is not None:
        return direct
    reverse = entries.get((y, x), {})
    sign = -1 if parity[x] and parity[y] else 1
    return {label: -sign * coeff for label, coeff in reverse.items()}


def _add_scaled(target: dict[str, dict[str, Fraction]],
                source: dict[str, Fraction],
                parameter: str,
                scale: Fraction) -> None:
    for label, coeff in source.items():
        parameters = target.setdefault(label, {})
        parameters[parameter] = parameters.get(parameter, Fraction()) + scale * coeff
        if not parameters[parameter]:
            del parameters[parameter]
        if not parameters:
            del target[label]


def _coboundary_pair(
    x: str,
    y: str,
    labels: list[str],
    parity: dict[str, int],
    entries: dict[tuple[str, str], dict[str, Fraction]],
) -> dict[str, dict[str, Fraction]]:
    result: dict[str, dict[str, Fraction]] = {}
    p_x, p_y = parity[x], parity[y]

    for target in labels:
        if parity[target] != 1 - p_y:
            continue
        parameter = _parameter(target, y)
        scale = Fraction(-1 if p_x else 1)
        _add_scaled(result, _bracket(x, target, parity, entries), parameter, scale)

    for target in labels:
        if parity[target] != 1 - p_x:
            continue
        parameter = _parameter(target, x)
        exponent = ((p_x + 1) * p_y) % 2
        scale = Fraction(-1 if exponent == 0 else 1)
        _add_scaled(result, _bracket(y, target, parity, entries), parameter, scale)

    for middle, bracket_coeff in _bracket(x, y, parity, entries).items():
        for target in labels:
            if parity[target] != 1 - parity[middle]:
                continue
            parameter = _parameter(target, middle)
            _add_scaled(result, {target: Fraction(1)}, parameter, -bracket_coeff)
    return result


def build_coboundary_schema(structure: dict,
                            generation_date: str | None = None) -> dict:
    labels, parity, entries = _bracket_table(structure)
    even_labels = structure["basis"]["even"]
    odd_labels = structure["basis"]["odd"]
    parameters = [
        {
            "source": source,
            "target": target,
            "label": _parameter(target, source),
        }
        for source in labels
        for target in (odd_labels if parity[source] == 0 else even_labels)
    ]
    rows = []
    for left_index, x in enumerate(labels):
        for y in labels[left_index:]:
            for z, terms in _coboundary_pair(x, y, labels, parity, entries).items():
                if terms:
                    rows.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "terms": [
                            {"parameter": parameter, "coeff": _fraction_string(coeff)}
                            for parameter, coeff in sorted(terms.items())
                        ],
                    })

    n = structure["algebra"]["n"]
    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "basis": structure["basis"],
        "parity": parity,
        "odd_linear_map": {
            "parity": 1,
            "definition": "f(source) = sum_target phi_target_from_source * target",
            "parameters": parameters,
        },
        "coboundary": {
            "formula": (
                "delta_f(X,Y) = (-1)^pX [X,f(Y)] "
                "- (-1)^((pX+1)pY) [Y,f(X)] - f([X,Y])"
            ),
            "coefficients": rows,
        },
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": generation_date or date.today().isoformat(),
            "source_structure": f"C_{n}_structure.json",
            "references": ["docs/math/C_coboundary_definition.md"],
        },
    }


def generate_files(data_dir: Path, ranks: tuple[int, ...] = (1, 2, 3)) -> list[Path]:
    outputs = []
    for n in ranks:
        source = data_dir / f"C_{n}_structure.json"
        structure = json.loads(source.read_text(encoding="utf-8"))
        result = build_coboundary_schema(structure)
        path = data_dir / f"C_{n}_coboundary.json"
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        outputs.append(path)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=(1, 2, 3))
    args = parser.parse_args()
    for path in generate_files(args.data_dir, tuple(args.ranks)):
        print(path)


if __name__ == "__main__":
    main()
