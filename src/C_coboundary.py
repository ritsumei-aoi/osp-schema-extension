"""
C_coboundary.py
Generates Schema 4 (Coboundary Structure) for C(n+1) = osp(2|2n).

Mathematical background (docs/math/C_coboundary_definition.md):
  A deformation gamma is trivial iff there exists an odd linear map f: g -> g s.t.
  gamma = delta_f, where:
  (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X, Y])

  f is parametrized by coefficients phi_{ij}: f(Z_j) = sum_i phi_{ij} * Z_i
  The map f reverses parity: even generators map to odd, odd to even.

  In this Schema 4, we compute delta_f symbolically in terms of phi_{ij} parameters.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import build_basis, build_parity, bracket


def phi_label(i, j):
    """Label for phi_{ij} coefficient: f(Z_j) = sum_i phi_ij * Z_i."""
    return f"phi_{i}_{j}"


def compute_coboundary(n, all_basis, parity):
    """
    Compute the coboundary (delta f)(X, Y) symbolically.

    Since f is an odd linear map parametrized by phi_{ij} (only parity-reversing entries are nonzero),
    we compute each (delta f)(X, Y)^Z as a linear combination of phi_{ij} parameters.

    (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X, Y])

    For f(Z_j) = sum_i phi_{ij} Z_i (where p(Z_j) + p(Z_i) = 1 mod 2, i.e., parity-reversing):
    """
    even_gens = [g for g in all_basis if parity[g] == 0]
    odd_gens = [g for g in all_basis if parity[g] == 1]
    basis_idx = {g: i for i, g in enumerate(all_basis)}
    basis_set = set(all_basis)

    # Nonzero phi entries: f maps even -> odd and odd -> even
    # phi_{i,j} is nonzero only when parity[Z_i] != parity[Z_j]
    valid_phi_pairs = []
    for Z_j in all_basis:
        for Z_i in all_basis:
            if parity[Z_i] != parity[Z_j]:
                valid_phi_pairs.append((Z_i, Z_j))

    # f(Z_j) = sum_{Z_i: parity(Z_i)!=parity(Z_j)} phi_{Z_i,Z_j} * Z_i
    def f_of(Z_j):
        """Return dict {Z_i: phi_label(Z_i, Z_j)} for f(Z_j)."""
        result = {}
        for Z_i in all_basis:
            if parity[Z_i] != parity[Z_j]:
                result[Z_i] = phi_label(Z_i, Z_j)
        return result

    # Accumulate coboundary: (X,Y,Z) -> dict {phi_label: coeff}
    coboundary = {}  # (X, Y, Z) -> {phi_lbl: Fraction}

    for i_x, X in enumerate(all_basis):
        for i_y, Y in enumerate(all_basis):
            if i_y <= i_x:
                continue
            px = parity[X]
            py = parity[Y]

            # Term 1: (-1)^{p(X)} [X, f(Y)]
            # f(Y) = sum_i phi_{i,Y} Z_i
            # [X, f(Y)] = sum_i phi_{i,Y} [X, Z_i]
            fY = f_of(Y)
            for Z_i, phi_lbl in fY.items():
                sub = bracket(X, Z_i, n, parity)
                for Z, c in sub.items():
                    if Z not in basis_set:
                        continue
                    sign1 = (-1) ** px
                    coeff = Fraction(sign1) * c
                    key = (X, Y, Z)
                    if key not in coboundary:
                        coboundary[key] = {}
                    coboundary[key][phi_lbl] = coboundary[key].get(phi_lbl, Fraction(0)) + coeff

            # Term 2: -(-1)^{(p(X)+1)*p(Y)} [Y, f(X)]
            fX = f_of(X)
            for Z_i, phi_lbl in fX.items():
                sub = bracket(Y, Z_i, n, parity)
                for Z, c in sub.items():
                    if Z not in basis_set:
                        continue
                    sign2 = -(-1) ** ((px + 1) * py)
                    coeff = Fraction(sign2) * c
                    key = (X, Y, Z)
                    if key not in coboundary:
                        coboundary[key] = {}
                    coboundary[key][phi_lbl] = coboundary[key].get(phi_lbl, Fraction(0)) + coeff

            # Term 3: -f([X, Y])
            xy_bracket = bracket(X, Y, n, parity)
            # f([X,Y]) = sum_{Z: [X,Y]^Z != 0} c_Z * f(Z)
            for Z_j, c_z in xy_bracket.items():
                if Z_j not in basis_set:
                    continue
                fZj = f_of(Z_j)
                for Z_i, phi_lbl in fZj.items():
                    coeff = Fraction(-1) * c_z
                    key = (X, Y, Z_i)
                    if key not in coboundary:
                        coboundary[key] = {}
                    coboundary[key][phi_lbl] = coboundary[key].get(phi_lbl, Fraction(0)) + coeff

    # Convert to list
    result_list = []
    for (X, Y, Z), phi_dict in coboundary.items():
        for phi_lbl, coeff in phi_dict.items():
            if coeff != 0:
                result_list.append({
                    "X": X, "Y": Y, "Z": Z,
                    "phi_param": phi_lbl,
                    "coeff": str(coeff)
                })

    return result_list


def build_schema4(n):
    """Build Schema 4 JSON for C(n+1) with bosonic rank n."""
    even, odd = build_basis(n)
    all_basis = even + odd
    parity = build_parity(even, odd)

    print(f"Computing coboundary for C({n+1}) (n={n})...")
    coboundary_list = compute_coboundary(n, all_basis, parity)
    print(f"  Found {len(coboundary_list)} coboundary coefficient terms.")

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})"}
        },
        "linear_map_f": {
            "description": "Odd linear map f: g -> g parametrized by phi_{i,j}",
            "convention": "f(Z_j) = sum_i phi_{Z_i,Z_j} Z_i where parity(Z_i) != parity(Z_j)",
            "coboundary_formula": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])"
        },
        "coboundary_coefficients": coboundary_list,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": str(date.today()),
            "references": ["docs/math/C_coboundary_definition.md"]
        }
    }


def main():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema4(n)
        fname = f"data/C_{n}_coboundary.json"
        with open(fname, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Written {fname}")


if __name__ == "__main__":
    main()
