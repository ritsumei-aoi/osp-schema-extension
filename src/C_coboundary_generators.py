import os
import sys
import json
from fractions import Fraction
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.verify_C_structure import load_structure

def get_phi_params(basis, parity):
    # f: g -> g is an odd linear map (p(f) = 1)
    # f(V) = sum_U phi_{U, V} U where p(U) = 1 - p(V)
    # Target U can also be central element K (parity 0) when V is odd (parity 1)
    extended_basis = list(basis) + ["K"]
    extended_parity = dict(parity)
    extended_parity["K"] = 0

    params = {} # phi_name -> {"target": U, "source": V, "parity": 1}
    for V in basis:
        p_V = parity[V]
        for U in extended_basis:
            p_U = extended_parity[U]
            if p_U == 1 - p_V:
                phi_name = f"phi_{U}_{V}"
                params[phi_name] = {
                    "target": U,
                    "source": V,
                    "parity": 1
                }
    return params

def generate_c_coboundary(n):
    struct_path = f"data/C_{n}_structure.json"
    if not os.path.exists(struct_path):
        raise FileNotFoundError(f"Missing structure file: {struct_path}")

    basis, parity, brackets = load_structure(struct_path)
    all_basis = list(basis) # odd < even in PBW order
    phi_params = get_phi_params(basis, parity)

    coboundary_coeffs = []

    # Iterate over all pairs X <= Y in PBW order
    for i in range(len(all_basis)):
        for j in range(i, len(all_basis)):
            X = all_basis[i]
            Y = all_basis[j]
            p_X = parity[X]
            p_Y = parity[Y]

            # (delta f)(X, Y) = (-1)^p_X [X, f(Y)} - (-1)^((p_X+1)p_Y) [Y, f(X)\} - f([X, Y\})
            sign1 = -1 if p_X == 1 else 1
            sign2 = -1 if ((p_X + 1) * p_Y) % 2 == 1 else 1

            # Dict: (phi_param, Z) -> Fraction coeff
            contributions = {}

            # 1. Term 1: (-1)^p_X [X, f(Y)\}
            # f(Y) = sum_V phi_{V, Y} V. [X, V\} = sum_Z c_{XV}^Z Z
            for V in basis:
                if parity[V] == 1 - p_Y or V == "K":
                    phi_name = f"phi_{V}_{Y}"
                    if phi_name in phi_params:
                        for Z, c_XV_Z in brackets[(X, V)].items():
                            if c_XV_Z != 0:
                                val = sign1 * c_XV_Z
                                key = (phi_name, Z)
                                contributions[key] = contributions.get(key, Fraction(0)) + val

            # 2. Term 2: - (-1)^((p_X+1)p_Y) [Y, f(X)\}
            # f(X) = sum_U phi_{U, X} U. [Y, U\} = sum_Z c_{YU}^Z Z
            for U in basis:
                if parity[U] == 1 - p_X or U == "K":
                    phi_name = f"phi_{U}_{X}"
                    if phi_name in phi_params:
                        for Z, c_YU_Z in brackets[(Y, U)].items():
                            if c_YU_Z != 0:
                                val = -sign2 * c_YU_Z
                                key = (phi_name, Z)
                                contributions[key] = contributions.get(key, Fraction(0)) + val

            # 3. Term 3: - f([X, Y\})
            # [X, Y\} = sum_W c_{XY}^W W. f(W) = sum_Z phi_{Z, W} Z
            for W, c_XY_W in brackets[(X, Y)].items():
                if c_XY_W != 0:
                    for Z in list(basis) + ["K"]:
                        phi_name = f"phi_{Z}_{W}"
                        if phi_name in phi_params:
                            val = -c_XY_W
                            key = (phi_name, Z)
                            contributions[key] = contributions.get(key, Fraction(0)) + val

            for (phi_name, Z), coeff in sorted(contributions.items()):
                if coeff != 0:
                    c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                    coboundary_coeffs.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "phi_param": phi_name,
                        "coeff": c_str
                    })

    with open(struct_path, "r") as f:
        s1 = json.load(f)

    schema_data = {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "odd_linear_map_f": {
            "description": "Odd linear map f: g -> g parameterized by phi_{U, V}",
            "parameter_count": len(phi_params),
            "phi_parameters": phi_params
        },
        "coboundary_structure": {
            "description": "Coboundary coefficients (delta f)_{XY}^Z = sum_{U,V} c * phi_{U,V}",
            "coboundary_coefficients": coboundary_coeffs
        },
        "metadata": {
            "generated_by": "src/C_coboundary_generators.py",
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }

    return schema_data

def main():
    os.makedirs("data", exist_ok=True)
    for n in (1, 2, 3):
        data = generate_c_coboundary(n)
        filename = f"data/C_{n}_coboundary.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename}: phi_params={data['odd_linear_map_f']['parameter_count']}, coboundary_coefficients={len(data['coboundary_structure']['coboundary_coefficients'])}")

if __name__ == "__main__":
    main()
