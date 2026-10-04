"""Compare evaluated C(n+1) gamma data with the odd-map coboundary image."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any


def _rank(matrix: list[list[Fraction]]) -> int:
    if not matrix:
        return 0
    reduced = [row[:] for row in matrix]
    columns = len(reduced[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (r for r in range(pivot_row, len(reduced)) if reduced[r][column]),
            None,
        )
        if pivot is None:
            continue
        reduced[pivot_row], reduced[pivot] = reduced[pivot], reduced[pivot_row]
        scale = reduced[pivot_row][column]
        reduced[pivot_row] = [value / scale for value in reduced[pivot_row]]
        for r in range(len(reduced)):
            if r != pivot_row and reduced[r][column]:
                factor = reduced[r][column]
                reduced[r] = [
                    value - factor * pivot
                    for value, pivot in zip(reduced[r], reduced[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == len(reduced):
            break
    return pivot_row


def analyze_rank(data_dir: Path, n: int) -> dict[str, Any]:
    gamma = json.loads((data_dir / f"C_{n}_gamma.json").read_text(encoding="utf-8"))
    evaluated = json.loads(
        (data_dir / f"C_{n}_evaluated.json").read_text(encoding="utf-8")
    )
    coboundary = json.loads(
        (data_dir / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
    )
    parameters = [
        parameter
        for row in gamma["gb_matrix"]["parameters"]
        for parameter in row
    ]
    kappa_rows: dict[tuple[str, str], dict[str, Fraction]] = {}
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        if entry["Z"] == "K":
            pair = (entry["X"], entry["Y"])
            row = kappa_rows.setdefault(pair, {})
            row[entry["parameter"]] = row.get(entry["parameter"], Fraction(0)) + Fraction(
                entry["coeff"]
            )
    matrix = [
        [row.get(parameter, Fraction(0)) for parameter in parameters]
        for row in kappa_rows.values()
    ]
    isolated_equations = [
        {
            "parameter": next(parameter for parameter, coeff in row.items() if coeff),
            "pair": list(pair),
            "coefficient": str(next(coeff for coeff in row.values() if coeff)),
        }
        for pair, row in kappa_rows.items()
        if len({parameter for parameter, coeff in row.items() if coeff}) == 1
    ]
    coboundary_pairs = {
        (entry["X"], entry["Y"], entry["Z"])
        for entry in coboundary["coboundary_coefficients"]
    }
    evaluated_kappa = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["kappa_coeff"])
        for entry in evaluated["evaluated_structure_constants"]
    }
    sample_pair = ("E_eps1_del1_mm", "E_2del1_p")
    sample_gamma = evaluated_kappa.get((*sample_pair, "K"), Fraction(0))
    return {
        "rank": n,
        "parameter_count": len(parameters),
        "kappa_equation_count": len(kappa_rows),
        "kappa_obstruction_rank": _rank(matrix),
        "isolated_equations": isolated_equations,
        "isolated_parameter_count": len(
            {equation["parameter"] for equation in isolated_equations}
        ),
        "all_plus_kappa_support_size": sum(
            1 for (x, y, z), coeff in evaluated_kappa.items() if z == "K" and coeff
        ),
        "sample_pair": list(sample_pair),
        "sample_kappa_coefficient": str(sample_gamma),
        "sample_has_coboundary_k_component": (*sample_pair, "K") in coboundary_pairs,
        "coboundary_has_any_k_component": any(z == "K" for _, _, z in coboundary_pairs),
        "zero_assignment_trivial": all(
            Fraction(entry["coeff"]) * 0 == 0
            for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]
        ),
    }


def report(data_dir: Path = Path("data"), ranks: tuple[int, ...] = (1, 2, 3)) -> list[dict[str, Any]]:
    results = [analyze_rank(data_dir, n) for n in ranks]
    for result in results:
        n = result["rank"]
        print(
            f"C_{n}: K-obstruction rank={result['kappa_obstruction_rank']}/"
            f"{result['parameter_count']}, isolated parameters="
            f"{result['isolated_parameter_count']}/{result['parameter_count']}, "
            f"all-plus K-support={result['all_plus_kappa_support_size']}, "
            f"sample K coefficient={result['sample_kappa_coefficient']}, "
            f"coboundary has K={result['coboundary_has_any_k_component']}"
        )
    return results


if __name__ == "__main__":
    report()
