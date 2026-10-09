"""
Schema 4 (Coboundary Structure) generator for C(n+1) = osp(2|2n).

Computes the coboundary (delta f)(X, Y) for an odd linear map f: g -> g,
parameterized by coefficients phi_{ij}.

The coboundary formula:
  (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
"""

import json
import os
import datetime
from fractions import Fraction
import sys

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, get_parity


def load_structure(n, data_dir=None):
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def build_bracket_lookup(structure_data):
    """Build lookup: (X, Y) -> {Z: coeff}."""
    parity = {k: v for k, v in structure_data["parity"].items()}
    lookup = {}

    for sc in structure_data["structure_constants"]:
        x, y = sc["X"], sc["Y"]
        result = {}
        for term in sc["result"]:
            result[term["Z"]] = Fraction(term["coeff"])
        lookup[(x, y)] = result

        px, py = parity[x], parity[y]
        sign = (-1) ** (px * py)
        reversed_result = {z: -sign * c for z, c in result.items()}
        lookup[(y, x)] = {z: c for z, c in reversed_result.items() if c != 0}

    return lookup, parity


def bracket(lookup, x, y):
    """Get [X, Y] from lookup."""
    return dict(lookup.get((x, y), {}))


def apply_f_to_result(result_dict, f_matrix, parity_map):
    """Apply linear map f to a result expressed as sum of basis generators.
    f(sum c_i Z_i) = sum c_i f(Z_i) = sum c_i sum_j phi_{j,i} Z_j
    """
    total = {}
    for z, cz in result_dict.items():
        fz = f_matrix.get(z, {})
        for w, phi in fz.items():
            total[w] = total.get(w, Fraction(0)) + cz * phi
    return {k: v for k, v in total.items() if v != 0}


def compute_coboundary_entry(x, y, f_matrix, bracket_lookup, parity_map):
    """Compute (delta f)(X, Y) for a specific pair.

    Formula:
      (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    """
    px = parity_map[x]
    py = parity_map[y]

    fy = f_matrix.get(y, {})
    fx = f_matrix.get(x, {})
    bxy = bracket(bracket_lookup, x, y)

    term1 = {}
    sign1 = Fraction((-1) ** px)
    for z_fy, c_fy in fy.items():
        bx_fy = bracket(bracket_lookup, x, z_fy)
        for w, c_bx in bx_fy.items():
            term1[w] = term1.get(w, Fraction(0)) + sign1 * c_fy * c_bx

    term2 = {}
    sign2 = Fraction((-1) ** ((px + 1) * py))
    for z_fx, c_fx in fx.items():
        by_fx = bracket(bracket_lookup, y, z_fx)
        for w, c_by in by_fx.items():
            term2[w] = term2.get(w, Fraction(0)) - sign2 * c_fx * c_by

    term3 = {}
    f_bxy = apply_f_to_result(bxy, f_matrix, parity_map)
    for w, c in f_bxy.items():
        term3[w] = term3.get(w, Fraction(0)) - c

    result = {}
    for d in [term1, term2, term3]:
        for w, c in d.items():
            result[w] = result.get(w, Fraction(0)) + c

    return {k: v for k, v in result.items() if v != 0}


def build_generic_f(n, structure_data):
    """Build a generic odd linear map f parameterized by phi_{ij}.

    f is odd: maps even generators to odd, and odd to even.
    f(Z_j) = sum_i phi_{ij} Z_i where p(Z_i) = 1 - p(Z_j).

    Returns: dict label -> dict(label -> symbolic_name)
    """
    even = structure_data["basis"]["even"]
    odd = structure_data["basis"]["odd"]

    f_matrix = {}

    for j, ej in enumerate(even):
        f_matrix[ej] = {}
        for i, oi in enumerate(odd):
            param = f"phi_{oi}_from_{ej}"
            f_matrix[ej][oi] = param

    for j, oj in enumerate(odd):
        f_matrix[oj] = {}
        for i, ei in enumerate(even):
            param = f"phi_{ei}_from_{oj}"
            f_matrix[oj][ei] = param

    return f_matrix


def compute_coboundary_symbolic(n, structure_data):
    """Compute symbolic coboundary coefficients.

    For each pair (X, Y) and each phi parameter, compute the coefficient
    of each basis generator Z in (delta f)(X, Y).
    """
    bracket_lookup, parity_map = build_bracket_lookup(structure_data)
    even = structure_data["basis"]["even"]
    odd = structure_data["basis"]["odd"]
    all_labels = odd + even

    results = []

    for idx_x, x in enumerate(all_labels):
        for idx_y, y in enumerate(all_labels):
            if idx_y <= idx_x:
                continue

            px = parity_map[x]
            py = parity_map[y]

            target_parity = (px + py + 1) % 2

            if target_parity == 0:
                target_gens = even
            else:
                target_gens = odd

            source_even = even
            source_odd = odd

            phi_contributions = {}

            for src in all_labels:
                p_src = parity_map[src]
                if p_src == 0:
                    f_targets = odd
                else:
                    f_targets = even

                for tgt in f_targets:
                    phi_name = f"phi_{tgt}_from_{src}"

                    f_single = {label: {} for label in all_labels}
                    f_single[src] = {tgt: Fraction(1)}

                    coboundary = compute_coboundary_entry(
                        x, y, f_single, bracket_lookup, parity_map
                    )

                    if coboundary:
                        if phi_name not in phi_contributions:
                            phi_contributions[phi_name] = {}
                        for w, c in coboundary.items():
                            phi_contributions[phi_name][w] = (
                                phi_contributions[phi_name].get(w, Fraction(0)) + c
                            )

            for phi_name, coeffs in sorted(phi_contributions.items()):
                cleaned = {w: c for w, c in coeffs.items() if c != 0}
                if not cleaned:
                    continue

                result_list = []
                for z, c in sorted(cleaned.items()):
                    result_list.append({"Z": z, "coeff": str(c)})

                results.append({
                    "X": x,
                    "Y": y,
                    "phi_parameter": phi_name,
                    "result": result_list,
                    "type": "coboundary"
                })

    return results


def generate_schema4_json(n):
    structure_data = load_structure(n)
    coboundary_coefficients = compute_coboundary_symbolic(n, structure_data)

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": dim_even + dim_odd,
                "even": dim_even,
                "odd": dim_odd
            }
        },
        "linear_map_f": {
            "description": "Generic odd linear map f: g -> g",
            "parity": "odd (reverses parity)",
            "parameterization": "phi_{target}_from_{source}",
            "even_to_odd_params": dim_even * dim_odd,
            "odd_to_even_params": dim_odd * dim_even,
            "total_params": 2 * dim_even * dim_odd
        },
        "coboundary_coefficients": coboundary_coefficients,
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }

    return schema


def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C({n + 1}) coboundary structure (n={n})...")
        schema = generate_schema4_json(n)
        filename = os.path.join(data_dir, f"C_{n}_coboundary.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        cc = len(schema["coboundary_coefficients"])
        tp = schema["linear_map_f"]["total_params"]
        print(f"  -> {filename}: {cc} coboundary entries, {tp} phi parameters")


if __name__ == "__main__":
    main()
