"""
C(n+1) Coboundary Structure Generator (Schema 4 Module)
"""
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple, Any

def generate_C_coboundary_json(n: int) -> Dict[str, Any]:
    filepath_struct = f"data/C_{n}_structure.json"
    with open(filepath_struct, "r") as f:
        data_struct = json.load(f)

    basis = data_struct["basis"]["odd"] + data_struct["basis"]["even"]
    parity = data_struct["parity"]
    dim_g = len(basis)

    # Build structure constants map: (X, Y) -> {Z: Fraction}
    sc_map: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in data_struct["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        if (x, y) not in sc_map:
            sc_map[(x, y)] = {}
        sc_map[(x, y)][z] = Fraction(entry["coeff"])

    def get_c(x: str, y: str, z: str) -> Fraction:
        return sc_map.get((x, y), {}).get(z, Fraction(0))

    # Identify all valid odd linear map parameters phi_{i, j} where p(Z_i) = 1 - p(Z_j)
    phi_parameters = []
    phi_keys = []
    for i_idx, z_i in enumerate(basis):
        for j_idx, z_j in enumerate(basis):
            if parity[z_i] == 1 - parity[z_j]:
                param_name = f"phi_{z_i}__{z_j}"
                phi_parameters.append({
                    "name": param_name,
                    "target": z_i,
                    "source": z_j,
                    "target_parity": parity[z_i],
                    "source_parity": parity[z_j]
                })
                phi_keys.append((z_i, z_j, param_name))

    coboundary_terms = []

    # Compute coboundary (delta f)(X, Y) for each phi_{z_i, z_j}
    # (\delta f_{ij})(X, Y) = (-1)^{p(X)} [X, f_{ij}(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f_{ij}(X)] - f_{ij}([X, Y])
    for x in basis:
        px = parity[x]
        for y in basis:
            py = parity[y]

            for (z_i, z_j, param_name) in phi_keys:
                # We want to find the resulting vector (delta f)(X, Y) in basis element W
                # 1. If Y == z_j: (+1) * (-1)^{px} [X, z_i] => coeff on W is (-1)^{px} * c(X, z_i, W)
                # 2. If X == z_j: (-1) * (-1)^{(px+1)*py} [Y, z_i] => coeff on W is - (-1)^{(px+1)*py} * c(Y, z_i, W)
                # 3. If W == z_i: - c(X, Y, z_j)

                res_w: Dict[str, Fraction] = {}

                # Term 1
                if y == z_j:
                    sign1 = -1 if px % 2 == 1 else 1
                    for w in basis:
                        c1 = get_c(x, z_i, w)
                        if c1 != 0:
                            res_w[w] = res_w.get(w, Fraction(0)) + sign1 * c1

                # Term 2
                if x == z_j:
                    sign2 = -1 if ((px + 1) * py) % 2 == 1 else 1
                    for w in basis:
                        c2 = get_c(y, z_i, w)
                        if c2 != 0:
                            res_w[w] = res_w.get(w, Fraction(0)) - sign2 * c2

                # Term 3
                c3 = get_c(x, y, z_j)
                if c3 != 0:
                    res_w[z_i] = res_w.get(z_i, Fraction(0)) - c3

                for w, coeff in res_w.items():
                    if coeff != 0:
                        coboundary_terms.append({
                            "X": x,
                            "Y": y,
                            "Z": w,
                            "phi_param": param_name,
                            "coeff": str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                        })

    schema_json = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})"
        },
        "linear_map_f": {
            "description": "Odd linear map f: g -> g reversing parity (p(f(X)) = 1 - p(X))",
            "phi_matrix_shape": [dim_g, dim_g],
            "parameter_count": len(phi_parameters),
            "parameters": phi_parameters
        },
        "coboundary_terms": coboundary_terms,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "references": [
                "docs/math/C_coboundary_definition.md",
                "docs/json_schema_specification.md"
            ]
        }
    }
    return schema_json

def save_all_C_coboundary_json(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in (1, 2, 3):
        data = generate_C_coboundary_json(n)
        filepath = os.path.join(output_dir, f"C_{n}_coboundary.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {filepath} (phi_count: {data['linear_map_f']['parameter_count']}, coboundary_terms count: {len(data['coboundary_terms'])})")

if __name__ == "__main__":
    save_all_C_coboundary_json()
