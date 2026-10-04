"""
C_coboundary.py: Layer 4 Coboundary Structure generator for C(n+1) = osp(2|2n).
Constructs the odd linear map f, evaluates coboundary delta f, and verifies triviality of deformations.
"""

from fractions import Fraction
import json
import os
from typing import Dict, List, Tuple, Any
import numpy as np

from src.C_generators import get_C_generators, generate_structure_constants
from src.C_evaluated import build_schema_3_json


def get_phi_parameters(all_basis: List[str], parity: Dict[str, int]) -> List[Tuple[int, int, str]]:
    """
    Returns list of (target_idx, src_idx, param_name) for odd map f: g -> g.
    f(Z_j) = sum_i phi_{Z_i, Z_j} * Z_i where p(Z_i) != p(Z_j).
    """
    phi_params = []
    for j, z_j in enumerate(all_basis):
        pj = parity[z_j]
        for i, z_i in enumerate(all_basis):
            pi = parity[z_i]
            if pi == (pj + 1) % 2:
                phi_params.append((i, j, f"phi_{z_i}_{z_j}"))
    return phi_params


def compute_delta_f_coefficients(
    n: int
) -> Tuple[Dict[str, Dict[Tuple[str, str], Dict[str, Fraction]]], List[str], List[Tuple[int, int, str]]]:
    """
    Computes (delta f)_{abc} for each basis component of f:
    (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    """
    even_basis, odd_basis, parity, _, _ = get_C_generators(n)
    all_basis = odd_basis + even_basis
    sc = generate_structure_constants(n)

    sc_map = {}
    for entry in sc:
        sc_map[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    def bracket(x, y):
        res = {}
        for z in all_basis:
            c = sc_map.get((x, y, z), Fraction(0))
            if c != 0:
                res[z] = c
        return res

    phi_params = get_phi_parameters(all_basis, parity)
    param_names = [p[2] for p in phi_params]

    delta_f_map: Dict[str, Dict[Tuple[str, str], Dict[str, Fraction]]] = {p[2]: {} for p in phi_params}

    for i, j, param_name in phi_params:
        target_z = all_basis[i]
        src_z = all_basis[j]
        for x in all_basis:
            px = parity[x]
            for y in all_basis:
                py = parity[y]

                # Term 1: (-1)^{p(X)} [X, f(Y)]
                t1 = {}
                if y == src_z:
                    s1 = -1 if px == 1 else 1
                    b = bracket(x, target_z)
                    for z, cz in b.items():
                        t1[z] = t1.get(z, Fraction(0)) + s1 * cz

                # Term 2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                t2 = {}
                if x == src_z:
                    s2_exp = ((px + 1) * py) % 2
                    s2 = -1 if s2_exp == 1 else 1
                    b = bracket(y, target_z)
                    for z, cz in b.items():
                        t2[z] = t2.get(z, Fraction(0)) - s2 * cz

                # Term 3: - f([X, Y])
                t3 = {}
                b_xy = bracket(x, y)
                if src_z in b_xy:
                    c_src = b_xy[src_z]
                    t3[target_z] = t3.get(target_z, Fraction(0)) - c_src

                total = {}
                for d in [t1, t2, t3]:
                    for z, cz in d.items():
                        total[z] = total.get(z, Fraction(0)) + cz
                total = {k: v for k, v in total.items() if v != 0}
                if total:
                    delta_f_map[param_name][(x, y)] = total

    return delta_f_map, param_names, phi_params


def solve_triviality(n: int, eval_data: Dict[str, Any] = None) -> Dict[str, Any]:
    even_basis, odd_basis, parity, _, _ = get_C_generators(n)
    all_basis = odd_basis + even_basis
    dim = len(all_basis)

    delta_f_map, param_names, phi_params = compute_delta_f_coefficients(n)

    if eval_data is None:
        eval_data = build_schema_3_json(n, assignment_name="all_ones")

    # Build PBW ordered pair list (x <= y)
    pair_list = []
    for idx_x, x in enumerate(all_basis):
        for idx_y in range(idx_x, len(all_basis)):
            pair_list.append((x, all_basis[idx_y]))

    eq_map = {}
    eq_idx = 0
    for (x, y) in pair_list:
        for z in all_basis:
            eq_map[(x, y, z)] = eq_idx
            eq_idx += 1

    num_equations = eq_idx
    num_vars = len(param_names)

    A = np.zeros((num_equations, num_vars), dtype=float)
    for col_idx, (i, j, param_name) in enumerate(phi_params):
        for (x, y), z_dict in delta_f_map[param_name].items():
            for z, val in z_dict.items():
                if (x, y, z) in eq_map:
                    A[eq_map[(x, y, z)], col_idx] = float(val)

    b_vec = np.zeros(num_equations, dtype=float)
    for entry in eval_data["evaluated_gamma_structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        coeff = float(Fraction(entry["coeff"]))
        if (x, y, z) in eq_map:
            b_vec[eq_map[(x, y, z)]] = coeff

    sol, residuals, rank, s = np.linalg.lstsq(A, b_vec, rcond=None)
    reconst = A @ sol
    res_norm = float(np.linalg.norm(b_vec - reconst))
    is_trivial = bool(res_norm < 1e-6)

    solution_dict = {}
    for col_idx, param_name in enumerate(param_names):
        val = sol[col_idx]
        if abs(val) > 1e-7:
            frac = Fraction(val).limit_denominator(120)
            solution_dict[param_name] = str(frac.numerator) if frac.denominator == 1 else f"{frac.numerator}/{frac.denominator}"

    return {
        "is_trivial": is_trivial,
        "coboundary_rank": int(rank),
        "total_parameters": num_vars,
        "residual_norm": res_norm,
        "solution": solution_dict
    }


def build_schema_4_json(n: int, eval_data: Dict[str, Any] = None) -> Dict[str, Any]:
    even_basis, odd_basis, parity, _, _ = get_C_generators(n)
    all_basis = odd_basis + even_basis
    delta_f_map, param_names, phi_params = compute_delta_f_coefficients(n)

    if eval_data is None:
        eval_data = build_schema_3_json(n, assignment_name="all_ones")

    triv_res = solve_triviality(n, eval_data)

    # Format symbolic delta f terms
    coboundary_terms = []
    for (idx_x, x) in enumerate(all_basis):
        for idx_y in range(idx_x, len(all_basis)):
            y = all_basis[idx_y]
            z_set = set()
            for p in param_names:
                if (x, y) in delta_f_map[p]:
                    z_set.update(delta_f_map[p][(x, y)].keys())

            for z in sorted(z_set):
                linear_comb = []
                for p in param_names:
                    c = delta_f_map[p].get((x, y), {}).get(z, Fraction(0))
                    if c != 0:
                        c_str = str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"
                        linear_comb.append({
                            "param": p,
                            "coeff": c_str
                        })
                if linear_comb:
                    coboundary_terms.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "linear_combination": linear_comb
                    })

    data = {
        "schema_version": "5.0",
        "algebra": eval_data["algebra"],
        "coboundary_formula": "(\\delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])",
        "map_f_parameters": {
            "total_count": len(param_names),
            "parameters": param_names
        },
        "coboundary_structure_constants": coboundary_terms,
        "triviality_verification": {
            "evaluation_profile": eval_data["evaluation_profile"],
            "is_trivial": triv_res["is_trivial"],
            "coboundary_rank": triv_res["coboundary_rank"],
            "total_parameters": triv_res["total_parameters"],
            "residual_norm": triv_res["residual_norm"],
            "map_f_solution": triv_res["solution"]
        },
        "metadata": {
            "generated_by": "C_coboundary.py",
            "generation_date": "2026-10-04",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras",
                "C_coboundary_definition.md"
            ]
        }
    }
    return data


def generate_and_save_all_coboundary(data_dir: str = "data"):
    os.makedirs(data_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = build_schema_4_json(n)
        filename = os.path.join(data_dir, f"C_{n}_coboundary.json")
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename}: {len(data['coboundary_structure_constants'])} coboundary terms, is_trivial={data['triviality_verification']['is_trivial']}")


if __name__ == "__main__":
    generate_and_save_all_coboundary()
