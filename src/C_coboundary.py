"""
C_coboundary.py - Coboundary generator (Layer 4) for C(n+1) = osp(2|2n).

Computes the coboundary delta f for odd linear maps f: g -> g.
Outputs Schema 4 JSON files to data/C_{n}_coboundary.json (n=1, 2, 3).
"""

import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple, Any


def generate_schema4_data(n: int) -> Dict[str, Any]:
    filepath_s1 = f"data/C_{n}_structure.json"
    with open(filepath_s1, "r", encoding="utf-8") as f:
        s1_data = json.load(f)

    basis_odd = s1_data["basis"]["odd"]
    basis_even = s1_data["basis"]["even"]
    full_basis = basis_odd + basis_even
    parity = s1_data["parity"]

    # Build bracket lookup table: (X, Y) -> Dict[Z, Fraction]
    bracket_dict: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in s1_data["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        if (x, y) not in bracket_dict:
            bracket_dict[(x, y)] = {}
        bracket_dict[(x, y)][z] = c

    # Parameterize odd linear maps f: g -> g
    # f(Z_j) = Z_i where p(Z_i) != p(Z_j)
    # Map basis: f_{i, j} for (Z_i in odd, Z_j in even) and (Z_i in even, Z_j in odd)
    f_params: List[Tuple[str, str]] = []
    # Block 1: even -> odd
    for zj in basis_even:
        for zi in basis_odd:
            f_params.append((zi, zj))
    # Block 2: odd -> even
    for zj in basis_odd:
        for zi in basis_even:
            f_params.append((zi, zj))

    f_param_names = [f"phi_{zi}__{zj}" for zi, zj in f_params]

    # Compute coboundary delta f_{i,j} for all pairs (X, Y)
    # (delta f_{i,j})(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    coboundary_structure = []

    for zi, zj in f_params:
        f_param_name = f"phi_{zi}__{zj}"
        pj = parity[zj]
        pi = parity[zi]

        for a_idx, za in enumerate(full_basis):
            pa = parity[za]
            for b_idx, zb in enumerate(full_basis):
                pb = parity[zb]

                # Accumulate Z coefficients for this (za, zb)
                z_coeffs: Dict[str, Fraction] = {}

                # Term 1: (-1)^{p(X)} [X, f(Y)]
                # Non-zero only if zb == zj, then f(Y) = zi
                if zb == zj:
                    sign1 = -1 if pa == 1 else 1
                    br_a_i = bracket_dict.get((za, zi), {})
                    for zk, c in br_a_i.items():
                        z_coeffs[zk] = z_coeffs.get(zk, Fraction(0)) + sign1 * c

                # Term 2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                # Non-zero only if za == zj, then f(X) = zi
                if za == zj:
                    sign2_exp = (pa + 1) * pb
                    sign2 = -1 if (sign2_exp % 2 == 1) else 1
                    factor2 = -sign2
                    br_b_i = bracket_dict.get((zb, zi), {})
                    for zk, c in br_b_i.items():
                        z_coeffs[zk] = z_coeffs.get(zk, Fraction(0)) + factor2 * c

                # Term 3: - f([X, Y])
                # [za, zb] = sum_k c_{ab}^k zk. If zk == zj, f(zj) = zi with coeff -c_{ab}^j
                br_a_b = bracket_dict.get((za, zb), {})
                if zj in br_a_b:
                    c_ab_j = br_a_b[zj]
                    z_coeffs[zi] = z_coeffs.get(zi, Fraction(0)) - c_ab_j

                for zk, c_val in z_coeffs.items():
                    if c_val != 0:
                        coboundary_structure.append({
                            "X": za,
                            "Y": zb,
                            "Z": zk,
                            "f_param": f_param_name,
                            "coeff": str(c_val.numerator) if c_val.denominator == 1 else f"{c_val.numerator}/{c_val.denominator}"
                        })

    schema4_data = {
        "schema_version": "5.0",
        "algebra": s1_data["algebra"],
        "central_elements": s1_data["central_elements"],
        "oscillator_generators": s1_data["oscillator_generators"],
        "oscillator_relations": s1_data["oscillator_relations"],
        "basis": s1_data["basis"],
        "parity": s1_data["parity"],
        "generator_realization": s1_data["generator_realization"],
        "f_map_parameters": {
            "description": "Basis parameters for odd linear maps f: g -> g (reversing parity)",
            "count": len(f_param_names),
            "parameters": f_param_names
        },
        "coboundary_operator": {
            "description": "Symbolic coboundary coefficients (delta f)_{ab}^k(phi_{i,j}) where (delta f)(X,Y) = (-1)^{p(X)}[X, f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y, f(X)] - f([X,Y])",
            "f_dim": len(f_param_names),
            "terms_count": len(coboundary_structure),
            "coboundary_structure": coboundary_structure
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": "2026-10-05",
            "references": [
                "docs/math/C_coboundary_definition.md",
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }

    return schema4_data


def generate_all_schema4_files(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        schema4 = generate_schema4_data(n)
        filepath = os.path.join(output_dir, f"C_{n}_coboundary.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(schema4, f, indent=2)
        terms = schema4["coboundary_operator"]["terms_count"]
        f_dim = schema4["coboundary_operator"]["f_dim"]
        print(f"Generated {filepath}: {terms} coboundary terms across {f_dim} f-map parameters.")


if __name__ == "__main__":
    generate_all_schema4_files()
