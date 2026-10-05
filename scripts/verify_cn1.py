#!/usr/bin/env python3
"""
Comprehensive verification and analysis of the inhomogeneous deformation of C(n+1) = osp(2|2n).
Computes structure constants, deformation 2-cocycles, coboundary operator, and triviality conditions.
"""

import sympy as sp
import numpy as np
import json
import itertools
from collections import defaultdict

def build_cn1_basis(n):
    """
    Constructs basis for C(n+1) = osp(2|2n) in terms of oscillator quadratics.
    Even generators:
      - Z = a1^+ a1^- - 1/2  (so(2) component)
      - h_k = b_k^+ b_k^- + 1/2  (sp(2n) cartan) for k=1..n
      - E_{delta_k - delta_l} = b_k^+ b_l^- (k != l)
      - E_{delta_k + delta_l} = b_k^+ b_l^+ (k < l)
      - E_{-delta_k - delta_l} = b_k^- b_l^- (k < l)
      - E_{2 delta_k} = 1/2 (b_k^+)^2
      - E_{-2 delta_k} = 1/2 (b_k^-)^2
    Odd generators:
      - E_{eps + delta_l} = a1^+ b_l^+
      - E_{eps - delta_l} = a1^+ b_l^-
      - E_{-eps + delta_l} = a1^- b_l^+
      - E_{-eps - delta_l} = a1^- b_l^-
    """
    even_basis = []
    odd_basis = []

    # Even: Z (so(2))
    # Represented as linear combination of normal-ordered monomials
    # Each monomial is (coeff, a_plus_power, a_minus_power, [(b_k_plus_power, b_k_minus_power)])
    # More simply: list of (coeff, (a_plus, a_minus, tuple of (bp_1, bm_1, ..., bp_n, bm_n)))
    
    # Let's represent basis elements by their name, parity, and quadratic expression:
    # A quadratic expression is a dict: tuple of two oscillator indices -> coefficient.
    # Oscillator indexing:
    # 0: a1^+, 1: a1^-
    # For k in 1..n:
    # 2*k: b_k^+, 2*k+1: b_k^-
    
    # Parity of single oscillators:
    # p(0) = 1, p(1) = 1
    # p(2*k) = 0, p(2*k+1) = 0
    
    basis = []
    
    # 1. Even generators:
    # Z = a1^+ a1^- (or a1^+ a1^- - 1/2)
    basis.append({
        'name': 'Z',
        'parity': 0,
        'terms': [((0, 1), sp.Rational(1, 1))]  # a1^+ a1^-
    })
    
    # sp(2n) cartan: h_k = b_k^+ b_k^- for k=1..n
    for k in range(1, n + 1):
        bp = 2 * k
        bm = 2 * k + 1
        basis.append({
            'name': f'h_{k}',
            'parity': 0,
            'terms': [((bp, bm), sp.Rational(1, 1))]
        })
        
    # sp(2n) root vectors:
    # E_{2 delta_k} = 1/2 (b_k^+)^2
    for k in range(1, n + 1):
        bp = 2 * k
        basis.append({
            'name': f'E_2d_{k}',
            'parity': 0,
            'terms': [((bp, bp), sp.Rational(1, 2))]
        })
        
    # E_{-2 delta_k} = 1/2 (b_k^-)^2
    for k in range(1, n + 1):
        bm = 2 * k + 1
        basis.append({
            'name': f'E_-2d_{k}',
            'parity': 0,
            'terms': [((bm, bm), sp.Rational(1, 2))]
        })
        
    # E_{delta_k - delta_l} for k != l
    for k in range(1, n + 1):
        for l in range(1, n + 1):
            if k != l:
                bp_k = 2 * k
                bm_l = 2 * l + 1
                basis.append({
                    'name': f'E_d{k}-d{l}',
                    'parity': 0,
                    'terms': [((bp_k, bm_l), sp.Rational(1, 1))]
                })
                
    # E_{delta_k + delta_l} for k < l
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            bp_k = 2 * k
            bp_l = 2 * l
            basis.append({
                'name': f'E_d{k}+d{l}',
                'parity': 0,
                'terms': [((bp_k, bp_l), sp.Rational(1, 1))]
            })
            
    # E_{-delta_k - delta_l} for k < l
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            bm_k = 2 * k + 1
            bm_l = 2 * l + 1
            basis.append({
                'name': f'E_-d{k}-d{l}',
                'parity': 0,
                'terms': [((bm_k, bm_l), sp.Rational(1, 1))]
            })
            
    # 2. Odd generators:
    for l in range(1, n + 1):
        bp = 2 * l
        bm = 2 * l + 1
        # E_{eps + delta_l} = a1^+ b_l^+
        basis.append({
            'name': f'E_eps+d{l}',
            'parity': 1,
            'terms': [((0, bp), sp.Rational(1, 1))]
        })
        # E_{eps - delta_l} = a1^+ b_l^-
        basis.append({
            'name': f'E_eps-d{l}',
            'parity': 1,
            'terms': [((0, bm), sp.Rational(1, 1))]
        })
        # E_{-eps + delta_l} = a1^- b_l^+
        basis.append({
            'name': f'E_-eps+d{l}',
            'parity': 1,
            'terms': [((1, bp), sp.Rational(1, 1))]
        })
        # E_{-eps - delta_l} = a1^- b_l^-
        basis.append({
            'name': f'E_-eps-d{l}',
            'parity': 1,
            'terms': [((1, bm), sp.Rational(1, 1))]
        })
        
    return basis

def osc_parity(idx):
    if idx in (0, 1):
        return 1
    return 0

def osc_supercommutator(idx1, idx2, gb_symbols):
    """
    Computes [xi_idx1, xi_idx2] in the deformed oscillator algebra.
    Returns (c_0, c_kappa) where:
    bracket = c_0 + c_kappa * kappa
    """
    p1 = osc_parity(idx1)
    p2 = osc_parity(idx2)
    
    # 1. Fermionic-Fermionic: CAR {a1^sigma, a1^sigma'}
    if idx1 in (0, 1) and idx2 in (0, 1):
        if (idx1, idx2) == (0, 1): # {a1^+, a1^-} = 1
            return (sp.Rational(1, 1), sp.Integer(0))
        elif (idx1, idx2) == (1, 0): # {a1^-, a1^+} = 1
            return (sp.Rational(1, 1), sp.Integer(0))
        else:
            return (sp.Integer(0), sp.Integer(0))
            
    # 2. Bosonic-Bosonic: CCR [b_j^s, b_k^s']
    if idx1 >= 2 and idx2 >= 2:
        j = idx1 // 2
        s1 = '+' if idx1 % 2 == 0 else '-'
        k = idx2 // 2
        s2 = '+' if idx2 % 2 == 0 else '-'
        if j == k:
            if s1 == '-' and s2 == '+': # [b_j^-, b_j^+] = 1
                return (sp.Rational(1, 1), sp.Integer(0))
            elif s1 == '+' and s2 == '-': # [b_j^+, b_j^-] = -1
                return (sp.Rational(-1, 1), sp.Integer(0))
        return (sp.Integer(0), sp.Integer(0))
        
    # 3. Bosonic-Fermionic: [b_j^s, a1^sigma] = - gb_{sigma, j, s} * kappa
    # Note: [a1^sigma, b_j^s] = - [b_j^s, a1^sigma] = + gb_{sigma, j, s} * kappa
    if idx1 >= 2 and idx2 in (0, 1): # [b_j^s, a1^sigma]
        j = idx1 // 2
        s = '+' if idx1 % 2 == 0 else '-'
        sigma = '+' if idx2 == 0 else '-'
        gb = gb_symbols[(sigma, j, s)]
        return (sp.Integer(0), -gb)
    elif idx1 in (0, 1) and idx2 >= 2: # [a1^sigma, b_j^s]
        j = idx2 // 2
        s = '+' if idx2 % 2 == 0 else '-'
        sigma = '+' if idx1 == 0 else '-'
        gb = gb_symbols[(sigma, j, s)]
        return (sp.Integer(0), gb)
        
    return (sp.Integer(0), sp.Integer(0))

def bracket_monomials(m1, m2, gb_symbols):
    """
    Computes supercommutator [xi_1 xi_2, eta_1 eta_2] using super-Leibniz:
    [AB, CD] = A [B, CD] + (-1)^{p(B)(p(C)+p(D))} [A, CD] B
    where [X, CD] = [X, C] D + (-1)^{p(X)p(C)} C [X, D]
    
    Returns a dict mapping (ordered pair of osc indices or single osc index or scalar) to (c0, c_kappa).
    Note: single commutator between two osc is scalar + kappa*gb.
    So the product of 4 oscillators reduces to quadratic terms + kappa * quadratic terms!
    """
    A, B = m1
    C, D = m2
    
    pA = osc_parity(A)
    pB = osc_parity(B)
    pC = osc_parity(C)
    pD = osc_parity(D)
    
    # [B, CD] = [B, C] D + (-1)^{pB * pC} C [B, D]
    comm_BC_0, comm_BC_k = osc_supercommutator(B, C, gb_symbols)
    comm_BD_0, comm_BD_k = osc_supercommutator(B, D, gb_symbols)
    
    # [A, CD] = [A, C] D + (-1)^{pA * pC} C [A, D]
    comm_AC_0, comm_AC_k = osc_supercommutator(A, C, gb_symbols)
    comm_AD_0, comm_AD_k = osc_supercommutator(A, D, gb_symbols)
    
    # Result terms: each is a term of form coeff * (i, j)
    # [AB, CD] = A [B, C] D + (-1)^{pB pC} A C [B, D] 
    #            + (-1)^{pB(pC+pD)} [A, C] D B + (-1)^{pB(pC+pD) + pA pC} C [A, D] B
    # Since [B, C], [B, D], [A, C], [A, D] are central elements (scalars or kappa*scalar):
    # Term 1: [B, C] * A D
    # Term 2: (-1)^{pB pC} [B, D] * A C
    # Term 3: (-1)^{pB(pC+pD)} [A, C] * D B
    # Term 4: (-1)^{pB(pC+pD) + pA pC} [A, D] * C B
    
    raw_terms = []
    
    # 1. [B, C] * (A, D)
    raw_terms.append(((comm_BC_0, comm_BC_k), (A, D), 1))
    
    # 2. (-1)^{pB pC} [B, D] * (A, C)
    sign2 = (-1)**(pB * pC)
    raw_terms.append(((comm_BD_0, comm_BD_k), (A, C), sign2))
    
    # 3. (-1)^{pB(pC+pD)} [A, C] * (D, B)
    sign3 = (-1)**(pB * (pC + pD))
    raw_terms.append(((comm_AC_0, comm_AC_k), (D, B), sign3))
    
    # 4. (-1)^{pB(pC+pD) + pA pC} [A, D] * (C, B)
    sign4 = (-1)**(pB * (pC + pD) + pA * pC)
    raw_terms.append(((comm_AD_0, comm_AD_k), (C, B), sign4))
    
    return raw_terms

def canonicalize_quadratic(i, j):
    """
    Expresses an arbitrary product xi_i xi_j in standard normal ordering.
    If i > j:
      for even-even (i, j >= 2): xi_i xi_j = xi_j xi_i + [xi_i, xi_j]_0
      for odd-odd (i, j in 0, 1): xi_1 xi_0 = 1 - xi_0 xi_1
      for odd-even: xi_b xi_a = xi_a xi_b + (no undeformed scalar since [b, a]_0 = 0)
    Returns a dict mapping (canonical_pair) -> coeff, plus constant scalar term if any.
    """
    p_i = osc_parity(i)
    p_j = osc_parity(j)
    
    # We want standard ordering:
    # Odd oscillators (0, 1) first, then bosonic (2, 3, ...).
    # Within odd: 0 (a1^+) before 1 (a1^-).
    # Within bosonic: lower index before higher index.
    
    # Let's check if (i, j) is already ordered:
    # Order: 0, 1, 2, 3, 4, ...
    if i <= j:
        return { (i, j): sp.Rational(1, 1) }, sp.Rational(0, 1)
    else:
        # i > j:
        if i in (0, 1) and j in (0, 1):
            # (1, 0): a1^- a1^+ = 1 - a1^+ a1^-
            return { (0, 1): sp.Rational(-1, 1) }, sp.Rational(1, 1)
        elif i >= 2 and j >= 2:
            # Bosonic: b_i b_j = b_j b_i + [b_i, b_j]_0
            comm_0, _ = osc_supercommutator(i, j, {})
            return { (j, i): sp.Rational(1, 1) }, comm_0
        else:
            # i >= 2 (bosonic) and j in (0, 1) (fermionic)
            # b a = a b + [b, a]_0 = a b (since undeformed [b, a]_0 = 0)
            return { (j, i): sp.Rational(1, 1) }, sp.Rational(0, 1)

def express_in_basis(quad_dict, basis):
    """
    Expresses a linear combination of canonical oscillator pairs in the basis of C(n+1).
    quad_dict: dict of (i, j) -> coeff
    basis: list of basis elements
    Returns a vector of coefficients for basis elements.
    """
    # Build transition matrix from basis elements to canonical pairs
    dim = len(basis)
    # We will match coordinates
    coords = [sp.Rational(0, 1)] * dim
    
    # Note: our basis elements are already simple monomials or single canonical pairs!
    # Let's verify:
    # Z = (0, 1)
    # h_k = (2k, 2k+1)
    # E_2d_k = 1/2 (2k, 2k) -> (2k, 2k) has coeff 2 * E_2d_k
    # E_-2d_k = 1/2 (2k+1, 2k+1) -> (2k+1, 2k+1) has coeff 2 * E_-2d_k
    # E_d_k-d_l = (2k, 2l+1) (where 2k < 2l+1 if k < l, or 2k > 2l+1 if k > l? wait!)
    
    for b_idx, b in enumerate(basis):
        # b['terms'] is list of (pair, coeff)
        pass
        
    return coords

def main():
    print("Running comprehensive C(n+1) deformation analysis...")

if __name__ == '__main__':
    main()
