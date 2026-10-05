#!/usr/bin/env python3
import sympy as sp
from itertools import product

def get_algebra(n):
    # Oscillators:
    # 'a+': fermionic, p=1
    # 'a-': fermionic, p=1
    # ('b+', i): bosonic, p=0
    # ('b-', i): bosonic, p=0
    
    # Let's define basis of C(n+1)
    # Even:
    # 1. N_a = a^+ a^- - 1/2
    # 2. B++_{i,j} = b_i^+ b_j^+ (1 <= i <= j <= n)
    # 3. B--_{i,j} = b_i^- b_j^- (1 <= i <= j <= n)
    # 4. B+-_{i,j} = (1/2)(b_i^+ b_j^- + b_j^- b_i^+) = b_i^+ b_j^- + 1/2 delta_ij (1 <= i, j <= n)
    # Odd:
    # 5. F++_j = a^+ b_j^+
    # 6. F+-_j = a^+ b_j^-
    # 7. F-+_j = a^- b_j^+
    # 8. F--_j = a^- b_j^-
    
    basis = []
    
    # N_a
    basis.append({
        'name': 'N_a',
        'parity': 0,
        'terms': [(1, ('a+', 'a-')), (-sp.Rational(1,2), ())]
    })
    
    for i in range(1, n+1):
        for j in range(i, n+1):
            basis.append({
                'name': f'B++_{i}_{j}',
                'parity': 0,
                'terms': [(1, (('b+', i), ('b+', j)))]
            })
            
    for i in range(1, n+1):
        for j in range(i, n+1):
            basis.append({
                'name': f'B--_{i}_{j}',
                'parity': 0,
                'terms': [(1, (('b-', i), ('b-', j)))]
            })
            
    for i in range(1, n+1):
        for j in range(1, n+1):
            terms = [(1, (('b+', i), ('b-', j)))]
            if i == j:
                terms.append((sp.Rational(1,2), ()))
            basis.append({
                'name': f'B+-_{i}_{j}',
                'parity': 0,
                'terms': terms
            })
            
    for j in range(1, n+1):
        basis.append({'name': f'F++_{j}', 'parity': 1, 'terms': [(1, ('a+', ('b+', j)))]})
        basis.append({'name': f'F+-_j', 'parity': 1, 'terms': [(1, ('a+', ('b-', j)))]})
        basis.append({'name': f'F-+_{j}', 'parity': 1, 'terms': [(1, ('a-', ('b+', j)))]})
        basis.append({'name': f'F--_{j}', 'parity': 1, 'terms': [(1, ('a-', ('b-', j)))]})
        
    return basis

def osc_parity(u):
    if u in ('a+', 'a-'):
        return 1
    return 0

def osc_bracket_0(u, v):
    # [u, v]_0 = uv - (-1)^{p(u)p(v)} vu
    # Returns scalar c
    if u == 'a-' and v == 'a+':
        return sp.Integer(1)
    if u == 'a+' and v == 'a-':
        return sp.Integer(1) # {a+, a-} = 1, so [a+, a-]_super = a+ a- + a- a+ = 1
    if isinstance(u, tuple) and isinstance(v, tuple):
        # both bosonic
        u_type, u_i = u
        v_type, v_i = v
        if u_type == 'b-' and v_type == 'b+' and u_i == v_i:
            return sp.Integer(1)
        if u_type == 'b+' and v_type == 'b-' and u_i == v_i:
            return sp.Integer(-1)
    return sp.Integer(0)

def osc_bracket_gamma(u, v, gb_vars):
    # Returns coefficient of kappa in [u, v]
    # [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
    # [a_1^sigma, b_j^s] = gb_{sigma, j, s} * kappa
    if isinstance(u, tuple) and v in ('a+', 'a-'):
        s = '+' if u[0] == 'b+' else '-'
        j = u[1]
        sigma = '+' if v == 'a+' else '-'
        # [b_j^s, a^\sigma] = - gb_{sigma, j, s}
        return -gb_vars[(sigma, j, s)]
    elif u in ('a+', 'a-') and isinstance(v, tuple):
        sigma = '+' if u == 'a+' else '-'
        s = '+' if v[0] == 'b+' else '-'
        j = v[1]
        # [a^\sigma, b_j^s] = gb_{sigma, j, s}
        return gb_vars[(sigma, j, s)]
    return sp.Integer(0)

# Product of two oscillators normal ordering / canonical representation
# Standard quadratic basis in U(A):
# a+ a- (even)
# (b+ i)(b+ j) for i <= j (even)
# (b- i)(b- j) for i <= j (even)
# (b+ i)(b- j) for all i, j (even)
# (a+)(b+ j), (a+)(b- j), (a-)(b+ j), (a-)(b- j) (odd)
# 1 (scalar)

def reduce_pair_0(u, v):
    # rewrites u*v in terms of canonical quadratic elements + scalar
    p_u = osc_parity(u)
    p_v = osc_parity(v)
    
    # Fermionic:
    if u in ('a+', 'a-') and v in ('a+', 'a-'):
        if u == 'a+' and v == 'a+':
            return [] # (a+)^2 = 0
        if u == 'a-' and v == 'a-':
            return [] # (a-)^2 = 0
        if u == 'a+' and v == 'a-':
            return [(sp.Integer(1), ('a+', 'a-'))]
        if u == 'a-' and v == 'a+':
            # a- a+ = 1 - a+ a-
            return [(sp.Integer(1), ()), (sp.Integer(-1), ('a+', 'a-'))]
            
    # Bosonic:
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
            # b-_u_i b+_v_i = b+_v_i b-_u_i + delta_{u_i, v_i}
            res = [(sp.Integer(1), (('b+', v_i), ('b-', u_i)))]
            if u_i == v_i:
                res.append((sp.Integer(1), ()))
            return res
            
    # Mixed: fermion & boson
    if u in ('a+', 'a-') and isinstance(v, tuple):
        return [(sp.Integer(1), (u, v))]
    if isinstance(u, tuple) and v in ('a+', 'a-'):
        # b * a = a * b in undeformed
        return [(sp.Integer(1), (v, u))]
        
    raise ValueError(f"Unknown pair {u}, {v}")

def compute_supercommutator_terms(term1, term2, gb_vars):
    # term1 = (coeff1, (u1, u2)) or (coeff1, ())
    # term2 = (coeff2, (v1, v2)) or (coeff2, ())
    c1, ops1 = term1
    c2, ops2 = term2
    if len(ops1) == 0 or len(ops2) == 0:
        return [], []
    u1, u2 = ops1
    v1, v2 = ops2
    
    p_u1, p_u2 = osc_parity(u1), osc_parity(u2)
    p_v1, p_v2 = osc_parity(v1), osc_parity(v2)
    
    # [u1 u2, v1 v2] = [u2, v1] u1 v2 + (-1)^{p(u2)p(v1)} [u2, v2] u1 v1 
    #                 + (-1)^{p(u2)(p(v1)+p(v2))} [u1, v1] v2 u2 + (-1)^{p(u2)(p(v1)+p(v2)) + p(u1)p(v1)} [u1, v2] v1 u2
    # Wait, let's double check signs carefully:
    # [A, B] = AB - (-1)^{p(A)p(B)} BA
    # [u1 u2, V] = u1 [u2, V] + (-1)^{p(u2)p(V)} [u1, V] u2
    # [u, v1 v2] = [u, v1] v2 + (-1)^{p(u)p(v1)} v1 [u, v2]
    
    # Let's derive [u1 u2, v1 v2]:
    # u1 [u2, v1 v2] = u1 ( [u2, v1] v2 + (-1)^{p(u2)p(v1)} v1 [u2, v2] )
    # Since [u2, v1] is central / scalar: u1 [u2, v1] v2 = [u2, v1] u1 v2
    # And u1 v1 [u2, v2] = [u2, v2] u1 v1
    # Second part:
    # (-1)^{p(u2)(p(v1)+p(v2))} [u1, v1 v2] u2
    # = (-1)^{p(u2)(p(v1)+p(v2))} ( [u1, v1] v2 + (-1)^{p(u1)p(v1)} v1 [u1, v2] ) u2
    # = (-1)^{p(u2)(p(v1)+p(v2))} [u1, v1] v2 u2 + (-1)^{p(u2)(p(v1)+p(v2)) + p(u1)p(v1)} [u1, v2] v1 u2
    
    # This formula is completely exact!
    
    sign3 = (-1)**(p_u2 * (p_v1 + p_v2))
    sign4 = (-1)**(p_u2 * (p_v1 + p_v2) + p_u1 * p_v1)
    sign2 = (-1)**(p_u2 * p_v1)
    sign1 = 1
    
    pieces = [
        (sign1, (u2, v1), (u1, v2)),
        (sign2, (u2, v2), (u1, v1)),
        (sign3, (u1, v1), (v2, u2)),
        (sign4, (u1, v2), (v1, u2))
    ]
    
    comm_0 = []
    comm_gamma = []
    
    for sign, (br_u, br_v), (rem_1, rem_2) in pieces:
        # 0-order bracket
        b0 = osc_bracket_0(br_u, br_v)
        if b0 != 0:
            # rem_1 * rem_2 reduced
            red = reduce_pair_0(rem_1, rem_2)
            for r_coeff, r_ops in red:
                comm_0.append((c1 * c2 * sign * b0 * r_coeff, r_ops))
                
        # gamma bracket
        bg = osc_bracket_gamma(br_u, br_v, gb_vars)
        if bg != 0:
            red = reduce_pair_0(rem_1, rem_2)
            for r_coeff, r_ops in red:
                comm_gamma.append((c1 * c2 * sign * bg * r_coeff, r_ops))
                
    return comm_0, comm_gamma

print("Setup completed successfully.")
