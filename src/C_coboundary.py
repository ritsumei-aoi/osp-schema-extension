"""
C_coboundary.py

Computes Schema 4 (Coboundary Structure) for C(n+1) = osp(2|2n).

Mathematical basis: docs/math/C_coboundary_definition.md

The coboundary of an odd linear map f: g -> g is:
  (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])

A deformation gamma is trivial iff gamma = delta f for some odd f.

The odd map f is parametrized by:
  f(Z_j) = sum_i phi_{ij} Z_i
where phi_{ij} != 0 only when p(Z_i) + p(Z_j) = 1 mod 2 (f reverses parity).

For the triviality analysis:
  - Odd generators Z_j (p=1) map to even generators Z_i (p=0)
  - Even generators Z_j (p=0) map to odd generators Z_i (p=1)

We compute the general coboundary (delta f)(X,Y) as a linear combination
of basis elements, with coefficients that are linear in the phi parameters.
This represents the space of all coboundaries.
"""

from __future__ import annotations
import json
import datetime
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))


def load_schema1(n: int) -> dict:
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", f"C_{n}_structure.json")
    with open(data_path) as f:
        return json.load(f)


def build_bracket_map(schema: dict) -> dict:
    """Build (X,Y) -> {Z: coeff} from structure constants."""
    bracket = {}
    for sc in schema["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        key = (X, Y)
        if key not in bracket:
            bracket[key] = {}
        bracket[key][Z] = bracket[key].get(Z, Fraction(0)) + coeff
    return bracket


def compute_coboundary(n: int) -> tuple:
    """
    Compute the general coboundary (delta f)(X,Y) for all basis pairs.

    Returns:
      - coboundary_entries: list of {X, Y, Z, phi_label, coeff}
      - phi_labels: list of phi parameter labels
    """
    schema1 = load_schema1(n)
    basis = schema1["basis"]["odd"] + schema1["basis"]["even"]
    parity = schema1["parity"]
    bracket_map = build_bracket_map(schema1)

    # phi_{ij}: label = phi_{Zi}_{Zj} where p(Zi) != p(Zj)
    # f(Zj) = sum_i phi_{Zi,Zj} * Zi (where p(Zi) != p(Zj))
    # Build phi labels
    phi_labels = []
    phi_map = {}  # (i, j) -> phi_label (generator indices)
    for j, Zj in enumerate(basis):
        for i, Zi in enumerate(basis):
            if (parity[Zi] + parity[Zj]) % 2 == 1:  # p(Zi) != p(Zj)
                lbl = f"phi_{Zi}__{Zj}"
                phi_labels.append(lbl)
                phi_map[(i, j)] = lbl

    # Compute (delta f)(X,Y) for all pairs
    # (delta f)(X,Y) = (-1)^{pX} [X, f(Y)] - (-1)^{(pX+1)*pY} [Y, f(X)] - f([X,Y])
    # where f(Z_j) = sum_i phi_{ij} Z_i

    coboundary_entries = []

    for X_label in basis:
        for Y_label in basis:
            pX = parity[X_label]
            pY = parity[Y_label]

            # Collect contributions to (delta f)(X,Y) as {Z: {phi_label: coeff}}
            contributions = {}  # Z_label -> {phi_label: total_coeff}

            # Term 1: (-1)^{pX} [X, f(Y)]
            # f(Y) = sum_i phi_{Zi,Y} * Zi (where p(Zi) != p(Y))
            sign1 = Fraction((-1) ** pX)
            j_Y = basis.index(Y_label)
            for i, Zi in enumerate(basis):
                if (i, j_Y) not in phi_map:
                    continue
                phi_lbl = phi_map[(i, j_Y)]
                # [X, Zi} = sum_W f^W_{X,Zi} W
                inner = bracket_map.get((X_label, Zi), {})
                for W_label, c in inner.items():
                    if W_label not in contributions:
                        contributions[W_label] = {}
                    contributions[W_label][phi_lbl] = \
                        contributions[W_label].get(phi_lbl, Fraction(0)) + sign1 * c

            # Term 2: -(-1)^{(pX+1)*pY} [Y, f(X)]
            sign2 = Fraction(-((-1) ** ((pX + 1) * pY)))
            j_X = basis.index(X_label)
            for i, Zi in enumerate(basis):
                if (i, j_X) not in phi_map:
                    continue
                phi_lbl = phi_map[(i, j_X)]
                inner = bracket_map.get((Y_label, Zi), {})
                for W_label, c in inner.items():
                    if W_label not in contributions:
                        contributions[W_label] = {}
                    contributions[W_label][phi_lbl] = \
                        contributions[W_label].get(phi_lbl, Fraction(0)) + sign2 * c

            # Term 3: -f([X,Y})
            # [X,Y} = sum_k f^k_{XY} Z_k
            # f([X,Y}) = sum_k f^k_{XY} * f(Z_k) = sum_k f^k_{XY} sum_i phi_{Zi,Zk} Zi
            bracket_XY = bracket_map.get((X_label, Y_label), {})
            for Z_k_label, c_k in bracket_XY.items():
                j_k = basis.index(Z_k_label)
                for i, Zi in enumerate(basis):
                    if (i, j_k) not in phi_map:
                        continue
                    phi_lbl = phi_map[(i, j_k)]
                    # -f([X,Y}) contribution: -c_k * phi_{Zi,Zk} * Zi
                    if Zi not in contributions:
                        contributions[Zi] = {}
                    contributions[Zi][phi_lbl] = \
                        contributions[Zi].get(phi_lbl, Fraction(0)) + (-c_k)

            # Flatten to entries
            for W_label, phi_dict in contributions.items():
                for phi_lbl, coeff in phi_dict.items():
                    if coeff != 0:
                        coboundary_entries.append({
                            "X": X_label,
                            "Y": Y_label,
                            "Z": W_label,
                            "phi": phi_lbl,
                            "coeff": str(coeff),
                            "description": f"(delta f)({X_label},{Y_label})[{W_label}] += {coeff} * {phi_lbl}"
                        })

    return coboundary_entries, phi_labels


def build_schema4(n: int) -> dict:
    """Build Schema 4 JSON for C(n+1) with bosonic rank n."""
    coboundary_entries, phi_labels = compute_coboundary(n)

    schema = {
        "schema_version": "5.0",
        "algebra": f"C({n+1})",
        "n": n,
        "description": "Schema 4: Coboundary structure for C(n+1). (delta f)(X,Y) for general odd linear map f.",
        "f_map": {
            "description": "Odd linear map f: g -> g parametrized by phi_{Zi,Zj} where p(Zi) != p(Zj)",
            "convention": "f(Z_j) = sum_i phi_{Zi,Zj} * Z_i",
            "phi_labels": phi_labels,
            "total_parameters": len(phi_labels)
        },
        "coboundary_formula": "(-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])",
        "coboundary_coefficients": coboundary_entries,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": ["docs/math/C_coboundary_definition.md"]
        }
    }
    return schema


def verify_consistency_with_schema1(n: int, schema4: dict) -> bool:
    """Check all Z generators in coboundary entries are in Schema 1 basis."""
    schema1 = load_schema1(n)
    basis_set = set(schema1["basis"]["odd"] + schema1["basis"]["even"])
    for entry in schema4["coboundary_coefficients"]:
        if entry["Z"] not in basis_set:
            return False
    return True


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C_{n}_coboundary.json (C({n+1}) = osp(2|{2*n}))...")
        schema = build_schema4(n)
        n_cobound = len(schema["coboundary_coefficients"])
        n_phi = schema["f_map"]["total_parameters"]
        print(f"  phi parameters (f map): {n_phi}")
        print(f"  coboundary entries: {n_cobound}")

        ok = verify_consistency_with_schema1(n, schema)
        print(f"  Consistency with Schema 1: {'PASS' if ok else 'FAIL'}")

        out_path = os.path.join(data_dir, f"C_{n}_coboundary.json")
        with open(out_path, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written to {out_path}")


if __name__ == "__main__":
    main()
