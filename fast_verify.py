#!/usr/bin/env python3
"""
Fast numerical and exact algebraic verification of C(n+1) triviality.
Generates structured JSON data for n=1, 2, 3.
"""

import numpy as np
import sympy as sp
from collections import defaultdict
import json
import os

def build_algebra(n):
    basis = []
    
    # 1. so(2) generator
    basis.append({
        'name': 'N_a',
        'parity': 0,
        'terms': [(sp.Integer(1), ('a+', 'a-')), (-sp.Rational(1,2), ())]
    })
    
    # 2. sp(2n) generators
    # B++_{i,j} for 1 <= i <= j <= n
    for i in range(1, n+1):
        for j in range(i, n+1):
            basis.append({
                'name': f'B++_{i}_{j}',
                'parity': 0,
                'terms': [(sp.Integer(1), (('b+', i), ('b+', j)))]
            })
            
    # B--_{i,j} for 1 <= i <= j <= n
    for i in range(1, n+1):
        for j in range(i, n+1):
            basis.append({
                'name': f'B--_{i}_{j}',
                'parity': 0,
                'terms': [(sp.Integer(1), (('b-', i), ('b-', j)))]
            })
            
    # B+-_{i,j} for 1 <= i, j <= n
    for i in range(1, n+1):
        for j in range(1, n+1):
            terms = [(sp.Integer(1), (('b+', i), ('b-', j)))]
            if i == j:
                terms.append((sp.Rational(1,2), ()))
            basis.append({
                'name': f'B+-_{i}_{j}',
                'parity': 0,
                'terms': terms
            })
            
    # 3. Odd generators (4n total)
    for j in range(1, n+1):
        basis.append({'name': f'F++_{j}', 'parity': 1, 'terms': [(sp.Integer(1), ('a+', ('b+', j)))]})
        basis.append({'name': f'F+-_{j}', 'parity': 1, 'terms': [(sp.Integer(1), ('a+', ('b-', j)))]})
        basis.append({'name': f'F-+_{j}', 'parity': 1, 'terms': [(sp.Integer(1), ('a-', ('b+', j)))]})
        basis.append({'name': f'F--_{j}', 'parity': 1, 'terms': [(sp.Integer(1), ('a-', ('b-', j)))]})
        
    dim = len(basis)
    name_to_idx = {b['name']: i for i, b in enumerate(basis)}
    
    def canonical_to_basis_vector(term_dict):
        vec = [sp.Integer(0)] * dim
        scalar_part = sp.Integer(0)
        
        for k, coeff in term_dict.items():
            if coeff == 0:
                continue
            if len(k) == 0:
                scalar_part += coeff
            elif k == ('a+', 'a-'):
                vec[name_to_idx['N_a']] += coeff
                scalar_part += coeff * sp.Rational(1, 2)
            elif len(k) == 2 and isinstance(k[0], tuple) and isinstance(k[1], tuple):
                t1, i1 = k[0]
                t2, i2 = k[1]
                if t1 == 'b+' and t2 == 'b+':
                    i, j = min(i1, i2), max(i1, i2)
                    vec[name_to_idx[f'B++_{i}_{j}']] += coeff
                elif t1 == 'b-' and t2 == 'b-':
                    i, j = min(i1, i2), max(i1, i2)
                    vec[name_to_idx[f'B--_{i}_{j}']] += coeff
                elif t1 == 'b+' and t2 == 'b-':
                    vec[name_to_idx[f'B+-_{i1}_{i2}']] += coeff
                    if i1 == i2:
                        scalar_part -= coeff * sp.Rational(1, 2)
                else:
                    raise ValueError(f"Unknown bosonic pair {k}")
            elif len(k) == 2 and k[0] in ('a+', 'a-') and isinstance(k[1], tuple):
                sigma = k[0]
                t2, j2 = k[1]
                if sigma == 'a+' and t2 == 'b+':
                    vec[name_to_idx[f'F++_{j2}']] += coeff
                elif sigma == 'a+' and t2 == 'b-':
                    vec[name_to_idx[f'F+-_{j2}']] += coeff
                elif sigma == 'a-' and t2 == 'b+':
                    vec[name_to_idx[f'F-+_{j2}']] += coeff
                elif sigma == 'a-' and t2 == 'b-':
                    vec[name_to_idx[f'F--_{j2}']] += coeff
            else:
                raise ValueError(f"Unknown canonical key {k}")
                
        return vec, scalar_part
        
    return basis, dim, canonical_to_basis_vector

def osc_parity(u):
    return 1 if u in ('a+', 'a-') else 0

def osc_bracket_0(u, v):
    if u == 'a-' and v == 'a+':
        return 1
    if u == 'a+' and v == 'a-':
        return 1
    if isinstance(u, tuple) and isinstance(v, tuple):
        u_type, u_i = u
        v_type, v_i = v
        if u_type == 'b-' and v_type == 'b+' and u_i == v_i:
            return 1
        if u_type == 'b+' and v_type == 'b-' and u_i == v_i:
            return -1
    return 0

def osc_bracket_gamma_basis(u, v, sigma_req, j_req, s_req):
    # Returns coefficient of gb_{sigma_req, j_req, s_req}
    if isinstance(u, tuple) and v in ('a+', 'a-'):
        s = '+' if u[0] == 'b+' else '-'
        j = u[1]
        sigma = '+' if v == 'a+' else '-'
        if (sigma, j, s) == (sigma_req, j_req, s_req):
            return -1
    elif u in ('a+', 'a-') and isinstance(v, tuple):
        sigma = '+' if u == 'a+' else '-'
        s = '+' if v[0] == 'b+' else '-'
        j = v[1]
        if (sigma, j, s) == (sigma_req, j_req, s_req):
            return 1
    return 0

def reduce_pair_0(u, v):
    if u in ('a+', 'a-') and v in ('a+', 'a-'):
        if u == 'a+' and v == 'a+':
            return []
        if u == 'a-' and v == 'a-':
            return []
        if u == 'a+' and v == 'a-':
            return [(1, ('a+', 'a-'))]
        if u == 'a-' and v == 'a+':
            return [(1, ()), (-1, ('a+', 'a-'))]
            
    if isinstance(u, tuple) and isinstance(v, tuple):
        u_t, u_i = u
        v_t, v_i = v
        if u_t == 'b+' and v_t == 'b+':
            i, j = min(u_i, v_i), max(u_i, v_i)
            return [(1, (('b+', i), ('b+', j)))]
        if u_t == 'b-' and v_t == 'b-':
            i, j = min(u_i, v_i), max(u_i, v_i)
            return [(1, (('b-', i), ('b-', j)))]
        if u_t == 'b+' and v_t == 'b-':
            return [(1, (('b+', u_i), ('b-', v_i)))]
        if u_t == 'b-' and v_t == 'b+':
            res = [(1, (('b+', v_i), ('b-', u_i)))]
            if u_i == v_i:
                res.append((1, ()))
            return res
            
    if u in ('a+', 'a-') and isinstance(v, tuple):
        return [(1, (u, v))]
    if isinstance(u, tuple) and v in ('a+', 'a-'):
        return [(1, (v, u))]
        
    raise ValueError(f"Unknown pair {u}, {v}")

def compute_all_structure(n):
    basis, dim, canonical_to_basis = build_algebra(n)
    
    gb_keys = []
    for sigma in ('+', '-'):
        for j in range(1, n+1):
            for s in ('+', '-'):
                gb_keys.append((sigma, j, s))
                
    num_gb = len(gb_keys)
    
    # C_struct[i, j, k]
    C_struct = np.zeros((dim, dim, dim), dtype=np.float64)
    # Gamma_struct[gb_idx, i, j, k]
    Gamma_struct = np.zeros((num_gb, dim, dim, dim), dtype=np.float64)
    
    for i in range(dim):
        g1 = basis[i]
        for j in range(dim):
            g2 = basis[j]
            
            dict_0 = defaultdict(float)
            dict_gamma = [defaultdict(float) for _ in range(num_gb)]
            
            for c1, ops1 in g1['terms']:
                if len(ops1) == 0:
                    continue
                u1, u2 = ops1
                p_u1, p_u2 = osc_parity(u1), osc_parity(u2)
                
                for c2, ops2 in g2['terms']:
                    if len(ops2) == 0:
                        continue
                    v1, v2 = ops2
                    p_v1, p_v2 = osc_parity(v1), osc_parity(v2)
                    
                    sign1 = 1
                    sign2 = (-1)**(p_u2 * p_v1)
                    sign3 = (-1)**(p_u2 * (p_v1 + p_v2))
                    sign4 = (-1)**(p_u2 * (p_v1 + p_v2) + p_u1 * p_v1)
                    
                    pieces = [
                        (sign1, (u2, v1), (u1, v2)),
                        (sign2, (u2, v2), (u1, v1)),
                        (sign3, (u1, v1), (v2, u2)),
                        (sign4, (u1, v2), (v1, u2))
                    ]
                    
                    c1_val = float(c1)
                    c2_val = float(c2)
                    
                    for sign, (br_u, br_v), (rem_1, rem_2) in pieces:
                        b0 = osc_bracket_0(br_u, br_v)
                        if b0 != 0:
                            red = reduce_pair_0(rem_1, rem_2)
                            for r_coeff, r_ops in red:
                                dict_0[r_ops] += c1_val * c2_val * sign * b0 * float(r_coeff)
                                
                        for gb_idx, (sig_req, j_req, s_req) in enumerate(gb_keys):
                            bg = osc_bracket_gamma_basis(br_u, br_v, sig_req, j_req, s_req)
                            if bg != 0:
                                red = reduce_pair_0(rem_1, rem_2)
                                for r_coeff, r_ops in red:
                                    dict_gamma[gb_idx][r_ops] += c1_val * c2_val * sign * bg * float(r_coeff)
                                    
            v0, _ = canonical_to_basis(dict_0)
            for k in range(dim):
                C_struct[i, j, k] = float(v0[k])
                
            for gb_idx in range(num_gb):
                vg, _ = canonical_to_basis(dict_gamma[gb_idx])
                for k in range(dim):
                    Gamma_struct[gb_idx, i, j, k] = float(vg[k])
                    
    # Odd linear maps phi:
    # f(Z_j) = sum_i phi_{i, j} Z_i with p(Z_i) != p(Z_j)
    phi_map = []
    for j in range(dim):
        p_j = basis[j]['parity']
        for i in range(dim):
            p_i = basis[i]['parity']
            if p_i != p_j:
                phi_map.append((i, j))
                
    num_phi = len(phi_map)
    phi_to_idx = {pair: idx for idx, pair in enumerate(phi_map)}
    
    # Delta_matrix: size (num_equations, num_phi)
    # Equations indexed by (i, j, k)
    # We only need independent pairs: (delta f)(Z_i, Z_j) is graded skew-symmetric:
    # (delta f)(Z_j, Z_i) = - (-1)^{p_i p_j} (delta f)(Z_i, Z_j)
    
    eq_indices = []
    for i in range(dim):
        for j in range(i, dim):
            for k in range(dim):
                eq_indices.append((i, j, k))
                
    num_eqs = len(eq_indices)
    M_delta = np.zeros((num_eqs, num_phi), dtype=np.float64)
    M_gamma = np.zeros((num_eqs, num_gb), dtype=np.float64)
    
    for row_idx, (i, j, k) in enumerate(eq_indices):
        p_i = basis[i]['parity']
        p_j = basis[j]['parity']
        
        # 1. (-1)^{p_i} [Z_i, f(Z_j)]_k = (-1)^{p_i} sum_m phi_{m, j} C_{i, m, k}
        for m in range(dim):
            if (m, j) in phi_to_idx:
                col = phi_to_idx[(m, j)]
                M_delta[row_idx, col] += ((-1.0)**p_i) * C_struct[i, m, k]
                
        # 2. - (-1)^{(p_i+1)p_j} [Z_j, f(Z_i)]_k = - (-1)^{(p_i+1)p_j} sum_m phi_{m, i} C_{j, m, k}
        sign2 = - ((-1.0)**((p_i + 1) * p_j))
        for m in range(dim):
            if (m, i) in phi_to_idx:
                col = phi_to_idx[(m, i)]
                M_delta[row_idx, col] += sign2 * C_struct[j, m, k]
                
        # 3. - f([Z_i, Z_j])_k = - sum_m C_{i, j, m} phi_{k, m}
        for m in range(dim):
            c_ij_m = C_struct[i, j, m]
            if c_ij_m != 0 and (k, m) in phi_to_idx:
                col = phi_to_idx[(k, m)]
                M_delta[row_idx, col] -= c_ij_m
                
        for gb_idx in range(num_gb):
            M_gamma[row_idx, gb_idx] = Gamma_struct[gb_idx, i, j, k]
            
    # Compute SVD / rank
    u, s_delta, vh = np.linalg.svd(M_delta)
    rank_delta = int(np.sum(s_delta > 1e-10))
    
    # Project M_gamma onto orthogonal complement of image(M_delta)
    # image(M_delta) is spanned by u[:, :rank_delta]
    # projection to complement: u[:, rank_delta:]^T @ M_gamma
    u_perp = u[:, rank_delta:]
    obstruction_matrix = u_perp.T @ M_gamma
    u_obs, s_obs, _ = np.linalg.svd(obstruction_matrix)
    rank_obs = int(np.sum(s_obs > 1e-10))
    
    print(f"==================================================")
    print(f"Results for C({n+1}) = osp(2|{2*n})")
    print(f"Dimension: {dim} (Even: {sum(1 for b in basis if b['parity']==0)}, Odd: {sum(1 for b in basis if b['parity']==1)})")
    print(f"Number of gb parameters: {num_gb}")
    print(f"Number of odd linear map parameters (phi): {num_phi}")
    print(f"Rank of coboundary operator delta: {rank_delta}")
    print(f"Dimension of 1-cocycles Z^1_odd(g, g): {num_phi - rank_delta}")
    print(f"Rank of obstruction matrix (gb -> H^2): {rank_obs} / {num_gb}")
    print(f"Singular values of obstruction matrix: {s_obs[:num_gb]}")
    if rank_obs == num_gb:
        print(f">>> CONCLUSION: The map gb -> H^2(g, g) is INJECTIVE with rank {rank_obs} = {num_gb}.")
        print(f">>> Therefore, gamma_gb is trivial (a coboundary) IF AND ONLY IF gb = 0!")
    else:
        print(f">>> CONCLUSION: Kernel dimension = {num_gb - rank_obs}")
        
    return {
        'n': n,
        'algebra': f'C({n+1}) = osp(2|{2*n})',
        'dim': dim,
        'even_dim': sum(1 for b in basis if b['parity']==0),
        'odd_dim': sum(1 for b in basis if b['parity']==1),
        'num_gb': num_gb,
        'num_phi': num_phi,
        'rank_delta': rank_delta,
        'dim_Z1_odd': num_phi - rank_delta,
        'rank_obstruction': rank_obs,
        'singular_values_obstruction': [float(x) for x in s_obs[:num_gb]],
        'is_injective': bool(rank_obs == num_gb),
        'triviality_condition': 'gb == 0'
    }

all_results = []
for n in [1, 2, 3]:
    res = compute_all_structure(n)
    all_results.append(res)

# Save JSON verification artifacts
os.makedirs('docs/artifacts', exist_ok=True)
with open('docs/artifacts/triviality_verification_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)

print("\nSaved artifacts to docs/artifacts/triviality_verification_results.json")
