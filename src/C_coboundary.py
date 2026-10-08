"""Construct a sparse odd-map coboundary reference for C(n+1)."""

from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path

from verify_C_structure import StructureTable

LinearCombination = dict[str, Fraction]


def _add_scaled(
    target: LinearCombination, source: LinearCombination, scale: Fraction
) -> None:
    for name, coefficient in source.items():
        target[name] = target.get(name, Fraction(0)) + scale * coefficient
        if not target[name]:
            del target[name]


def _apply_map(
    linear_map: dict[str, LinearCombination], vector: LinearCombination
) -> LinearCombination:
    result: LinearCombination = {}
    for source, coefficient in vector.items():
        _add_scaled(result, linear_map.get(source, {}), coefficient)
    return result


def _bracket_map(
    table: StructureTable, x: str, vector: LinearCombination
) -> LinearCombination:
    result: LinearCombination = {}
    for y, coefficient in vector.items():
        _add_scaled(result, table.bracket(x, y), coefficient)
    return result


def coboundary_coefficients(data: dict) -> tuple[dict, list[dict]]:
    table = StructureTable(data)
    if "H_eps" not in data["basis"]["even"] or "E_eps1_del1_pp" not in data["basis"]["odd"]:
        raise ValueError("The rank-one Cartan and odd root generators are required")
    odd_map: dict[str, LinearCombination] = {
        "H_eps": {"E_eps1_del1_pp": Fraction(1)},
        "E_eps1_del1_pp": {"H_eps": Fraction(1)},
    }
    coefficients = []
    for left_index, x in enumerate(table.names):
        for y in table.names[left_index:]:
            px, py = table.parity[x], table.parity[y]
            value: LinearCombination = {}
            _add_scaled(
                value,
                _bracket_map(table, x, odd_map.get(y, {})),
                Fraction(-1 if px else 1),
            )
            second_sign = -1 if (px + 1) * py % 2 else 1
            _add_scaled(
                value,
                _bracket_map(table, y, odd_map.get(x, {})),
                Fraction(-second_sign),
            )
            _add_scaled(
                value,
                _apply_map(odd_map, table.bracket(x, y)),
                Fraction(-1),
            )
            for z, coefficient in value.items():
                coefficients.append(
                    {
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coeff": str(coefficient),
                    }
                )
    return odd_map, coefficients


def generate_coboundary(evaluated_data: dict) -> dict:
    odd_map, coefficients = coboundary_coefficients(evaluated_data)
    result = copy.deepcopy(evaluated_data)
    result["coboundary"] = {
        "input_file": f"C_{evaluated_data['algebra']['n']}_evaluated.json",
        "odd_map": [
            {"source": source, "target": target, "coeff": str(coefficient)}
            for source, image in odd_map.items()
            for target, coefficient in image.items()
        ],
        "formula": (
            "delta_f(X,Y)=(-1)^p(X)[X,f(Y)]"
            "-(-1)^((p(X)+1)p(Y))[Y,f(X)]-f([X,Y])"
        ),
        "coboundary_coefficients": coefficients,
    }
    return result


def write_coboundary(rank: int, data_dir: Path) -> Path:
    input_path = data_dir / f"C_{rank}_evaluated.json"
    with input_path.open(encoding="utf-8") as source:
        evaluated = json.load(source)
    output_path = data_dir / f"C_{rank}_coboundary.json"
    output_path.write_text(
        json.dumps(generate_coboundary(evaluated), indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for rank in (1, 2, 3):
        print(write_coboundary(rank, root / "data"))
