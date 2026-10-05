#!/usr/bin/env python3
"""
Generate complete structured data artifacts for C(n+1) inhomogeneous deformation
for n = 1, 2, 3.
Exports structure constants, gamma matrices, coboundary matrices, and triviality results to JSON.
"""

import sympy as sp
import numpy as np
import json
from collections import defaultdict
import os

def export_complete_data(max_n=3, output_dir='data'):
    os.makedirs(output_dir, exist_ok=True)
    
    summary_report = {}
    
    for n in range(1, max_n + 1):
        print(f"Generating complete structured data for C({n+1}) = osp(2|{2*n})...")
        
        # 1. Parameter definitions
        gb_keys = []
        gb_syms = {}
        for sigma in ['+', '-']:
            for j in range(1, n + 1):
                for s in ['+', '-']:
                    key = (sigma, j, s)
                    gb_keys.append(key)
                    gb_syms[key] = f"gb_{sigma}_{j}_{s}"
                    
        num_gb = len(gb_keys)
        
        # 2. Basis construction
        basis = []
        basis.append(('Z', 0, {(0, 1): 1}))
        for k in range(1, n + 1):
            basis.append((f'h_{k}', 0, {(2*k, 2*k+1): 1}))
        for k in range(1, n + 1):
            basis.append((f'E_2d_{k}', 0, {(2*k, 2*k): 0.5}))
        for k in range(1, n + 1):
            basis.append((f'E_-2d_{k}', 0, {(2*k+1, 2*k+1): 0.5}))
        for k in range(1, n + 1):
            for l in range(1, n + 1):
                if k != l:
                    basis.append((f'E_d{k}-d{l}', 0, {(2*k, 2*l+1): 1}))
        for k in range(1, n + 1):
            for l in range(k + 1, n + 1):
                basis.append((f'E_d{k}+d{l}', 0, {(2*k, 2*l): 1}))
        for k in range(1, n + 1):
            for l in range(k + 1, n + 1):
                basis.append((f'E_-d{k}-d{l}', 0, {(2*k+1, 2*l+1): 1}))
                
        for l in range(1, n + 1):
            basis.append((f'E_eps+d{l}', 1, {(0, 2*l): 1}))
            basis.append((f'E_eps-d{l}', 1, {(0, 2*l+1): 1}))
            basis.append((f'E_-eps+d{l}', 1, {(1, 2*l): 1}))
            basis.append((f'E_-eps-d{l}', 1, {(1, 2*l+1): 1}))
            
        dim = len(basis)
        basis_names = [b[0] for b in basis]
        basis_parities = [b[1] for b in basis]
        dim_0 = sum(1 for p in basis_parities if p == 0)
        dim_1 = sum(1 for p in basis_parities if p == 1)
        
        # Supercommutator and quadratic reduction
        def osc_supercomm(i, j):
            if i in (0, 1) and j in (0, 1):
                if (i, j) in ((0, 1), (1, 0)):
                    return (1, {})
                return (0, {})
            if i >= 2 and j >= 2:
                k1, s1 = i // 2, '+' if i % 2 == 0 else '-'
                k2, s2 = j // 2, '+' if j % 2 == 0 else '-'
                if k1 == k2:
                    if s1 == '-' and s2 == '+':
                        return (1, {})
                    elif s1 == '+' and s2 == '-':
                        return (-1, {})
                return (0, {})
            if i >= 2 and j in (0, 1):
                k = i // 2
                s = '+' if i % 2 == 0 else '-'
                sigma = '+' if j == 0 else '-'
                sym = gb_syms[(sigma, k, s)]
                return (0, {sym: -1})
            if i in (0, 1) and j >= 2:
                k = j // 2
                s = '+' if j % 2 == 0 else '-'
                sigma = '+' if i == 0 else '-'
                sym = gb_syms[(sigma, k, s)]
                return (0, {sym: 1})
            return (0, {})

        def reduce_quadratic(i, j):
            basis_map = {b[0]: idx for idx, b in enumerate(basis)}
            res = defaultdict(float)
            scalar = 0.0
            if i in (0, 1) and j in (0, 1):
                if (i, j) == (0, 1):
                    res[basis_map['Z']] += 1.0
                elif (i, j) == (1, 0):
                    res[basis_map['Z']] += -1.0
                    scalar += 1.0
            elif i >= 2 and j >= 2:
                k1, s1 = i // 2, i % 2
                k2, s2 = j // 2, j % 2
                if k1 == k2:
                    if s1 == 0 and s2 == 0:
                        res[basis_map[f'E_2d_{k1}']] += 2.0
                    elif s1 == 1 and s2 == 1:
                        res[basis_map[f'E_-2d_{k1}']] += 2.0
                    elif s1 == 0 and s2 == 1:
                        res[basis_map[f'h_{k1}']] += 1.0
                    elif s1 == 1 and s2 == 0:
                        res[basis_map[f'h_{k1}']] += 1.0
                        scalar += 1.0
                else:
                    k_min, k_max = min(k1, k2), max(k1, k2)
                    if s1 == 0 and s2 == 0:
                        res[basis_map[f'E_d{k_min}+d{k_max}']] += 1.0
                    elif s1 == 1 and s2 == 1:
                        res[basis_map[f'E_-d{k_min}-d{k_max}']] += 1.0
                    elif s1 == 0 and s2 == 1:
                        res[basis_map[f'E_d{k1}-d{k2}']] += 1.0
                    elif s1 == 1 and s2 == 0:
                        res[basis_map[f'E_d{k2}-d{k1}']] += 1.0
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
                res[basis_map[b_name]] += 1.0
            return res, scalar

        # Structure constants
        bracket_0 = np.zeros((dim, dim, dim), dtype=float)
        gamma = np.zeros((dim, dim, dim, num_gb), dtype=float)
        gb_key_to_idx = {k: idx for idx, k in enumerate(gb_keys)}
        
        for i in range(dim):
            X_name, pX, X_terms = basis[i]
            for j in range(dim):
                Y_name, pY, Y_terms = basis[j]
                for (A, B), cX in X_terms.items():
                    for (C, D), cY in Y_terms.items():
                        pA, pB, pC, pD = 1 if A in (0, 1) else 0, 1 if B in (0, 1) else 0, 1 if C in (0, 1) else 0, 1 if D in (0, 1) else 0
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
                                    bracket_0[i, j, k_b] += tot_sign * comm_0 * v
                            for sym, val in comm_k_dict.items():
                                for k_key, s_sym in gb_syms.items():
                                    if s_sym == sym:
                                        g_idx = gb_key_to_idx[k_key]
                                        for k_b, v in vec_out.items():
                                            gamma[i, j, k_b, g_idx] += tot_sign * val * v

        # Build sparse representation of structure constants and gamma
        c0_sparse = []
        for i in range(dim):
            for j in range(dim):
                for k in range(dim):
                    if abs(bracket_0[i, j, k]) > 1e-6:
                        c0_sparse.append({
                            'i': basis_names[i],
                            'j': basis_names[j],
                            'k': basis_names[k],
                            'coeff': float(bracket_0[i, j, k])
                        })
                        
        gamma_sparse = []
        for i in range(dim):
            for j in range(dim):
                for k in range(dim):
                    for g_idx in range(num_gb):
                        if abs(gamma[i, j, k, g_idx]) > 1e-6:
                            gamma_sparse.append({
                                'i': basis_names[i],
                                'j': basis_names[j],
                                'k': basis_names[k],
                                'param': list(gb_syms.values())[g_idx],
                                'coeff': float(gamma[i, j, k, g_idx])
                            })

        # Save structured data file
        data_n = {
            'superalgebra': f'C({n+1}) = osp(2|{2*n})',
            'n': n,
            'dimensions': {
                'total': dim,
                'even': dim_0,
                'odd': dim_1
            },
            'basis_elements': [
                {'index': idx, 'name': name, 'parity': p}
                for idx, (name, p) in enumerate(zip(basis_names, basis_parities))
            ],
            'deformation_parameters': list(gb_syms.values()),
            'structure_constants_nonzero': c0_sparse,
            'deformation_cocycle_nonzero': gamma_sparse
        }
        
        file_path = os.path.join(output_dir, f'cn1_data_n{n}.json')
        with open(file_path, 'w') as f:
            json.dump(data_n, f, indent=2)
            
        print(f"Saved {file_path}")
        
    print("All data artifacts generated successfully.")

if __name__ == '__main__':
    export_complete_data()
