"""Generate symbolic coboundary coefficients for C(n+1)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Iterable

Vector = dict[str, Fraction]
LinearCombination = dict[tuple[str, str], Fraction]


def _pbw_order(n: int) -> list[str]:
    negative_odd = [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("mp", "mm")
    ]
    negative_even = [
        f"E_del{i}_del{j}_{suffix}"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
        for suffix in ("mp", "mm")
    ] + [f"E_2del{k}_m" for k in range(1, n + 1)]
    cartan = [f"H_{k}" for k in range(1, n + 2)]
    positive_even = [
        f"E_del{i}_del{j}_{suffix}"
        for i in range(1, n + 1)
        for j in range(i + 1, n + 1)
        for suffix in ("pm", "pp")
    ] + [f"E_2del{k}_p" for k in range(1, n + 1)]
    positive_odd = [
        f"E_eps1_del{k}_{suffix}"
        for k in range(1, n + 1)
        for suffix in ("pm", "pp")
    ]
    return negative_odd + negative_even + cartan + positive_even + positive_odd


def _make_linear_map(
    order: list[str],
    parity: dict[str, int],
) -> dict[str, list[tuple[str, str]]]:
    return {
        input_label: [
            (
                f"phi_{output_label}_{input_label}",
                output_label,
            )
            for output_label in order
            if parity[output_label] != parity[input_label]
        ]
        for input_label in order
    }


def _add_scaled(
    target: LinearCombination,
    source: LinearCombination,
    scale: Fraction,
) -> None:
    for key, coefficient in source.items():
        target[key] = target.get(key, Fraction()) + scale * coefficient


def _structure_bracket(
    left: str,
    right: str,
    parity: dict[str, int],
    order_index: dict[str, int],
    bracket_table: dict[tuple[str, str], Vector],
) -> Vector:
    if order_index[left] <= order_index[right]:
        return bracket_table.get((left, right), {})
    canonical = bracket_table.get((right, left), {})
    sign = -1 if parity[left] * parity[right] % 2 else 1
    return {label: -sign * value for label, value in canonical.items()}


def _compute_pair_coboundary(
    x: str,
    y: str,
    parity: dict[str, int],
    order_index: dict[str, int],
    bracket_table: dict[tuple[str, str], Vector],
    linear_map: dict[str, list[tuple[str, str]]],
) -> LinearCombination:
    px, py = parity[x], parity[y]
    result: LinearCombination = {}

    for phi, image in linear_map[y]:
        vector = _structure_bracket(x, image, parity, order_index, bracket_table)
        _add_scaled(
            result,
            {(phi, label): coefficient for label, coefficient in vector.items()},
            Fraction(-1 if px else 1),
        )

    second_sign = -1 if ((px + 1) * py) % 2 else 1
    for phi, image in linear_map[x]:
        vector = _structure_bracket(y, image, parity, order_index, bracket_table)
        _add_scaled(
            result,
            {(phi, label): coefficient for label, coefficient in vector.items()},
            Fraction(-second_sign),
        )

    bracket_xy = _structure_bracket(x, y, parity, order_index, bracket_table)
    for label, bracket_coeff in bracket_xy.items():
        for phi, image in linear_map[label]:
            result[(phi, image)] = (
                result.get((phi, image), Fraction()) - bracket_coeff
            )

    return {key: value for key, value in result.items() if value}


def build_coboundary(structure: dict) -> dict:
    n = structure["algebra"]["n"]
    order = _pbw_order(n)
    parity = structure["parity"]
    if (
        structure["algebra"]["family"] != "C"
        or structure["algebra"]["m"] != 1
        or set(order) != set(parity)
        or structure["basis"]["even"]
        != [label for label in order if parity.get(label) == 0]
        or structure["basis"]["odd"]
        != [label for label in order if parity.get(label) == 1]
    ):
        raise ValueError("Schema 1 does not contain the expected C(n+1) basis")

    order_index = {label: index for index, label in enumerate(order)}
    bracket_table: defaultdict[tuple[str, str], dict[str, Fraction]] = defaultdict(dict)
    for term in structure["structure_constants"]:
        bracket_table[(term["X"], term["Y"])][term["Z"]] = Fraction(term["coeff"])
    linear_map = _make_linear_map(order, parity)

    coefficients = []
    for i, x in enumerate(order):
        for y in order[i:]:
            pair_terms = _compute_pair_coboundary(
                x, y, parity, order_index, bracket_table, linear_map
            )
            for (parameter, output), coefficient in sorted(pair_terms.items()):
                coefficients.append(
                    {
                        "X": x,
                        "Y": y,
                        "phi_parameter": parameter,
                        "Z": output,
                        "coeff": str(coefficient),
                        "sign_rule": "graded",
                    }
                )
    for term in coefficients:
        if parity[term["Z"]] != (
            parity[term["X"]] + parity[term["Y"]] + 1
        ) % 2:
            raise ValueError("Coboundary coefficient violates its odd-map parity")

    map_coefficients = [
        {
            "input": input_label,
            "output": output_label,
            "parameter": parameter,
            "parity": 0,
        }
        for input_label in order
        for parameter, output_label in linear_map[input_label]
    ]
    even_count = len(structure["basis"]["even"])
    odd_count = len(structure["basis"]["odd"])
    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "source_structure_file": f"C_{n}_structure.json",
        "basis": structure["basis"],
        "pbw_order": order,
        "linear_map_f": {
            "parity": 1,
            "description": "Odd map: f reverses basis parity",
            "parameter_count": 2 * even_count * odd_count,
            "coefficients": map_coefficients,
        },
        "coboundary": {
            "formula": (
                "(delta f)(X,Y) = (-1)^p(X)[X,f(Y)] "
                "- (-1)^((p(X)+1)p(Y))[Y,f(X)] - f([X,Y])"
            ),
            "coefficients": coefficients,
        },
        "consistency": {
            "basis_matches_schema_1": True,
            "parity_map_matches_schema_1": True,
            "all_coboundary_terms_have_parity": 1,
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": date.today().isoformat(),
            "references": [
                "docs/math/C_coboundary_definition.md",
                f"data/C_{n}_structure.json",
            ],
        },
    }


def generate(data_directory: Path, ranks: Iterable[int] = (1, 2, 3)) -> list[Path]:
    generated = []
    for n in ranks:
        structure = json.loads(
            (data_directory / f"C_{n}_structure.json").read_text(encoding="utf-8")
        )
        schema = build_coboundary(structure)
        path = data_directory / f"C_{n}_coboundary.json"
        path.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        generated.append(path)
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    parser.add_argument("--ranks", type=int, nargs="+", default=[1, 2, 3])
    args = parser.parse_args()
    for path in generate(args.data_dir, args.ranks):
        print(path)


if __name__ == "__main__":
    main()
