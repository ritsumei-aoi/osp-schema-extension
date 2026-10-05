"""
C(n+1) = osp(2|2n) evaluated structure (Schema 3) generator.

Substitutes the representative gb sign profile (Option A: all gb = +1) into
the Schema 2 gamma coefficients and produces Schema 3 JSON files
C_{n}_evaluated.json for n=1, 2, 3.

Schema 3 format: gamma coefficients become rational numbers (numerator/denominator)
after substitution.  Entries with zero total coefficient are omitted.

Usage:
    python src/build_C_evaluated.py
"""

import json
import os
from fractions import Fraction
from collections import defaultdict
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_schema2(n):
    path = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
    with open(path) as f:
        return json.load(f)


def evaluate_gamma(gamma_coefficients, gb_values):
    """
    Substitute gb values into gamma coefficients and sum over gb_key.

    gamma_coefficients: list of dicts with keys X, Y, gb_key, Z, coeff (string fraction)
    gb_values: dict mapping gb_label -> Fraction value

    Returns list of dicts with keys X, Y, Z, coeff (string "p/q" or "p").
    """
    # Accumulate (X, Y, Z) -> Fraction
    acc = defaultdict(Fraction)
    for entry in gamma_coefficients:
        gb_label = entry["gb_key"]
        if gb_label not in gb_values:
            raise KeyError(f"Unknown gb parameter: {gb_label}")
        gb_val = gb_values[gb_label]
        coeff = Fraction(entry["coeff"])
        acc[(entry["X"], entry["Y"], entry["Z"])] += coeff * gb_val

    result = []
    for (X, Y, Z), val in sorted(acc.items()):
        if val == 0:
            continue
        result.append({
            "X": X,
            "Y": Y,
            "Z": Z,
            "coeff": str(val),
        })
    return result


def build_gb_values(schema2):
    """Build the Option A (all +1) gb substitution dict from schema2 metadata."""
    params = schema2["inhomogeneous_deformation"]["gb_matrix"]["parameters"]
    return {p["label"]: Fraction(1) for p in params}


def build_schema3(n):
    schema2 = load_schema2(n)
    gb_values = build_gb_values(schema2)

    evaluated = evaluate_gamma(
        schema2["inhomogeneous_deformation"]["gamma_coefficients"],
        gb_values,
    )

    dim = schema2["algebra"]["dimension"]
    alg = schema2["algebra"]

    schema3 = {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": alg,
        "inhomogeneous_deformation": {
            "deformation_type": "gb",
            "sign_convention": "Option_A",
            "defining_relation": "[bj^s, a1^sigma] = -gb_{sigma,j,s} * kappa",
            "gb_profile": {
                "name": "Option_A_uniform",
                "description": "All gb parameters set to +1 (uniform profile)",
                "assignments": {p["label"]: 1 for p in
                                schema2["inhomogeneous_deformation"]["gb_matrix"]["parameters"]},
            },
            "gamma_description": (
                "Evaluated gamma coefficients after substituting all gb=+1. "
                "gamma(X,Y) = sum_Z coeff(X,Y,Z) * Z. "
                "Records stored for X <= Y in PBW order only. "
                "Graded anti-symmetry: gamma(Y,X) = -(-1)^{p(X)p(Y)} gamma(X,Y)."
            ),
            "gamma_evaluated": evaluated,
        },
        "metadata": {
            "generated_by": "build_C_evaluated.py",
            "generation_date": str(date.today()),
            "source_schema2": f"C_{n}_gamma.json",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "C_inhomogeneous_definition.md",
            ],
        },
    }
    return schema3


def verify_consistency(n, schema2, schema3):
    """
    Check that every (X,Y,Z) entry in schema3 can be traced back to schema2.
    Also verify that the number of distinct (X,Y) pairs matches.
    """
    # Build schema2 set of (X,Y) pairs
    s2_xy = set()
    for e in schema2["inhomogeneous_deformation"]["gamma_coefficients"]:
        s2_xy.add((e["X"], e["Y"]))

    s3_xy = set()
    for e in schema3["inhomogeneous_deformation"]["gamma_evaluated"]:
        s3_xy.add((e["X"], e["Y"]))

    # Every evaluated (X,Y) must exist in schema2
    extra = s3_xy - s2_xy
    if extra:
        raise ValueError(f"n={n}: Schema 3 has (X,Y) pairs not in Schema 2: {extra}")

    # Recompute from scratch and compare
    gb_values = {p["label"]: Fraction(1) for p in
                 schema2["inhomogeneous_deformation"]["gb_matrix"]["parameters"]}
    recomputed = evaluate_gamma(
        schema2["inhomogeneous_deformation"]["gamma_coefficients"], gb_values
    )

    def to_set(entries):
        return {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in entries}

    s3_map = to_set(schema3["inhomogeneous_deformation"]["gamma_evaluated"])
    re_map = to_set(recomputed)

    if s3_map != re_map:
        raise ValueError(f"n={n}: Schema 3 entries do not match recomputed values.")

    return True


def main():
    for n in [1, 2, 3]:
        print(f"Building Schema 3 for n={n} (C({n+1}) = osp(2|{2*n}))...")
        schema3 = build_schema3(n)
        schema2 = load_schema2(n)

        verify_consistency(n, schema2, schema3)
        print(f"  Consistency check passed.")

        count = len(schema3["inhomogeneous_deformation"]["gamma_evaluated"])
        print(f"  Non-zero evaluated entries: {count}")

        out_path = os.path.join(DATA_DIR, f"C_{n}_evaluated.json")
        with open(out_path, "w") as f:
            json.dump(schema3, f, indent=2)
        print(f"  Written: {out_path}")

    print("Done.")


if __name__ == "__main__":
    main()
