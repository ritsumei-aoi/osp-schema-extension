#!/usr/bin/env python3
"""
Verification script for C(n+1) = osp(2|2n) inhomogeneous deformation triviality.
Computes:
1. Basis of C(n+1) for n=1, 2, 3.
2. Structure constants of C(n+1) using oscillator representation.
3. Inhomogeneous deformation gamma_gb(X, Y).
4. Coboundary delta f(X, Y) for general odd linear map f.
5. Linear system gamma_gb = delta f and its solutions.
"""

import sympy as sp
from itertools import product

def get_algebra_basis(n):
    """
    Returns the basis elements of C(n+1) = osp(2|2n) as quadratic expressions in oscillators.
    Oscillators:
      Fermionic: a^+ (index ('a', '+')), a^- (index ('a', '-'))
      Bosonic: b_i^+ (index ('b', i, '+')), b_i^- (index ('b', i, '-')) for i=1..n
    
    Generators:
      Even generators (parity 0):
        - so(2): N_a = a^+ a^- - 1/2
        - sp(2n):
            b_i^+ b_j^+ (1 <= i <= j <= n)  [n(n+1)/2]
            b_i^- b_j^- (1 <= i <= j <= n)  [n(n+1)/2]
            (1/2)(b_i^+ b_j^- + b_j^- b_i^+) = b_i^+ b_j^- + 1/2 delta_ij (1 <= i, j <= n) [n^2]
      Odd generators (parity 1):
        - a^+ b_j^+ (1 <= j <= n)
        - a^+ b_j^- (1 <= j <= n)
        - a^- b_j^+ (1 <= j <= n)
        - a^- b_j^- (1 <= j <= n)
    """
    even_basis = []
    odd_basis = []
    
    # 1. so(2) generator
    even_basis.append(('N_a', [ (1, (('a', '+'), ('a', '-'))), (-sp.Rational(1,2), ()) ]))
    
    # 2. sp(2n) generators
    # b_i^+ b_j^+ (i <= j)
    for i in range(1, n+1):
        for j in range(i, n+1):
            even_basis.append((f'B++_{i}_{j}', [ (1, (('b', i, '+'), ('b', j, '+'))) ]))
    # b_i^- b_j^- (i <= j)
    for i in range(1, n+1):
        for j in range(i, n+1):
            even_basis.append((f'B--_{i}_{j}', [ (1, (('b', i, '-'), ('b', j, '-'))) ]))
    # (1/2)(b_i^+ b_j^- + b_j^- b_i^+) = b_i^+ b_j^- + 1/2 delta_ij
    for i in range(1, n+1):
        for j in range(1, n+1):
            terms = [ (1, (('b', i, '+'), ('b', j, '-'))) ]
            if i == j:
                terms.append((sp.Rational(1,2), ()))
            even_basis.append((f'B+-_{i}_{j}', terms))
            
    # 3. Odd generators (4n total)
    for j in range(1, n+1):
        odd_basis.append((f'F++_{j}', [ (1, (('a', '+'), ('b', j, '+'))) ]))
        odd_basis.append((f'F+-_{j}', [ (1, (('a', '+'), ('b', j, '-'))) ]))
        odd_basis.append((f'F-+_{j}', [ (1, (('a', '-'), ('b', j, '+'))) ]))
        odd_basis.append((f'F--_{j}', [ (1, (('a', '-'), ('b', j, '-'))) ]))
        
    basis = []
    for name, expr in even_basis:
        basis.append({'name': name, 'parity': 0, 'expr': expr})
    for name, expr in odd_basis:
        basis.append({'name': name, 'parity': 1, 'expr': expr})
        
    return basis

print("Basis for n=1:")
b1 = get_algebra_basis(1)
print(f"Total generators: {len(b1)}, Even: {sum(1 for x in b1 if x['parity']==0)}, Odd: {sum(1 for x in b1 if x['parity']==1)}")
for g in b1:
    print(f"  {g['name']} (p={g['parity']}): {g['expr']}")
