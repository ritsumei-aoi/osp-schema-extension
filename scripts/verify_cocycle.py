#!/usr/bin/env python3
"""
Test graded Jacobi identity for [ , ]_gamma with correct parity of kappa.
"""

import sympy as sp
import numpy as np
from collections import defaultdict

def test_deformed_jacobi_corrected(n=1):
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

    basis = []
    basis.append(('Z', 0, {(0, 1): sp.Rational(1, 1)}))
    for k in range(1, n + 1):
        bp, bm = 2 * k, 2 * k + 1
        basis.append((f'h_{k}', 0, {(bp, bm): sp.Rational(1, 1)}))
    for k in range(1, n + 1):
        bp = 2 * k
        basis.append((f'E_2d_{k}', 0, {(bp, bp): sp.Rational(1, 2)}))
    for k in range(1, n + 1):
        bm = 2 * k + 1
        basis.append((f'E_-2d_{k}', 0, {(bm, bm): sp.Rational(1, 2)}))
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                bp_k, bm_l = 2 * k, 2 * l + 1
                basis.append((f'E_d{k}-d{l}', 0, {(bp_k, bm_l): sp.Rational(1, 1)}))
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            bp_k, bp_l = 2 * k, 2 * l
            basis.append((f'E_d{k}+d{l}', 0, {(bp_k, bp_l): sp.Rational(1, 1)}))
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            bm_k, bm_l = 2 * k + 1, 2 * l + 1
            basis.append((f'E_-d{k}-d{l}', 0, {(bm_k, bm_l): sp.Rational(1, 1)}))
            
    for l in range(1, n + 1):
        bp, bm = 2 * l, 2 * l + 1
        basis.append((f'E_eps+d{l}', 1, {(0, bp): sp.Rational(1, 1)}))
        basis.append((f'E_eps-d{l}', 1, {(0, bm): sp.Rational(1, 1)}))
        basis.append((f'E_-eps+d{l}', 1, {(1, bp): sp.Rational(1, 1)}))
        basis.append((f'E_-eps-d{l}', 1, {(1, bm): sp.Rational(1, 1)}))
        
    dim = len(basis)
    
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
            b_name = f'E_eps+d{b_k}' if (f_sig == '+' and b_sig == '+') else \
                     f'E_eps-d{b_k}' if (f_sig == '+' and b_sig == '-') else \
                     f'E_-eps+d{b_k}' if (f_sig == '-' and b_sig == '+') else \
                     f'E_-eps-d{b_k}'
            res[basis_map[b_name]] += sp.Rational(1, 1)
        return res, scalar

    c0_table = np.zeros((dim, dim, dim), dtype=object)
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
                                c0_table[i, j, k_b] += tot_sign * comm_0 * v
                        for sym, val in comm_k_dict.items():
                            for k_key, s_sym in gb_syms.items():
                                if s_sym == sym:
                                    g_idx = gb_key_to_idx[k_key]
                                    for k_b, v in vec_out.items():
                                        gamma_table[i, j, k_b, g_idx] += tot_sign * val * v

    # Check Jacobi in L = g + kappa g:
    # For any elements X, Y, Z in g:
    # J(X, Y, Z) = (-1)^{pX pZ} [X, [Y, Z]_gamma]_gamma + (-1)^{pY pX} [Y, [Z, X]_gamma]_gamma + (-1)^{pZ pY} [Z, [X, Y]_gamma]_gamma
    # At order kappa:
    # Term 1: [X, [Y, Z]_0 + kappa gamma(Y, Z)] = [X, [Y, Z]_0]_0 + kappa gamma(X, [Y, Z]_0) + (-1)^{pX} kappa [X, gamma(Y, Z)]_0
    print(f"Checking Lie superalgebra Jacobi identity for L = g + kappa g on C({n+1})...")
    violations = 0
    for g_idx in range(num_gb):
        for i in range(dim):
            p_i = basis[i][1]
            for j in range(dim):
                p_j = basis[j][1]
                for k in range(dim):
                    p_k = basis[k][1]
                    
                    # Term 1: (-1)^{p_i} [X_i, gamma(X_j, X_k)]_0 + gamma(X_i, [X_j, X_k]_0)
                    t1 = np.zeros(dim, dtype=object)
                    for m in range(dim):
                        g_jk_m = gamma_table[j, k, m, g_idx]
                        if g_jk_m != 0:
                            for l in range(dim):
                                t1[l] += ((-1)**p_i) * g_jk_m * c0_table[i, m, l]
                        c_jk_m = c0_table[j, k, m]
                        if c_jk_m != 0:
                            for l in range(dim):
                                t1[l] += c_jk_m * gamma_table[i, m, l, g_idx]
                                
                    # Term 2: (-1)^{p_j} [X_j, gamma(X_k, X_i)]_0 + gamma(X_j, [X_k, X_i]_0)
                    t2 = np.zeros(dim, dtype=object)
                    for m in range(dim):
                        g_ki_m = gamma_table[k, i, m, g_idx]
                        if g_ki_m != 0:
                            for l in range(dim):
                                t2[l] += ((-1)**p_j) * g_ki_m * c0_table[j, m, l]
                        c_ki_m = c0_table[k, i, m]
                        if c_ki_m != 0:
                            for l in range(dim):
                                t2[l] += c_ki_m * gamma_table[j, m, l, g_idx]
                                
                    # Term 3: (-1)^{p_k} [X_k, gamma(X_i, X_j)]_0 + gamma(X_k, [X_i, X_j]_0)
                    t3 = np.zeros(dim, dtype=object)
                    for m in range(dim):
                        g_ij_m = gamma_table[i, j, m, g_idx]
                        if g_ij_m != 0:
                            for l in range(dim):
                                t3[l] += ((-1)**p_k) * g_ij_m * c0_table[k, m, l]
                        c_ij_m = c0_table[i, j, m]
                        if c_ij_m != 0:
                            for l in range(dim):
                                t3[l] += c_ij_m * gamma_table[k, m, l, g_idx]
                                
                    s1 = (-1)**(p_i * p_k)
                    s2 = (-1)**(p_j * p_i)
                    s3 = (-1)**(p_k * p_j)
                    tot = s1 * t1 + s2 * t2 + s3 * t3
                    if any(x != 0 for x in tot):
                        violations += 1
                        
    print(f"Total Jacobi violations at order kappa: {violations}")
    assert violations == 0
    print("CONFIRMED: Jacobi identity holds identically on L = g + kappa g!")

test_deformed_jacobi_corrected(1)
test_deformed_jacobi_corrected(2)
test_deformed_jacobi_corrected(3)
