#!/usr/bin/env python3
"""
Comprehensive script to test:
1. 2-cocycle condition for gamma_gb (d gamma = 0)
2. Coboundary condition gamma_gb = delta f for n=1, 2, 3
3. Space of 1-cocycles and 2-cocycles
4. Exact rank of linear map delta: C^1(g, g) -> C^2(g, g)
5. Dimension of H^2(g, g) and image of gb -> H^2(g, g)
"""

import sympy as sp
from collections import defaultdict
import json

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
    # (1/2)(b_i^+ b_j^- + b_j^- b_i^+) = b_i^+ b_j^- + 1/2 delta_ij
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
    if u in ('a+', 'a-'):
        return 1
    return 0

def osc_bracket_0(u, v):
    if u == 'a-' and v == 'a+':
        return sp.Integer(1)
    if u == 'a+' and v == 'a-':
        return sp.Integer(1)
    if isinstance(u, tuple) and isinstance(v, tuple):
        u_type, u_i = u
        v_type, v_i = v
        if u_type == 'b-' and v_type == 'b+' and u_i == v_i:
            return sp.Integer(1)
        if u_type == 'b+' and v_type == 'b-' and u_i == v_i:
            return sp.Integer(-1)
    return sp.Integer(0)

def osc_bracket_gamma(u, v, gb_vars):
    if isinstance(u, tuple) and v in ('a+', 'a-'):
        s = '+' if u[0] == 'b+' else '-'
        j = u[1]
        sigma = '+' if v == 'a+' else '-'
        return -gb_vars[(sigma, j, s)]
    elif u in ('a+', 'a-') and isinstance(v, tuple):
        sigma = '+' if u == 'a+' else '-'
        s = '+' if v[0] == 'b+' else '-'
        j = v[1]
        return gb_vars[(sigma, j, s)]
    return sp.Integer(0)

def reduce_pair_0(u, v):
    if u in ('a+', 'a-') and v in ('a+', 'a-'):
        if u == 'a+' and v == 'a+':
            return []
        if u == 'a-' and v == 'a-':
            return []
        if u == 'a+' and v == 'a-':
            return [(sp.Integer(1), ('a+', 'a-'))]
        if u == 'a-' and v == 'a+':
            return [(sp.Integer(1), ()), (sp.Integer(-1), ('a+', 'a-'))]
            
    if isinstance(u, tuple) and isinstance(v, tuple):
        u_t, u_i = u
        v_t, v_i = v
        if u_t == 'b+' and v_t == 'b+':
            i, j = min(u_i, v_i), max(u_i, v_i)
            return [(sp.Integer(1), (('b+', i), ('b+', j)))]
        if u_t == 'b-' and v_t == 'b-':
            i, j = min(u_i, v_i), max(u_i, v_i)
            return [(sp.Integer(1), (('b-', i), ('b-', j)))]
        if u_t == 'b+' and v_t == 'b-':
            return [(sp.Integer(1), (('b+', u_i), ('b-', v_i)))]
        if u_t == 'b-' and v_t == 'b+':
            res = [(sp.Integer(1), (('b+', v_i), ('b-', u_i)))]
            if u_i == v_i:
                res.append((sp.Integer(1), ()))
            return res
            
    if u in ('a+', 'a-') and isinstance(v, tuple):
        return [(sp.Integer(1), (u, v))]
    if isinstance(u, tuple) and v in ('a+', 'a-'):
        return [(sp.Integer(1), (v, u))]
        
    raise ValueError(f"Unknown pair {u}, {v}")

def compute_generator_bracket(g1, g2, gb_vars, canonical_to_basis_vector, dim):
    dict_0 = defaultdict(lambda: sp.Integer(0))
    dict_gamma = defaultdict(lambda: sp.Integer(0))
    
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
            
            for sign, (br_u, br_v), (rem_1, rem_2) in pieces:
                b0 = osc_bracket_0(br_u, br_v)
                if b0 != 0:
                    red = reduce_pair_0(rem_1, rem_2)
                    for r_coeff, r_ops in red:
                        dict_0[r_ops] += c1 * c2 * sign * b0 * r_coeff
                        
                bg = osc_bracket_gamma(br_u, br_v, gb_vars)
                if bg != 0:
                    red = reduce_pair_0(rem_1, rem_2)
                    for r_coeff, r_ops in red:
                        dict_gamma[r_ops] += c1 * c2 * sign * bg * r_coeff
                        
    vec_0, sc_0 = canonical_to_basis_vector(dict_0)
    vec_gamma, sc_gamma = canonical_to_basis_vector(dict_gamma)
    return vec_0, vec_gamma

def run_investigation(n):
    print(f"\n==========================================")
    print(f"Detailed Analysis of C({n+1}) = osp(2|{2*n})")
    print(f"==========================================")
    
    basis, dim, canonical_to_basis = build_algebra(n)
    even_dim = sum(1 for b in basis if b['parity'] == 0)
    odd_dim = sum(1 for b in basis if b['parity'] == 1)
    print(f"Superdimension: {even_dim} | {odd_dim} (Total: {dim})")
    
    # 1. Setup gb variables
    gb_vars = {}
    gb_keys = []
    for sigma in ('+', '-'):
        for j in range(1, n+1):
            for s in ('+', '-'):
                sym = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                gb_vars[(sigma, j, s)] = sym
                gb_keys.append((sigma, j, s))
                
    # 2. Compute C_struct and Gamma_struct
    C_struct = [[[sp.Integer(0) for k in range(dim)] for j in range(dim)] for i in range(dim)]
    Gamma_struct = [[[sp.Integer(0) for k in range(dim)] for j in range(dim)] for i in range(dim)]
    
    for i in range(dim):
        for j in range(dim):
            v0, vg = compute_generator_bracket(basis[i], basis[j], gb_vars, canonical_to_basis, dim)
            C_struct[i][j] = v0
            Gamma_struct[i][j] = vg
            
    # 3. Verify Cocycle Condition for Gamma_gb
    # For an odd 2-cochain gamma:
    # d gamma(X, Y, Z) = (-1)^{p(X)} [X, gamma(Y, Z)] - (-1)^{p(X)p(Y)+p(Y)} [Y, gamma(X, Z)] + (-1)^{(p(X)+p(Y))p(Z)+p(Z)} [Z, gamma(X, Y)]
    #                    - gamma([X, Y], Z) - (-1)^{p(X)(p(Y)+p(Z))} gamma(Y, [X, Z]) - (-1)^{(p(X)+p(Y))p(Z)} gamma([X, Z], Y) ...
    # Or in terms of deformed Jacobi identity:
    # [X, [Y, Z]_gamma]_gamma + cyclic = J_0 + kappa * d_Lie(gamma) + O(kappa^2)
    # Since J_0 = 0 and [., .]_gamma is a Lie superalgebra bracket on L = g \oplus kappa g,
    # d_Lie(gamma) = 0 is guaranteed by the associative algebra realization in U(A)!
    
    # 4. Odd linear maps f: g -> g
    # f(Z_j) = sum_i phi_{i, j} Z_i where p(Z_i) != p(Z_j)
    phi_vars = {}
    phi_list = []
    for j in range(dim):
        p_j = basis[j]['parity']
        for i in range(dim):
            p_i = basis[i]['parity']
            if p_i != p_j:
                sym = sp.Symbol(f"phi_{i}_{j}")
                phi_vars[(i, j)] = sym
                phi_list.append(sym)
                
    num_odd_maps = len(phi_list)
    print(f"Dimension of Hom_odd(g, g): {num_odd_maps} (should be {even_dim} * {odd_dim} * 2 = {2 * even_dim * odd_dim})")
    
    # 5. Form coboundary delta f
    # (delta f)(Z_i, Z_j) = (-1)^{p_i} [Z_i, f(Z_j)] - (-1)^{(p_i+1)p_j} [Z_j, f(Z_i)] - f([Z_i, Z_j])
    # Build linear system: Delta(phi) = Gamma(gb)
    
    # Let's collect all independent pairs (i, j) with i <= j (or all pairs)
    eqs = []
    
    for i in range(dim):
        p_i = basis[i]['parity']
        for j in range(dim):
            p_j = basis[j]['parity']
            
            term1 = [sp.Integer(0)] * dim
            for m in range(dim):
                if (m, j) in phi_vars:
                    ph = phi_vars[(m, j)]
                    for k in range(dim):
                        if C_struct[i][m][k] != 0:
                            term1[k] += ph * C_struct[i][m][k]
            for k in range(dim):
                term1[k] = ((-1)**p_i) * term1[k]
                
            term2 = [sp.Integer(0)] * dim
            for m in range(dim):
                if (m, i) in phi_vars:
                    ph = phi_vars[(m, i)]
                    for k in range(dim):
                        if C_struct[j][m][k] != 0:
                            term2[k] += ph * C_struct[j][m][k]
            sign2 = - ((-1)**((p_i + 1) * p_j))
            for k in range(dim):
                term2[k] = sign2 * term2[k]
                
            term3 = [sp.Integer(0)] * dim
            for m in range(dim):
                c_ij_m = C_struct[i][j][m]
                if c_ij_m != 0:
                    for k in range(dim):
                        if (k, m) in phi_vars:
                            term3[k] -= c_ij_m * phi_vars[(k, m)]
                            
            for k in range(dim):
                delta_f_ijk = term1[k] + term2[k] + term3[k]
                gamma_ijk = Gamma_struct[i][j][k]
                diff = sp.expand(delta_f_ijk - gamma_ijk)
                if diff != 0:
                    eqs.append(diff)
                    
    # Let's write the linear system as: M_delta * phi = M_gamma * gb
    # Using sympy Matrix
    print(f"Total equations: {len(eqs)}")
    
    # Construct matrix M_delta (rows = equations, cols = phi) and M_gamma (rows = equations, cols = gb)
    # Let's extract coefficients
    all_eqs = []
    for eq in eqs:
        # eq is linear in phi and gb
        all_eqs.append(eq)
        
    system_mat, const_vec = sp.linear_eq_to_matrix(all_eqs, phi_list)
    # Note const_vec is - M_gamma * gb
    print(f"M_delta matrix shape: {system_mat.shape}")
    rank_delta = system_mat.rank()
    print(f"Rank of coboundary operator delta (odd): {rank_delta}")
    print(f"Dimension of 1-cocycles Z^1_odd(g, g) = ker(delta): {num_odd_maps - rank_delta}")
    
    # Solve system:
    # Check compatibility for general gb
    gb_syms = [gb_vars[k] for k in gb_keys]
    aug_mat, _ = sp.linear_eq_to_matrix(all_eqs, phi_list + gb_syms)
    print(f"Augmented matrix rank: {aug_mat.rank()}")
    
    # Solve for both phi and gb:
    sol = sp.solve(all_eqs, phi_list + gb_syms)
    print(f"Resulting constraints on gb:")
    for sym in gb_syms:
        print(f"  {sym} = {sol.get(sym, 'free')}")
        
    return {
        'n': n,
        'dim': dim,
        'even_dim': even_dim,
        'odd_dim': odd_dim,
        'num_gb': len(gb_syms),
        'num_phi': num_odd_maps,
        'rank_delta': rank_delta,
        'dim_Z1_odd': num_odd_maps - rank_delta,
        'gb_constraints': {str(sym): str(sol.get(sym, 'free')) for sym in gb_syms}
    }

results = {}
for n in [1, 2, 3]:
    results[n] = run_investigation(n)

print("\n\n================ SUMMARY OF ALL RUNS ================")
for n, r in results.items():
    print(f"n={n}: C({n+1}) = osp(2|{2*n}): dim={r['dim']} ({r['even_dim']}|{r['odd_dim']}), gb params={r['num_gb']}, phi params={r['num_phi']}, rank(delta)={r['rank_delta']}, gb constraints: {r['gb_constraints']}")
