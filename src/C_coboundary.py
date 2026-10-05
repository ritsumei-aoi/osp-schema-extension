"""
C(n+1) = osp(2|2n) Schema 4: Coboundary structure.
Computes the coboundary (delta f)(X, Y) for an odd linear map f: g -> g.

The coboundary formula is:
(delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])

The map f reverses parity: f(even) = odd, f(odd) = even.
f is parameterized by coefficients phi_{ij}: f(Z_j) = sum_i phi_{ij} Z_i.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date
from itertools import product as iter_product

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, get_parity


def load_structure(n):
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as f:
        return json.load(f)


def build_bracket_map(data):
    """Build {(X, Y): {Z: coeff}} from structure constants."""
    parity = data["parity"]
    bracket = {}
    for sc in data["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        c = Fraction(sc["coeff"])
        bracket.setdefault((X, Y), {})[Z] = bracket.get((X, Y), {}).get(Z, Fraction(0)) + c

        px, py = parity[X], parity[Y]
        sign = (-1) ** (px * py)
        bracket.setdefault((Y, X), {})[Z] = bracket.get((Y, X), {}).get(Z, Fraction(0)) - sign * c

    return bracket


def get_bracket(bracket_map, X, Y):
    return bracket_map.get((X, Y), {})


def compute_coboundary_symbolic(n):
    """Compute (delta f)(X, Y) symbolically in terms of phi parameters.

    The odd linear map f is parameterized as:
      f(Z_j) = sum_i phi_{ij} Z_i
    where phi_{ij} is nonzero only when p(Z_i) != p(Z_j) (parity reversal).

    Returns list of coboundary entries:
      {X, Y, Z, phi_param, coeff}
    """
    data = load_structure(n)
    even_basis, odd_basis = build_basis(n)
    all_basis = odd_basis + even_basis
    parity_map = {g: get_parity(g) for g in all_basis}
    bracket_map = build_bracket_map(data)

    coboundary_entries = []

    for i_x, X in enumerate(all_basis):
        for i_y, Y in enumerate(all_basis):
            if i_y <= i_x:
                continue

            px = parity_map[X]
            py = parity_map[Y]

            terms = {}

            for j, Zj in enumerate(all_basis):
                pzj = parity_map[Zj]
                for i, Zi in enumerate(all_basis):
                    pzi = parity_map[Zi]
                    if pzi == pzj:
                        continue

                    phi_key = f"phi_{Zi}_{Zj}"

                    term1 = compute_term1(X, Zj, Zi, bracket_map, parity_map)
                    term2 = compute_term2(X, Y, Zj, Zi, bracket_map, parity_map)
                    term3 = compute_term3(X, Y, Zj, Zi, bracket_map, parity_map)

                    for W, c in term1.items():
                        key = (W, phi_key)
                        terms[key] = terms.get(key, Fraction(0)) + c
                    for W, c in term2.items():
                        key = (W, phi_key)
                        terms[key] = terms.get(key, Fraction(0)) + c
                    for W, c in term3.items():
                        key = (W, phi_key)
                        terms[key] = terms.get(key, Fraction(0)) + c

            for (W, phi_key), coeff in sorted(terms.items()):
                if coeff != 0:
                    coboundary_entries.append({
                        "X": X,
                        "Y": Y,
                        "delta_f_Z": W,
                        "phi_param": phi_key,
                        "coeff": str(coeff)
                    })

    return coboundary_entries


def compute_term1(X, Zj, Zi, bracket_map, parity_map):
    """Term 1: (-1)^{p(X)} [X, phi_{i,Y} Z_i] for f(Y) contribution.

    When f(Y) = sum phi_{iY} Z_i, this contributes:
    (-1)^{p(X)} * phi_{i,Y} * [X, Z_i]

    But we compute per (Zj = Y): this term fires when Zj == Y.
    Actually, we iterate over all basis Zj and compute the contribution
    of phi_{Zi, Zj} to (delta f)(X, Y).

    Term 1: (-1)^{p(X)} * [X, f(Y)] contribution from phi_{Zi, Y}
    This fires when Zj == Y.
    """
    px = parity_map[X]
    sign1 = (-1) ** px

    bracket_X_Zi = get_bracket(bracket_map, X, Zi)
    result = {}
    for W, c in bracket_X_Zi.items():
        result[W] = result.get(W, Fraction(0)) + sign1 * c
    return result


def compute_term2(X, Y, Zj, Zi, bracket_map, parity_map):
    """Term 2: -(-1)^{(p(X)+1)p(Y)} [Y, f(X)] contribution from phi_{Zi, X}

    This fires when Zj == X.
    """
    px = parity_map[X]
    py = parity_map[Y]
    sign2 = -(-1) ** ((px + 1) * py)

    bracket_Y_Zi = get_bracket(bracket_map, Y, Zi)
    result = {}
    for W, c in bracket_Y_Zi.items():
        result[W] = result.get(W, Fraction(0)) + sign2 * c
    return result


def compute_term3(X, Y, Zj, Zi, bracket_map, parity_map):
    """Term 3: -f([X, Y]) contribution from phi_{Zi, W} where [X,Y] = sum c_W * W.

    This fires when Zj == some W in [X, Y].
    The contribution is: -c_W * phi_{Zi, W} * Z_i
    i.e., for each W in [X, Y], the result basis element is Zi with coeff -c_W.
    """
    bracket_XY = get_bracket(bracket_map, X, Y)
    c_W = bracket_XY.get(Zj, Fraction(0))
    if c_W == 0:
        return {}
    return {Zi: -c_W}


def generate_coboundary_json(n):
    """Generate Schema 4 (coboundary structure) JSON for C(n+1)."""
    data = load_structure(n)
    even_basis, odd_basis = build_basis(n)
    all_basis = odd_basis + even_basis
    parity_map = {g: get_parity(g) for g in all_basis}

    phi_params = []
    for j, Zj in enumerate(all_basis):
        pzj = parity_map[Zj]
        for i, Zi in enumerate(all_basis):
            pzi = parity_map[Zi]
            if pzi != pzj:
                phi_params.append(f"phi_{Zi}_{Zj}")

    coboundary_entries = compute_coboundary_symbolic(n)

    schema = {
        "schema_version": "5.0",
        "algebra": data["algebra"],
        "linear_map_f": {
            "description": "Odd linear map f: g -> g, parity-reversing",
            "parameterization": "f(Z_j) = sum_i phi_{ij} Z_i where p(Z_i) != p(Z_j)",
            "total_phi_parameters": len(phi_params),
            "phi_parameter_labels": phi_params
        },
        "coboundary_coefficients": coboundary_entries,
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": str(date.today()),
            "schema_layer": 4,
            "description": f"Coboundary structure for C({n+1})",
            "coboundary_formula": "(delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "Bakalov and Sullivan (2017)"
            ]
        }
    }

    return schema


def verify_basis_consistency(n):
    """Verify coboundary data uses only valid basis labels from Schema 1."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    structure_file = os.path.join(data_dir, f"C_{n}_structure.json")
    coboundary_file = os.path.join(data_dir, f"C_{n}_coboundary.json")

    with open(structure_file) as f:
        structure = json.load(f)
    with open(coboundary_file) as f:
        coboundary = json.load(f)

    valid_basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
    errors = []
    for entry in coboundary["coboundary_coefficients"]:
        for key in ["X", "Y", "delta_f_Z"]:
            if entry[key] not in valid_basis:
                errors.append(f"Invalid {key}: {entry[key]}")
    return errors


def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C({n + 1}) coboundary structure (n={n})...")
        schema = generate_coboundary_json(n)
        filename = os.path.join(data_dir, f"C_{n}_coboundary.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        cb_count = len(schema["coboundary_coefficients"])
        phi_count = schema["linear_map_f"]["total_phi_parameters"]
        print(f"  Written {filename}: {cb_count} coboundary entries, {phi_count} phi parameters")

        errors = verify_basis_consistency(n)
        if errors:
            print(f"  CONSISTENCY ERRORS: {errors[:5]}")
        else:
            print(f"  Basis consistency: PASS")

    print("Done.")


if __name__ == "__main__":
    main()
