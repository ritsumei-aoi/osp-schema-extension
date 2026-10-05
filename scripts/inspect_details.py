#!/usr/bin/env python3
import sympy as sp
import numpy as np
from collections import defaultdict

def print_deformed_brackets(n=1):
    gb_keys = []
    gb_syms = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                key = (sigma, j, s)
                gb_keys.append(key)
                sym = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                gb_syms[key] = sym
                
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

    print(f"\n--- Non-zero gamma_gb(X_i, X_j) brackets for C({n+1}) ---")
    for i in range(dim):
        for j in range(i, dim):
            if i == j and basis[i][1] == 0:
                continue
            name_i, p_i, terms_i = basis[i]
            name_j, p_j, terms_j = basis[j]
            
            gamma_terms = defaultdict(lambda: defaultdict(lambda: sp.Rational(0, 1)))
            for (A, B), cX in terms_i.items():
                for (C, D), cY in terms_j.items():
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
                        for sym, val in comm_k_dict.items():
                            for k_b, v in vec_out.items():
                                gamma_terms[sym][basis[k_b][0]] += tot_sign * val * v
                                
            # Filter non-zero
            active = {}
            for sym, out_dict in gamma_terms.items():
                non_z = {k: v for k, v in out_dict.items() if v != 0}
                if non_z:
                    active[sym] = non_z
            if active:
                print(f"gamma({name_i}, {name_j}):")
                for sym, non_z in active.items():
                    parts = [f"{v} * {k}" for k, v in non_z.items()]
                    print(f"   [{sym}]: {' + '.join(parts)}")

print_deformed_brackets(1)
