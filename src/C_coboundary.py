"""
Schema 4 (coboundary structure) generator for C(n+1) = osp(2|2n).

Computes the coboundary delta_f of an odd linear map f: g -> g.

The coboundary operator (from C_coboundary_definition.md):
  (delta_f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])

f is parameterized by coefficients phi_{ij}:
  f(Z_j) = sum_i phi_{ij} Z_i

Since f is odd, if p(Z_j) = 0 then p(f(Z_j)) = 1, and vice versa.
Non-zero phi_{ij} only allowed when p(Z_i) != p(Z_j).

For Schema 4, we compute the coboundary structure symbolically in terms of phi_{ij},
so each coboundary entry is a linear combination of phi parameters.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (
    build_basis, build_parity_dict, build_generator_realizations,
    compute_structure_constants
)


def build_phi_labels(n):
    """
    Build all allowed phi_{ij} labels for the odd linear map f: g -> g.

    f(Z_j) = sum_i phi_{ij} Z_i, where p(Z_i) != p(Z_j).

    Returns list of (i_label, j_label, phi_label) triples.
    """
    even_basis, odd_basis = build_basis(n)
    parity = build_parity_dict(even_basis, odd_basis)
    basis = odd_basis + even_basis

    phi_labels = []
    for j, Zj in enumerate(basis):
        for i, Zi in enumerate(basis):
            if parity[Zi] != parity[Zj]:
                label = f"phi_{Zi}_{Zj}"
                phi_labels.append((Zi, Zj, label))
    return phi_labels


def compute_coboundary(n):
    """
    Compute coboundary coefficients (delta_f)_{XY,Z} for C(n+1).

    Each entry: {X, Y, Z, phi_coeffs: {phi_label: Fraction}}
    meaning (delta_f)(X,Y) has component coeff in direction Z,
    as a linear function of the phi parameters.

    (delta_f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])
    """
    even_basis, odd_basis = build_basis(n)
    basis = odd_basis + even_basis
    parity = build_parity_dict(even_basis, odd_basis)

    # Load structure constants (undeformed)
    with open(f"data/C_{n}_structure.json") as f:
        s1 = json.load(f)

    # Build bracket lookup: bra[(X,Y)] = {Z: coeff}
    bra = {}
    for entry in s1["structure_constants"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        key = (X, Y)
        if key not in bra:
            bra[key] = {}
        bra[key][Z] = bra[key].get(Z, Fraction(0)) + Fraction(entry["coeff"])

    def bracket(X, Y):
        """Return {Z: Fraction} for [X,Y]."""
        pX, pY = parity[X], parity[Y]
        if (X, Y) in bra:
            return dict(bra[(X, Y)])
        elif (Y, X) in bra:
            raw = bra[(Y, X)]
            sign = Fraction((-1) ** (pX * pY + 1))
            return {Z: sign * c for Z, c in raw.items() if c != 0}
        return {}

    def add_elem(e1, e2):
        result = dict(e1)
        for Z, c in e2.items():
            result[Z] = result.get(Z, Fraction(0)) + c
        return {Z: c for Z, c in result.items() if c != 0}

    def scale_elem(e, s):
        return {Z: s * c for Z, c in e.items() if s * c != 0}

    # f(Zj) = sum_i phi_{ij} Z_i, stored as dict {Zj: {(phi_label, Zi): Fraction}}
    # We'll compute (delta_f)(X,Y) as a linear combination of phi parameters.
    # Result: {(X,Y,Z): {phi_label: Fraction}}

    coboundary = {}  # {(X,Y,Z): {phi_label: Fraction}}

    def add_phi(X, Y, Z, phi_label, coeff):
        key = (X, Y, Z)
        if key not in coboundary:
            coboundary[key] = {}
        coboundary[key][phi_label] = coboundary[key].get(phi_label, Fraction(0)) + coeff

    # Get phi labels
    phi_triples = build_phi_labels(n)  # (Zi, Zj, phi_label)

    # For each pair (X, Y) and each phi parameter phi_{Zi,Zj}:
    # Contribution of phi_{Zi,Zj} to (delta_f)(X,Y):
    #   - (-1)^{p(X)} [X, f(Y)] contributes when Zj = Y: (-1)^{p(X)} * [X, Zi] * phi_{Zi,Y}
    #   - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] contributes when Zj = X: sign2 * [Y, Zi] * phi_{Zi,X}
    #   - f([X,Y]) contributes when Zj = Z' for each Z' s.t. [X,Y] has component Z': phi_{Zi,Z'} * c_{XY,Z'}

    for xi, X in enumerate(basis):
        for yi, Y in enumerate(basis):
            pX, pY = parity[X], parity[Y]
            bXY = bracket(X, Y)

            # Term 1: (-1)^{p(X)} [X, f(Y)]
            # f(Y) = sum_i phi_{Zi, Y} * Zi (where p(Zi) != p(Y))
            s1_sign = Fraction((-1) ** pX)
            for Zi, Zj, phi_label in phi_triples:
                if Zj != Y:
                    continue
                # Contribution: s1_sign * [X, Zi] * phi_label
                bXZi = bracket(X, Zi)
                for Z, c in bXZi.items():
                    add_phi(X, Y, Z, phi_label, s1_sign * c)

            # Term 2: -(-1)^{(p(X)+1)*p(Y)} [Y, f(X)]
            s2_sign = Fraction(-(-1) ** ((pX + 1) * pY))
            for Zi, Zj, phi_label in phi_triples:
                if Zj != X:
                    continue
                # Contribution: s2_sign * [Y, Zi] * phi_label
                bYZi = bracket(Y, Zi)
                for Z, c in bYZi.items():
                    add_phi(X, Y, Z, phi_label, s2_sign * c)

            # Term 3: -f([X,Y])
            # [X,Y] = sum_{Z'} c_{XY,Z'} Z'
            # -f([X,Y]) = -sum_{Z'} c_{XY,Z'} * f(Z') = -sum_{Z',Zi} c_{XY,Z'} * phi_{Zi,Z'} * Zi
            for Zprime, cXY in bXY.items():
                for Zi, Zj, phi_label in phi_triples:
                    if Zj != Zprime:
                        continue
                    # Contribution: -cXY * phi_label to Z=Zi
                    add_phi(X, Y, Zi, phi_label, -cXY)

    # Clean up zeros
    result = []
    for (X, Y, Z), phi_dict in coboundary.items():
        phi_dict = {k: v for k, v in phi_dict.items() if v != 0}
        if phi_dict:
            result.append({
                "X": X, "Y": Y, "Z": Z,
                "phi_coeffs": {k: str(v) for k, v in phi_dict.items()}
            })

    return result


def build_schema4(n):
    """Build Schema 4 JSON."""
    phi_triples = build_phi_labels(n)
    phi_labels = [t[2] for t in phi_triples]
    coboundary_entries = compute_coboundary(n)

    schema = {
        "schema_version": "5.0",
        "algebra_ref": f"C_{n}_structure.json",
        "coboundary": {
            "description": "Coboundary delta_f of odd linear map f: g -> g",
            "formula": "(delta_f)(X,Y) = (-1)^{p(X)} [X,f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y,f(X)] - f([X,Y])",
            "f_parameterization": "f(Z_j) = sum_i phi_{ij} Z_i, p(Z_i) != p(Z_j)",
            "phi_labels": phi_labels,
            "n_phi": len(phi_labels),
            "coboundary_coefficients": coboundary_entries
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": str(date.today()),
            "n_coboundary_entries": len(coboundary_entries)
        }
    }
    return schema


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Computing coboundary C_{n}_coboundary.json (n={n})...")
        schema = build_schema4(n)
        fname = f"data/C_{n}_coboundary.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        cb = schema["coboundary"]
        print(f"  Done: {schema['metadata']['n_coboundary_entries']} coboundary entries, "
              f"{cb['n_phi']} phi parameters.")


if __name__ == "__main__":
    main()
