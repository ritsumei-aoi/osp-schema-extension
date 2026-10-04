"""
C_gamma_generators.py: Computes the inhomogeneous deformation (gamma structure)
and exports Schema 2 JSON for C(n+1) = osp(2|2n).
"""

from fractions import Fraction
import json
import os
import sys
from typing import Dict, List, Tuple, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.C_generators import (
    build_basis, multiply_poly, add_poly, scale_poly, sub_poly
)


def get_gb_params(n: int) -> List[str]:
    """Returns the ordered list of 4n deformation parameters for C(n+1)."""
    params = []
    for sig in ["p", "m"]:
        for k in range(1, n + 1):
            for s in ["p", "m"]:
                params.append(f"gb_a1{sig}_b{k}{s}")
    return params


def solve_in_basis_mod_K(poly: Dict[Tuple, Fraction],
                         basis_list: List[Dict[str, Any]],
                         n: int) -> Optional[Dict[str, Fraction]]:
    """Expresses an oscillator polynomial as a linear combination of basis elements modulo scalar center K."""
    if not poly:
        return {}

    dim_mon = 2 + 2 * n
    zero_mon = tuple([0] * dim_mon)
    all_mons = sorted(list(set().union(*[b["poly"].keys() for b in basis_list] + [poly.keys()] + [{zero_mon: 1}])))
    ext_basis = [b["poly"] for b in basis_list] + [{zero_mon: Fraction(1)}]

    M = []
    for mon in all_mons:
        row = [b.get(mon, Fraction(0)) for b in ext_basis]
        row.append(poly.get(mon, Fraction(0)))
        M.append(row)

    rows = len(M)
    cols = len(ext_basis)
    r = 0
    pivots = {}
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if M[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        lead = M[r][c]
        M[r] = [x / lead for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                factor = M[i][c]
                M[i] = [M[i][k] - factor * M[r][k] for k in range(cols + 1)]
        pivots[c] = r
        r += 1

    for i in range(r, rows):
        if M[i][-1] != 0:
            return None

    coeffs = {}
    for c, row_idx in pivots.items():
        if c < len(basis_list):
            val = M[row_idx][-1]
            if val != 0:
                coeffs[basis_list[c]["name"]] = val
    return coeffs


def mult_mon_deformed_kappa(m1: Tuple, m2: Tuple, n: int) -> Dict[str, Dict[Tuple, Fraction]]:
    """
    Computes the first-order kappa contribution from the deformed product m1 * m2
    arising from [b_k^s, a_1^sigma] = - gb_{sigma, k, s} kappa.
    """
    f1 = (m1[0], m1[1])
    f2 = (m2[0], m2[1])
    b1_modes = [(m1[2 + 2 * k], m1[3 + 2 * k]) for k in range(n)]
    b2_modes = [(m2[2 + 2 * k], m2[3 + 2 * k]) for k in range(n)]

    b1_list = []
    for k in range(n):
        u, v = b1_modes[k]
        for _ in range(u):
            b1_list.append((k + 1, "p"))
        for _ in range(v):
            b1_list.append((k + 1, "m"))

    f2_list = []
    if f2[0] == 1:
        f2_list.append("p")
    if f2[1] == 1:
        f2_list.append("m")

    kappa_terms: Dict[str, Dict[Tuple, Fraction]] = {}
    if not b1_list or not f2_list:
        return kappa_terms

    for (b_k, b_s) in b1_list:
        for f_sig in f2_list:
            cur_param = f"gb_a1{f_sig}_b{b_k}{b_s}"
            f1_part = f1
            rem_f2 = (0, 0) if len(f2_list) == 1 else ((0, 1) if f_sig == "p" else (1, 0))
            rem_b1_modes = list(b1_modes)
            u, v = rem_b1_modes[b_k - 1]
            if b_s == "p":
                rem_b1_modes[b_k - 1] = (u - 1, v)
            else:
                rem_b1_modes[b_k - 1] = (u, v - 1)

            m1_rem = (f1_part[0], f1_part[1]) + tuple([x for mode in rem_b1_modes for x in mode])
            m2_rem = (rem_f2[0], rem_f2[1]) + tuple([x for mode in b2_modes for x in mode])
            rem_prod = multiply_poly({m1_rem: Fraction(1)}, {m2_rem: Fraction(1)}, n)
            rem_prod = scale_poly(rem_prod, -1)

            if cur_param not in kappa_terms:
                kappa_terms[cur_param] = {}
            kappa_terms[cur_param] = add_poly(kappa_terms[cur_param], rem_prod)

    return kappa_terms


def compute_gamma_structure(n: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Computes all gamma terms for C(n+1) and constructs Schema 2 data structure."""
    even_basis, odd_basis = build_basis(n)
    all_basis = odd_basis + even_basis
    gb_params = get_gb_params(n)

    gamma_structure = []
    for g1 in all_basis:
        for g2 in all_basis:
            sign = -1 if (g1["parity"] == 1 and g2["parity"] == 1) else 1

            k_12: Dict[str, Dict[Tuple, Fraction]] = {}
            for m1, c1 in g1["poly"].items():
                for m2, c2 in g2["poly"].items():
                    kt = mult_mon_deformed_kappa(m1, m2, n)
                    for param, p_poly in kt.items():
                        k_12[param] = add_poly(k_12.get(param, {}), scale_poly(p_poly, c1 * c2))

            k_21: Dict[str, Dict[Tuple, Fraction]] = {}
            for m2, c2 in g2["poly"].items():
                for m1, c1 in g1["poly"].items():
                    kt = mult_mon_deformed_kappa(m2, m1, n)
                    for param, p_poly in kt.items():
                        k_21[param] = add_poly(k_21.get(param, {}), scale_poly(p_poly, c1 * c2))

            all_params = set(list(k_12.keys()) + list(k_21.keys()))
            for param in sorted(all_params):
                poly_gamma = sub_poly(k_12.get(param, {}), scale_poly(k_21.get(param, {}), sign))
                if poly_gamma:
                    sol = solve_in_basis_mod_K(poly_gamma, all_basis, n)
                    if sol is None:
                        raise ValueError(f"Failed to decompose gamma({g1['name']}, {g2['name']}) for {param}")
                    for z_name, coeff in sol.items():
                        coeff_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                        gamma_structure.append({
                            "X": g1["name"],
                            "Y": g2["name"],
                            "Z": z_name,
                            "gb_param": param,
                            "coeff": coeff_str
                        })

    schema_dict = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": 2 * n**2 + 5 * n + 1,
                "even": 2 * n**2 + n + 1,
                "odd": 4 * n
            }
        },
        "gb_matrix": {
            "parameters": gb_params,
            "count": len(gb_params),
            "shape": [2, 2 * n],
            "description": "Inhomogeneous deformation parameters between fermion modes (a_1^±) and boson modes (b_k^±)"
        },
        "inhomogeneous_deformation": {
            "description": "Inhomogeneous deformation 2-cocycle gamma structure constants: [X, Y]_gamma = [X, Y]_0 + kappa * sum(gb_param * coeff * Z)",
            "gamma_structure": gamma_structure
        },
        "metadata": {
            "generated_by": "src/C_gamma_generators.py",
            "generation_date": "2026-10-04",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Frappat et al. (2000)"
            ]
        }
    }
    return gamma_structure, schema_dict


def save_c_gamma(n: int, output_dir: str = "data") -> str:
    """Generates and writes C_{n}_gamma.json to the output directory."""
    os.makedirs(output_dir, exist_ok=True)
    _, schema = compute_gamma_structure(n)
    filepath = os.path.join(output_dir, f"C_{n}_gamma.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    return filepath


if __name__ == "__main__":
    for n_val in [1, 2, 3]:
        out_path = save_c_gamma(n_val)
        print(f"Generated {out_path} for C({n_val+1})")
