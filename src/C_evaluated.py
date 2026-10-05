"""
C(n+1) = osp(2|2n) evaluated structure (Schema 3) generator.

Substitutes concrete sign assignments into gb parameters
and produces numerically evaluated deformed structure constants.
"""

import json
import os
from fractions import Fraction
from datetime import date


def define_gb_profiles(n):
    """Define representative gb assignments for C(n+1).
    Returns dict mapping profile_name -> {gb_label: value}.
    """
    profiles = {}

    # Profile 1: all gb = +1
    all_plus = {}
    for sigma in ['p', 'm']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                all_plus[f"gb_a1{sigma}_b{j}{s}"] = Fraction(1)
    profiles["all_plus"] = all_plus

    # Profile 2: alternating signs
    alternating = {}
    sign = 1
    for sigma in ['p', 'm']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                alternating[f"gb_a1{sigma}_b{j}{s}"] = Fraction(sign)
                sign *= -1
    profiles["alternating"] = alternating

    return profiles


def evaluate_gamma(gamma_data, gb_assignment):
    """Substitute gb values into gamma coefficients.
    Returns list of (X, Y, Z, evaluated_coeff).
    """
    evaluated = {}
    for entry in gamma_data:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        gb = entry["gb_param"]
        coeff = Fraction(entry["coeff"])
        gb_val = gb_assignment.get(gb, Fraction(0))
        val = coeff * gb_val

        key = (X, Y, Z)
        evaluated[key] = evaluated.get(key, Fraction(0)) + val

    return [(k[0], k[1], k[2], v) for k, v in evaluated.items() if v != 0]


def build_evaluated_structure(n, structure_data, gamma_data, gb_assignment, profile_name):
    """Build the full evaluated deformed bracket: [X,Y]_γ = [X,Y]_0 + κ·γ(X,Y)."""
    # Original structure constants
    original = []
    for sc in structure_data["structure_constants"]:
        original.append({
            "X": sc["X"],
            "Y": sc["Y"],
            "Z": sc["Z"],
            "coeff": sc["coeff"],
            "layer": "original",
        })

    # Evaluated gamma (κ-corrections)
    gamma_evaluated = evaluate_gamma(gamma_data, gb_assignment)
    kappa_corrections = []
    for X, Y, Z, coeff in gamma_evaluated:
        kappa_corrections.append({
            "X": X,
            "Y": Y,
            "Z": Z,
            "coeff": str(coeff),
            "layer": "kappa_correction",
        })

    return {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "gb_assignment": {
            "profile_name": profile_name,
            "values": {k: str(v) for k, v in gb_assignment.items()},
        },
        "original_structure_constants": original,
        "kappa_corrections": kappa_corrections,
        "metadata": {
            "generated_by": "C_evaluated.py",
            "generation_date": str(date.today()),
        },
    }


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        with open(os.path.join(output_dir, f"C_{n}_structure.json")) as f:
            structure = json.load(f)
        with open(os.path.join(output_dir, f"C_{n}_gamma.json")) as f:
            gamma = json.load(f)

        profiles = define_gb_profiles(n)
        profile_name = "all_plus"
        gb_assignment = profiles[profile_name]

        schema = build_evaluated_structure(
            n, structure, gamma["gamma_coefficients"],
            gb_assignment, profile_name
        )

        path = os.path.join(output_dir, f"C_{n}_evaluated.json")
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)

        print(f"Generated {path}: "
              f"{len(schema['original_structure_constants'])} original + "
              f"{len(schema['kappa_corrections'])} κ-corrections, "
              f"profile={profile_name}")


def verify_consistency(n, data_dir="data"):
    """Verify Schema 3 consistency with Schema 2."""
    with open(os.path.join(data_dir, f"C_{n}_gamma.json")) as f:
        s2 = json.load(f)
    with open(os.path.join(data_dir, f"C_{n}_evaluated.json")) as f:
        s3 = json.load(f)

    # Check all gb params are assigned
    gb_params_s2 = {p["label"] for p in s2["gb_matrix"]["parameters"]}
    gb_assigned = set(s3["gb_assignment"]["values"].keys())

    missing = gb_params_s2 - gb_assigned
    if missing:
        print(f"  n={n}: Missing gb assignments: {missing}")
        return False

    # Check kappa corrections reference valid generators
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    basis = set(s1["basis"]["even"] + s1["basis"]["odd"])
    for entry in s3["kappa_corrections"]:
        for key in ["X", "Y", "Z"]:
            if entry[key] not in basis:
                print(f"  n={n}: Invalid generator {entry[key]}")
                return False

    print(f"  Consistency check for n={n}: PASS")
    return True


if __name__ == "__main__":
    generate_all()
    print("\nConsistency checks:")
    for n in [1, 2, 3]:
        verify_consistency(n)
