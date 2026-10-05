#!/usr/bin/env python3
"""
Complete algebraic engine for C(n+1) = osp(2|2n) Lie superalgebra,
its inhomogeneous deformations, and coboundary analysis.
"""

import sympy as sp
from itertools import product
import json

def get_basis(n):
    """
    Returns list of basis elements.
    Each element is (name, parity, [(coeff, osc1, osc2)])
    Oscillators:
      ('a', '+'), ('a', '-') : parity 1
      ('b', i, '+'), ('b', i, '-') for i=1..n : parity 0
    """
    basis = []
    
    # 1. J0 = a^+ a^-
    basis.append(('J0', 0, [(sp.Integer(1), ('a', '+'), ('a', '-'))]))
    
    # 2. Bosonic pairs
    # b_i^+ b_j^+ for 1 <= i <= j <= n
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            basis.append((f"E_bp_{i}_bp_{j}", 0, [(sp.Integer(1), ('b', i, '+'), ('b', j, '+'))]))
            
    # b_i^- b_j^- for 1 <= i <= j <= n
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            basis.append((f"E_bm_{i}_bm_{j}", 0, [(sp.Integer(1), ('b', i, '-'), ('b', j, '-'))]))
            
    # b_i^+ b_j^- for 1 <= i, j <= n
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            basis.append((f"E_bp_{i}_bm_{j}", 0, [(sp.Integer(1), ('b', i, '+'), ('b', j, '-'))]))
            
    # 3. Odd generators (4n total)
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                basis.append((f"F_a{sigma}_b{j}{s}", 1, [(sp.Integer(1), ('a', sigma), ('b', j, s))]))
                
    return basis

def osc_parity(u):
    return 1 if u[0] == 'a' else 0

def single_osc_bracket_undeformed(u, v):
    """
    Computes [u, v]_0 (supercommutator) as a scalar.
    Returns sympy scalar.
    """
    # [a^-, a^+] = 1, [a^+, a^-] = 1, [a^\pm, a^\pm] = 0
    if u[0] == 'a' and v[0] == 'a':
        if u[1] != v[1]:
            return sp.Integer(1)
        else:
            return sp.Integer(0)
    # [b_i^-, b_j^+] = delta_ij, [b_i^+, b_j^-] = -delta_ij
    if u[0] == 'b' and v[0] == 'b':
        i, su = u[1], u[2]
        j, sv = v[1], v[2]
        if i == j:
            if su == '-' and sv == '+':
                return sp.Integer(1)
            elif su == '+' and sv == '-':
                return sp.Integer(-1)
        return sp.Integer(0)
    return sp.Integer(0)

def single_osc_bracket_deformed(u, v, gb_vars):
    """
    Computes the delta term in [u, v]_def = [u, v]_0 + kappa * delta(u, v).
    Returns sympy expression linear in gb_vars.
    gb_vars is dict: ('+', j, '+') -> gb_{a1^+, bj^+}, etc.
    Recall:
      [b_j^s, a_1^sigma] = - gb_{sigma, j, s} kappa
      [a_1^sigma, b_j^s] = + gb_{sigma, j, s} kappa
    """
    if u[0] == 'a' and v[0] == 'b':
        sigma = u[1]
        j, s = v[1], v[2]
        return gb_vars[(sigma, j, s)]
    elif u[0] == 'b' and v[0] == 'a':
        j, s = u[1], u[2]
        sigma = v[1]
        return -gb_vars[(sigma, j, s)]
    return sp.Integer(0)

def reduce_osc_pair_to_basis(u, v, basis_names):
    """
    Reduces a product u * v of two oscillators to a linear combination of basis elements.
    Returns dict: basis_name -> coeff. (Scalars/central terms are dropped for adjoint rep).
    """
    res = {}
    
    # 1. Odd: a * b or b * a
    if u[0] == 'a' and v[0] == 'b':
        name = f"F_a{u[1]}_b{v[1]}{v[2]}"
        res[name] = sp.Integer(1)
        return res
    if u[0] == 'b' and v[0] == 'a':
        # b * a = a * b (modulo kappa, but here this is in undeformed product)
        name = f"F_a{v[1]}_b{u[1]}{u[2]}"
        res[name] = sp.Integer(1)
        return res
        
    # 2. Fermion-fermion: a * a
    if u[0] == 'a' and v[0] == 'a':
        if u[1] == '+' and v[1] == '-':
            # a^+ a^- = J0
            res['J0'] = sp.Integer(1)
        elif u[1] == '-' and v[1] == '+':
            # a^- a^+ = 1 - a^+ a^- = -J0 (modulo 1)
            res['J0'] = sp.Integer(-1)
        # a^+ a^+ = 0, a^- a^- = 0
        return res
        
    # 3. Boson-boson: b * b
    if u[0] == 'b' and v[0] == 'b':
        i, su = u[1], u[2]
        j, sv = v[1], v[2]
        if su == '+' and sv == '+':
            if i <= j:
                res[f"E_bp_{i}_bp_{j}"] = sp.Integer(1)
            else:
                res[f"E_bp_{j}_bp_{i}"] = sp.Integer(1)
        elif su == '-' and sv == '-':
            if i <= j:
                res[f"E_bm_{i}_bm_{j}"] = sp.Integer(1)
            else:
                res[f"E_bm_{j}_bm_{i}"] = sp.Integer(1)
        elif su == '+' and sv == '-':
            res[f"E_bp_{i}_bm_{j}"] = sp.Integer(1)
        elif su == '-' and sv == '+':
            # b_i^- b_j^+ = b_j^+ b_i^- + delta_ij
            res[f"E_bp_{j}_bm_{i}"] = sp.Integer(1)
        return res
        
    return res

def compute_supercommutator_bracket(gen1, gen2, basis_names, gb_vars=None):
    """
    Computes [gen1, gen2] = [gen1, gen2]_0 (+ kappa * gamma(gen1, gen2) if gb_vars given).
    gen1 and gen2 are basis tuples (name, parity, [(coeff, u1, u2), ...])
    Returns:
      if gb_vars is None: dict {basis_name: coeff}
      if gb_vars is not None: (bracket_0_dict, gamma_dict)
    """
    name1, p1, terms1 = gen1
    name2, p2, terms2 = gen2
    
    bracket_0 = {name: sp.Integer(0) for name in basis_names}
    gamma = {name: sp.Integer(0) for name in basis_names}
    
    for c1, u1, u2 in terms1:
        pu1, pu2 = osc_parity(u1), osc_parity(u2)
        for c2, v1, v2 in terms2:
            pv1, pv2 = osc_parity(v1), osc_parity(v2)
            c = c1 * c2
            
            # [u1 u2, v1 v2] =
            #   u1 [u2, v1] v2
            # + (-1)^{pu2 * pv1} u1 v1 [u2, v2]
            # + (-1)^{pu2 * (pv1 + pv2)} [u1, v1] v2 u2
            # + (-1)^{pu2 * (pv1 + pv2) + pu1 * pv1} v1 [u1, v2] u2
            
            pairs = [
                (u2, v1, u1, v2, 1),
                (u2, v2, u1, v1, (-1)**(pu2 * pv1)),
                (u1, v1, v2, u2, (-1)**(pu2 * (pv1 + pv2))),
                (u1, v2, v1, u2, (-1)**(pu2 * (pv1 + pv2) + pu1 * pv1))
            ]
            
            for comm_a, comm_b, rem_a, rem_b, sign in pairs:
                # 1. Undeformed part
                comm_0 = single_osc_bracket_undeformed(comm_a, comm_b)
                if comm_0 != 0:
                    red = reduce_osc_pair_to_basis(rem_a, rem_b, basis_names)
                    for bname, bcoeff in red.items():
                        bracket_0[bname] += c * sign * comm_0 * bcoeff
                        
                # 2. Deformed part
                if gb_vars is not None:
                    comm_def = single_osc_bracket_deformed(comm_a, comm_b, gb_vars)
                    if comm_def != 0:
                        red = reduce_osc_pair_to_basis(rem_a, rem_b, basis_names)
                        for bname, bcoeff in red.items():
                            gamma[bname] += c * sign * comm_def * bcoeff
                            
    # Clean zero entries
    bracket_0 = {k: v for k, v in bracket_0.items() if v != 0}
    gamma = {k: v for k, v in gamma.items() if v != 0}
    
    if gb_vars is None:
        return bracket_0
    else:
        return bracket_0, gamma

