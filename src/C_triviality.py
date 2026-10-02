#!/usr/bin/env python3
"""Compare evaluated C deformations with the odd-map coboundary space."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


def analyze_rank(n: int, data_dir: Path | str = "data") -> dict:
    data_dir = Path(data_dir)
    gamma = json.loads((data_dir / f"C_{n}_gamma.json").read_text(encoding="utf-8"))
    evaluated = json.loads(
        (data_dir / f"C_{n}_evaluated.json").read_text(encoding="utf-8")
    )
    coboundary = json.loads(
        (data_dir / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
    )
    structure = json.loads(
        (data_dir / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
    parameters = set(gamma["gb_matrix"]["parameters"])
    if coboundary["basis"]["even"] != structure["basis"]["even"]:
        raise ValueError(f"Layer 4 even basis mismatch for rank {n}")
    if coboundary["basis"]["odd"] != structure["basis"]["odd"]:
        raise ValueError(f"Layer 4 odd basis mismatch for rank {n}")

    coboundary_outputs = {
        entry["Z"] for entry in coboundary["coboundary"]["coboundary_coefficients"]
    }
    if "K" in coboundary_outputs:
        raise ValueError("Layer 4 unexpectedly contains the excluded scalar identity K")
    kappa_terms = {
        (entry["X"], entry["Y"], entry["Z"]): Fraction(entry["kappa_coeff"])
        for entry in evaluated["structure_constants"]
        if Fraction(entry["kappa_coeff"])
    }
    central_terms = {
        pair: coeff for pair, coeff in kappa_terms.items() if pair[2] == "K"
    }
    if any(z not in basis and z != "K" for _, _, z in kappa_terms):
        raise ValueError("Layer 3 contains an output outside the Schema 1 basis and K")

    witnesses = []
    for k in range(1, n + 1):
        cases = (
            ("p", "p", f"E_2del{k}_p", f"E_eps1_del{k}_pm", Fraction(1, 2)),
            ("p", "m", f"E_2del{k}_m", f"E_eps1_del{k}_pp", Fraction(-1, 2)),
            ("m", "p", f"E_2del{k}_p", f"E_eps1_del{k}_mm", Fraction(1, 2)),
            ("m", "m", f"E_2del{k}_m", f"E_eps1_del{k}_mp", Fraction(-1, 2)),
        )
        for fermion_sign, boson_sign, x, y, expected_coeff in cases:
            parameter = f"gb_a_1_{fermion_sign}_b_{k}_{boson_sign}"
            key = (x, y, "K")
            matching = [
                entry for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]
                if (entry["X"], entry["Y"], entry["Z"]) == key
            ]
            if len(matching) != 1 or matching[0]["parameter"] != parameter:
                raise ValueError(f"Missing isolated K witness for {parameter}: {key}")
            if Fraction(matching[0]["coeff"]) != expected_coeff:
                raise ValueError(f"Unexpected K coefficient for {parameter}: {key}")
            witnesses.append({
                "parameter": parameter,
                "X": x,
                "Y": y,
                "coefficient": str(expected_coeff),
            })

    if len(witnesses) != 4 * n or len({item["parameter"] for item in witnesses}) != 4 * n:
        raise ValueError(f"Did not obtain independent K witnesses for all gb parameters")

    return {
        "rank": n,
        "parameter_count": len(parameters),
        "evaluated_gamma_terms": len(kappa_terms),
        "evaluated_central_obstructions": len(central_terms),
        "isolated_parameter_witnesses": witnesses,
        "all_plus_is_trivial": not bool(kappa_terms),
        "zero_assignment_is_trivial": True,
        "triviality_condition_conjecture": "all gb parameters vanish",
    }


def main(data_dir: Path | str = "data") -> int:
    for n in (1, 2, 3):
        result = analyze_rank(n, data_dir)
        print(
            f"C({n + 1}): {result['parameter_count']} parameters; "
            f"{result['evaluated_gamma_terms']} evaluated gamma terms; "
            f"{result['evaluated_central_obstructions']} K obstructions; "
            f"all-plus trivial={result['all_plus_is_trivial']}; "
            "conjectured triviality iff all gb=0"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
