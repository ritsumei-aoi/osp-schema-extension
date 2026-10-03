"""
C_coboundary.py

Produces Schema 4 (Coboundary Structure) for C(n+1) = osp(2|2n).

Computes the coboundary (delta f)(X,Y) for an odd linear map f: g -> g.

The coboundary is defined as:
  (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X, Y])

Since f is odd: f maps parity-0 elements to parity-1 and vice versa.
f is parametrized by coefficients phi_{ij}:
  f(Z_j) = sum_i phi_{ij} Z_i

For the general odd linear map f on C(n+1), phi_{ij} != 0 only when p(Z_i) + p(Z_j) = 1 mod 2.

This file:
1. Computes (delta f)(X,Y) symbolically in terms of phi coefficients.
2. Outputs the coboundary as a Schema 4 JSON.

The coboundary coefficients (delta f)_{XYZ} are expressed as linear combinations of phi_{ij}.

Output: C_{n}_coboundary.json for n=1, 2, 3.
"""

import json
import os
from fractions import Fraction
from datetime import date


def load_structure(n):
    path = os.path.join("data", f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def build_bracket_dict(sc_list):
    """Build {(X,Y): {Z: Fraction}} from structure_constants list."""
    d = {}
    for e in sc_list:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        c = Fraction(e["coeff"])
        d.setdefault((X, Y), {})
        d[(X, Y)][Z] = d[(X, Y)].get(Z, Fraction(0)) + c
    # Remove zeros
    return {k: {z: c for z, c in v.items() if c != 0} for k, v in d.items()}


def compute_coboundary(n):
    """
    Compute the coboundary (delta f)_{XYZ} in terms of phi_{ij} coefficients.

    f: g -> g is odd: f(Z_j) = sum_i phi_{ij} Z_i
    where p(Z_i) + p(Z_j) = 1 (f reverses parity).

    (delta f)(X,Y) has component Z:
      coeff = sum_{phi_{ij}} c_{XYZ, phi_{ij}} * phi_{ij}

    Returns dict: {(X,Y,Z): {phi_label: Fraction}}
    """
    schema = load_structure(n)
    all_basis = schema["basis"]["even"] + schema["basis"]["odd"]
    parity = schema["parity"]
    sc_list = schema["structure_constants"]
    bd = build_bracket_dict(sc_list)

    def bkt(X, Y):
        return dict(bd.get((X, Y), {}))

    # phi_label: phi_{Z_i, Z_j} where p(Z_i) != p(Z_j)
    # Means f(Z_j) has Z_i component phi_{Z_i,Z_j}

    coboundary = {}  # {(X,Y,Z): {phi_label: Fraction}}

    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]

            # Compute (delta f)(X,Y):
            # = (-1)^{pX} [X, f(Y)] - (-1)^{(pX+1)*pY} [Y, f(X)] - f([X,Y])

            # Term 1: (-1)^{pX} [X, f(Y)]
            # f(Y) = sum_i phi_{i,Y} Z_i (where p(Z_i) = 1 - pY)
            # [X, f(Y)] = sum_i phi_{i,Y} [X, Z_i]
            # So Term 1 = (-1)^{pX} sum_i phi_{i,Y} [X, Z_i]
            sign1 = Fraction((-1) ** pX)
            for Zi in all_basis:
                if parity[Zi] != (1 - pY) % 2:
                    continue  # f(Y) maps parity pY to parity 1-pY
                phi_label = f"phi_{Zi}_{Y}"
                bXZi = bkt(X, Zi)
                for Z, c in bXZi.items():
                    key = (X, Y, Z)
                    if key not in coboundary:
                        coboundary[key] = {}
                    coboundary[key][phi_label] = (
                        coboundary[key].get(phi_label, Fraction(0)) + sign1 * c
                    )

            # Term 2: -(-1)^{(pX+1)*pY} [Y, f(X)]
            # f(X) = sum_i phi_{i,X} Z_i (where p(Z_i) = 1 - pX)
            # [Y, f(X)] = sum_i phi_{i,X} [Y, Z_i]
            sign2 = Fraction(-1) * Fraction((-1) ** ((pX + 1) * pY))
            for Zi in all_basis:
                if parity[Zi] != (1 - pX) % 2:
                    continue
                phi_label = f"phi_{Zi}_{X}"
                bYZi = bkt(Y, Zi)
                for Z, c in bYZi.items():
                    key = (X, Y, Z)
                    if key not in coboundary:
                        coboundary[key] = {}
                    coboundary[key][phi_label] = (
                        coboundary[key].get(phi_label, Fraction(0)) + sign2 * c
                    )

            # Term 3: -f([X,Y])
            # [X,Y] = sum_W c_W W
            # f([X,Y]) = f(sum_W c_W W) = sum_W c_W f(W) = sum_W c_W sum_i phi_{i,W} Z_i
            # - f([X,Y]) = -sum_W c_W sum_i phi_{i,W} Z_i
            bXY = bkt(X, Y)
            for W, cW in bXY.items():
                for Zi in all_basis:
                    if parity[Zi] != (1 - parity[W]) % 2:
                        continue
                    phi_label = f"phi_{Zi}_{W}"
                    key = (X, Y, Zi)
                    if key not in coboundary:
                        coboundary[key] = {}
                    coboundary[key][phi_label] = (
                        coboundary[key].get(phi_label, Fraction(0)) - cW
                    )

    # Clean up zeros
    result = {}
    for key, phi_dict in coboundary.items():
        clean = {lbl: v for lbl, v in phi_dict.items() if v != 0}
        if clean:
            result[key] = clean

    return result


def build_coboundary_schema(n):
    """Build Schema 4 JSON for C(n+1)."""
    schema_struct = load_structure(n)
    all_basis = schema_struct["basis"]["even"] + schema_struct["basis"]["odd"]
    parity = schema_struct["parity"]

    coboundary = compute_coboundary(n)

    # Build phi parameter labels (all odd linear map coefficients)
    phi_labels = []
    for Zi in all_basis:
        for Zj in all_basis:
            if parity[Zi] != parity[Zj]:  # f reverses parity
                phi_labels.append(f"phi_{Zi}_{Zj}")

    # Format coboundary entries
    cb_list = []
    for (X, Y, Z), phi_dict in sorted(coboundary.items()):
        entry = {
            "X": X,
            "Y": Y,
            "Z": Z,
            "coboundary_coeff": {lbl: str(c) for lbl, c in sorted(phi_dict.items())},
        }
        cb_list.append(entry)

    schema = {
        "schema_version": "5.0",
        "algebra": f"C({n+1})",
        "n": n,
        "layer": 4,
        "description": (
            "Coboundary structure: (delta f)(X,Y) for odd linear map f: g -> g. "
            "Entries express (delta f)(X,Y)[Z] as linear combinations of phi_{i,j} coefficients."
        ),
        "coboundary_definition": {
            "formula": "(delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])",
            "f_parametrization": "f(Z_j) = sum_i phi_{i,j} Z_i, where p(Z_i) + p(Z_j) = 1 mod 2",
        },
        "phi_parameters": {
            "count": len(phi_labels),
            "description": "phi_{Z_i, Z_j} for p(Z_i) != p(Z_j)",
        },
        "coboundary_coefficients": cb_list,
        "summary": {
            "non_zero_coboundary_entries": len(cb_list),
            "phi_parameter_count": len(phi_labels),
            "basis_size": len(all_basis),
        },
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": str(date.today()),
            "schema1_reference": f"C_{n}_structure.json",
            "math_reference": "docs/math/C_coboundary_definition.md",
        },
    }
    return schema, coboundary


def verify_coboundary(n, coboundary, parity):
    """
    Verify that coboundary entries have correct parity.
    (delta f)(X,Y) has parity p(X)+p(Y)+1 mod 2 (odd, since f is odd).
    """
    errors = []
    all_basis_parities = parity
    for (X, Y, Z), phi_dict in coboundary.items():
        expected_pZ = (all_basis_parities[X] + all_basis_parities[Y] + 1) % 2
        if all_basis_parities[Z] != expected_pZ:
            errors.append(
                f"Parity error (delta f)({X},{Y})[{Z}]: "
                f"expected parity {expected_pZ}, got {all_basis_parities[Z]}"
            )
    return errors


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Building C_{n}_coboundary.json (C({n+1}) = osp(2|{2*n}))...")
        schema, coboundary = build_coboundary_schema(n)

        struct_schema = load_structure(n)
        parity = struct_schema["parity"]
        errors = verify_coboundary(n, coboundary, parity)
        if errors:
            print(f"  ERRORS for n={n}:")
            for e in errors[:5]:
                print(f"    {e}")
        else:
            print(f"  Parity consistency: OK")

        outfile = f"data/C_{n}_coboundary.json"
        with open(outfile, "w") as f:
            json.dump(schema, f, indent=2)
        s = schema["summary"]
        print(f"  Non-zero coboundary entries: {s['non_zero_coboundary_entries']}")
        print(f"  phi parameter count: {s['phi_parameter_count']}")
        print(f"  Written to {outfile}")


if __name__ == "__main__":
    main()
