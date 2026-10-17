"""
C_evaluated.py: Evaluates the gamma structure (Layer 3: Evaluated Structure)
for C(n+1) = osp(2|2n) at concrete gb deformation parameter assignments.
"""

import json
import os
import sys
from datetime import datetime
from fractions import Fraction
from collections import defaultdict

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.C_gamma import generate_schema_2_dict, get_gb_matrix_info


def evaluate_gamma_constants(gamma_constants, param_values):
    """
    Evaluates gamma structure constants given a dictionary of parameter values.
    param_values: dict mapping parameter name to int, Fraction, or str.
    Returns list of non-zero evaluated entries: {X, Y, Z, coeff, sign_rule}.
    """
    accum = defaultdict(Fraction)
    for entry in gamma_constants:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        par = entry["param"]
        coeff = Fraction(entry["coeff"])
        val = Fraction(param_values.get(par, 0))
        accum[(X, Y, Z)] += coeff * val

    evaluated_list = []
    for (X, Y, Z), total_coeff in sorted(accum.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])):
        if total_coeff != 0:
            c_str = str(total_coeff.numerator) if total_coeff.denominator == 1 else f"{total_coeff.numerator}/{total_coeff.denominator}"
            evaluated_list.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": c_str,
                "sign_rule": "graded"
            })
    return evaluated_list


def build_total_evaluated_bracket(undeformed_struct_consts, evaluated_gamma):
    """
    Build combined representation of [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)|_eval.
    """
    table_0 = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in undeformed_struct_consts}
    table_g = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in evaluated_gamma}

    all_triples = sorted(list(set(table_0.keys()) | set(table_g.keys())))
    total_list = []
    for X, Y, Z in all_triples:
        c0 = table_0.get((X, Y, Z), Fraction(0))
        cg = table_g.get((X, Y, Z), Fraction(0))
        c0_str = str(c0.numerator) if c0.denominator == 1 else f"{c0.numerator}/{c0.denominator}"
        cg_str = str(cg.numerator) if cg.denominator == 1 else f"{cg.numerator}/{cg.denominator}"
        total_list.append({
            "X": X,
            "Y": Y,
            "Z": Z,
            "coeff_undeformed": c0_str,
            "coeff_kappa": cg_str,
            "sign_rule": "graded"
        })
    return total_list


def generate_schema_3_dict(n, profile_name="all_plus_one", custom_param_values=None, schema2_data=None):
    """
    Generate complete Schema 3 dictionary for C(n+1) given a parameter profile.
    """
    if schema2_data is None:
        schema2_data = generate_schema_2_dict(n)

    gb_info = get_gb_matrix_info(n)
    flat_params = gb_info["flat_parameters"]

    if custom_param_values is not None:
        param_values = {p: Fraction(custom_param_values.get(p, 0)) for p in flat_params}
    elif profile_name == "all_plus_one":
        param_values = {p: Fraction(1) for p in flat_params}
    elif profile_name == "alternating_signs":
        # gb_{sigma, j, s} = sgn(sigma) * sgn(s)
        param_values = {}
        for p in flat_params:
            sigma_sign = 1 if "a1p" in p else -1
            s_sign = 1 if p.endswith("p") else -1
            param_values[p] = Fraction(sigma_sign * s_sign)
    else:
        raise ValueError(f"Unknown profile: {profile_name}")

    param_val_strings = {
        p: (str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}")
        for p, v in param_values.items()
    }

    # Evaluate gamma structure constants
    gamma_consts = schema2_data["gamma_structure_constants"]
    eval_gamma = evaluate_gamma_constants(gamma_consts, param_values)

    # Load undeformed structure constants from C_{n}_structure.json if available
    struct_path = os.path.join("data", f"C_{n}_structure.json")
    if os.path.exists(struct_path):
        with open(struct_path, "r", encoding="utf-8") as f:
            struct_data = json.load(f)
            undeformed_consts = struct_data["structure_constants"]
    else:
        # Fallback to computing via C_generators
        from src.C_generators import compute_structure_constants
        undeformed_consts = compute_structure_constants(n)

    total_bracket = build_total_evaluated_bracket(undeformed_consts, eval_gamma)

    schema3 = {
        "schema_version": "5.0",
        "algebra": schema2_data["algebra"],
        "central_elements": schema2_data["central_elements"],
        "evaluated_parameters": {
            "profile_name": profile_name,
            "parameter_values": param_val_strings
        },
        "basis": schema2_data["basis"],
        "parity": schema2_data["parity"],
        "evaluated_gamma_structure_constants": eval_gamma,
        "total_evaluated_bracket": total_bracket,
        "metadata": {
            "generated_by": "src/C_evaluated.py",
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "profile": profile_name,
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "docs/math/C_inhomogeneous_definition.md"
            ]
        }
    }
    return schema3


def generate_all_evaluated_files(output_dir="data", profile_name="all_plus_one"):
    os.makedirs(output_dir, exist_ok=True)
    generated_files = []
    for n in [1, 2, 3]:
        filepath = os.path.join(output_dir, f"C_{n}_evaluated.json")
        print(f"Generating {filepath} for C({n+1}) with profile '{profile_name}'...")
        schema_dict = generate_schema_3_dict(n, profile_name=profile_name)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2, ensure_ascii=False)
        print(f"Saved {filepath} ({len(schema_dict['evaluated_gamma_structure_constants'])} evaluated gamma entries).")
        generated_files.append(filepath)
    return generated_files


if __name__ == "__main__":
    generate_all_evaluated_files()
