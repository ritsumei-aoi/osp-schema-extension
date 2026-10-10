"""Schema 3 (evaluated structure) generator for C(n+1) (I06).

Substitutes a concrete numeric assignment for the 4n gb parameters into the
symbolic Schema 2 gamma structure and emits C_{n}_evaluated.json.

Default representative assignment: all gb = +1.

Usage: python3 src/C_evaluate.py
"""

import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import DATA_DIR
from C_gamma import gb_labels


def load_gamma(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_gamma.json")) as f:
        return json.load(f)


def evaluate_gamma(n, assignment, gamma_data=None):
    """Evaluate symbolic gamma at a gb assignment {label: Fraction}.

    Returns a list of {X, Y, Z, coeff} records (coeff as exact-rational str),
    omitting terms that evaluate to zero.
    """
    gamma_data = gamma_data or load_gamma(n)
    records = []
    for e in gamma_data["inhomogeneous_deformation"]["entries"]:
        acc = {}
        for t in e["terms"]:
            val = assignment[t["gb"]] * Fraction(t["coeff"])
            if val:
                acc[t["Z"]] = acc.get(t["Z"], Fraction(0)) + val
        for z, c in sorted(acc.items()):
            if c != 0:
                records.append({"X": e["X"], "Y": e["Y"], "Z": z, "coeff": str(c)})
    return records


def schema3(n, assignment_name="all_plus_one", assignment=None):
    labels = gb_labels(n)
    if assignment is None:
        assignment = {l: Fraction(1) for l in labels}
    assert set(assignment) == set(labels)
    gamma_data = load_gamma(n)
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra_ref": f"C_{n}_structure.json",
        "gamma_ref": f"C_{n}_gamma.json",
        "gb_assignment_name": assignment_name,
        "gb_assignment": {l: str(assignment[l]) for l in labels},
        "evaluated_gamma": evaluate_gamma(n, assignment, gamma_data),
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": ["docs/math/C_inhomogeneous_definition.md"],
        },
    }


def check_against_schema2(n, data):
    """Re-evaluate symbolic gamma at the stored assignment; must match."""
    assignment = {l: Fraction(v) for l, v in data["gb_assignment"].items()}
    fresh = evaluate_gamma(n, assignment)
    return data["evaluated_gamma"] == fresh


def main():
    for n in (1, 2, 3):
        data = schema3(n)
        path = os.path.join(DATA_DIR, f"C_{n}_evaluated.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=1)
        ok = check_against_schema2(n, data)
        print(
            f"C({n + 1}): gb = all +1, {len(data['evaluated_gamma'])} evaluated "
            f"records -> {os.path.relpath(path)} "
            f"[Schema 2 consistency: {'PASS' if ok else 'FAIL'}]"
        )


if __name__ == "__main__":
    main()
