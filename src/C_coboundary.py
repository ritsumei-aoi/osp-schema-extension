"""
C(n+1) = osp(2|2n) coboundary structure generator (Layer 4).

Computes the coboundary δf for an odd linear map f: g -> g.
  (δf)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])

The map f reverses parity: f(even) = odd, f(odd) = even.
f is parameterized by symbolic coefficients phi_{i,j}.

Outputs Schema 4 JSON files for n=1, 2, 3.
"""

import json
import os
import sys
from fractions import Fraction
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import build_basis, get_parity


def load_structure(data_dir, n):
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def build_bracket_table(structure):
    table = {}
    parity = structure["parity"]
    for sc in structure["structure_constants"]:
        x, y = sc["X"], sc["Y"]
        result = {}
        for term in sc["result"]:
            result[term["Z"]] = Fraction(term["coeff"])
        table[(x, y)] = result
    return table


def get_bracket(table, parity, x, y):
    if (x, y) in table:
        return dict(table[(x, y)])
    if (y, x) in table:
        px = parity[x]
        py = parity[y]
        sign = -(-1) ** (px * py)
        return {z: Fraction(sign) * c for z, c in table[(y, x)].items()}
    return {}


def build_f_map(n):
    """Build the odd linear map f parameterized by phi coefficients.

    f reverses parity: maps even generators to odd, odd generators to even.
    Returns dict: source_gen -> list of (phi_label, target_gen) pairs.
    """
    even, odd = build_basis(n)
    f_map = {}

    for e_gen in even:
        targets = []
        for o_gen in odd:
            phi_label = f"phi_{o_gen}_{e_gen}"
            targets.append((phi_label, o_gen))
        f_map[e_gen] = targets

    for o_gen in odd:
        targets = []
        for e_gen in even:
            phi_label = f"phi_{e_gen}_{o_gen}"
            targets.append((phi_label, e_gen))
        f_map[o_gen] = targets

    return f_map


def compute_coboundary(n, structure):
    """Compute all coboundary coefficients (δf)(X, Y) for all generator pairs.

    Returns list of entries, each containing:
      X, Y, result: list of {Z, coeff_expr} where coeff_expr is a dict
      mapping phi labels to rational coefficients.
    """
    table = build_bracket_table(structure)
    parity_map = structure["parity"]
    even, odd = build_basis(n)
    all_gens = odd + even
    f_map = build_f_map(n)

    coboundary_entries = []

    for i, x in enumerate(all_gens):
        for j, y in enumerate(all_gens):
            if j <= i:
                continue

            px = parity_map[x]
            py = parity_map[y]

            z_phi_coeffs = {}

            sign1 = (-1) ** px
            for phi_label, f_y_gen in f_map[y]:
                bracket_x_fy = get_bracket(table, parity_map, x, f_y_gen)
                for z, c in bracket_x_fy.items():
                    key = (z, phi_label)
                    z_phi_coeffs[key] = z_phi_coeffs.get(key, Fraction(0)) + Fraction(sign1) * c

            sign2 = (-1) ** ((px + 1) * py)
            for phi_label, f_x_gen in f_map[x]:
                bracket_y_fx = get_bracket(table, parity_map, y, f_x_gen)
                for z, c in bracket_y_fx.items():
                    key = (z, phi_label)
                    z_phi_coeffs[key] = z_phi_coeffs.get(key, Fraction(0)) - Fraction(sign2) * c

            bracket_xy = get_bracket(table, parity_map, x, y)
            for w, c_w in bracket_xy.items():
                for phi_label, f_w_gen in f_map[w]:
                    key = (f_w_gen, phi_label)
                    z_phi_coeffs[key] = z_phi_coeffs.get(key, Fraction(0)) - c_w

            result_by_z = {}
            for (z, phi), c in z_phi_coeffs.items():
                if c == 0:
                    continue
                if z not in result_by_z:
                    result_by_z[z] = []
                result_by_z[z].append({
                    "phi": phi,
                    "coeff": str(c)
                })

            if result_by_z:
                result_list = []
                for z in sorted(result_by_z.keys()):
                    for term in sorted(result_by_z[z], key=lambda t: t["phi"]):
                        result_list.append({
                            "Z": z,
                            "phi_param": term["phi"],
                            "coeff": term["coeff"]
                        })

                coboundary_entries.append({
                    "X": x,
                    "Y": y,
                    "result": result_list
                })

    return coboundary_entries


def generate_schema4(n):
    """Generate Schema 4 JSON for C(n+1) with bosonic rank n."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")

    structure = load_structure(data_dir, n)
    coboundary_entries = compute_coboundary(n, structure)
    f_map = build_f_map(n)

    dim_even = 2 * n * n + n + 1
    dim_odd = 4 * n
    n_phi = dim_even * dim_odd + dim_odd * dim_even

    phi_params = []
    even, odd = build_basis(n)
    for e_gen in even:
        for o_gen in odd:
            phi_params.append(f"phi_{o_gen}_{e_gen}")
    for o_gen in odd:
        for e_gen in even:
            phi_params.append(f"phi_{e_gen}_{o_gen}")

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
            "alternative_notation": {
                "osp": f"osp(2|{2 * n})"
            },
            "dimension": {
                "total": dim_even + dim_odd,
                "even": dim_even,
                "odd": dim_odd
            }
        },
        "f_map": {
            "description": "Odd linear map f: g -> g (parity-reversing)",
            "total_phi_parameters": n_phi,
            "even_to_odd_count": dim_even * dim_odd,
            "odd_to_even_count": dim_odd * dim_even
        },
        "coboundary_coefficients": coboundary_entries,
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": str(date.today()),
            "schema_version": "5.0",
            "description": f"Coboundary structure (delta f) for C({n + 1})"
        }
    }

    return schema


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")
    os.makedirs(data_dir, exist_ok=True)

    for n in [1, 2, 3]:
        print(f"Generating C({n + 1}) coboundary structure (n={n})...")
        schema = generate_schema4(n)
        filename = os.path.join(data_dir, f"C_{n}_coboundary.json")
        with open(filename, "w") as f:
            json.dump(schema, f, indent=2)
        print(f"  Written to {filename}")
        print(f"  Phi parameters: {schema['f_map']['total_phi_parameters']}")
        print(f"  Coboundary entries: {len(schema['coboundary_coefficients'])}")


if __name__ == "__main__":
    main()
