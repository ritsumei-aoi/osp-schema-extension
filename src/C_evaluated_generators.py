import os
import sys
import json
from fractions import Fraction
from typing import Dict, List, Tuple, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.C_generators import CSuperalgebra
from src.C_gamma_generators import get_all_gb_params


def evaluate_structure(n: int, gb_assignment: Dict[str, int] = None) -> Dict[str, Any]:
    # Load Schema 1 and Schema 2
    with open(f"data/C_{n}_structure.json", "r") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json", "r") as f:
        s2 = json.load(f)

    gb_params = s2["gb_matrix"]["parameters"]
    if gb_assignment is None:
        # Default representative assignment: all +1
        gb_assignment = {p: 1 for p in gb_params}

    # Map (X, Y, Z) -> c0
    undeformed_map: Dict[Tuple[str, str, str], Fraction] = {}
    for entry in s1["structure_constants"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        undeformed_map[key] = Fraction(entry["coeff"])

    # Map (X, Y, Z) -> gamma_evaluated = sum gb * gamma
    gamma_eval_map: Dict[Tuple[str, str, str], Fraction] = {}
    for entry in s2["inhomogeneous_deformation"]["gamma_structure"]:
        p = entry["gb_param"]
        val = gb_assignment.get(p, 0)
        if val != 0:
            key = (entry["X"], entry["Y"], entry["Z"])
            c = Fraction(entry["coeff"]) * Fraction(val)
            gamma_eval_map[key] = gamma_eval_map.get(key, Fraction(0)) + c
            if gamma_eval_map[key] == Fraction(0):
                del gamma_eval_map[key]

    # Combine all (X, Y, Z) keys
    all_keys = sorted(list(set(undeformed_map.keys()).union(set(gamma_eval_map.keys()))))

    evaluated_brackets = []
    for (X, Y, Z) in all_keys:
        c0 = undeformed_map.get((X, Y, Z), Fraction(0))
        c_gamma = gamma_eval_map.get((X, Y, Z), Fraction(0))

        c0_str = str(c0.numerator) if c0.denominator == 1 else f"{c0.numerator}/{c0.denominator}"
        c_gamma_str = str(c_gamma.numerator) if c_gamma.denominator == 1 else f"{c_gamma.numerator}/{c_gamma.denominator}"

        evaluated_brackets.append({
            "X": X,
            "Y": Y,
            "Z": Z,
            "c0": c0_str,
            "c_kappa": c_gamma_str,
            "formula": f"({c0_str}) + ({c_gamma_str})*kappa" if c_gamma != 0 else c0_str
        })

    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "gb_assignment": gb_assignment,
        "evaluated_brackets_count": len(evaluated_brackets),
        "evaluated_structure_constants": evaluated_brackets,
        "metadata": {
            "generated_by": "C_evaluated_generators.py",
            "generation_date": "2026-10-05",
            "source_files": [f"data/C_{n}_structure.json", f"data/C_{n}_gamma.json"]
        }
    }


def generate_all_schema3():
    for n in [1, 2, 3]:
        data = evaluate_structure(n)
        out_path = f"data/C_{n}_evaluated.json"
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {out_path}: {data['evaluated_brackets_count']} evaluated bracket entries.")


if __name__ == "__main__":
    generate_all_schema3()
