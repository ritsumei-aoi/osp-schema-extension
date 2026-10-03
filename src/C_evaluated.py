"""
C_evaluated.py

Produces Schema 3 (Evaluated Structure) for C(n+1) = osp(2|2n).
Substitutes concrete values for the gb deformation parameters and
evaluates the gamma coefficients gamma_{XYZ}.

Representative assignment: gb_{sigma,j,s} = +1 for all sigma, j, s.
This is the "all-ones" profile, useful as a canonical reference.

Output: C_{n}_evaluated.json for n=1, 2, 3.
"""

import json
import os
from fractions import Fraction
from datetime import date


def load_gamma(n):
    path = os.path.join("data", f"C_{n}_gamma.json")
    with open(path) as f:
        return json.load(f)


def load_structure(n):
    path = os.path.join("data", f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def evaluate_gamma(gamma_list, gb_values):
    """
    Substitute concrete gb values into gamma coefficients.

    gamma_list: list of {X, Y, Z, gamma_coeff: {gb_label: str}}
    gb_values: dict {gb_label: Fraction}

    Returns list of {X, Y, Z, coeff: str} with evaluated coefficients.
    Also returns combined_list including Structure constants (Schema 1) + kappa*gamma.
    """
    evaluated = []
    for entry in gamma_list:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        gb_coeff_dict = {lbl: Fraction(c) for lbl, c in entry["gamma_coeff"].items()}

        # Evaluate: coeff = sum_gb gb_value * gb_coeff
        total = Fraction(0)
        for lbl, c in gb_coeff_dict.items():
            total += gb_values.get(lbl, Fraction(0)) * c

        if total != 0:
            evaluated.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": str(total),
            })
    return evaluated


def build_evaluated_schema(n, gb_profile="all_ones"):
    """Build Schema 3 JSON for C(n+1)."""
    gamma_schema = load_gamma(n)
    structure_schema = load_structure(n)

    gamma_list = gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]
    sc_list = structure_schema["structure_constants"]
    basis = structure_schema["basis"]
    parity = structure_schema["parity"]

    # Build gb parameter labels
    gb_labels = []
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                gb_labels.append(f"gb_{sigma}_{j}_{s}")

    # Set gb values
    if gb_profile == "all_ones":
        gb_values = {lbl: Fraction(1) for lbl in gb_labels}
        profile_desc = "All gb parameters set to +1"
    elif gb_profile == "alternating":
        gb_values = {}
        for i, lbl in enumerate(gb_labels):
            gb_values[lbl] = Fraction(1) if i % 2 == 0 else Fraction(-1)
        profile_desc = "Alternating +1/-1 pattern"
    else:
        gb_values = {lbl: Fraction(1) for lbl in gb_labels}
        profile_desc = "All gb parameters set to +1"

    # Evaluate gamma
    gamma_evaluated = evaluate_gamma(gamma_list, gb_values)

    # Build combined bracket: [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)
    # Represent as separate layers:
    # Layer 0: structure constants (Schema 1 brackets)
    # Kappa layer: evaluated gamma * kappa

    # Combine into one list for easy analysis
    # Each entry has "source": "structure" or "kappa"
    combined = []
    for e in sc_list:
        combined.append({
            "X": e["X"],
            "Y": e["Y"],
            "Z": e["Z"],
            "coeff": e["coeff"],
            "source": "structure",
        })
    for e in gamma_evaluated:
        combined.append({
            "X": e["X"],
            "Y": e["Y"],
            "Z": e["Z"],
            "coeff": e["coeff"],
            "source": "kappa_gamma",
        })

    schema = {
        "schema_version": "5.0",
        "algebra": f"C({n+1})",
        "n": n,
        "layer": 3,
        "description": "Evaluated structure: Schema 1 + kappa*gamma with specific gb values",
        "gb_assignment": {
            "profile": gb_profile,
            "description": profile_desc,
            "values": {lbl: str(v) for lbl, v in gb_values.items()},
        },
        "evaluated_gamma": gamma_evaluated,
        "combined_bracket": {
            "description": "[X,Y]_gamma = [X,Y]_0 (structure) + kappa * gamma(X,Y) (kappa_gamma)",
            "entries": combined,
        },
        "summary": {
            "structure_constant_count": len(sc_list),
            "non_zero_gamma_count": len(gamma_evaluated),
            "total_combined": len(combined),
        },
        "metadata": {
            "generated_by": "C_evaluated.py",
            "generation_date": str(date.today()),
            "schema1_reference": f"C_{n}_structure.json",
            "schema2_reference": f"C_{n}_gamma.json",
        },
    }
    return schema


def verify_consistency_with_schema1(n, schema):
    """
    Verify that the evaluated gamma entries reference only valid basis generators.
    Also check that evaluated gamma has the correct parity structure.
    """
    structure = load_structure(n)
    parity = structure["parity"]
    all_basis = set(structure["basis"]["even"] + structure["basis"]["odd"])

    errors = []
    for e in schema["evaluated_gamma"]:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        if X not in all_basis:
            errors.append(f"X={X} not in basis")
        if Y not in all_basis:
            errors.append(f"Y={Y} not in basis")
        if Z not in all_basis:
            errors.append(f"Z={Z} not in basis")
        # Parity check: gamma(X,Y) component Z has parity p(X)+p(Y)+1 (mod 2)
        expected_p = (parity.get(X, 0) + parity.get(Y, 0) + 1) % 2
        actual_p = parity.get(Z, -1)
        if actual_p != expected_p:
            errors.append(f"Parity error gamma({X},{Y})[{Z}]: expected {expected_p}, got {actual_p}")
    return errors


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Building C_{n}_evaluated.json (C({n+1}) = osp(2|{2*n}))...")
        schema = build_evaluated_schema(n, gb_profile="all_ones")

        # Consistency check
        errors = verify_consistency_with_schema1(n, schema)
        if errors:
            print(f"  CONSISTENCY ERRORS for n={n}:")
            for e in errors[:5]:
                print(f"    {e}")
        else:
            print(f"  Consistency with Schema 1: OK")

        outfile = f"data/C_{n}_evaluated.json"
        with open(outfile, "w") as f:
            json.dump(schema, f, indent=2)

        s = schema["summary"]
        print(f"  Structure constants: {s['structure_constant_count']}")
        print(f"  Non-zero gamma (evaluated): {s['non_zero_gamma_count']}")
        print(f"  Total combined entries: {s['total_combined']}")
        print(f"  Written to {outfile}")


if __name__ == "__main__":
    main()
