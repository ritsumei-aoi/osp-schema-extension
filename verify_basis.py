#!/usr/bin/env python3
"""
Verification of triviality conditions for C(n+1) inhomogeneous deformations.
Algebra: C(n+1) = osp(2|2n).
"""

import sympy as sp
import json

def get_algebra_basis(n):
    """
    Returns basis elements of C(n+1) = osp(2|2n).
    Each basis element is represented as:
    (name, parity, [(coeff, osc1, osc2), ...])
    Oscillators:
    Fermionic: ('a', '+'), ('a', '-')  [parity 1]
    Bosonic: ('b', i, '+'), ('b', i, '-') for i=1..n [parity 0]
    """
    basis = []
    
    # 1. so(2) generator: J0 = (a^+ a^- - a^- a^+)/2 = a^+ a^- - 1/2
    # In normal ordered form: a^+ a^-
    basis.append({
        'name': 'J0',
        'parity': 0,
        'terms': [(1, ('a', '+'), ('a', '-'))] # representing a^+ a^-
    })
    
    # 2. sp(2n) generators:
    # E_{b_i^+, b_j^+} for 1 <= i <= j <= n
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            if i == j:
                name = f"E_b{i}+_b{i}+"
                basis.append({
                    'name': name,
                    'parity': 0,
                    'terms': [(sp.Rational(1, 1), ('b', i, '+'), ('b', i, '+'))]
                })
            else:
                name = f"E_b{i}+_b{j}+"
                basis.append({
                    'name': name,
                    'parity': 0,
                    'terms': [(sp.Rational(1, 1), ('b', i, '+'), ('b', j, '+'))]
                })
                
    # E_{b_i^-, b_j^-} for 1 <= i <= j <= n
    for i in range(1, n + 1):
        for j in range(i, n + 1):
            if i == j:
                name = f"E_b{i}-_b{i}-"
                basis.append({
                    'name': name,
                    'parity': 0,
                    'terms': [(sp.Rational(1, 1), ('b', i, '-'), ('b', i, '-'))]
                })
            else:
                name = f"E_b{i}-_b{j}-"
                basis.append({
                    'name': name,
                    'parity': 0,
                    'terms': [(sp.Rational(1, 1), ('b', i, '-'), ('b', j, '-'))]
                })
                
    # E_{b_i^+, b_j^-} for 1 <= i, j <= n
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            name = f"E_b{i}+_b{j}-"
            basis.append({
                'name': name,
                'parity': 0,
                'terms': [(sp.Rational(1, 1), ('b', i, '+'), ('b', j, '-'))]
            })
            
    # Odd generators (4n total):
    # F_{a1^\sigma, b_j^s} = a_1^\sigma b_j^s
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                name = f"F_a{sigma}_b{j}{s}"
                basis.append({
                    'name': name,
                    'parity': 1,
                    'terms': [(sp.Rational(1, 1), ('a', sigma), ('b', j, s))]
                })
                
    return basis

print("Testing basis generation for n=1, 2, 3:")
for n in [1, 2, 3]:
    b = get_algebra_basis(n)
    even = [x for x in b if x['parity'] == 0]
    odd = [x for x in b if x['parity'] == 1]
    print(f"n={n}: even={len(even)} (expected {2*n**2+n+1}), odd={len(odd)} (expected {4*n}), total={len(b)}")
