"""
Schema 4: Coboundary Structure for C(n+1) = osp(2|2n).
Computes the coboundary operator delta(f) associated with an odd linear map f: g -> g.
Formula:
(delta f)(X, Y) = (-1)^p(X) [X, f(Y)] - (-1)^((p(X)+1)p(Y)) [Y, f(X)] - f([X, Y])
"""

import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractions import Fraction
import json
from typing import Dict, List, Tuple, Any

from src.C_generators import get_basis, get_parity, compute_structure_constants


def get_f_map_info(n: int) -> Dict[str, Any]:
    """Returns parameterization info for odd linear map f: g -> g."""
    basis = get_basis(n)
    parity = get_parity(n)
    all_gens = basis["even"] + basis["odd"]
    
    params = []
    for src in all_gens:
        p_src = parity[src]
        for tgt in all_gens:
            p_tgt = parity[tgt]
            if p_tgt != p_src:
                params.append(f"phi_{tgt}_{src}")
                
    even_dim = len(basis["even"])
    odd_dim = len(basis["odd"])
    return {
        "type": "odd_linear_map",
        "description": "Odd linear map f: g -> g reversing parity (f(g_0) in g_1, f(g_1) in g_0)",
        "formula": "(delta f)(X, Y) = (-1)^p(X) [X, f(Y)] - (-1)^((p(X)+1)p(Y)) [Y, f(X)] - f([X, Y])",
        "even_dim": even_dim,
        "odd_dim": odd_dim,
        "total_parameters": len(params),
        "parameter_list": params
    }


def compute_coboundary_coefficients(n: int) -> List[Dict[str, str]]:
    """
    Computes all non-zero coefficients of (delta f)(X, Y):
    (delta f)(X, Y) = sum_Z sum_param coeff * f_param * Z.
    """
    basis = get_basis(n)
    parity = get_parity(n)
    all_gens = basis["even"] + basis["odd"]
    
    raw_sc = compute_structure_constants(n)
    br_map: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in raw_sc:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        if (x, y) not in br_map:
            br_map[(x, y)] = {}
        br_map[(x, y)][z] = c

    coboundary_terms = []
    
    for x in all_gens:
        px = parity[x]
        for y in all_gens:
            py = parity[y]
            sign1 = -1 if px % 2 == 1 else 1
            sign2 = -1 if ((px + 1) * py) % 2 == 1 else 1
            
            # Map (z, param_name) -> Fraction
            xy_res: Dict[Tuple[str, str], Fraction] = {}
            
            # Term 1: (-1)^px [X, f(Y)], where f(Y) = sum_{tgt, p(tgt)!=py} phi_{tgt, y} tgt
            src = y
            p_src = py
            for tgt in all_gens:
                if parity[tgt] != p_src:
                    p_name = f"phi_{tgt}_{src}"
                    for z, c in br_map.get((x, tgt), {}).items():
                        xy_res[(z, p_name)] = xy_res.get((z, p_name), Fraction(0)) + sign1 * c
                        
            # Term 2: -(-1)^((px + 1)py) [Y, f(X)], where f(X) = sum_{tgt, p(tgt)!=px} phi_{tgt, x} tgt
            src = x
            p_src = px
            for tgt in all_gens:
                if parity[tgt] != p_src:
                    p_name = f"phi_{tgt}_{src}"
                    for z, c in br_map.get((y, tgt), {}).items():
                        xy_res[(z, p_name)] = xy_res.get((z, p_name), Fraction(0)) - sign2 * c
                        
            # Term 3: - f([X, Y]), where [X, Y] = sum_src c_{xy}^src src
            for src, c_xy_src in br_map.get((x, y), {}).items():
                p_src = parity[src]
                for tgt in all_gens:
                    if parity[tgt] != p_src:
                        p_name = f"phi_{tgt}_{src}"
                        xy_res[(tgt, p_name)] = xy_res.get((tgt, p_name), Fraction(0)) - c_xy_src
                        
            for (z, p_name), coeff in xy_res.items():
                if coeff != 0:
                    c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                    coboundary_terms.append({
                        "X": x,
                        "Y": y,
                        "Z": z,
                        "f_param": p_name,
                        "coeff": c_str
                    })
                    
    return coboundary_terms


def generate_coboundary_json(n: int) -> Dict[str, Any]:
    """Generates complete Schema 4 JSON object for C(n+1)."""
    basis = get_basis(n)
    parity = get_parity(n)
    f_info = get_f_map_info(n)
    coboundary_coeffs = compute_coboundary_coefficients(n)
    
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
        "linear_map_f": f_info,
        "basis": basis,
        "parity": parity,
        "coboundary_coefficients": coboundary_coeffs,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": "2026-10-05",
            "references": [
                "docs/math/C_coboundary_definition.md"
            ]
        }
    }
    return data


def save_coboundary_json(n: int, output_dir: str = "data") -> str:
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"C_{n}_coboundary.json")
    data = generate_coboundary_json(n)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return filepath


if __name__ == "__main__":
    for rank in [1, 2, 3]:
        p = save_coboundary_json(rank)
        print(f"Generated {p}")
