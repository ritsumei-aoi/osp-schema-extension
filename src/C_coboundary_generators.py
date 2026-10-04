"""
Schema 4 (Coboundary Operator & Triviality Reference) Generator for C(n+1) = osp(2|2n)
"""

import os
import sys
import json
import datetime
from fractions import Fraction

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.C_generators import get_C_structure, compute_graded_bracket_numeric

def compute_coboundary_matrix(n, phi_assignment=None):
    r"""
    Computes (\delta f)(X, Y) = (-1)^p(X) [X, f(Y)] - (-1)^((p(X)+1)p(Y)) [Y, f(X)] - f([X, Y])
    for an odd linear map f parameterized by phi_{i, j} where f(Z_j) = sum_i phi_{i, j} Z_i.
    
    If phi_assignment is None, computes both symbolic phi components and evaluated (with default phi=1).
    """
    struct_data = get_C_structure(n)
    even_basis = struct_data["basis"]["even"]
    odd_basis = struct_data["basis"]["odd"]
    all_basis = even_basis + odd_basis
    parity = struct_data["parity"]
    
    # Valid phi_{i, j}: f reverses parity, so Z_i and Z_j must have opposite parity!
    # f: Even -> Odd and Odd -> Even
    valid_phi_pairs = []
    phi_params = {}
    
    for j, Z_j in enumerate(all_basis):
        for i, Z_i in enumerate(all_basis):
            if parity[Z_i] != parity[Z_j]:
                param_name = f"phi_{Z_i}_{Z_j}"
                valid_phi_pairs.append((Z_i, Z_j, param_name))
                phi_params[param_name] = 1 if phi_assignment is None else phi_assignment.get(param_name, 1)

    # Compute delta f(X, Y) for all pairs X, Y
    coboundary_terms = []
    
    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            
            sign1 = Fraction(-1 if pX == 1 else 1)
            sign2 = Fraction(-1 if ((pX + 1) * pY) % 2 == 1 else 1)
            
            # Map of target Z -> Fraction coeff (evaluated)
            target_eval = {}
            # Map of target Z -> list of (param_name, Fraction_coeff)
            target_sym = {}
            
            # Term 1: (-1)^pX [X, f(Y)] = (-1)^pX sum_i phi_{i, Y} [X, Z_i]
            for Z_i in all_basis:
                if parity[Z_i] != pY:
                    param = f"phi_{Z_i}_{Y}"
                    val = Fraction(phi_params[param])
                    brackets = compute_graded_bracket_numeric(X, Z_i, n)
                    for W, c in brackets.items():
                        c_frac = Fraction(c)
                        target_eval[W] = target_eval.get(W, Fraction(0)) + sign1 * val * c_frac
                        
                        if W not in target_sym: target_sym[W] = []
                        target_sym[W].append((param, sign1 * c_frac))
                        
            # Term 2: - (-1)^((pX+1)pY) [Y, f(X)] = - (-1)^((pX+1)pY) sum_i phi_{i, X} [Y, Z_i]
            for Z_i in all_basis:
                if parity[Z_i] != pX:
                    param = f"phi_{Z_i}_{X}"
                    val = Fraction(phi_params[param])
                    brackets = compute_graded_bracket_numeric(Y, Z_i, n)
                    for W, c in brackets.items():
                        c_frac = Fraction(c)
                        target_eval[W] = target_eval.get(W, Fraction(0)) - sign2 * val * c_frac
                        
                        if W not in target_sym: target_sym[W] = []
                        target_sym[W].append((param, -sign2 * c_frac))

            # Term 3: - f([X, Y]) = - f(sum_k c_{XY}^k Z_k) = - sum_k c_{XY}^k sum_W phi_{W, k} W
            brackets_XY = compute_graded_bracket_numeric(X, Y, n)
            for Z_k, c_k in brackets_XY.items():
                c_k_frac = Fraction(c_k)
                pK = parity[Z_k]
                for W in all_basis:
                    if parity[W] != pK:
                        param = f"phi_{W}_{Z_k}"
                        val = Fraction(phi_params[param])
                        target_eval[W] = target_eval.get(W, Fraction(0)) - c_k_frac * val
                        
                        if W not in target_sym: target_sym[W] = []
                        target_sym[W].append((param, -c_k_frac))

            for W, val in target_eval.items():
                if val != 0:
                    sym_list = target_sym[W]
                    # Consolidate sym_list
                    sym_dict = {}
                    for p_name, c_val in sym_list:
                        sym_dict[p_name] = sym_dict.get(p_name, Fraction(0)) + c_val
                    sym_dict = {p: str(c) for p, c in sym_dict.items() if c != 0}
                    
                    coboundary_terms.append({
                        "X": X,
                        "Y": Y,
                        "Z": W,
                        "evaluated_coeff": str(val),
                        "symbolic_phi_terms": sym_dict
                    })

    schema_4 = {
        "schema_version": "5.0",
        "algebra": struct_data["algebra"],
        "basis": struct_data["basis"],
        "odd_linear_map_f": {
            "description": "Odd linear map f: g -> g reversing parity f(Z_j) = sum_i phi_{i, j} Z_i",
            "total_phi_parameters": len(valid_phi_pairs),
            "phi_assignments": {k: str(v) for k, v in phi_params.items()}
        },
        "coboundary_structure": {
            "description": "Coboundary (delta f)(X, Y) = (-1)^pX [X, f(Y)] - (-1)^((pX+1)pY) [Y, f(X)] - f([X, Y])",
            "coefficients": coboundary_terms
        },
        "metadata": {
            "generated_by": "src/C_coboundary_generators.py",
            "generation_date": datetime.date.today().isoformat()
        }
    }
    return schema_4

def generate_all_C_coboundaries(data_dir="data"):
    os.makedirs(data_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = compute_coboundary_matrix(n)
        filename = os.path.join(data_dir, f"C_{n}_coboundary.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename} (total_phi={data['odd_linear_map_f']['total_phi_parameters']}, coboundary_terms_count={len(data['coboundary_structure']['coefficients'])})")

if __name__ == "__main__":
    generate_all_C_coboundaries()
