"""
C_evaluate.py — Schema 3: evaluate gamma structure at specific gb values.

Substitutes concrete numerical values for gb parameters and produces
evaluated structure constants for the deformed bracket.

Default assignment: all gb = +1 (sign profile: all positive).
Additional profiles: all -1, mixed signs.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_schema2(n):
    path = os.path.join(DATA_DIR, f'C_{n}_gamma.json')
    with open(path) as f:
        return json.load(f)


def load_schema1(n):
    path = os.path.join(DATA_DIR, f'C_{n}_structure.json')
    with open(path) as f:
        return json.load(f)


def evaluate_gamma(gamma_entries, gb_assignment):
    """
    Substitute gb values into symbolic gamma entries.
    Returns list of {X, Y, Z, coeff} with concrete numerical coefficients.
    """
    evaluated = {}
    for entry in gamma_entries:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        gb_lbl = entry['gb_label']
        sym_coeff = Fraction(entry['coeff'])
        gb_val = Fraction(gb_assignment.get(gb_lbl, 0))
        num_coeff = sym_coeff * gb_val
        if num_coeff != 0:
            key = (X, Y, Z)
            evaluated[key] = evaluated.get(key, Fraction(0)) + num_coeff

    result = []
    for (X, Y, Z), c in evaluated.items():
        if c != 0:
            result.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c)})
    return result


def build_schema3(n, gb_assignment, label="all_plus_1"):
    """Build Schema 3 JSON for given gb assignment."""
    s1 = load_schema1(n)
    s2 = load_schema2(n)

    # Combine structure constants (undeformed) and evaluated gamma
    sc_undeformed = [e for e in s1['structure_constants'] if e['Z'] != 'K']
    gamma_eval = evaluate_gamma(s2['gamma_coefficients'], gb_assignment)

    # Merge: deformed SC = undeformed SC + evaluated gamma
    merged = {}
    for entry in sc_undeformed:
        key = (entry['X'], entry['Y'], entry['Z'])
        merged[key] = merged.get(key, Fraction(0)) + Fraction(entry['coeff'])
    for entry in gamma_eval:
        key = (entry['X'], entry['Y'], entry['Z'])
        merged[key] = merged.get(key, Fraction(0)) + Fraction(entry['coeff'])

    deformed_sc = []
    for (X, Y, Z), c in merged.items():
        if c != 0:
            deformed_sc.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c)})

    return {
        "schema_version": "5.0",
        "algebra": s1['algebra'],
        "gb_assignment": {k: str(v) for k, v in gb_assignment.items()},
        "gb_assignment_label": label,
        "evaluated_gamma": gamma_eval,
        "deformed_structure_constants": deformed_sc,
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": str(date.today()),
            "description": (
                "Deformed bracket [X,Y]_gb = [X,Y]_0 + sum_Z gamma(X,Y)^Z * Z "
                "evaluated at the given gb assignment."
            )
        }
    }


def default_gb_assignment(n, value=1):
    """Return gb assignment with all parameters set to value."""
    params = {}
    for sigma in ["p", "m"]:
        for j in range(1, n + 1):
            for s in ["p", "m"]:
                params[f"gb_{sigma}_{j}_{s}"] = Fraction(value)
    return params


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in [1, 2, 3]:
        gb = default_gb_assignment(n, value=1)
        print(f"Generating C_{n}_evaluated.json (n={n}, gb=+1)...")
        schema = build_schema3(n, gb, label="all_plus_1")
        path = os.path.join(DATA_DIR, f'C_{n}_evaluated.json')
        with open(path, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"  Evaluated gamma entries: {len(schema['evaluated_gamma'])}")
        print(f"  Deformed SC (non-zero): {len(schema['deformed_structure_constants'])}")
    print("Done.")


if __name__ == "__main__":
    main()
