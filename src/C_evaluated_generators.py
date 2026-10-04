import os
import sys
import json
from fractions import Fraction
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def generate_c_evaluated(n, assignment=None):
    struct_path = f"data/C_{n}_structure.json"
    gamma_path = f"data/C_{n}_gamma.json"

    with open(struct_path, "r") as f:
        s1 = json.load(f)
    with open(gamma_path, "r") as f:
        s2 = json.load(f)

    gb_params = s2["gb_matrix"]["parameters"]

    # Default assignment: all gb parameters set to 1
    if assignment is None:
        assignment = {param: Fraction(1) for param in gb_params}

    # Map (X, Y, Z) -> Fraction base_coeff
    base_constants = {}
    for entry in s1["structure_constants"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        base_constants[(X, Y, Z)] = Fraction(entry["coeff"])

    # Map (X, Y, Z) -> Fraction gamma_eval_coeff
    gamma_eval = {}
    for entry in s2["inhomogeneous_deformation"]["gamma_coefficients"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        param = entry["gb_param"]
        coeff = Fraction(entry["coeff"])
        val = assignment[param]
        gamma_eval[(X, Y, Z)] = gamma_eval.get((X, Y, Z), Fraction(0)) + coeff * val

    all_keys = set(base_constants.keys()) | set(gamma_eval.keys())

    evaluated_list = []
    for (X, Y, Z) in sorted(all_keys):
        c_base = base_constants.get((X, Y, Z), Fraction(0))
        c_gamma = gamma_eval.get((X, Y, Z), Fraction(0))
        c_total = c_base + c_gamma

        fmt = lambda f: str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"

        evaluated_list.append({
            "X": X,
            "Y": Y,
            "Z": Z,
            "base_coeff": fmt(c_base),
            "gamma_coeff": fmt(c_gamma),
            "total_coeff": fmt(c_total)
        })

    assignment_json = {k: fmt(v) for k, v in assignment.items()}

    schema_data = {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "gb_assignment": assignment_json,
        "evaluated_structure_constants": evaluated_list,
        "metadata": {
            "generated_by": "src/C_evaluated_generators.py",
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "references": ["Frappat et al. (2000)"]
        }
    }

    return schema_data

def main():
    os.makedirs("data", exist_ok=True)
    for n in (1, 2, 3):
        data = generate_c_evaluated(n)
        filename = f"data/C_{n}_evaluated.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename}: evaluated_entries={len(data['evaluated_structure_constants'])}")

if __name__ == "__main__":
    main()
