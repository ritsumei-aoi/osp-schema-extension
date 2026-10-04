"""Schema 4: Coboundary structure for C(n+1).

Implements:
1. Definition and parameterization of the odd linear map space Hom_{1}(g, g).
2. Computation of coboundary coefficients (delta f)_{abc}(phi) from:
   (delta f)(X, Y) = (-1)^p(X) [X, f(Y)] - (-1)^((p(X)+1)p(Y)) [Y, f(X)] - f([X, Y]).
3. Generation of Schema 4 JSON files: data/C_{n}_coboundary.json for n=1, 2, 3.
"""

from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import sys

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def compute_coboundary_structure(n, struct_path=None):
    if struct_path is None:
        struct_path = f"data/C_{n}_structure.json"

    with open(struct_path, "r", encoding="utf-8") as f:
        sdata = json.load(f)

    all_gens = sdata["basis"]["odd"] + sdata["basis"]["even"]
    parities = sdata["parity"]

    c_table = defaultdict(dict)
    for sc in sdata["structure_constants"]:
        c_table[(sc["X"], sc["Y"])][sc["Z"]] = Fraction(sc["coeff"])

    def br(x, y):
        return c_table.get((x, y), {})

    # Elementary odd map basis: phi_{i, j} where f(Zj) = Zi with p(Zi) != p(Zj)
    odd_map_parameters = []
    for zi in all_gens:
        for zj in all_gens:
            if parities[zi] != parities[zj]:
                param_name = f"phi_{zi}_{zj}"
                odd_map_parameters.append((param_name, zi, zj))

    # Evaluate elementary coboundaries for all basis pairs (X, Y) with X <= Y
    coboundary_coefficients = []
    for param_name, zi, zj in odd_map_parameters:
        for x in all_gens:
            px = parities[x]
            for y in all_gens:
                py = parities[y]
                # delta f(X, Y) = (-1)^pX [X, f(Y)] - (-1)^((pX+1)pY) [Y, f(X)] - f([X, Y])
                res = defaultdict(Fraction)

                # Term 1: delta_{Y, Zj} (-1)^pX [X, Zi]
                if y == zj:
                    s1 = -1 if (px % 2 == 1) else 1
                    for z, c in br(x, zi).items():
                        res[z] += s1 * c

                # Term 2: - delta_{X, Zj} (-1)^((pX+1)pY) [Y, Zi]
                if x == zj:
                    s2 = -1 if (((px + 1) * py) % 2 == 1) else 1
                    for z, c in br(y, zi).items():
                        res[z] -= s2 * c

                # Term 3: - c_{XY}^j Zi
                c_xy_j = br(x, y).get(zj, Fraction(0))
                if c_xy_j != 0:
                    res[zi] -= c_xy_j

                for z in all_gens:
                    val = res.get(z, Fraction(0))
                    if val != 0:
                        val_str = str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
                        coboundary_coefficients.append({
                            "X": x,
                            "Y": y,
                            "Z": z,
                            "phi": param_name,
                            "coeff": val_str,
                        })

    return sdata, odd_map_parameters, coboundary_coefficients


def generate_schema4_json(n, struct_path=None, output_path=None):
    if struct_path is None:
        struct_path = f"data/C_{n}_structure.json"
    if output_path is None:
        output_path = f"data/C_{n}_coboundary.json"

    sdata, odd_map_parameters, coboundary_coefficients = compute_coboundary_structure(n, struct_path=struct_path)

    param_list = [p[0] for p in odd_map_parameters]

    data = {
        "schema_version": "5.0",
        "algebra": sdata["algebra"],
        "central_elements": sdata["central_elements"],
        "basis": sdata["basis"],
        "parity": sdata["parity"],
        "odd_linear_map_space": {
            "description": "Basis of odd linear maps f: g -> g reversing parity, f(Zj) = Zi",
            "total_dimension": len(param_list),
            "parameters": param_list,
        },
        "coboundary_operator": {
            "description": "(delta f)(X, Y) = (-1)^p(X)[X, f(Y)] - (-1)^((p(X)+1)p(Y))[Y, f(X)] - f([X, Y])",
            "sign_rule": "graded",
            "total_terms": len(coboundary_coefficients),
            "coboundary_coefficients": coboundary_coefficients,
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": "2026-10-04",
            "source_structure_file": str(struct_path),
            "references": [
                "docs/math/C_coboundary_definition.md",
                "docs/math/Cn1_definition.md",
            ],
        },
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


def main():
    for n in [1, 2, 3]:
        out = f"data/C_{n}_coboundary.json"
        print(f"Generating Schema 4 for n={n} -> {out}...")
        generate_schema4_json(n, output_path=out)
        print(f"Done generating {out}.")


if __name__ == "__main__":
    main()
