"""Schema 3: Evaluated structure for C(n+1).

Substitutes concrete numerical/sign assignments for the gb matrix deformation
parameters into the symbolic Schema 2 gamma structure.

Generates:
  data/C_{n}_evaluated.json for n=1, 2, 3
"""

from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import sys

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def evaluate_gamma_structure(gamma_data, gb_assignment=None, profile_name="all_ones"):
    """Evaluates symbolic gamma coefficients using a concrete assignment of gb parameters."""
    all_gbs = [p for row in gamma_data["gb_matrix"]["matrix"] for p in row]

    if gb_assignment is None:
        gb_assignment = {p: Fraction(1) for p in all_gbs}
    else:
        gb_assignment = {p: Fraction(gb_assignment.get(p, 1)) for p in all_gbs}

    eval_dict = defaultdict(Fraction)
    for entry in gamma_data["inhomogeneous_deformation"]["gamma_coefficients"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        gb = entry["gb"]
        coeff = Fraction(entry["coeff"])
        eval_dict[(x, y, z)] += coeff * gb_assignment[gb]

    evaluated_entries = []
    all_gens = gamma_data["basis"]["odd"] + gamma_data["basis"]["even"]
    for x in all_gens:
        for y in all_gens:
            for z in all_gens:
                val = eval_dict.get((x, y, z), Fraction(0))
                if val != 0:
                    val_str = str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
                    evaluated_entries.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "coeff": val_str,
                    })

    return gb_assignment, evaluated_entries


def generate_schema3_json(n, input_path=None, output_path=None, gb_assignment=None, profile_name="all_ones"):
    if input_path is None:
        input_path = f"data/C_{n}_gamma.json"
    if output_path is None:
        output_path = f"data/C_{n}_evaluated.json"

    with open(input_path, "r", encoding="utf-8") as f:
        gamma_data = json.load(f)

    assignment, evaluated_entries = evaluate_gamma_structure(
        gamma_data, gb_assignment=gb_assignment, profile_name=profile_name
    )

    data = {
        "schema_version": "5.0",
        "algebra": gamma_data["algebra"],
        "central_elements": gamma_data["central_elements"],
        "gb_assignment": {
            "profile": profile_name,
            "values": {k: str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}" for k, v in assignment.items()},
        },
        "basis": gamma_data["basis"],
        "parity": gamma_data["parity"],
        "evaluated_deformation": {
            "description": f"Evaluated gamma coefficients under the '{profile_name}' parameter assignment",
            "sign_rule": "graded",
            "total_evaluated_terms": len(evaluated_entries),
            "evaluated_coefficients": evaluated_entries,
        },
        "metadata": {
            "generated_by": "src/C_evaluated.py",
            "generation_date": "2026-10-04",
            "source_file": str(input_path),
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "docs/math/Cn1_definition.md",
            ],
        },
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def main():
    for n in [1, 2, 3]:
        out = f"data/C_{n}_evaluated.json"
        print(f"Generating Schema 3 for n={n} -> {out}...")
        generate_schema3_json(n, output_path=out)
        print(f"Done generating {out}.")


if __name__ == "__main__":
    main()
