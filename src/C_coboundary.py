"""
C(n+1) = osp(2|2n) Layer 4: Coboundary structure.

Computes the coboundary (δf)(X,Y) for an odd linear map f: g -> g,
parameterized by coefficients φ_{ij}.

Formula: (δf)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])
"""

import json
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, __import__('os').path.dirname(__file__))
from C_generators import build_basis, build_parity


def load_bracket_table(structure_data):
    """Build bracket lookup from structure constants."""
    table = {}
    parity = structure_data["parity"]
    for sc in structure_data["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        key = (X, Y)
        if key not in table:
            table[key] = {}
        table[key][Z] = table[key].get(Z, Fraction(0)) + coeff
    return table


def bracket(table, parity_map, X, Y):
    """Return {Z: coeff} for [X, Y}."""
    if (X, Y) in table:
        return dict(table[(X, Y)])
    elif (Y, X) in table:
        sign = Fraction(-1) ** (parity_map[X] * parity_map[Y])
        return {Z: -sign * c for Z, c in table[(Y, X)].items()}
    return {}


def build_f_params(all_gens, parity_map):
    """Build symbolic parameters for the odd linear map f.
    f reverses parity, so f(even) -> odd, f(odd) -> even.
    Parameters: phi_{Z,X} where p(Z) = 1 - p(X)."""
    params = []
    param_map = {}
    for X in all_gens:
        pX = parity_map[X]
        target_parity = 1 - pX
        targets = [Z for Z in all_gens if parity_map[Z] == target_parity]
        for Z in targets:
            param_name = f"phi_{Z}_{X}"
            params.append(param_name)
            if X not in param_map:
                param_map[X] = []
            param_map[X].append((Z, param_name))
    return params, param_map


def compute_coboundary_symbolic(structure_data):
    """Compute (δf)(X,Y) symbolically in terms of φ parameters.

    Returns list of {X, Y, Z, phi_param, coeff} entries.
    """
    basis_even = structure_data["basis"]["even"]
    basis_odd = structure_data["basis"]["odd"]
    all_gens = basis_odd + basis_even
    parity_map = structure_data["parity"]
    table = load_bracket_table(structure_data)
    phi_params, param_map = build_f_params(all_gens, parity_map)

    coboundary_entries = []

    for i_idx, X in enumerate(all_gens):
        for j_idx, Y in enumerate(all_gens):
            if j_idx <= i_idx:
                continue
            pX = parity_map[X]
            pY = parity_map[Y]

            for W, phi_param in param_map.get(Y, []):
                sign1 = Fraction(-1) ** pX
                br = bracket(table, parity_map, X, W)
                for Z, c in br.items():
                    coboundary_entries.append({
                        "X": X, "Y": Y, "Z": Z,
                        "phi_param": phi_param,
                        "coeff": str(sign1 * c),
                    })

            for W, phi_param in param_map.get(X, []):
                sign2 = -Fraction(-1) ** ((pX + 1) * pY)
                br = bracket(table, parity_map, Y, W)
                for Z, c in br.items():
                    coboundary_entries.append({
                        "X": X, "Y": Y, "Z": Z,
                        "phi_param": phi_param,
                        "coeff": str(sign2 * c),
                    })

            xy_bracket = bracket(table, parity_map, X, Y)
            for W, c_w in xy_bracket.items():
                if W == "scalar":
                    continue
                for Z, phi_param in param_map.get(W, []):
                    coboundary_entries.append({
                        "X": X, "Y": Y, "Z": Z,
                        "phi_param": phi_param,
                        "coeff": str(-c_w),
                    })

    merged = {}
    for entry in coboundary_entries:
        key = (entry["X"], entry["Y"], entry["Z"], entry["phi_param"])
        merged[key] = merged.get(key, Fraction(0)) + Fraction(entry["coeff"])

    result = []
    for (X, Y, Z, phi), coeff in merged.items():
        if coeff != 0:
            result.append({
                "X": X, "Y": Y, "Z": Z,
                "phi_param": phi, "coeff": str(coeff),
            })
    return result


def generate_schema4(n):
    with open(f"data/C_{n}_structure.json") as f:
        structure_data = json.load(f)

    all_gens = structure_data["basis"]["odd"] + structure_data["basis"]["even"]
    parity_map = structure_data["parity"]
    phi_params, _ = build_f_params(all_gens, parity_map)

    coboundary = compute_coboundary_symbolic(structure_data)

    schema4 = {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": structure_data["algebra"],
        "odd_linear_map_f": {
            "description": "Odd linear map f: g -> g parameterized by phi coefficients",
            "parameter_count": len(phi_params),
            "parameters": phi_params,
            "parity_rule": "f reverses parity: f(even) in odd, f(odd) in even",
        },
        "coboundary_coefficients": coboundary,
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": str(date.today()),
            "source_schema": f"C_{n}_structure.json",
        },
    }
    return schema4


def main():
    for n in [1, 2, 3]:
        print(f"Generating Schema 4 for C({n+1}) = osp(2|{2*n}) [n={n}]...")
        schema4 = generate_schema4(n)
        filename = f"data/C_{n}_coboundary.json"
        with open(filename, "w") as f:
            json.dump(schema4, f, indent=2)
        n_cob = len(schema4["coboundary_coefficients"])
        n_phi = schema4["odd_linear_map_f"]["parameter_count"]
        print(f"  -> {filename}: {n_cob} coboundary entries, {n_phi} phi parameters")
    print("Done.")


if __name__ == "__main__":
    main()
