"""
C_evaluate.py
Generates Schema 3 (evaluated deformation) for C(n+1).

Substitutes concrete values into the gb parameters from Schema 2
and produces numerical gamma coefficients.

Representative assignment: all gb parameters set to +1 (uniform sign profile).
"""

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, build_parity_dict
from C_gamma import build_gb_params


def evaluate_gamma(gamma_json_path, gb_assignment):
    """
    Load Schema 2 JSON and evaluate all gamma_expr with given gb_assignment.

    gb_assignment: dict {gb_label: Fraction}
    Returns list of {X, Y, Z, coeff} with numerical coeff.
    """
    with open(gamma_json_path) as f:
        data = json.load(f)

    evaluated = []
    for entry in data["inhomogeneous_deformation"]["gamma_coefficients"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        expr = entry["gamma_expr"]  # dict {gb_label: str(coeff)}

        # Evaluate: sum over gb_label of expr[gb_label] * gb_assignment[gb_label]
        total = Fraction(0)
        for gb_label, str_coeff in expr.items():
            val = gb_assignment.get(gb_label, Fraction(0))
            total += Fraction(str_coeff) * val

        if total != 0:
            evaluated.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": str(total)
            })

    return evaluated


def build_schema3(n, gb_values, data_dir="data"):
    """Build Schema 3 for given gb assignment."""
    gamma_path = os.path.join(data_dir, f"C_{n}_gamma.json")

    # Build gb_assignment dict
    gb_params = build_gb_params(n)
    gb_assignment = {p: Fraction(gb_values.get(p, 1)) for p in gb_params}

    evaluated = evaluate_gamma(gamma_path, gb_assignment)

    even_basis, odd_basis = build_basis(n)
    algebra_names = {1: "C(2)", 2: "C(3)", 3: "C(4)"}
    osp_names = {1: "osp(2|2)", 2: "osp(2|4)", 3: "osp(2|6)"}
    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": algebra_names.get(n, f"C({n+1})"),
            "alternative_notation": {"osp": osp_names.get(n, f"osp(2|{2*n})")},
            "dimension": {"total": even_dim + odd_dim, "even": even_dim, "odd": odd_dim}
        },
        "gb_assignment": {p: str(gb_assignment[p]) for p in gb_params},
        "evaluated_gamma": evaluated,
        "metadata": {
            "generated_by": "C_evaluate.py",
            "generation_date": "2026-10-04",
            "gb_profile": "all gb = +1 (uniform assignment)"
        }
    }
    return schema


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)

    # Uniform assignment: all gb = +1
    for n in [1, 2, 3]:
        schema = build_schema3(n, {}, data_dir=output_dir)
        out_path = os.path.join(output_dir, f"C_{n}_evaluated.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        nb = len(schema["evaluated_gamma"])
        print(f"Written {out_path}: {nb} evaluated gamma entries")

    # Consistency check: verify Z labels in evaluated gamma are in basis
    for n in [1, 2, 3]:
        even, odd = build_basis(n)
        basis_set = set(even + odd)
        path = os.path.join(output_dir, f"C_{n}_evaluated.json")
        with open(path) as f:
            data = json.load(f)
        for entry in data["evaluated_gamma"]:
            for lbl in [entry["X"], entry["Y"], entry["Z"]]:
                if lbl not in basis_set:
                    print(f"  WARNING n={n}: label {lbl} not in basis!")
        # Verify Schema 2 consistency: evaluated entries are subset of gamma entries
        gamma_path = os.path.join(output_dir, f"C_{n}_gamma.json")
        with open(gamma_path) as f:
            gamma_data = json.load(f)
        gamma_keys = {(e["X"], e["Y"], e["Z"]) for e in gamma_data["inhomogeneous_deformation"]["gamma_coefficients"]}
        for entry in data["evaluated_gamma"]:
            key = (entry["X"], entry["Y"], entry["Z"])
            if key not in gamma_keys:
                print(f"  WARNING n={n}: evaluated entry {key} not in gamma!")
        print(f"  n={n}: consistency check OK")


if __name__ == "__main__":
    generate_all()
