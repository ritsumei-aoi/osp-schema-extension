"""
Schema 3: Evaluated structure for C(n+1) = osp(2|2n).

Substitutes concrete values for gb parameters and produces
C_{n}_evaluated.json for n=1,2,3.

Default assignment: all gb = 1 (uniform sign profile).
"""

from __future__ import annotations
import json
import os
from datetime import date
from fractions import Fraction


def evaluate_gamma(s1: dict, s2: dict, gb_assignment: dict[str, int]) -> list[dict]:
    """
    Substitute gb values into gamma_coefficients from Schema 2.
    Returns list of evaluated entries: {X, Y, Z, coeff_numeric}.
    """
    parity = s1["parity"]
    basis = set(s1["basis"]["even"] + s1["basis"]["odd"])

    # Accumulate gamma(X,Y)[Z] = sum_gb gb_val * coeff
    combined: dict[tuple[str, str, str], Fraction] = {}

    for e in s2["gamma_coefficients"]:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        gb = e["gb_param"]
        c = Fraction(e["coeff"])
        gb_val = Fraction(gb_assignment.get(gb, 0))
        contribution = gb_val * c
        key = (X, Y, Z)
        combined[key] = combined.get(key, Fraction(0)) + contribution

    result = []
    for (X, Y, Z), total in combined.items():
        if total != 0:
            result.append({
                "X": X, "Y": Y, "Z": Z,
                "coeff_numeric": str(total),
                "sign_rule": "graded"
            })

    return result


def build_schema3(n: int, gb_assignment: dict[str, int]) -> dict:
    with open(f"data/C_{n}_structure.json") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json") as f:
        s2 = json.load(f)

    gamma_entries = evaluate_gamma(s1, s2, gb_assignment)

    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "gb_assignment": {k: str(v) for k, v in gb_assignment.items()},
        "deformation_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
        "gamma_coefficients": gamma_entries,
        "metadata": {
            "generated_by": "src/C_evaluated.py",
            "generation_date": str(date.today()),
            "source_schema1": f"C_{n}_structure.json",
            "source_schema2": f"C_{n}_gamma.json",
            "references": [
                "Frappat, Sciarrino, Sorba (2000)",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }


def make_gb_assignment(n: int, value: int = 1) -> dict[str, int]:
    """Uniform assignment: all 4n gb parameters = value."""
    params = {}
    for j in range(1, n + 1):
        for sigma in ['p', 'm']:
            for s in ['p', 'm']:
                params[f"gb_{sigma}_{j}_{s}"] = value
    return params


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Building evaluated n={n}...", flush=True)
        gb = make_gb_assignment(n, value=1)
        schema = build_schema3(n, gb)
        fname = f"data/C_{n}_evaluated.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        gc = len(schema["gamma_coefficients"])
        print(f"  C_{n}_evaluated.json: {gc} nonzero gamma entries (all gb=1)")


if __name__ == "__main__":
    main()
