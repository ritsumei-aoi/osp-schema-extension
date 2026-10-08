"""
C_evaluate.py
Layer 3: Evaluate Schema 2 gamma coefficients at a specific gb assignment.
Default assignment: all gb parameters = +1.

The coeff_expr in Schema 2 is a linear polynomial in gb labels.
Substitution: parse coeff_expr, replace each gb_label with its numeric value,
and sum the result.
"""

import json
import os
import re
from fractions import Fraction

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def parse_coeff_expr(expr, gb_values):
    """
    Parse a linear expression in gb labels and evaluate to Fraction.
    Format: "c1*gb_xxx + c2*gb_yyy + ..."
    where c_i are rational numbers or absent (meaning 1 or -1).
    """
    if expr == "0":
        return Fraction(0)

    total = Fraction(0)
    # Split on " + " and " - ", preserving sign
    # Normalize: replace " - " with " + -"
    expr_norm = expr.strip().replace(" - ", " + -")
    terms = [t.strip() for t in expr_norm.split(" + ") if t.strip()]

    for term in terms:
        if not term:
            continue
        # Check for "*" separator between coeff and gb_label
        if "*" in term:
            coeff_str, gb_lbl = term.split("*", 1)
            coeff_str = coeff_str.strip()
            gb_lbl = gb_lbl.strip()
            if "/" in coeff_str:
                num, den = coeff_str.split("/")
                coeff = Fraction(int(num), int(den))
            else:
                coeff = Fraction(int(coeff_str))
        else:
            # Term is just a gb_label (coeff=1) or -gb_label (coeff=-1)
            gb_lbl = term.strip()
            if gb_lbl.startswith("-"):
                coeff = Fraction(-1)
                gb_lbl = gb_lbl[1:]
            else:
                coeff = Fraction(1)

        gb_val = gb_values.get(gb_lbl, Fraction(0))
        total += coeff * gb_val

    return total


def rational_str(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def build_evaluated(n, gb_values=None):
    """
    Evaluate the gamma coefficients for the given gb assignment.
    gb_values: dict {gb_label: Fraction}. Defaults to all +1.
    """
    gamma_path = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
    with open(gamma_path) as f:
        s2 = json.load(f)

    params = s2["inhomogeneous_deformation"]["gb_matrix"]["parameters"]

    if gb_values is None:
        gb_values = {p["label"]: Fraction(1) for p in params}

    gb_assignment = {p["label"]: rational_str(gb_values.get(p["label"], Fraction(1)))
                     for p in params}

    evaluated = []
    for entry in s2["inhomogeneous_deformation"]["gamma_coefficients"]:
        val = parse_coeff_expr(entry["coeff_expr"], gb_values)
        if val != 0:
            evaluated.append({
                "X": entry["X"],
                "Y": entry["Y"],
                "Z": entry["Z"],
                "coeff": rational_str(val)
            })

    struct_path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(struct_path) as f:
        s1 = json.load(f)

    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "basis": s1["basis"],
        "parity": s1["parity"],
        "gb_assignment": gb_assignment,
        "evaluated_gamma": evaluated,
        "metadata": {
            "generated_by": "C_evaluate.py",
            "generation_date": "2026-10-09",
            "source_gamma": f"C_{n}_gamma.json",
            "assignment_rule": "all gb = +1"
        }
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Evaluating C({n+1}) at gb=+1...", end=" ", flush=True)
        schema = build_evaluated(n)
        path = os.path.join(DATA_DIR, f"C_{n}_evaluated.json")
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
        ne = len(schema["evaluated_gamma"])
        print(f"done. evaluated_gamma entries={ne}")


if __name__ == "__main__":
    main()
