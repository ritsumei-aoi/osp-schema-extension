"""
C_evaluate.py — Generate Schema 3 (Evaluated Structure) JSON for C(n+1) = osp(2|2n).

Substitutes concrete values for all gb parameters in the gamma cocycle (Schema 2),
producing a numerically evaluated deformation.

We use the representative assignment: all gb = +1 (sign profile: all positive).
This is the simplest non-trivial choice and gives a concrete deformed algebra.
"""

from __future__ import annotations
import json
import datetime
import os
import re
from fractions import Fraction


def load(n: int, suffix: str) -> dict:
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    path = os.path.join(data_dir, f"C_{n}_{suffix}.json")
    with open(path) as f:
        return json.load(f)


def evaluate_expr(expr: str, gb_values: dict) -> Fraction:
    """
    Evaluate a symbolic expression string like "-2*gb_a1p_b1p" or "1*gb_a1m_b2m"
    given a dict of gb_label -> numeric value.

    Expression format: "sign * coeff * gb_label" or "coeff * gb_label" or "-(coeff * gb_label)".
    We parse simple expressions of the form N*gb_label or -N*gb_label or -(N*gb_label).
    """
    expr = expr.strip()

    # Handle wrapped negation: -(...)
    if expr.startswith("-(") and expr.endswith(")"):
        inner = evaluate_expr(expr[2:-1], gb_values)
        return -inner

    # Split on '*' to get coefficient and gb_label
    # Format: "coeff*gb_label" or "-coeff*gb_label"
    parts = expr.split("*", 1)
    if len(parts) == 2:
        coeff_str, gb_label = parts
        coeff = Fraction(coeff_str)
        gb_val = gb_values.get(gb_label, Fraction(0))
        return coeff * gb_val

    # Plain number
    try:
        return Fraction(expr)
    except (ValueError, ZeroDivisionError):
        return Fraction(0)


def build_schema3(n: int, gb_assignment: str = "all_plus_one") -> dict:
    """
    Build Schema 3 by evaluating Schema 2 gamma coefficients with concrete gb values.

    gb_assignment options:
    - "all_plus_one": all gb parameters = +1
    """
    schema2 = load(n, "gamma")
    schema1 = load(n, "structure")

    # Define gb values
    gb_values = {}
    for label in schema2["gb_matrix"]["parameters"]:
        if gb_assignment == "all_plus_one":
            gb_values[label] = Fraction(1)

    # Evaluate gamma coefficients
    evaluated_gamma = {}
    for entry in schema2["inhomogeneous_deformation"]["gamma_coefficients"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        coeff_str = entry["gamma_coeff"]
        coeff = evaluate_expr(coeff_str, gb_values)
        if coeff != 0:
            key = (X, Y)
            if key not in evaluated_gamma:
                evaluated_gamma[key] = {}
            evaluated_gamma[key][Z] = evaluated_gamma[key].get(Z, Fraction(0)) + coeff

    # Format as list
    gamma_list = []
    for (X, Y), zcoeffs in evaluated_gamma.items():
        for Z, coeff in zcoeffs.items():
            if coeff != 0:
                gamma_list.append({
                    "X": X, "Y": Y, "Z": Z,
                    "gamma_coeff": str(coeff),
                })

    schema = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "evaluation": {
            "gb_assignment": gb_assignment,
            "gb_values": {label: str(v) for label, v in gb_values.items()},
            "description": "All gb parameters set to +1 (representative sign profile).",
        },
        "evaluated_gamma": {
            "description": (
                "Numerically evaluated gamma cocycle [X,Y]_deformed = [X,Y]_0 + kappa*gamma(X,Y). "
                "All gb = +1."
            ),
            "gamma_coefficients": gamma_list,
        },
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": datetime.date.today().isoformat(),
            "source_schema2": f"C_{n}_gamma.json",
        },
    }
    return schema


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in range(1, 4):
        schema = build_schema3(n)
        out_path = os.path.join(data_dir, f"C_{n}_evaluated.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        n_eval = len(schema["evaluated_gamma"]["gamma_coefficients"])
        print(f"Generated {out_path}: {n_eval} evaluated gamma entries (gb=+1)")


if __name__ == "__main__":
    main()
