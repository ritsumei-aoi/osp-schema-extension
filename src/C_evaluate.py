"""Substitute a representative numeric gb assignment into C(n+1) gamma data."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Iterable


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


def evaluate(gamma: dict, structure: dict) -> dict:
    n = structure["algebra"]["n"]
    if (
        gamma["algebra"] != structure["algebra"]
        or gamma["consistency"]["source_structure_file"]
        != f"C_{n}_structure.json"
        or not gamma["consistency"]["basis_matches_schema_1"]
        or not gamma["consistency"]["parity_matches_schema_1"]
    ):
        raise ValueError("Schema 2 metadata does not match the supplied Schema 1")

    parameters = [
        item["label"] for item in gamma["gb_matrix"]["parameters"]
    ]
    if len(parameters) != 4 * n or len(set(parameters)) != len(parameters):
        raise ValueError(f"expected exactly {4 * n} distinct gb parameters")
    assignment = {label: 1 for label in parameters}
    order = _pbw_order(n)
    order_index = {label: index for index, label in enumerate(order)}
    basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
    coefficients: defaultdict[tuple[str, str, str], Fraction] = defaultdict(Fraction)

    for term in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        if term["gb_parameter"] not in assignment:
            raise ValueError(f"unknown gb parameter {term['gb_parameter']!r}")
        if (
            term["X"] not in basis
            or term["Y"] not in basis
            or term["Z"] not in basis | {"K"}
        ):
            raise ValueError("Schema 2 gamma term references a non-Schema 1 generator")
        if order_index[term["X"]] > order_index[term["Y"]]:
            raise ValueError("Schema 2 gamma input pair is not in PBW order")
        key = (term["X"], term["Y"], term["Z"])
        coefficients[key] += Fraction(term["coeff"]) * assignment[term["gb_parameter"]]

    evaluated_gamma = [
        {
            "X": left,
            "Y": right,
            "Z": result,
            "coeff": str(coefficient),
            "sign_rule": "graded",
        }
        for (left, right, result), coefficient in sorted(
            coefficients.items(),
            key=lambda item: (
                order_index[item[0][0]],
                order_index[item[0][1]],
                order_index.get(item[0][2], len(order)),
            ),
        )
        if coefficient
    ]
    return {
        "schema_version": "5.0",
        "algebra": structure["algebra"],
        "source_structure_file": f"C_{n}_structure.json",
        "source_gamma_file": f"C_{n}_gamma.json",
        "structure_constants": structure["structure_constants"],
        "deformation_evaluation": {
            "profile": "all_plus",
            "parameter_assignment": assignment,
            "gamma_coefficients": evaluated_gamma,
            "bracket_convention": (
                "[X,Y]_evaluated = [X,Y]_0 + kappa*gamma(X,Y); "
                "coefficients are exact rational strings"
            ),
            "parity_status": gamma["consistency"]["parity_status"],
            "parity_warning": gamma["consistency"]["parity_warning"],
        },
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": date.today().isoformat(),
            "references": [
                f"data/C_{n}_structure.json",
                f"data/C_{n}_gamma.json",
            ],
        },
    }


def generate(data_directory: Path, ranks: Iterable[int] = (1, 2, 3)) -> list[Path]:
    generated = []
    for n in ranks:
        structure = json.loads(
            (data_directory / f"C_{n}_structure.json").read_text(encoding="utf-8")
        )
        gamma = json.loads(
            (data_directory / f"C_{n}_gamma.json").read_text(encoding="utf-8")
        )
        evaluated = evaluate(gamma, structure)
        path = data_directory / f"C_{n}_evaluated.json"
        path.write_text(
            json.dumps(evaluated, indent=2, ensure_ascii=False) + "\n",
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
