"""
Triviality Condition Search and Comparison Script for C(n+1)
Solves the linear system (\delta f)(X, Y) = \gamma(X, Y) over \phi parameters.
"""

import os
import sys
import json
import numpy as np
from fractions import Fraction

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.C_gamma_generators import get_gamma_structure
from src.C_coboundary_generators import compute_coboundary_matrix
from src.C_generators import get_C_basis

def build_triviality_linear_system(n, gb_assignment=None):
    """
    Builds the matrix M and vector b for M * phi = b.
    M comes from Layer 4 coboundary symbolic phi coefficients.
    b comes from Layer 2/3 gamma deformation coefficients for given gb_assignment.
    """
    gamma_data = get_gamma_structure(n)
    cob_data = compute_coboundary_matrix(n)
    
    basis_info = get_C_basis(n)
    even = basis_info["even"]
    odd = basis_info["odd"]
    all_basis = even + odd
    
    # 1. Map all phi parameters to column indices
    all_phi_params = list(cob_data["odd_linear_map_f"]["phi_assignments"].keys())
    phi_idx = {p: idx for idx, p in enumerate(all_phi_params)}
    num_phi = len(all_phi_params)
    
    # 2. Build list of all possible equations indexed by (X, Y, Z) triples
    # Since X, Y anti-symmetry holds for both gamma and delta f, we can restrict to i <= j in all_basis
    triple_keys = []
    triple_idx = {}
    for i, X in enumerate(all_basis):
        for j in range(i, len(all_basis)):
            Y = all_basis[j]
            for Z in all_basis:
                key = (X, Y, Z)
                triple_idx[key] = len(triple_keys)
                triple_keys.append(key)
                
    num_eqs = len(triple_keys)
    
    M = np.zeros((num_eqs, num_phi), dtype=float)
    b = np.zeros(num_eqs, dtype=float)
    
    # Populate M from Layer 4
    for entry in cob_data["coboundary_structure"]["coefficients"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        # Normalize pair ordering if needed
        key = (X, Y, Z)
        if key in triple_idx:
            eq_row = triple_idx[key]
            for p_name, c_str in entry["symbolic_phi_terms"].items():
                c_val = float(Fraction(c_str))
                col_idx = phi_idx[p_name]
                M[eq_row, col_idx] += c_val
                
    # Populate b from Layer 2/3 (using gb_assignment)
    all_gb_params = []
    for row in gamma_data["gb_matrix"]["parameters"]:
        all_gb_params.extend(row)
    if gb_assignment is None:
        gb_assignment = {param: 1.0 for param in all_gb_params}
        
    for entry in gamma_data["inhomogeneous_deformation"]["coefficients"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        gb = entry["gb_param"]
        coeff = float(Fraction(entry["coeff"]))
        gb_val = float(gb_assignment.get(gb, 1.0))
        
        # Check index ordering
        if (X, Y, Z) in triple_idx:
            eq_row = triple_idx[(X, Y, Z)]
            b[eq_row] += coeff * gb_val
        elif (Y, X, Z) in triple_idx:
            # Graded anti-symmetry for gamma
            pX, pY = basis_info["parity"][X], basis_info["parity"][Y]
            sign = 1.0 if (pX == 1 and pY == 1) else -1.0
            eq_row = triple_idx[(Y, X, Z)]
            b[eq_row] += sign * coeff * gb_val
            
    return M, b, triple_keys, all_phi_params

def analyze_triviality_rank(n, gb_assignment=None):
    M, b, triple_keys, phi_params = build_triviality_linear_system(n, gb_assignment)
    
    rank_M = np.linalg.matrix_rank(M)
    M_b = np.column_stack([M, b])
    rank_Mb = np.linalg.matrix_rank(M_b)
    
    is_solvable = (rank_M == rank_Mb)
    
    residuals = []
    if not is_solvable:
        # Solve least squares and find discrepancy triples
        phi_sol, res, rank, s = np.linalg.lstsq(M, b, rcond=None)
        diff = np.abs(M @ phi_sol - b)
        bad_indices = np.where(diff > 1e-4)[0]
        
        for idx in bad_indices[:15]:
            X, Y, Z = triple_keys[idx]
            residuals.append({
                "triple": (X, Y, Z),
                "b_val": b[idx],
                "M_phi_val": float(M[idx] @ phi_sol),
                "diff": float(diff[idx])
            })
            
    return {
        "n": n,
        "bosonic_rank": n,
        "algebra": f"C({n+1})",
        "num_equations": M.shape[0],
        "num_phi_variables": M.shape[1],
        "rank_M": int(rank_M),
        "rank_Mb": int(rank_Mb),
        "is_trivial": is_solvable,
        "discrepancies": residuals
    }

def run_triviality_analysis():
    print("=== Triviality Condition Analysis for C(n+1) ===")
    results = {}
    for n in [1, 2, 3]:
        # Case 1: All gb = +1
        res_all_ones = analyze_triviality_rank(n, gb_assignment=None)
        results[f"C_{n}_ones"] = res_all_ones
        
        print(f"\nAlgebra C({n+1}) (n={n}) [Assignment: all gb = +1]:")
        print(f"  Equations: {res_all_ones['num_equations']}, Variables (phi): {res_all_ones['num_phi_variables']}")
        print(f"  rank(M) = {res_all_ones['rank_M']}, rank(M|b) = {res_all_ones['rank_Mb']}")
        print(f"  Deformation Triviality: {'TRIVIAL (Coboundary)' if res_all_ones['is_trivial'] else 'NON-TRIVIAL (Essential Cohomology)'}")
        
        if not res_all_ones['is_trivial']:
            print(f"  Sample Discrepancies ({len(res_all_ones['discrepancies'])} triples shown):")
            for d in res_all_ones['discrepancies'][:5]:
                print(f"    Triple {d['triple']}: gamma={d['b_val']}, coboundary={d['M_phi_val']:.4f}, diff={d['diff']:.4f}")
                
    return results

if __name__ == "__main__":
    run_triviality_analysis()
