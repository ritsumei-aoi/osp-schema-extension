#!/usr/bin/env python3
"""
Full symbolic verification of triviality of C(n+1) inhomogeneous deformation.
"""

import sympy as sp
from collections import defaultdict
import json

def build_algebra(n):
    # Oscillators:
    # 'a+': fermionic, p=1
    # 'a-': fermionic, p=1
    # ('b+', i): bosonic, p=0
    # ('b-', i): bosonic, p=0
    
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
    
    # We also want to map any canonical oscillator quadratic / scalar expression into basis coefficients
    # Canonical terms:
    # ('a+', 'a-') -> N_a + 1/2
    # (('b+', i), ('b+', j)) with i <= j -> B++_{i,j}
    # (('b-', i), ('b-', j)) with i <= j -> B--_{i,j}
    # (('b+', i), ('b-', j)) -> B+-_{i,j} - (1/2 if i==j else 0)
    # ('a+', ('b+', j)) -> F++_j
    # ('a+', ('b-', j)) -> F+-_j
    # ('a-', ('b+', j)) -> F-+_j
    # ('a-', ('b-', j)) -> F--_j
    
    def canonical_to_basis_vector(term_dict):
        # term_dict: dict of tuple_key -> coeff
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
    p_u = osc_parity(u)
    p_v = osc_parity(v)
    
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
    # g1, g2 are basis dicts
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
    
    # Check that scalar parts are 0
    if sc_0 != 0:
        print(f"Warning: non-zero scalar part in undeformed bracket [{g1['name']}, {g2['name']}]: {sc_0}")
    if sc_gamma != 0:
        print(f"Warning: non-zero scalar part in deformed bracket [{g1['name']}, {g2['name']}]: {sc_gamma}")
        
    return vec_0, vec_gamma

def analyze_n(n):
    print(f"\n==========================================")
    print(f"Analyzing C({n+1}) = osp(2|{2*n})")
    print(f"==========================================")
    
    basis, dim, canonical_to_basis = build_algebra(n)
    even_count = sum(1 for b in basis if b['parity'] == 0)
    odd_count = sum(1 for b in basis if b['parity'] == 1)
    print(f"Dimension: {dim} (Even: {even_count}, Odd: {odd_count})")
    
    # Create symbolic gb variables
    gb_vars = {}
    for sigma in ('+', '-'):
        for j in range(1, n+1):
            for s in ('+', '-'):
                sym = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                gb_vars[(sigma, j, s)] = sym
                
    print(f"Number of gb parameters: {len(gb_vars)}")
    
    # Compute structure constants C_ij^k and gamma_ij^k
    # C[i][j][k]
    C_struct = [[[sp.Integer(0) for k in range(dim)] for j in range(dim)] for i in range(dim)]
    Gamma_struct = [[[sp.Integer(0) for k in range(dim)] for j in range(dim)] for i in range(dim)]
    
    for i in range(dim):
        for j in range(dim):
            v0, vg = compute_generator_bracket(basis[i], basis[j], gb_vars, canonical_to_basis, dim)
            C_struct[i][j] = v0
            Gamma_struct[i][j] = vg
            
    # Verify Super-Jacobi identity for undeformed bracket
    # J(X, Y, Z) = (-1)^{p(X)p(Z)} [X, [Y, Z]] + (-1)^{p(Y)p(X)} [Y, [Z, X]] + (-1)^{p(Z)p(Y)} [Z, [X, Y]] = 0
    jacobi_errors = 0
    for i in range(dim):
        p_i = basis[i]['parity']
        for j in range(i, dim):
            p_j = basis[j]['parity']
            for k in range(j, dim):
                p_k = basis[k]['parity']
                
                # [Y, Z]
                bracket_jk = C_struct[j][k]
                term1 = [sp.Integer(0)] * dim
                for m in range(dim):
                    if bracket_jk[m] != 0:
                        for l in range(dim):
                            term1[l] += bracket_jk[m] * C_struct[i][m][l]
                            
                # [Z, X]
                bracket_ki = C_struct[k][i]
                term2 = [sp.Integer(0)] * dim
                for m in range(dim):
                    if bracket_ki[m] != 0:
                        for l in range(dim):
                            term2[l] += bracket_ki[m] * C_struct[j][m][l]
                            
                # [X, Y]
                bracket_ij = C_struct[i][j]
                term3 = [sp.Integer(0)] * dim
                for m in range(dim):
                    if bracket_ij[m] != 0:
                        for l in range(dim):
                            term3[l] += bracket_ij[m] * C_struct[k][m][l]
                            
                s1 = (-1)**(p_i * p_k)
                s2 = (-1)**(p_j * p_i)
                s3 = (-1)**(p_k * p_j)
                
                for l in range(dim):
                    val = s1 * term1[l] + s2 * term2[l] + s3 * term3[l]
                    if val != 0:
                        jacobi_errors += 1
                        
    print(f"Undeformed Super-Jacobi errors: {jacobi_errors} (should be 0)")
    
    # Check 2-cocycle condition for Gamma:
    # d_Lie(Gamma)(X, Y, Z) = 0
    # Let's verify that Gamma is indeed a 2-cocycle!
    
    # Now let's set up the coboundary delta f
    # f is an odd linear map f: g -> g.
    # So if p(X) = 0, f(X) in g_1 (odd).
    # If p(X) = 1, f(X) in g_0 (even).
    # Parameterize f by matrix phi of size dim x dim:
    # f(Z_j) = sum_{i} phi_{i, j} Z_i.
    # Non-zero phi_{i, j} only when p(Z_i) != p(Z_j).
    
    phi_vars = {}
    for j in range(dim):
        p_j = basis[j]['parity']
        for i in range(dim):
            p_i = basis[i]['parity']
            if p_i != p_j: # odd map reverses parity
                phi_vars[(i, j)] = sp.Symbol(f"phi_{i}_{j}")
                
    print(f"Number of linear map parameters (phi): {len(phi_vars)}")
    
    # Formula for delta f:
    # (delta f)(X_i, X_j) = (-1)^{p(X_i)} [X_i, f(X_j)] - (-1)^{(p(X_i)+1)p(X_j)} [X_j, f(X_i)] - f([X_i, X_j])
    # Let's compute delta f in basis:
    # (delta f)(Z_i, Z_j) = sum_k Delta_{i, j}^k Z_k
    
    # Linear equations: Gamma_{i, j}^k = Delta_{i, j}^k
    # We collect all equations: Delta_{i, j}^k(phi) - Gamma_{i, j}^k(gb) = 0
    
    eqs = []
    
    for i in range(dim):
        p_i = basis[i]['parity']
        for j in range(dim):
            p_j = basis[j]['parity']
            
            # 1. (-1)^{p_i} [Z_i, f(Z_j)]
            # f(Z_j) = sum_m phi_{m, j} Z_m
            term1 = [sp.Integer(0)] * dim
            for m in range(dim):
                if (m, j) in phi_vars:
                    ph = phi_vars[(m, j)]
                    for k in range(dim):
                        if C_struct[i][m][k] != 0:
                            term1[k] += ph * C_struct[i][m][k]
            for k in range(dim):
                term1[k] = ((-1)**p_i) * term1[k]
                
            # 2. - (-1)^{(p_i + 1) p_j} [Z_j, f(Z_i)]
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
                
            # 3. - f([Z_i, Z_j])
            # [Z_i, Z_j] = sum_m C_struct[i][j][m] Z_m
            # f([Z_i, Z_j]) = sum_m C_struct[i][j][m] sum_k phi_{k, m} Z_k
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
                    
    print(f"Total equations to satisfy (gamma = delta f): {len(eqs)}")
    
    # Solve the linear system for phi in terms of gb
    phi_list = list(phi_vars.values())
    gb_list = list(gb_vars.values())
    
    sol = sp.solve(eqs, phi_list)
    print(f"Solution type: {type(sol)}")
    if isinstance(sol, dict):
        print(f"Solution found! Number of determined phi vars: {len(sol)}")
        # Check if any constraints on gb remain:
        # Substitute solution back into equations
        remaining = [sp.expand(eq.subs(sol)) for eq in eqs]
        remaining = [eq for eq in remaining if eq != 0]
        print(f"Remaining constraints on gb parameters: {len(remaining)}")
        if len(remaining) == 0:
            print(">>> RESULT: gamma_gb IS A COBOUNDARY (TRIVIAL) FOR ALL gb PARAMETERS!")
        else:
            print(f">>> Remaining equations on gb: {remaining}")
    elif isinstance(sol, list):
        if len(sol) == 0:
            print(">>> RESULT: NO SOLUTION for general gb! Let's find constraints on gb.")
            # Solve for both phi and gb
            sol_all = sp.solve(eqs, phi_list + gb_list)
            print(f"Solution with gb: {sol_all}")
        else:
            print(f"List solution: {sol}")

analyze_n(1)
