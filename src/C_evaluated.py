#!/usr/bin/env python3
"""
src/C_evaluated.py

Generate Schema 3 (Evaluated Structure) for C(n+1) = osp(2|2n).
Outputs C_{n}_evaluated.json for n = 1, 2, 3.

gb sign profile: Option A — all 4n parameters set to +1.

Schema 3 stores two sub-tables:
  structure_constants        : Schema 1 entries unchanged (kappa=0 part)
  kappa_structure_constants  : Evaluated gamma entries with numeric coefficients
                               (gb parameters substituted; collected by (X,Y,Z))
"""

import json
import os
from fractions import Fraction
from datetime import date


DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load(n: int):
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    with open(os.path.join(DATA, f"C_{n}_gamma.json")) as f:
        s2 = json.load(f)
    return s1, s2


def _frac_str(f: Fraction) -> str:
    return str(f) if f.denominator != 1 else str(f.numerator)


def build_evaluated_schema(n: int, gb_value: int = 1) -> dict:
    s1, s2 = load(n)

    # ── Evaluate gamma entries (substitute gb = gb_value) ─────────────────────
    # Collect (X, Y, Z) -> Fraction by summing over gb_terms
    kappa_accum: dict = {}
    for e in s2["inhomogeneous_deformation"]["gamma_entries"]:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        total = Fraction(0)
        for t in e["gb_terms"]:
            total += Fraction(t["scalar"]) * Fraction(gb_value)
        if total:
            key = (X, Y, Z)
            kappa_accum[key] = kappa_accum.get(key, Fraction(0)) + total

    kappa_sc = [
        {"X": X, "Y": Y, "Z": Z,
         "coeff": _frac_str(c),
         "sign_rule": "graded"}
        for (X, Y, Z), c in kappa_accum.items()
        if c
    ]

    # gb profile description
    gb_count = s2["inhomogeneous_deformation"]["gb_count"]
    gb_profile = {lbl: gb_value
                  for row in s2["inhomogeneous_deformation"]["gb_matrix"]["labels"]
                  for lbl in row}

    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": s1["algebra"],
        "schema1_ref": f"C_{n}_structure.json",
        "schema2_ref": f"C_{n}_gamma.json",
        "evaluation": {
            "profile_name": "all_ones",
            "description": f"All {gb_count} gb parameters set to {gb_value}",
            "gb_values": gb_profile,
        },
        "structure_constants": s1["structure_constants"],
        "kappa_structure_constants": kappa_sc,
        "metadata": {
            "generated_by": "src/C_evaluated.py",
            "generation_date": date.today().isoformat(),
            "n": n,
            "structure_constant_count": len(s1["structure_constants"]),
            "kappa_structure_constant_count": len(kappa_sc),
            "references": s1["metadata"].get("references", []),
        },
    }


def main():
    for n in [1, 2, 3]:
        print(f"Evaluating C({n+1}) = osp(2|{2*n}), n={n}  [gb=1 for all]...")
        schema = build_evaluated_schema(n, gb_value=1)
        out = os.path.join(DATA, f"C_{n}_evaluated.json")
        with open(out, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  structure_constants        : {schema['metadata']['structure_constant_count']}")
        print(f"  kappa_structure_constants  : {schema['metadata']['kappa_structure_constant_count']}")
        print(f"  written: {out}")


if __name__ == "__main__":
    main()
