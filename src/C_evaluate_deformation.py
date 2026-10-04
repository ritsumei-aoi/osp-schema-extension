"""
C_evaluate_deformation.py: Evaluates the inhomogeneous deformation for C(n+1) = osp(2|2n)
under specific gb parameter assignments, producing Schema 3 JSON data.
"""

from fractions import Fraction
import json
import os
import sys
from typing import Dict, List, Tuple, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def evaluate_schema_3(n: int, gb_assignment: Optional[Dict[str, int]] = None,
                      data_dir: str = "data") -> Dict[str, Any]:
    """
    Evaluates deformed brackets [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)
    under the given gb parameter assignment (defaults to all +1).
    """
    struct_path = os.path.join(data_dir, f"C_{n}_structure.json")
    gamma_path = os.path.join(data_dir, f"C_{n}_gamma.json")

    with open(struct_path, "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(gamma_path, "r", encoding="utf-8") as f:
        s2 = json.load(f)

    gb_params = s2["gb_matrix"]["parameters"]
    if gb_assignment is None:
        gb_assignment = {p: 1 for p in gb_params}

    # Map unperturbed brackets: (X, Y, Z) -> Fraction
    c0_table: Dict[Tuple[str, str, str], Fraction] = {}
    for item in s1["structure_constants"]:
        c0_table[(item["X"], item["Y"], item["Z"])] = Fraction(item["coeff"])

    # Map gamma brackets: (X, Y, Z) -> Fraction evaluated
    ckappa_table: Dict[Tuple[str, str, str], Fraction] = {}
    for item in s2["inhomogeneous_deformation"]["gamma_structure"]:
        p = item["gb_param"]
        val = gb_assignment.get(p, 0)
        if val != 0:
            key = (item["X"], item["Y"], item["Z"])
            c = Fraction(item["coeff"]) * Fraction(val)
            ckappa_table[key] = ckappa_table.get(key, Fraction(0)) + c

    all_keys = sorted(set(list(c0_table.keys()) + list(ckappa_table.keys())))
    evaluated_brackets = []
    for x, y, z in all_keys:
        c0 = c0_table.get((x, y, z), Fraction(0))
        ck = ckappa_table.get((x, y, z), Fraction(0))
        if c0 != 0 or ck != 0:
            c0_str = str(c0.numerator) if c0.denominator == 1 else f"{c0.numerator}/{c0.denominator}"
            ck_str = str(ck.numerator) if ck.denominator == 1 else f"{ck.numerator}/{ck.denominator}"
            evaluated_brackets.append({
                "X": x,
                "Y": y,
                "Z": z,
                "coeff_unperturbed": c0_str,
                "coeff_kappa": ck_str
            })

    schema_dict = {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "gb_assignment": gb_assignment,
        "evaluated_brackets": evaluated_brackets,
        "metadata": {
            "generated_by": "src/C_evaluate_deformation.py",
            "generation_date": "2026-10-04",
            "assignment_type": "canonical_all_plus_one" if all(v == 1 for v in gb_assignment.values()) else "custom"
        }
    }
    return schema_dict


def save_c_evaluated(n: int, gb_assignment: Optional[Dict[str, int]] = None,
                     output_dir: str = "data") -> str:
    """Generates and writes C_{n}_evaluated.json to output directory."""
    os.makedirs(output_dir, exist_ok=True)
    schema = evaluate_schema_3(n, gb_assignment, data_dir=output_dir)
    filepath = os.path.join(output_dir, f"C_{n}_evaluated.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    return filepath


if __name__ == "__main__":
    for n_val in [1, 2, 3]:
        out_path = save_c_evaluated(n_val)
        print(f"Generated {out_path} for C({n_val+1})")
