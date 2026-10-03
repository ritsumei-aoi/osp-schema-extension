"""
C_evaluate.py

Generates Schema 3 (Evaluated Structure) for C(n+1) = osp(2|2n).
Substitutes concrete numerical values for gb parameters into Schema 2.

Representative assignment: all gb = +1 (uniform positive deformation).
"""

from __future__ import annotations
import json
import datetime
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))


def load_schema2(n: int) -> dict:
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", f"C_{n}_gamma.json")
    with open(data_path) as f:
        return json.load(f)


def evaluate_gamma(schema2: dict, gb_values: dict) -> list:
    """
    Substitute concrete gb values into gamma coefficients.
    Returns list of {X, Y, Z, coeff} with numerical coefficients.
    """
    evaluated = {}

    for entry in schema2["gamma_coefficients"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        gb = entry["gb"]
        coeff = Fraction(entry["coeff"])

        # Substitute gb value
        gb_val = Fraction(gb_values.get(gb, 1))
        val = coeff * gb_val

        key = (X, Y, Z)
        evaluated[key] = evaluated.get(key, Fraction(0)) + val

    result = []
    for (X, Y, Z), val in evaluated.items():
        if val != 0:
            result.append({
                "X": X,
                "Y": Y,
                "Z": Z,
                "coeff": str(val),
                "description": f"gamma_evaluated({X},{Y})[{Z}] = {val}"
            })

    return result


def build_schema3(n: int, gb_values: dict = None) -> dict:
    """Build Schema 3 JSON for C(n+1) with bosonic rank n."""
    if gb_values is None:
        # Default: all gb = +1
        from C_gamma import build_gb_params
        params = build_gb_params(n)
        gb_values = {p: 1 for p in params}

    schema2 = load_schema2(n)
    evaluated = evaluate_gamma(schema2, gb_values)

    schema = {
        "schema_version": "5.0",
        "algebra": f"C({n+1})",
        "n": n,
        "description": "Schema 3: Evaluated structure constants for specific gb assignment",
        "gb_assignment": {k: str(v) for k, v in gb_values.items()},
        "evaluated_gamma": evaluated,
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": datetime.date.today().isoformat(),
            "note": "Each entry gamma_evaluated(X,Y)[Z] is the numerical coefficient of Z in (1/kappa)*([X,Y]_gamma - [X,Y]_0).",
            "references": ["docs/math/C_inhomogeneous_definition.md"]
        }
    }
    return schema


def verify_consistency(n: int, schema3: dict) -> bool:
    """
    Verify Schema 3 is consistent with Schema 2:
    All (X,Y,Z) triples in Schema 3 should appear in Schema 2 (possibly with different coeff).
    """
    schema2 = load_schema2(n)
    schema2_triples = set(
        (e["X"], e["Y"], e["Z"]) for e in schema2["gamma_coefficients"]
    )
    schema3_triples = set(
        (e["X"], e["Y"], e["Z"]) for e in schema3["evaluated_gamma"]
    )

    # All evaluated triples must come from schema2 triples
    return schema3_triples.issubset(schema2_triples)


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C_{n}_evaluated.json (C({n+1}) = osp(2|{2*n}))...")
        schema = build_schema3(n)
        n_eval = len(schema["evaluated_gamma"])
        print(f"  gb assignment: all gb = +1")
        print(f"  evaluated gamma entries: {n_eval}")

        ok = verify_consistency(n, schema)
        print(f"  Consistency with Schema 2: {'PASS' if ok else 'FAIL'}")

        out_path = os.path.join(data_dir, f"C_{n}_evaluated.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written to {out_path}")


if __name__ == "__main__":
    main()
