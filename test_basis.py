import numpy as np
import sympy as sp
from sympy import symbols, Matrix, zeros, solve, Eq

def build_Cn1_algebra(n):
    """
    Build basis and structure constants for C(n+1) = osp(2|2n).
    
    Oscillators:
    Fermionic: a1+, a1-
    Bosonic: b_1^+, b_1^-, ..., b_n^+, b_n^-
    
    Generators of C(n+1):
    Even generators (dim = 2n^2 + n + 1):
      - Na = a1+ a1-
      - B_{i, s; j, r} = b_i^s b_j^r (1 <= i <= j <= n, s,r in {+, -})
    
    Odd generators (dim = 4n):
      - F_{\sigma, i, s} = a1^\sigma b_i^s (\sigma in {+, -}, i in {1..n}, s in {+, -})
    """
    basis_even = []
    basis_odd = []
    
    # Na
    basis_even.append(('Na',))
    
    # Bosonic quadratics
    # b_i^s b_j^r
    for i in range(1, n+1):
        for s in ['+', '-']:
            for j in range(i, n+1):
                start_r = ['+', '-'] if j > i else (['+'] if s == '+' else ['+','-'])
                # Wait, let's systematically list all independent b_i^s b_j^r
                # b_i^+ b_j^+ (1 <= i <= j <= n)
                # b_i^- b_j^- (1 <= i <= j <= n)
                # b_i^+ b_j^- (1 <= i, j <= n)
                pass

    # Let's be very systematic:
    # SP(2n) basis:
    # 1. b_i^+ b_j^+ for 1 <= i <= j <= n  (n(n+1)/2)
    # 2. b_i^- b_j^- for 1 <= i <= j <= n  (n(n+1)/2)
    # 3. b_i^+ b_j^- for 1 <= i, j <= n    (n^2)
    # Total sp(2n) = 2*n(n+1)/2 + n^2 = 2n^2 + n.
    
    sp_basis = []
    for i in range(1, n+1):
        for j in range(i, n+1):
            sp_basis.append(('b+b+', i, j))
    for i in range(1, n+1):
        for j in range(i, n+1):
            sp_basis.append(('b-b-', i, j))
    for i in range(1, n+1):
        for j in range(1, n+1):
            sp_basis.append(('b+b-', i, j))
            
    basis_even = [('Na',)] + sp_basis
    
    # Odd basis: a1^\sigma b_i^s
    for sigma in ['+', '-']:
        for i in range(1, n+1):
            for s in ['+', '-']:
                basis_odd.append(('F', sigma, i, s))
                
    return basis_even, basis_odd

print("Testing basis generation...")
for n in [1, 2, 3]:
    even, odd = build_Cn1_algebra(n)
    print(f"n={n}: even dim = {len(even)} (expected {2*n**2 + n + 1}), odd dim = {len(odd)} (expected {4*n}), total = {len(even)+len(odd)}")
