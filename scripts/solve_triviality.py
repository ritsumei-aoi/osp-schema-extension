#!/usr/bin/env python3
"""
Exact Symbolic and Numerical Solver for Triviality Conditions of C(n+1) Inhomogeneous Deformation.
Analyzes n=1, 2, 3 and computes the full cohomology / coboundary relations.
"""

import sympy as sp
import numpy as np
import json
from collections import defaultdict

def analyze_cn1_deformation(n):
    print(f"\n=======================================================")
    print(f"       ANALYSIS OF C({n+1}) = osp(2|{2*n})")
    print(f"=======================================================")
    
    # 1. Deformation parameter symbols
    gb_keys = []
    gb_syms = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                key = (sigma, j, s)
                gb_keys.append(key)
                sym = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                gb_syms[key] = sym
                
    num_gb = len(gb_keys)
    print(f"Number of gb deformation parameters: {num_gb}")

    # 2. Construct Basis of C(n+1)
    basis = []
    # Z
    basis.append(('Z', 0, {(0, 1): sp.Rational(1, 1)}))
    # h_k
    for k in range(1, n + 1):
        bp, bm = 2 * k, 2 * k + 1
        basis.append((f'h_{k}', 0, {(bp, bm): sp.Rational(1, 1)}))
    # E_2d_k
    for k in range(1, n + 1):
        bp = 2 * k
        basis.append((f'E_2d_{k}', 0, {(bp, bp): sp.Rational(1, 2)}))
    # E_-2d_k
    for k in range(1, n + 1):
        bm = 2 * k + 1
        basis.append((f'E_-2d_{k}', 0, {(bm, bm): sp.Rational(1, 2)}))
    # E_d{k}-d{l} for k != l
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                bp_k, bm_l = 2 * k, 2 * l + 1
                basis.append((f'E_d{k}-d{l}', 0, {(bp_k, bm_l): sp.Rational(1, 1)}))
    # E_d{k}+d{l} for k < l
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            bp_k, bp_l = 2 * k, 2 * l
            basis.append((f'E_d{k}+d{l}', 0, {(bp_k, bp_l): sp.Rational(1, 1)}))
    # E_-d{k}-d{l} for k < l
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            bm_k, bm_l = 2 * k + 1, 2 * l + 1
            basis.append((f'E_-d{k}-d{l}', 0, {(bm_k, bm_l): sp.Rational(1, 1)}))
            
    # Odd generators:
    for l in range(1, n + 1):
        bp, bm = 2 * l, 2 * l + 1
        basis.append((f'E_eps+d{l}', 1, {(0, bp): sp.Rational(1, 1)}))
        basis.append((f'E_eps-d{l}', 1, {(0, bm): sp.Rational(1, 1)}))
        basis.append((f'E_-eps+d{l}', 1, {(1, bp): sp.Rational(1, 1)}))
        basis.append((f'E_-eps-d{l}', 1, {(1, bm): sp.Rational(1, 1)}))
        
    dim = len(basis)
    even_indices = [i for i, b in enumerate(basis) if b[1] == 0]
    odd_indices = [i for i, b in enumerate(basis) if b[1] == 1]
    dim_0 = len(even_indices)
    dim_1 = len(odd_indices)
    print(f"Dimension of C({n+1}): total = {dim}, even = {dim_0}, odd = {dim_1}")

    def osc_parity(idx):
        return 1 if idx in (0, 1) else 0

    def osc_supercomm(i, j):
        if i in (0, 1) and j in (0, 1):
            if (i, j) in ((0, 1), (1, 0)):
                return (sp.Rational(1, 1), {})
            return (sp.Rational(0, 1), {})
        if i >= 2 and j >= 2:
            k1, s1 = i // 2, '+' if i % 2 == 0 else '-'
            k2, s2 = j // 2, '+' if j % 2 == 0 else '-'
            if k1 == k2:
                if s1 == '-' and s2 == '+':
                    return (sp.Rational(1, 1), {})
                elif s1 == '+' and s2 == '-':
                    return (sp.Rational(-1, 1), {})
            return (sp.Rational(0, 1), {})
        if i >= 2 and j in (0, 1):
            k = i // 2
            s = '+' if i % 2 == 0 else '-'
            sigma = '+' if j == 0 else '-'
            sym = gb_syms[(sigma, k, s)]
            return (sp.Rational(0, 1), {sym: sp.Rational(-1, 1)})
        if i in (0, 1) and j >= 2:
            k = j // 2
            s = '+' if j % 2 == 0 else '-'
            sigma = '+' if i == 0 else '-'
            sym = gb_syms[(sigma, k, s)]
            return (sp.Rational(0, 1), {sym: sp.Rational(1, 1)})
        return (sp.Rational(0, 1), {})

    def reduce_quadratic(i, j):
        basis_map = {b[0]: idx for idx, b in enumerate(basis)}
        res = defaultdict(lambda: sp.Rational(0, 1))
        scalar = sp.Rational(0, 1)
        
        if i in (0, 1) and j in (0, 1):
            if (i, j) == (0, 1):
                res[basis_map['Z']] += sp.Rational(1, 1)
            elif (i, j) == (1, 0):
                res[basis_map['Z']] += sp.Rational(-1, 1)
                scalar += sp.Rational(1, 1)
        elif i >= 2 and j >= 2:
            k1, s1 = i // 2, i % 2
            k2, s2 = j // 2, j % 2
            if k1 == k2:
                if s1 == 0 and s2 == 0:
                    res[basis_map[f'E_2d_{k1}']] += sp.Rational(2, 1)
                elif s1 == 1 and s2 == 1:
                    res[basis_map[f'E_-2d_{k1}']] += sp.Rational(2, 1)
                elif s1 == 0 and s2 == 1:
                    res[basis_map[f'h_{k1}']] += sp.Rational(1, 1)
                elif s1 == 1 and s2 == 0:
                    res[basis_map[f'h_{k1}']] += sp.Rational(1, 1)
                    scalar += sp.Rational(1, 1)
            else:
                k_min, k_max = min(k1, k2), max(k1, k2)
                if s1 == 0 and s2 == 0:
                    res[basis_map[f'E_d{k_min}+d{k_max}']] += sp.Rational(1, 1)
                elif s1 == 1 and s2 == 1:
                    res[basis_map[f'E_-d{k_min}-d{k_max}']] += sp.Rational(1, 1)
                elif s1 == 0 and s2 == 1:
                    res[basis_map[f'E_d{k1}-d{k2}']] += sp.Rational(1, 1)
                elif s1 == 1 and s2 == 0:
                    res[basis_map[f'E_d{k2}-d{k1}']] += sp.Rational(1, 1)
        else:
            f_idx = i if i in (0, 1) else j
            b_idx = j if i in (0, 1) else i
            f_sig = '+' if f_idx == 0 else '-'
            b_k = b_idx // 2
            b_sig = '+' if b_idx % 2 == 0 else '-'
            b_name = f'E_eps+{b_k}' if (f_sig == '+' and b_sig == '+') else \
                     f'E_eps-{b_k}' if (f_sig == '+' and b_sig == '-') else \
                     f'E_-eps+{b_k}' if (f_sig == '-' and b_sig == '+') else \
                     f'E_-eps-{b_k}'
            b_name = b_name.replace('E_eps+', 'E_eps+d').replace('E_eps-', 'E_eps-d').replace('E_-eps+', 'E_-eps+d').replace('E_-eps-', 'E_-eps-d')
            res[basis_map[b_name]] += sp.Rational(1, 1)
            
        return res, scalar

    # Compute bracket
    bracket_0_table = np.zeros((dim, dim, dim), dtype=object)
    # gamma_table: (dim, dim, dim, gb_index)
    gamma_table = np.zeros((dim, dim, dim, num_gb), dtype=object)
    
    gb_key_to_idx = {k: idx for idx, k in enumerate(gb_keys)}
    
    for i in range(dim):
        X_name, pX, X_terms = basis[i]
        for j in range(dim):
            Y_name, pY, Y_terms = basis[j]
            for (A, B), cX in X_terms.items():
                for (C, D), cY in Y_terms.items():
                    pA, pB, pC, pD = osc_parity(A), osc_parity(B), osc_parity(C), osc_parity(D)
                    terms = [
                        (osc_supercomm(B, C), (A, D), 1),
                        (osc_supercomm(B, D), (A, C), (-1)**(pB * pC)),
                        (osc_supercomm(A, C), (D, B), (-1)**(pB * (pC + pD))),
                        (osc_supercomm(A, D), (C, B), (-1)**(pB * (pC + pD) + pA * pC))
                    ]
                    for (comm_0, comm_k_dict), (i_out, j_out), sign in terms:
                        tot_sign = cX * cY * sign
                        vec_out, _ = reduce_quadratic(i_out, j_out)
                        if comm_0 != 0:
                            for k_b, v in vec_out.items():
                                bracket_0_table[i, j, k_b] += tot_sign * comm_0 * v
                        for sym, val in comm_k_dict.items():
                            # Find key for sym
                            # sym name is gb_sigma_j_s
                            # Let's extract key
                            for k_key, s_sym in gb_syms.items():
                                if s_sym == sym:
                                    g_idx = gb_key_to_idx[k_key]
                                    for k_b, v in vec_out.items():
                                        gamma_table[i, j, k_b, g_idx] += tot_sign * val * v

    # Now let's parameterize the odd linear map f: g -> g.
    # An odd map sends even elements to odd elements, and odd elements to even elements.
    # f(X_j) = sum_{i: p(X_i) != p(X_j)} phi_{i, j} X_i.
    
    phi_vars = []
    # (i, j) pairs where p(i) != p(j)
    phi_pairs = []
    for j in range(dim):
        for i in range(dim):
            if basis[i][1] != basis[j][1]:
                phi_pairs.append((i, j))
                phi_vars.append(sp.Symbol(f"phi_{i}_{j}"))
                
    num_phi = len(phi_vars)
    phi_pair_to_idx = {p: idx for idx, p in enumerate(phi_pairs)}
    print(f"Number of parameters in odd linear map f: {num_phi}")
    
    # 3. Compute the Coboundary Operator delta f(X_i, X_j)
    # (delta f)(X_i, X_j) = (-1)^{p(X_i)} [X_i, f(X_j)] - (-1)^{(p(X_i)+1)p(X_j)} [X_j, f(X_i)] - f([X_i, X_j])
    # Let's compute (delta f)(X_i, X_j) as a linear combination of phi_vars:
    # (delta f)(X_i, X_j)_k = sum_{p} M_{(i, j, k), p} phi_p
    
    # Independent pairs (i, j):
    # Due to graded skew-symmetry:
    # [Y, X] = - (-1)^{p(X)p(Y)} [X, Y]
    # For (delta f):
    # delta f(Y, X) = (-1)^{p(Y)} [Y, f(X)] - (-1)^{(p(Y)+1)p(X)} [X, f(Y)] - f([Y, X])
    # = - (-1)^{p(X)p(Y)} [ (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y]) ]
    # = - (-1)^{p(X)p(Y)} (delta f)(X, Y)
    # So delta f has the exact same graded skew-symmetry as gamma!
    
    independent_pairs = []
    for i in range(dim):
        for j in range(i, dim):
            # For odd-odd (p_i=1, p_j=1), [X_i, X_i] is symmetric, so i=j is non-trivial.
            # For even-even or even-odd, i=j gives 0 if i=j and p_i=0.
            if i == j and basis[i][1] == 0:
                continue
            independent_pairs.append((i, j))
            
    print(f"Number of independent generator pairs (X_i, X_j): {len(independent_pairs)}")
    
    # Build coboundary matrix M_delta: shape (num_eqs, num_phi)
    # num_eqs = len(independent_pairs) * dim
    
    eq_list = [] # (i, j, k)
    for (i, j) in independent_pairs:
        for k in range(dim):
            eq_list.append((i, j, k))
            
    num_eqs = len(eq_list)
    eq_to_idx = {eq: idx for idx, eq in enumerate(eq_list)}
    
    M_delta = sp.zeros(num_eqs, num_phi)
    M_gamma = sp.zeros(num_eqs, num_gb)
    
    for row_idx, (i, j, k) in enumerate(eq_list):
        p_i = basis[i][1]
        p_j = basis[j][1]
        p_k = basis[k][1]
        
        # 1. gamma part
        for g_idx in range(num_gb):
            M_gamma[row_idx, g_idx] = gamma_table[i, j, k, g_idx]
            
        # 2. delta f part:
        # Term 1: (-1)^{p_i} [X_i, f(X_j)]
        # f(X_j) = sum_{m: p(m)!=p(j)} phi_{m, j} X_m
        # [X_i, f(X_j)]_k = sum_m phi_{m, j} c_{i, m}^k
        sign1 = (-1)**p_i
        for m in range(dim):
            if basis[m][1] != p_j:
                phi_idx = phi_pair_to_idx[(m, j)]
                c_im_k = bracket_0_table[i, m, k]
                if c_im_k != 0:
                    M_delta[row_idx, phi_idx] += sign1 * c_im_k
                    
        # Term 2: - (-1)^{(p_i + 1)p_j} [X_j, f(X_i)]
        # f(X_i) = sum_{m: p(m)!=p(i)} phi_{m, i} X_m
        # [X_j, f(X_i)]_k = sum_m phi_{m, i} c_{j, m}^k
        sign2 = - ((-1)**((p_i + 1) * p_j))
        for m in range(dim):
            if basis[m][1] != p_i:
                phi_idx = phi_pair_to_idx[(m, i)]
                c_jm_k = bracket_0_table[j, m, k]
                if c_jm_k != 0:
                    M_delta[row_idx, phi_idx] += sign2 * c_jm_k
                    
        # Term 3: - f([X_i, X_j])
        # [X_i, X_j] = sum_m c_{i, j}^m X_m
        # f(X_m)_k = phi_{k, m} (if p(k) != p(m))
        for m in range(dim):
            c_ij_m = bracket_0_table[i, j, m]
            if c_ij_m != 0:
                if p_k != basis[m][1]:
                    phi_idx = phi_pair_to_idx[(k, m)]
                    M_delta[row_idx, phi_idx] -= c_ij_m

    print(f"Matrix M_delta shape: {M_delta.shape}")
    print(f"Matrix M_gamma shape: {M_gamma.shape}")
    
    # Convert to numeric float/rational for rank calculation
    M_delta_sp = sp.Matrix(M_delta)
    M_gamma_sp = sp.Matrix(M_gamma)
    
    # Let's check non-zero rows
    non_zero_rows = [r for r in range(num_eqs) if any(M_delta[r, c] != 0 for c in range(num_phi)) or any(M_gamma[r, g] != 0 for g in range(num_gb))]
    print(f"Number of non-trivial equation rows: {len(non_zero_rows)}")
    
    # Solve system: M_delta * phi = M_gamma * gb
    # Using sympy nullspace / rref
    # Augmented matrix: [M_delta | M_gamma]
    M_aug = sp.Matrix.hstack(M_delta_sp, M_gamma_sp)
    print("Computing RREF of augmented matrix...")
    rref_mat, pivot_cols = M_aug.rref()
    
    rank_delta = len([p for p in pivot_cols if p < num_phi])
    rank_aug = len(pivot_cols)
    print(f"Rank(M_delta) = {rank_delta} (out of {num_phi} parameters in f)")
    print(f"Rank([M_delta | M_gamma]) = {rank_aug}")
    
    # Look at the pivots that fall into the M_gamma columns (p >= num_phi)
    gamma_pivots = [p - num_phi for p in pivot_cols if p >= num_phi]
    print(f"Gamma pivots (obstructions to triviality): {gamma_pivots}")
    
    # If gamma_pivots is empty, then for ALL gb, gamma_gb is in the image of delta (always trivial)!
    # If gamma_pivots has len num_gb, then gamma_gb is trivial ONLY IF gb = 0!
    # If 0 < len(gamma_pivots) < num_gb, then triviality requires specific linear relations on gb.
    
    # Let's extract any relations on gb:
    # Each row in rref_mat with pivot in gamma column gives an obstruction equation:
    obstruction_equations = []
    for r in range(rank_delta, rank_aug):
        p_col = pivot_cols[r]
        if p_col >= num_phi:
            # This row has 0 in all delta cols, and linear combination of gb
            expr = sp.Integer(0)
            for g_idx in range(num_gb):
                coeff = rref_mat[r, num_phi + g_idx]
                if coeff != 0:
                    expr += coeff * gb_syms[gb_keys[g_idx]]
            obstruction_equations.append(expr)
            
    print(f"Number of obstruction equations on gb: {len(obstruction_equations)}")
    for idx_obs, obs in enumerate(obstruction_equations):
        print(f"  Obstruction {idx_obs + 1}: {obs} = 0")
        
    # Also, let's find the explicit solution for phi in terms of gb (if any)
    # or kernel of delta
    dim_kernel_delta = num_phi - rank_delta
    print(f"Dimension of 1-cocycles (Ker delta): {dim_kernel_delta}")
    
    # Return structured results
    res_data = {
        'n': n,
        'superalgebra': f'C({n+1}) = osp(2|{2*n})',
        'dim_total': dim,
        'dim_even': dim_0,
        'dim_odd': dim_1,
        'num_gb': num_gb,
        'gb_parameters': [str(gb_syms[k]) for k in gb_keys],
        'num_phi': num_phi,
        'rank_M_delta': rank_delta,
        'rank_augmented': rank_aug,
        'num_obstructions': len(obstruction_equations),
        'obstruction_equations': [str(eq) for eq in obstruction_equations],
        'is_always_trivial': (len(gamma_pivots) == 0),
        'is_never_trivial_for_nonzero_gb': (len(gamma_pivots) == num_gb)
    }
    
    return res_data

if __name__ == '__main__':
    results = {}
    for n in [1, 2, 3]:
        res = analyze_cn1_deformation(n)
        results[f'n={n}'] = res
        
    print("\n\n=======================================================")
    print("                    FINAL SUMMARY")
    print("=======================================================")
    print(json.dumps(results, indent=2))
    
    with open('scripts/verification_results.json', 'w') as f:
        json.dump(results, f, indent=2)
