import json
from fractions import Fraction
from typing import Dict, Any

def evaluate_schema_3(n: int, default_gb_val: int = 1) -> Dict[str, Any]:
    with open(f"data/C_{n}_gamma.json", "r") as f:
        schema2 = json.load(f)

    gb_params = schema2["inhomogeneous_deformation"]["gb_matrix"]["parameters"]
    gb_assignments = {param: default_gb_val for param in gb_params}

    # Start with un-deformed structure constants from Schema 1 / Schema 2
    # Bracket map: (X, Y, Z) -> Fraction
    eval_brackets: Dict[tuple, Fraction] = {}

    for sc in schema2["structure_constants"]:
        key = (sc["X"], sc["Y"], sc["Z"])
        eval_brackets[key] = eval_brackets.get(key, Fraction(0)) + Fraction(sc["coeff"])

    for gsc in schema2["inhomogeneous_deformation"]["gamma_structure_constants"]:
        key = (gsc["X"], gsc["Y"], gsc["Z"])
        gb_val = gb_assignments[gsc["gb_param"]]
        coeff_gamma = Fraction(gsc["coeff"])
        eval_brackets[key] = eval_brackets.get(key, Fraction(0)) + gb_val * coeff_gamma
        if eval_brackets[key] == 0:
            del eval_brackets[key]

    evaluated_sc_list = []
    for (x, y, z), coeff in eval_brackets.items():
        if coeff != 0:
            c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
            evaluated_sc_list.append({
                "X": x,
                "Y": y,
                "Z": z,
                "coeff": c_str
            })

    schema3 = dict(schema2)
    schema3["schema_version"] = "5.0"
    schema3["evaluated_structure"] = {
        "description": f"Evaluated structure constants with all gb parameters set to {default_gb_val}",
        "gb_assignments": gb_assignments,
        "evaluated_structure_constants": evaluated_sc_list
    }

    return schema3


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        data = evaluate_schema_3(n)
        filename = f"data/C_{n}_evaluated.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename} (Evaluated SC count: {len(data['evaluated_structure']['evaluated_structure_constants'])})")
