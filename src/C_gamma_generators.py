"""
C(n+1) Inhomogeneous Deformation (Gamma Structure) Generator.
Generates Schema 2 JSON specifications for n=1, 2, 3.
"""

import os
import json
from fractions import Fraction
from typing import Dict, List, Tuple, Any

try:
    from src.C_generators import (
        Monomial, Polynomial, normal_order_word, multiply_polynomials,
        get_basis_and_realizations, decompose_into_basis
    )
except ModuleNotFoundError:
    from C_generators import (
        Monomial, Polynomial, normal_order_word, multiply_polynomials,
        get_basis_and_realizations, decompose_into_basis
    )


def normal_order_with_gb(ops: List[str], max_b_idx: int) -> Tuple[Polynomial, Dict[str, Polynomial]]:
    """
    Normal orders a list of operators, returning:
    (order0_poly, order1_dict)
    order1_dict maps gb_param_name -> Polynomial
    Relation: b_j^s a_1^sigma = a_1^sigma b_j^s - gb_{sigma}_{j}_{s} * kappa
    """
    def op_rank(op: str) -> int:
        if op == 'a_1_p': return 0
        if op == 'a_1_m': return 1
        if op.startswith('b_'):
            parts = op.split('_')
            idx = int(parts[1])
            t = 0 if parts[2] == 'p' else 1
            return 2 * idx + t
        return 999

    for i in range(len(ops) - 1):
        r1, r2 = op_rank(ops[i]), op_rank(ops[i+1])
        if r1 > r2:
            op1, op2 = ops[i], ops[i+1]

            # Check if b_j^s is before a_1_sigma (needs deformation swap!)
            if op1.startswith('b_') and op2.startswith('a_1_'):
                # op1 is b_{j}_{s}, op2 is a_1_{sigma}
                p_b, j_str, s_type = op1.split('_')
                p_a, _, sigma_type = op2.split('_')
                gb_param = f"gb_a1{sigma_type}_b{j_str}{s_type}"

                # b_j^s a_1^sigma = a_1^sigma b_j^s - gb * kappa
                # Term 1: swapped (order 0 or recursively higher)
                ops_swapped = ops[:i] + [op2, op1] + ops[i+2:]
                poly_swapped, dict_swapped = normal_order_with_gb(ops_swapped, max_b_idx)

                # Term 2: - gb * kappa * (ops[:i] + ops[i+2:])
                # Note: remaining ops have order 0
                ops_rem = ops[:i] + ops[i+2:]
                poly_rem = normal_order_word(ops_rem, max_b_idx)

                order1_dict = dict(dict_swapped)
                order1_dict[gb_param] = order1_dict.get(gb_param, Polynomial()) - poly_rem

                return poly_swapped, order1_dict

            # Check standard fermion anticommutator
            elif op1 == 'a_1_m' and op2 == 'a_1_p':
                ops_t1 = ops[:i] + ops[i+2:]
                ops_t2 = ops[:i] + ['a_1_p', 'a_1_m'] + ops[i+2:]
                p1, d1 = normal_order_with_gb(ops_t1, max_b_idx)
                p2, d2 = normal_order_with_gb(ops_t2, max_b_idx)
                res_poly = p1 - p2
                res_dict = {}
                for k in set(d1.keys()).union(set(d2.keys())):
                    res_dict[k] = d1.get(k, Polynomial()) - d2.get(k, Polynomial())
                return res_poly, res_dict

            # Check standard boson commutator
            elif op1.startswith('b_') and op2.startswith('b_'):
                p1, idx1, sign1 = op1.split('_')
                p2, idx2, sign2 = op2.split('_')
                if idx1 == idx2 and sign1 == 'm' and sign2 == 'p':
                    ops_t1 = ops[:i] + [f'b_{idx1}_p', f'b_{idx1}_m'] + ops[i+2:]
                    ops_t2 = ops[:i] + ops[i+2:]
                    poly1, dict1 = normal_order_with_gb(ops_t1, max_b_idx)
                    poly2, dict2 = normal_order_with_gb(ops_t2, max_b_idx)
                    res_poly = poly1 + poly2
                    res_dict = {}
                    for k in set(dict1.keys()).union(set(dict2.keys())):
                        res_dict[k] = dict1.get(k, Polynomial()) + dict2.get(k, Polynomial())
                    return res_poly, res_dict

            if op1 == op2 and op1 in ('a_1_p', 'a_1_m'):
                return Polynomial(), {}

            ops_swapped = ops[:i] + [op2, op1] + ops[i+2:]
            return normal_order_with_gb(ops_swapped, max_b_idx)

    # Base case: sorted ops
    poly = normal_order_word(ops, max_b_idx)
    return poly, {}


def multiply_poly_with_gb(poly1: Polynomial, poly2: Polynomial, max_b_idx: int) -> Tuple[Polynomial, Dict[str, Polynomial]]:
    res_poly = Polynomial()
    res_dict: Dict[str, Polynomial] = {}

    for mon1, c1 in poly1.terms.items():
        ops1 = []
        if mon1.a1_p: ops1.append('a_1_p')
        if mon1.a1_m: ops1.append('a_1_m')
        for i in range(max_b_idx):
            ops1.extend([f'b_{i+1}_p'] * mon1.b_powers[2*i])
            ops1.extend([f'b_{i+1}_m'] * mon1.b_powers[2*i+1])

        for mon2, c2 in poly2.terms.items():
            ops2 = []
            if mon2.a1_p: ops2.append('a_1_p')
            if mon2.a1_m: ops2.append('a_1_m')
            for i in range(max_b_idx):
                ops2.extend([f'b_{i+1}_p'] * mon2.b_powers[2*i])
                ops2.extend([f'b_{i+1}_m'] * mon2.b_powers[2*i+1])

            combined_ops = ops1 + ops2
            term_poly, term_dict = normal_order_with_gb(combined_ops, max_b_idx)
            scale = c1 * c2
            res_poly = res_poly + (term_poly * scale)
            for k, p in term_dict.items():
                res_dict[k] = res_dict.get(k, Polynomial()) + (p * scale)

    return res_poly, res_dict


def compute_gamma_superbracket(g1_name: str, g2_name: str, n: int, parity_map: Dict[str, int], realizations: Dict[str, Polynomial]) -> Dict[str, Polynomial]:
    poly1 = realizations[g1_name]
    poly2 = realizations[g2_name]
    p1 = parity_map[g1_name]
    p2 = parity_map[g2_name]
    sign = (-1) ** (p1 * p2)

    p12_poly, p12_dict = multiply_poly_with_gb(poly1, poly2, n)
    p21_poly, p21_dict = multiply_poly_with_gb(poly2, poly1, n)

    gamma_dict: Dict[str, Polynomial] = {}
    all_gb_keys = set(p12_dict.keys()).union(set(p21_dict.keys()))
    for gb_param in all_gb_keys:
        d1 = p12_dict.get(gb_param, Polynomial())
        d2 = p21_dict.get(gb_param, Polynomial())
        gamma_dict[gb_param] = d1 - (d2 * Fraction(sign))

    return gamma_dict


def build_C_gamma_structure(n: int) -> Dict[str, Any]:
    even_basis, odd_basis, realizations, parity_map = get_basis_and_realizations(n)
    all_generators = odd_basis + even_basis

    # gb_matrix parameters
    gb_params = []
    for sigma in ['p', 'm']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                gb_params.append(f"gb_a1{sigma}_b{j}{s}")

    gb_matrix = {
        "rows": ["a_1_p", "a_1_m"],
        "columns": [f"b_{j}_p" for j in range(1, n+1)] + [f"b_{j}_m" for j in range(1, n+1)],
        "count": len(gb_params),
        "parameters": gb_params
    }

    gamma_structure = []

    for i, g1 in enumerate(all_generators):
        for j, g2 in enumerate(all_generators):
            gamma_dict = compute_gamma_superbracket(g1, g2, n, parity_map, realizations)

            gamma_val_json = {}
            for gb_param in gb_params:
                if gb_param in gamma_dict:
                    poly = gamma_dict[gb_param]
                    decomp = decompose_into_basis(poly, n, even_basis, odd_basis, realizations)
                    if decomp:
                        gamma_val_json[gb_param] = [
                            {"Z": target, "coeff": coeff} for target, coeff in decomp
                        ]

            if gamma_val_json:
                gamma_structure.append({
                    "X": g1,
                    "Y": g2,
                    "gamma_value": gamma_val_json
                })

    schema_data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})"
        },
        "gb_matrix": gb_matrix,
        "gamma_structure": gamma_structure,
        "metadata": {
            "generated_by": "src/C_gamma_generators.py",
            "generation_date": "2026-10-05"
        }
    }

    return schema_data


def generate_all_gamma():
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        data = build_C_gamma_structure(n)
        filepath = f"data/C_{n}_gamma.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filepath} (gamma entries: {len(data['gamma_structure'])})")


if __name__ == "__main__":
    generate_all_gamma()
