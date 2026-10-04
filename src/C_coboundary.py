"""
C_coboundary.py: Computes the coboundary operator delta f (Schema 4 / Layer 4)
for C(n+1) = osp(2|2n) across n=1, 2, 3.
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.C_generators import format_fraction


def compute_coboundary_structure(n, structure_json_path=None):
    if structure_json_path is None:
        structure_json_path = f"data/C_{n}_structure.json"

    with open(structure_json_path, "r") as f:
        data = json.load(f)

    basis = data["basis"]["even"] + data["basis"]["odd"]
    parity = data["parity"]

    bracket_map = defaultdict(lambda: defaultdict(Fraction))
    for entry in data["structure_constants"]:
        bracket_map[(entry["X"], entry["Y"])][entry["Z"]] = Fraction(entry["coeff"])

    # Odd linear maps basis: f_{ij} maps j_gen -> i_gen where p(i_gen) != p(j_gen)
    odd_maps = []
    coboundary_coefficients = []

    for i_gen in basis:
        for j_gen in basis:
            if parity[i_gen] == parity[j_gen]:
                continue
            phi_id = f"phi_{i_gen}_to_{j_gen}"
            odd_maps.append({
                "id": phi_id,
                "target": i_gen,
                "source": j_gen,
                "target_parity": parity[i_gen],
                "source_parity": parity[j_gen]
            })

            # Compute delta f_{ij}(X, Y)
            for X in basis:
                pX = parity[X]
                for Y in basis:
                    pY = parity[Y]
                    coeff_dict = defaultdict(Fraction)

                    # Term 1: (-1)^pX delta_{Y, j_gen} [X, i_gen]
                    if Y == j_gen:
                        sign1 = (-1) ** pX
                        for Z, c in bracket_map.get((X, i_gen), {}).items():
                            coeff_dict[Z] += sign1 * c

                    # Term 2: -(-1)^{(pX+1)pY} delta_{X, j_gen} [Y, i_gen]
                    if X == j_gen:
                        sign2 = - ((-1) ** ((pX + 1) * pY))
                        for Z, c in bracket_map.get((Y, i_gen), {}).items():
                            coeff_dict[Z] += sign2 * c

                    # Term 3: - c_{X, Y}^j * i_gen
                    c_xy_j = bracket_map.get((X, Y), {}).get(j_gen, Fraction(0))
                    if c_xy_j != 0:
                        coeff_dict[i_gen] -= c_xy_j

                    for Z, coeff in coeff_dict.items():
                        if coeff != 0:
                            coboundary_coefficients.append({
                                "X": X,
                                "Y": Y,
                                "Z": Z,
                                "phi_id": phi_id,
                                "coeff": format_fraction(coeff)
                            })

    schema4_data = {
        "schema_version": "5.0",
        "layer": "Schema 4: Coboundary Structure",
        "algebra": data["algebra"],
        "basis": data["basis"],
        "parity": parity,
        "odd_map_basis": odd_maps,
        "coboundary_coefficients": coboundary_coefficients,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": "2026-10-04",
            "references": [
                "docs/math/C_coboundary_definition.md",
                "Frappat et al. (2000)"
            ]
        }
    }
    return schema4_data


def generate_all_coboundary_files(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = compute_coboundary_structure(n)
        filepath = os.path.join(output_dir, f"C_{n}_coboundary.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filepath} ({len(data['odd_map_basis'])} map params, {len(data['coboundary_coefficients'])} coboundary terms)")


if __name__ == "__main__":
    generate_all_coboundary_files()
