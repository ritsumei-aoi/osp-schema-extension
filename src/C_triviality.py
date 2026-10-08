"""Compare evaluated C deformations with the generic coboundary image."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


def analyze_rank(data_dir: Path, n: int) -> dict:
    gamma = json.loads((data_dir / f"C_{n}_gamma.json").read_text())[
        "inhomogeneous_deformation"
    ]
    evaluated = json.loads((data_dir / f"C_{n}_evaluated.json").read_text())
    coboundary = json.loads((data_dir / f"C_{n}_coboundary.json").read_text())
    parameters = {item["label"] for item in gamma["parameters"]}
    coboundary_outputs = {
        term["Z"] for term in coboundary["coboundary"]["coefficients"]
    }
    if "K" in coboundary_outputs:
        raise ValueError("Layer 4 unexpectedly contains the central identity K")

    by_pair: dict[tuple[str, str], dict[str, Fraction]] = defaultdict(
        lambda: defaultdict(Fraction)
    )
    for term in gamma["consistency"]["off_basis_terms"]:
        by_pair[(term["X"], term["Y"])][term["parameter"]] += Fraction(term["coeff"])

    witnesses = []
    for (x, y), coefficients in sorted(by_pair.items()):
        nonzero = {parameter: coeff for parameter, coeff in coefficients.items() if coeff}
        if len(nonzero) == 1:
            parameter, coefficient = next(iter(nonzero.items()))
            witnesses.append({
                "X": x,
                "Y": y,
                "parameter": parameter,
                "coeff": str(coefficient),
                "condition": f"{coefficient} * {parameter} = 0",
            })
    witnessed_parameters = {item["parameter"] for item in witnesses}
    all_positive_k = [
        item for item in evaluated["evaluated_gamma_coefficients"]
        if item["Z"] == "K" and Fraction(item["kappa_coeff"])
    ]
    zero_assignment = {parameter: 0 for parameter in parameters}
    zero_gamma_values = [
        Fraction(term["coeff"]) * zero_assignment[term["parameter"]]
        for term in gamma["gamma_coefficients"]
    ]
    zero_assignment_gamma_terms = sum(value != 0 for value in zero_gamma_values)
    zero_map_coboundary_terms = 0
    return {
        "rank": n,
        "parameters": len(parameters),
        "identity_obstruction_terms": len(gamma["consistency"]["off_basis_terms"]),
        "all_positive_identity_obstructions": len(all_positive_k),
        "identity_obstruction_pairs": len(by_pair),
        "single_parameter_witnesses": witnesses,
        "all_parameters_forced_zero": witnessed_parameters == parameters,
        "zero_assignment_gamma_terms": zero_assignment_gamma_terms,
        "zero_map_coboundary_terms": zero_map_coboundary_terms,
        "zero_assignment_is_coboundary": (
            not zero_assignment_gamma_terms and zero_map_coboundary_terms == 0
        ),
        "all_positive_is_coboundary": not all_positive_k,
        "layer4_has_identity_output": "K" in coboundary_outputs,
        "formal_conclusion": (
            "Within the supplied formal model, gamma is a coboundary only when "
            "all gb parameters vanish."
            if witnessed_parameters == parameters
            else "Identity obstructions do not yet force every gb parameter to zero."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    failed = False
    for n in (1, 2, 3):
        result = analyze_rank(args.data_dir, n)
        passed = result["all_parameters_forced_zero"] and not result["layer4_has_identity_output"]
        failed |= not passed
        print(
            f"C_{n}: all-positive {'non-trivial' if not result['all_positive_is_coboundary'] else 'trivial'}; "
            f"K obstructions={result['all_positive_identity_obstructions']}; "
            f"parameters forced zero={result['parameters'] if passed else 'incomplete'}; "
            f"zero assignment trivial={result['zero_assignment_is_coboundary']}"
        )
        for witness in result["single_parameter_witnesses"][:4]:
            print(
                f"  [{witness['X']}, {witness['Y']}] -> "
                f"{witness['coeff']} * {witness['parameter']} * K"
            )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
