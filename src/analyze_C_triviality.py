"""Compare C(n+1) gamma data with coboundaries using central K obstructions."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def _matrix_rank(rows: list[list[Fraction]]) -> int:
    if not rows:
        return 0
    matrix = [row[:] for row in rows]
    columns = len(matrix[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (index for index in range(pivot_row, len(matrix)) if matrix[index][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        scale = matrix[pivot_row][column]
        matrix[pivot_row] = [value / scale for value in matrix[pivot_row]]
        for index in range(len(matrix)):
            if index == pivot_row or not matrix[index][column]:
                continue
            factor = matrix[index][column]
            matrix[index] = [
                value - factor * pivot_value
                for value, pivot_value in zip(matrix[index], matrix[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return pivot_row


def _witness_pair(n: int, fermion_sign: str, boson_sign: str, k: int) -> tuple[str, str]:
    if fermion_sign == "m" and boson_sign == "m":
        cartan = "H_1" if k == 1 else f"H_{k + 1}"
        return f"E_eps1_del{k}_mm", cartan
    if fermion_sign == "m" and boson_sign == "p":
        return f"E_eps1_del{k}_mm", f"E_2del{k}_p"
    if fermion_sign == "p" and boson_sign == "m":
        return f"E_eps1_del{k}_pp", f"E_2del{k}_m"
    return f"E_eps1_del{k}_pm", f"E_2del{k}_p"


def analyze_rank(n: int, data_dir: Path = Path("data")) -> dict:
    gamma_schema = json.loads(
        (data_dir / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )
    evaluated_schema = json.loads(
        (data_dir / f"C_{n}_evaluated.json").read_text(encoding="utf-8")
    )
    coboundary_schema = json.loads(
        (data_dir / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
    )

    gamma = gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]
    parameters = [
        item["name"] for item in gamma_schema["gb_matrix"]["parameters"]
    ]
    k_rows: dict[tuple[str, str], dict[str, Fraction]] = {}
    for term in gamma:
        if term["Z"] != "K":
            continue
        row = k_rows.setdefault((term["X"], term["Y"]), {})
        parameter = term["gb_parameter"]
        row[parameter] = row.get(parameter, Fraction(0)) + Fraction(term["coeff"])

    matrix = [
        [k_rows[pair].get(parameter, Fraction(0)) for parameter in parameters]
        for pair in sorted(k_rows)
    ]
    rank = _matrix_rank(matrix)
    witnesses = []
    for k in range(1, n + 1):
        for fermion_sign in ("p", "m"):
            for boson_sign in ("p", "m"):
                parameter = f"gb_a_1_{fermion_sign}_b_{k}_{boson_sign}"
                pair = _witness_pair(n, fermion_sign, boson_sign, k)
                row = k_rows.get(pair, {})
                nonzero = {key: value for key, value in row.items() if value}
                if set(nonzero) != {parameter}:
                    raise ValueError(
                        f"K witness {pair} does not isolate {parameter}: {nonzero}"
                    )
                witnesses.append(
                    {
                        "parameter": parameter,
                        "X": pair[0],
                        "Y": pair[1],
                        "kappa_coefficient": str(nonzero[parameter]),
                    }
                )

    evaluated_k = {
        (term["X"], term["Y"]): Fraction(term["kappa_coeff"])
        for term in evaluated_schema["structure_constants"]
        if term["Z"] == "K" and Fraction(term["kappa_coeff"])
    }
    for witness in witnesses:
        pair = (witness["X"], witness["Y"])
        if evaluated_k.get(pair) != Fraction(witness["kappa_coefficient"]):
            raise ValueError(f"all-positive evaluated K term disagrees at {pair}")

    coboundary_has_K = any(
        term["Z"] == "K"
        for term in coboundary_schema["coboundary_coefficients"]
    )
    if coboundary_has_K:
        raise ValueError("Layer 4 coboundary unexpectedly has a K output")
    zero_assignment_gamma_is_zero = all(
        Fraction(term["coeff"]) * 0 == 0 for term in gamma
    )
    return {
        "rank": n,
        "gb_parameter_count": len(parameters),
        "K_obstructed_pair_count": len(k_rows),
        "K_obstruction_rank": rank,
        "K_obstruction_nullity": len(parameters) - rank,
        "coboundary_has_K_output": coboundary_has_K,
        "all_positive_is_nontrivial": bool(evaluated_k),
        "zero_assignment_gamma_is_zero": zero_assignment_gamma_is_zero,
        "zero_assignment_is_trivial": zero_assignment_gamma_is_zero and not coboundary_has_K,
        "witnesses": witnesses,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", nargs="+", type=int, default=[1, 2, 3])
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    for n in args.ranks:
        report = analyze_rank(n, args.data_dir)
        print(
            f"C_{n}: K-obstruction rank {report['K_obstruction_rank']}/"
            f"{report['gb_parameter_count']}, nullity "
            f"{report['K_obstruction_nullity']}; "
            f"all-positive trivial={not report['all_positive_is_nontrivial']}; "
            f"zero trivial={report['zero_assignment_is_trivial']}"
        )
        for witness in report["witnesses"]:
            print(
                f"  {witness['parameter']}: "
                f"[{witness['X']}, {witness['Y']}] -> "
                f"{witness['kappa_coefficient']} K"
            )


if __name__ == "__main__":
    main()
