"""
C(n+1) Schema 4: Coboundary structure.

Computes coboundary coefficients (δf)_{X,Y,Z} for the odd linear map f: g -> g.
The coboundary formula:
  (δf)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])

The map f is parameterized by coefficients φ_{ij}: f(Z_j) = Σ_i φ_{ij} Z_i
where f is odd, so φ_{ij} ≠ 0 only when p(Z_i) ≠ p(Z_j).
"""

import json
import os
from fractions import Fraction
from C_generators import build_basis, get_parity


def load_schema1(n, data_dir="data"):
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as f:
        return json.load(f)


def build_bracket_lookup(structure_constants, parity):
    """Build a fast lookup for [X, Y} -> {Z: coeff}."""
    bracket = {}
    for sc in structure_constants:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        key = (X, Y)
        if key not in bracket:
            bracket[key] = {}
        bracket[key][Z] = bracket[key].get(Z, Fraction(0)) + coeff
    return bracket


def get_bracket(bracket_table, parity, X, Y):
    if (X, Y) in bracket_table:
        return dict(bracket_table[(X, Y)])
    elif (Y, X) in bracket_table:
        pX = parity[X]
        pY = parity[Y]
        sign = (-1) ** (pX * pY)
        result = {}
        for Z, c in bracket_table[(Y, X)].items():
            result[Z] = -sign * c
        return result
    return {}


def build_phi_parameters(all_gens, parity_dict):
    """Build the list of free parameters φ_{ij} for odd linear map f.

    f is odd: f maps even -> odd and odd -> even.
    So φ_{ij} is nonzero only when p(Z_i) != p(Z_j).
    """
    params = []
    for j, target in enumerate(all_gens):
        for i, source in enumerate(all_gens):
            if parity_dict[source] != parity_dict[target]:
                params.append({
                    "label": f"phi_{source}_{target}",
                    "source": source,
                    "target": target,
                    "source_parity": parity_dict[source],
                    "target_parity": parity_dict[target]
                })
    return params


def compute_coboundary_coefficients(n, data_dir="data"):
    """Compute symbolic coboundary coefficients (δf)(X,Y) for all pairs.

    Returns coefficients as list of {X, Y, Z, phi_param, coeff}.
    Each entry means: (δf)(X,Y) contains coeff * φ_{phi_param} * Z.
    """
    schema1 = load_schema1(n, data_dir)
    parity = schema1["parity"]
    even, odd = build_basis(n)
    all_gens = odd + even

    bracket = build_bracket_lookup(schema1["structure_constants"], parity)

    coboundary_coeffs = []

    for idx_x, X in enumerate(all_gens):
        for idx_y, Y in enumerate(all_gens):
            if idx_y <= idx_x:
                continue

            pX = parity[X]
            pY = parity[Y]

            # Term 1: (-1)^{p(X)} [X, f(Y)]
            # f(Y) = Σ_i φ_{i,Y} Z_i where p(Z_i) ≠ p(Y)
            for fY_gen in all_gens:
                if parity[fY_gen] == parity[Y]:
                    continue
                phi_label = f"phi_{fY_gen}_{Y}"
                sign1 = (-1) ** pX
                bracket_XfY = get_bracket(bracket, parity, X, fY_gen)
                for Z, coeff in bracket_XfY.items():
                    coboundary_coeffs.append({
                        "X": X, "Y": Y, "Z": Z,
                        "phi_param": phi_label,
                        "coeff": str(sign1 * coeff)
                    })

            # Term 2: -(-1)^{(p(X)+1)p(Y)} [Y, f(X)]
            for fX_gen in all_gens:
                if parity[fX_gen] == parity[X]:
                    continue
                phi_label = f"phi_{fX_gen}_{X}"
                sign2 = -((-1) ** ((pX + 1) * pY))
                bracket_YfX = get_bracket(bracket, parity, Y, fX_gen)
                for Z, coeff in bracket_YfX.items():
                    coboundary_coeffs.append({
                        "X": X, "Y": Y, "Z": Z,
                        "phi_param": phi_label,
                        "coeff": str(sign2 * coeff)
                    })

            # Term 3: -f([X, Y])
            bracket_XY = get_bracket(bracket, parity, X, Y)
            for W, c_XY in bracket_XY.items():
                for fW_gen in all_gens:
                    if parity[fW_gen] == parity[W]:
                        continue
                    phi_label = f"phi_{fW_gen}_{W}"
                    coboundary_coeffs.append({
                        "X": X, "Y": Y, "Z": fW_gen,
                        "phi_param": phi_label,
                        "coeff": str(-c_XY)
                    })

    return coboundary_coeffs


def build_schema4_json(n, data_dir="data"):
    even, odd = build_basis(n)
    all_gens = odd + even
    schema1 = load_schema1(n, data_dir)
    parity = schema1["parity"]

    phi_params = build_phi_parameters(all_gens, parity)
    coboundary_coeffs = compute_coboundary_coefficients(n, data_dir)

    schema = {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": schema1["algebra"],
        "coboundary_formula": "(δf)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])",
        "f_description": "Odd linear map f: g -> g, parameterized by φ_{ij}",
        "phi_parameter_count": len(phi_params),
        "coboundary_coefficients": coboundary_coeffs,
        "coboundary_coefficient_count": len(coboundary_coeffs),
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": "2026-10-05",
            "layer": "Schema 4 (coboundary structure)"
        }
    }
    return schema


def generate_all(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Generating Schema 4 for C({n+1}), n={n}...")
        schema = build_schema4_json(n, output_dir)
        filename = os.path.join(output_dir, f"C_{n}_coboundary.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written to {filename}")
        print(f"  φ parameters: {schema['phi_parameter_count']}, "
              f"coboundary coefficients: {schema['coboundary_coefficient_count']}")


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    generate_all(data_dir)
