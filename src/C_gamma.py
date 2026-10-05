"""
Schema 2: Inhomogeneous Deformation (gamma structure) for C(n+1) = osp(2|2n).
Computes deformation parameters (gb matrix) and 2-cocycle gamma coefficients.
"""

import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractions import Fraction
import json
from typing import Dict, List, Tuple, Any

from src.C_generators import (
    get_basis,
    get_parity,
    get_generator_operators,
    decompose_operator,
    _build_cartan_solver,
    normal_order_monomial
)


def get_gb_matrix(n: int) -> Dict[str, Any]:
    """
    Returns the gb matrix specification (size 2 x 2n) and parameter list.
    """
    row_labels = ["a_1_p", "a_1_m"]
    col_labels = []
    for j in range(1, n + 1):
        col_labels.append(f"b_{j}_p")
        col_labels.append(f"b_{j}_m")
        
    matrix = []
    param_list = []
    for r in row_labels:
        row = []
        for c in col_labels:
            p_name = f"gb_{r}_{c}"
            row.append(p_name)
            param_list.append(p_name)
        matrix.append(row)
        
    return {
        "dimensions": {
            "rows": 2,
            "cols": 2 * n,
            "total_parameters": 4 * n
        },
        "row_labels": row_labels,
        "col_labels": col_labels,
        "matrix": matrix,
        "parameter_list": param_list
    }


def _osc_parity(o: Tuple[str, int, str]) -> int:
    return 1 if o[0] == "a" else 0


def _single_bracket_deformed(o1: Tuple[str, int, str], o2: Tuple[str, int, str]) -> Dict[str, Fraction]:
    fam1, idx1, s1 = o1
    fam2, idx2, s2 = o2
    # [b_j^s, a_1^sigma] = - gb_{a_1^sigma, b_j^s} * kappa
    # [a_1^sigma, b_j^s] = + gb_{a_1^sigma, b_j^s} * kappa
    if fam1 == "b" and fam2 == "a":
        param = f"gb_a_1_{s2}_b_{idx1}_{s1}"
        return {param: Fraction(-1)}
    elif fam1 == "a" and fam2 == "b":
        param = f"gb_a_1_{s1}_b_{idx2}_{s2}"
        return {param: Fraction(1)}
    return {}


def compute_gamma_coefficients(n: int) -> List[Dict[str, str]]:
    """
    Computes non-zero gamma coefficients gamma(X, Y) = sum_Z coeff * gb_param * Z.
    """
    basis = get_basis(n)
    all_gens = basis["even"] + basis["odd"]
    gen_ops = get_generator_operators(n)
    solver = _build_cartan_solver(n)
    
    entries = []
    for x in all_gens:
        op_x = gen_ops[x]
        for y in all_gens:
            op_y = gen_ops[y]
            
            gb_operator_map: Dict[str, Dict[Tuple, Fraction]] = {}
            for mono_x, c_x in op_x.items():
                if len(mono_x) != 2:
                    continue
                u1, u2 = mono_x
                p1, p2 = _osc_parity(u1), _osc_parity(u2)
                for mono_y, c_y in op_y.items():
                    if len(mono_y) != 2:
                        continue
                    v1, v2 = mono_y
                    q1, q2 = _osc_parity(v1), _osc_parity(v2)
                    
                    # 4 Leibniz terms
                    terms = [
                        (_single_bracket_deformed(u2, v1), 1, (u1, v2)),
                        (_single_bracket_deformed(u2, v2), (-1)**(p2 * q1), (u1, v1)),
                        (_single_bracket_deformed(u1, v1), (-1)**(p2 * (q1 + q2)), (v2, u2)),
                        (_single_bracket_deformed(u1, v2), (-1)**(p2 * (q1 + q2) + p1 * q1), (v1, u2))
                    ]
                    for def_map, sign, rem_pair in terms:
                        for param, p_coeff in def_map.items():
                            factor = c_x * c_y * sign * p_coeff
                            rem_op = normal_order_monomial(rem_pair, factor)
                            if param not in gb_operator_map:
                                gb_operator_map[param] = {}
                            for m, c in rem_op.items():
                                gb_operator_map[param][m] = gb_operator_map[param].get(m, Fraction(0)) + c
                                
            # Decompose each parameter operator into basis
            for param, op in gb_operator_map.items():
                decomp = decompose_operator(op, n, gen_ops, solver)
                for z, coeff in decomp.items():
                    if coeff != 0:
                        c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                        entries.append({
                            "X": x,
                            "Y": y,
                            "Z": z,
                            "gb_param": param,
                            "coeff": c_str
                        })
    return entries


def generate_gamma_json(n: int) -> Dict[str, Any]:
    """Generates complete Schema 2 JSON object for C(n+1)."""
    basis = get_basis(n)
    parity = get_parity(n)
    gb_info = get_gb_matrix(n)
    gamma_coeffs = compute_gamma_coefficients(n)
    
    even_dim = 2 * n**2 + n + 1
    odd_dim = 4 * n
    total_dim = even_dim + odd_dim
    
    data = {
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
            "dimension_formulas": {
                "even": "2*n^2 + n + 1",
                "odd": "4*n",
                "total": "2*n^2 + 5*n + 1"
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim
            }
        },
        "inhomogeneous_deformation": {
            "type": "inhomogeneous_oscillator_deformation",
            "description": "Deformation defined by [b_j^s, a_1^sigma] = -gb_{sigma, j, s} * kappa",
            "gb_matrix": gb_info,
            "central_parameter": {
                "label": "kappa",
                "parity": 1,
                "nilpotent": True
            }
        },
        "basis": basis,
        "parity": parity,
        "gamma_coefficients": gamma_coeffs,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": "2026-10-05",
            "references": [
                "docs/math/C_inhomogeneous_definition.md",
                "Frappat et al. (2000)"
            ]
        }
    }
    return data


def save_gamma_json(n: int, output_dir: str = "data") -> str:
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"C_{n}_gamma.json")
    data = generate_gamma_json(n)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return filepath


if __name__ == "__main__":
    for rank in [1, 2, 3]:
        p = save_gamma_json(rank)
        print(f"Generated {p}")
