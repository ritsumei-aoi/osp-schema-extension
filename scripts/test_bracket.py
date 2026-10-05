#!/usr/bin/env python3
import sympy as sp
import numpy as np
from collections import defaultdict

def test_cn1(n=1):
    print(f"=== Testing C({n+1}) = osp(2|{2*n}) ===")
    
    # Define deformation parameter symbols
    gb_syms = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                sym = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                gb_syms[(sigma, j, s)] = sym

    # Basis elements
    # We will represent basis elements as named objects
    # and define the full linear mapping from quadratic monomials to basis elements.
    
    basis = []
    # Even:
    # 0: Z (a1^+ a1^-)
    basis.append(('Z', 0, {(0, 1): sp.Rational(1, 1)}))
    
    # h_k for k=1..n
    for k in range(1, n + 1):
        bp = 2 * k
        bm = 2 * k + 1
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
                bp_k = 2 * k
                bm_l = 2 * l + 1
                basis.append((f'E_d{k}-d{l}', 0, {(bp_k, bm_l): sp.Rational(1, 1)}))
                
    # E_d{k}+d{l} for k < l
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            bp_k = 2 * k
            bp_l = 2 * l
            basis.append((f'E_d{k}+d{l}', 0, {(bp_k, bp_l): sp.Rational(1, 1)}))
            
    # E_-d{k}-d{l} for k < l
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            bm_k = 2 * k + 1
            bm_l = 2 * l + 1
            basis.append((f'E_-d{k}-d{l}', 0, {(bm_k, bm_l): sp.Rational(1, 1)}))
            
    # Odd generators:
    for l in range(1, n + 1):
        bp = 2 * l
        bm = 2 * l + 1
        basis.append((f'E_eps+d{l}', 1, {(0, bp): sp.Rational(1, 1)}))
        basis.append((f'E_eps-d{l}', 1, {(0, bm): sp.Rational(1, 1)}))
        basis.append((f'E_-eps+d{l}', 1, {(1, bp): sp.Rational(1, 1)}))
        basis.append((f'E_-eps-d{l}', 1, {(1, bm): sp.Rational(1, 1)}))
        
    dim = len(basis)
    print(f"Dimension: {dim} (Even: {sum(1 for b in basis if b[1]==0)}, Odd: {sum(1 for b in basis if b[1]==1)})")
    
    def osc_parity(idx):
        return 1 if idx in (0, 1) else 0

    def osc_supercomm(i, j):
        # [xi_i, xi_j]
        # returns (c0, dict of gb symbols)
        if i in (0, 1) and j in (0, 1):
            if (i, j) in ((0, 1), (1, 0)):
                return (sp.Rational(1, 1), {})
            return (sp.Rational(0, 1), {})
        if i >= 2 and j >= 2:
            k1 = i // 2
            s1 = '+' if i % 2 == 0 else '-'
            k2 = j // 2
            s2 = '+' if j % 2 == 0 else '-'
            if k1 == k2:
                if s1 == '-' and s2 == '+':
                    return (sp.Rational(1, 1), {})
                elif s1 == '+' and s2 == '-':
                    return (sp.Rational(-1, 1), {})
            return (sp.Rational(0, 1), {})
        # bosonic - fermionic
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
        # Expresses xi_i * xi_j in terms of basis elements or normal ordered monomials
        # Returns a dict of (basis_idx) -> coeff, plus constant scalar
        # Note: we need to handle any pair (i, j)
        p_i = osc_parity(i)
        p_j = osc_parity(j)
        
        # Identify which basis element corresponds to (i, j) or its normal order
        # Even:
        # (0, 1): Z
        # (1, 0): a1^- a1^+ = 1 - a1^+ a1^- = 1 - Z
        # (0, 0): 0
        # (1, 1): 0
        # (2k, 2k): 2 * E_2d_k
        # (2k+1, 2k+1): 2 * E_-2d_k
        # (2k, 2k+1): h_k
        # (2k+1, 2k): b_k^- b_k^+ = b_k^+ b_k^- + 1 = h_k + 1
        # For k < l:
        # (2k, 2l): E_d{k}+d{l}
        # (2l, 2k): E_d{k}+d{l}
        # (2k+1, 2l+1): E_-d{k}-d{l}
        # (2l+1, 2k+1): E_-d{k}-d{l}
        # (2k, 2l+1): E_d{k}-d{l}
        # (2l+1, 2k): b_l^- b_k^+ = b_k^+ b_l^- = E_d{k}-d{l}
        # (2l, 2k+1): E_d{l}-d{k}
        # (2k+1, 2l): b_k^- b_l^+ = b_l^+ b_k^- = E_d{l}-d{k}
        # Odd:
        # (0, 2l): E_eps+d{l}
        # (2l, 0): b_l^+ a1^+ = a1^+ b_l^+ = E_eps+d{l}
        # (0, 2l+1): E_eps-d{l}
        # (2l+1, 0): b_l^- a1^+ = a1^+ b_l^- = E_eps-d{l}
        # (1, 2l): E_-eps+d{l}
        # (2l, 1): b_l^+ a1^- = a1^- b_l^+ = E_-eps+d{l}
        # (1, 2l+1): E_-eps-d{l}
        # (2l+1, 1): b_l^- a1^- = a1^- b_l^- = E_-eps-d{l}
        
        basis_map = {b[0]: idx for idx, b in enumerate(basis)}
        res = defaultdict(lambda: sp.Rational(0, 1))
        scalar = sp.Rational(0, 1)
        
        if i in (0, 1) and j in (0, 1):
            if (i, j) == (0, 1):
                res[basis_map['Z']] += sp.Rational(1, 1)
            elif (i, j) == (1, 0):
                res[basis_map['Z']] += sp.Rational(-1, 1)
                scalar += sp.Rational(1, 1)
            elif i == j:
                pass # 0
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
            # One fermionic, one bosonic
            f_idx = i if i in (0, 1) else j
            b_idx = j if i in (0, 1) else i
            f_sig = '+' if f_idx == 0 else '-'
            b_k = b_idx // 2
            b_sig = '+' if b_idx % 2 == 0 else '-'
            b_name = f'E_{f_sig}eps{b_sig}d{b_k}' if f_sig=='+' else f'E_-eps{b_sig}d{b_k}'
            # Fix naming:
            if f_sig == '+':
                b_name = f'E_eps+{b_k}' if b_sig == '+' else f'E_eps-{b_k}'
                # wait, in basis: E_eps+d1, E_eps-d1
                b_name = f'E_eps+d{b_k}' if b_sig == '+' else f'E_eps-d{b_k}'
            else:
                b_name = f'E_-eps+d{b_k}' if b_sig == '+' else f'E_-eps-d{b_k}'
            res[basis_map[b_name]] += sp.Rational(1, 1)
            
        return res, scalar

    # Now compute bracket between any two basis elements
    def compute_bracket(idx_X, idx_Y):
        X_name, pX, X_terms = basis[idx_X]
        Y_name, pY, Y_terms = basis[idx_Y]
        
        bracket_0 = [sp.Rational(0, 1)] * dim
        bracket_gamma = defaultdict(lambda: [sp.Rational(0, 1)] * dim) # sym -> vector of dim
        
        scalar_0 = sp.Rational(0, 1)
        scalar_gamma = defaultdict(lambda: sp.Rational(0, 1))
        
        for (A, B), cX in X_terms.items():
            for (C, D), cY in Y_terms.items():
                pA, pB, pC, pD = osc_parity(A), osc_parity(B), osc_parity(C), osc_parity(D)
                
                # 4 terms in [AB, CD]:
                terms = [
                    (osc_supercomm(B, C), (A, D), 1),
                    (osc_supercomm(B, D), (A, C), (-1)**(pB * pC)),
                    (osc_supercomm(A, C), (D, B), (-1)**(pB * (pC + pD))),
                    (osc_supercomm(A, D), (C, B), (-1)**(pB * (pC + pD) + pA * pC))
                ]
                
                for (comm_0, comm_k_dict), (i_out, j_out), sign in terms:
                    tot_sign = cX * cY * sign
                    vec_out, sc_out = reduce_quadratic(i_out, j_out)
                    
                    # 0-th order part:
                    if comm_0 != 0:
                        factor = tot_sign * comm_0
                        for k_b, v in vec_out.items():
                            bracket_0[k_b] += factor * v
                        scalar_0 += factor * sc_out
                        
                    # gamma part:
                    for sym, val in comm_k_dict.items():
                        factor = tot_sign * val
                        for k_b, v in vec_out.items():
                            bracket_gamma[sym][k_b] += factor * v
                        scalar_gamma[sym] += factor * sc_out
                        
        return bracket_0, scalar_0, bracket_gamma, scalar_gamma

    # Verify un-deformed bracket is a Lie superalgebra
    print("Checking un-deformed Lie superalgebra structure and scalar central terms...")
    max_scalar = 0
    c0_table = np.zeros((dim, dim, dim), dtype=object)
    for i in range(dim):
        for j in range(dim):
            b0, sc0, _, _ = compute_bracket(i, j)
            if sc0 != 0:
                print(f"Warning: non-zero scalar in [{basis[i][0]}, {basis[j][0]}]_0 = {sc0}")
            for k in range(dim):
                c0_table[i, j, k] = b0[k]
                
    # Check graded Jacobi identity
    print("Checking graded Jacobi identity for [ , ]_0 ...")
    jacobi_err = 0
    for i in range(dim):
        p_i = basis[i][1]
        for j in range(dim):
            p_j = basis[j][1]
            for k in range(dim):
                p_k = basis[k][1]
                # (-1)^{p_i p_k} [X_i, [X_j, X_k]] + (-1)^{p_j p_i} [X_j, [X_k, X_i]] + (-1)^{p_k p_j} [X_k, [X_i, X_j]]
                # Compute term 1: [X_j, X_k] = sum_m c_{jk}^m X_m
                # [X_i, [X_j, X_k]] = sum_m,l c_{jk}^m c_{im}^l X_l
                t1 = np.zeros(dim, dtype=object)
                t2 = np.zeros(dim, dtype=object)
                t3 = np.zeros(dim, dtype=object)
                for m in range(dim):
                    if c0_table[j, k, m] != 0:
                        for l in range(dim):
                            t1[l] += c0_table[j, k, m] * c0_table[i, m, l]
                    if c0_table[k, i, m] != 0:
                        for l in range(dim):
                            t2[l] += c0_table[k, i, m] * c0_table[j, m, l]
                    if c0_table[i, j, m] != 0:
                        for l in range(dim):
                            t3[l] += c0_table[i, j, m] * c0_table[k, m, l]
                s1 = (-1)**(p_i * p_k)
                s2 = (-1)**(p_j * p_i)
                s3 = (-1)**(p_k * p_j)
                tot = s1 * t1 + s2 * t2 + s3 * t3
                if any(x != 0 for x in tot):
                    jacobi_err += 1
    print(f"Jacobi identity violations: {jacobi_err}")
    
    return True

test_cn1(1)
test_cn1(2)
