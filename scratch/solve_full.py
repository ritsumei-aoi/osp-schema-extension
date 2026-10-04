import sys
import os
sys.path.append(os.path.abspath('.'))

import sympy as sp
import numpy as np
import json

from scratch.solve_triviality import Cn1Algebra, compute_all_brackets

def build_coboundary_system(n):
    """
    Builds the linear system for triviality of C(n+1) deformation:
    delta f(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    
    f is an odd map: f: g -> g.
    f(E_a) = sum_m phi_{a, m} O_m   (even to odd)
    f(O_m) = sum_a psi_{m, a} E_a   (odd to even)
    
    Unknowns x: phi (dim_even x dim_odd) and psi (dim_odd x dim_even).
    Total unknowns: 2 * dim_even * dim_odd.
    """
    alg = Cn1Algebra(n)
    C_tensor, gamma_tensor = compute_all_brackets(alg)
    
    dim_E = alg.dim_even
    dim_O = alg.dim_odd
    dim_total = alg.dim_total
    
    # Map index in basis to index in even/odd basis
    even_indices = list(range(dim_E))
    odd_indices = list(range(dim_E, dim_total))
    
    # Unknowns indexing
    # phi[a, m]: index = a * dim_O + m   (a in 0..dim_E-1, m in 0..dim_O-1)
    # psi[m, a]: index = dim_E * dim_O + m * dim_E + a  (m in 0..dim_O-1, a in 0..dim_E-1)
    num_unknowns = 2 * dim_E * dim_O
    
    # We collect equations for each pair (i, j) with 0 <= i < j < dim_total,
    # and each output component k in 0..dim_total-1.
    # Since gamma is odd, gamma(even, even) is odd, gamma(odd, odd) is odd, gamma(even, odd) is even.
    
    # We will build numpy arrays / sympy matrices.
    # Rows correspond to (i, j, k) where gamma(i, j)_k can be non-zero.
    
    equations = [] # list of (row_coeffs_dict, rhs_symbolic)
    
    # Helper to compute f(basis[idx]) as a linear combination of unknowns
    def get_f_idx(idx):
        # returns dict {basis_k: {unknown_idx: coeff}}
        res = {}
        if idx < dim_E:
            # basis[idx] is even (index a = idx)
            a = idx
            for m in range(dim_O):
                target_k = odd_indices[m]
                unkn_idx = a * dim_O + m
                res[target_k] = {unkn_idx: 1}
        else:
            # basis[idx] is odd (index m = idx - dim_E)
            m = idx - dim_E
            for a in range(dim_E):
                target_k = even_indices[a]
                unkn_idx = dim_E * dim_O + m * dim_E + a
                res[target_k] = {unkn_idx: 1}
        return res

    # Helper to compute [Z_idx, f(Z_jdx)]
    def bracket_basis_with_f(idx, jdx):
        # returns dict {out_k: {unkn_idx: coeff}}
        # f(Z_jdx) = sum_l coeffs * Z_l
        f_j = get_f_idx(jdx)
        res = {}
        for l, unkn_dict in f_j.items():
            # compute [Z_idx, Z_l]
            if idx == l:
                continue
            pair = (idx, l) if idx < l else (l, idx)
            sign_bracket = 1 if idx < l else (-1 if (alg.basis_parity[idx]*alg.basis_parity[l]%2 == 0) else 1)
            # Wait, [Z_l, Z_idx] = - (-1)^{p(l)p(idx)} [Z_idx, Z_l]
            # So if idx > l: [Z_idx, Z_l] = - (-1)^{p_idx p_l} [Z_l, Z_idx]
            
            vec = C_tensor.get(pair, {})
            p_idx, p_l = alg.basis_parity[idx], alg.basis_parity[l]
            bracket_sign = 1 if idx < l else (-1 if (p_idx * p_l % 2 == 0) else 1)
            
            for out_k, c in vec.items():
                if out_k not in res:
                    res[out_k] = {}
                for u_idx, u_c in unkn_dict.items():
                    res[out_k][u_idx] = res[out_k].get(u_idx, 0) + bracket_sign * c * u_c
        return res

    for i in range(dim_total):
        for j in range(i + 1, dim_total):
            p_i = alg.basis_parity[i]
            p_j = alg.basis_parity[j]
            
            # Formula: (delta f)(i, j) = (-1)^{p_i} [Z_i, f(Z_j)] - (-1)^{(p_i+1)p_j} [Z_j, f(Z_i)] - f([Z_i, Z_j])
            term1_sign = 1 if p_i == 0 else -1
            term2_sign = - (1 if ((p_i + 1) * p_j % 2 == 0) else -1)
            
            # Term 1: (-1)^{p_i} [Z_i, f(Z_j)]
            t1 = bracket_basis_with_f(i, j)
            
            # Term 2: - (-1)^{(p_i+1)p_j} [Z_j, f(Z_i)]
            t2 = bracket_basis_with_f(j, i)
            
            # Term 3: - f([Z_i, Z_j])
            # [Z_i, Z_j] = sum_l C_{ij}^l Z_l
            t3 = {}
            bracket_ij = C_tensor.get((i, j), {})
            for l, c_l in bracket_ij.items():
                f_l = get_f_idx(l)
                for out_k, unkn_dict in f_l.items():
                    if out_k not in t3:
                        t3[out_k] = {}
                    for u_idx, u_c in unkn_dict.items():
                        t3[out_k][u_idx] = t3[out_k].get(u_idx, 0) - c_l * u_c

            # Combine t1, t2, t3 for each out_k
            gamma_ij = gamma_tensor.get((i, j), {})
            
            all_out_k = set(t1.keys()).union(t2.keys()).union(t3.keys()).union(gamma_ij.keys())
            
            for out_k in all_out_k:
                row_dict = {}
                # from t1
                for u_idx, u_c in t1.get(out_k, {}).items():
                    row_dict[u_idx] = row_dict.get(u_idx, 0) + term1_sign * u_c
                # from t2
                for u_idx, u_c in t2.get(out_k, {}).items():
                    row_dict[u_idx] = row_dict.get(u_idx, 0) + term2_sign * u_c
                # from t3
                for u_idx, u_c in t3.get(out_k, {}).items():
                    row_dict[u_idx] = row_dict.get(u_idx, 0) + u_c
                    
                rhs = gamma_ij.get(out_k, 0)
                
                # Filter zero row coeffs
                row_dict = {u: sp.simplify(c) for u, c in row_dict.items() if sp.simplify(c) != 0}
                rhs = sp.simplify(rhs)
                
                if len(row_dict) > 0 or rhs != 0:
                    equations.append((row_dict, rhs, i, j, out_k))
                    
    return alg, num_unknowns, equations

print("build_coboundary_system defined.")

def analyze_triviality(n):
    print(f"\n==========================================")
    print(f"ANALYZING TRIVIALITY FOR C({n}+1) = osp(2|{2*n})")
    print(f"==========================================")
    
    alg, num_unknowns, equations = build_coboundary_system(n)
    
    print(f"Number of basis elements: {alg.dim_total} (even: {alg.dim_even}, odd: {alg.dim_odd})")
    print(f"Number of f map unknowns: {num_unknowns}")
    print(f"Number of gb parameters: {len(alg.gb_list)}")
    print(f"Number of coboundary equations: {len(equations)}")
    
    # Build Matrix M (equations x num_unknowns) and RHS matrix B (equations x 4n)
    M = np.zeros((len(equations), num_unknowns), dtype=float)
    B = np.zeros((len(equations), len(alg.gb_list)), dtype=float)
    
    gb_sym_to_idx = {sym: idx for idx, sym in enumerate(alg.gb_list)}
    
    for eq_idx, (row_dict, rhs, i, j, out_k) in enumerate(equations):
        for u_idx, coeff in row_dict.items():
            M[eq_idx, u_idx] = float(coeff)
            
        # Parse RHS (linear in gb parameters)
        if rhs != 0:
            # rhs is a sympy expression in gb_list
            for gb_sym in alg.gb_list:
                c = rhs.coeff(gb_sym)
                if c != 0:
                    gb_idx = gb_sym_to_idx[gb_sym]
                    B[eq_idx, gb_idx] = float(c)
                    
    rank_M = np.linalg.matrix_rank(M)
    print(f"Rank of Coboundary Matrix M (delta f): {rank_M}")
    
    # Check if any column of B is in Im(M)
    # Project B onto orth complement of Im(M): R = B - M M^+ B
    M_pinv = np.linalg.pinv(M)
    B_proj = M @ (M_pinv @ B)
    Residual = B - B_proj
    
    res_norms = np.linalg.norm(Residual, axis=0)
    print("\nResidual norms for each gb parameter (0 means trivial coboundary):")
    for idx, sym in enumerate(alg.gb_list):
        print(f"  {sym}: residual norm = {res_norms[idx]:.6f}")
        
    # Full augmented rank check for arbitrary linear combinations of gb
    MB = np.hstack([M, B])
    rank_MB = np.linalg.matrix_rank(MB)
    print(f"\nRank of M: {rank_M}")
    print(f"Rank of [M | B]: {rank_MB}")
    print(f"Dimension of trivial gb parameter subspace: {len(alg.gb_list) - (rank_MB - rank_M)}")
    
    return alg, M, B, res_norms, rank_M, rank_MB

if __name__ == '__main__':
    for n in [1, 2, 3]:
        analyze_triviality(n)
