import sympy as sp
import numpy as np
import json

def get_basis(n):
    """
    Construct basis elements for C(n+1) = osp(2|2n).
    Oscillators:
    Fermionic: a1+, a1- (index: ('a', '+'), ('a', '-'))
    Bosonic: b_1^+, b_1^-, ..., b_n^+, b_n^- (indices: ('b', j, '+'), ('b', j, '-'))
    
    Returns list of basis dicts:
    {'name': str, 'type': 'even'/'odd', 'ops': tuple of (op1, op2), 'coeff': number}
    """
    basis = []
    
    # Even basis:
    # 1. b_k^+ b_l^+ for 1 <= k <= l <= n
    for k in range(1, n+1):
        for l in range(k, n+1):
            basis.append({
                'name': f'B_{k}_{l}_++',
                'parity': 0,
                'ops': (('b', k, '+'), ('b', l, '+')),
                'coeff': 1
            })
            
    # 2. b_k^- b_l^- for 1 <= k <= l <= n
    for k in range(1, n+1):
        for l in range(k, n+1):
            basis.append({
                'name': f'B_{k}_{l}_--',
                'parity': 0,
                'ops': (('b', k, '-'), ('b', l, '-')),
                'coeff': 1
            })
            
    # 3. b_k^+ b_l^- for 1 <= k, l <= n
    for k in range(1, n+1):
        for l in range(1, n+1):
            basis.append({
                'name': f'B_{k}_{l}_+-',
                'parity': 0,
                'ops': (('b', k, '+'), ('b', l, '-')),
                'coeff': 1
            })
            
    # 4. Fermionic even element: F_0 = a1+ a1-
    basis.append({
        'name': 'F_0',
        'parity': 0,
        'ops': (('a', '+'), ('a', '-')),
        'coeff': 1
    })
    
    # Odd basis:
    # a1^\sigma b_k^s for \sigma in {+,-}, k in {1..n}, s in {+,-}
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                basis.append({
                    'name': f'O_{sigma}_{k}_{s}',
                    'parity': 1,
                    'ops': (('a', sigma), ('b', k, s)),
                    'coeff': 1
                })
                
    return basis

print("Basis script ready")
