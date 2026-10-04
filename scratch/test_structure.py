import sympy as sp
from itertools import product

def solve_cn(n):
    print(f"="*60)
    print(f"Solving triviality condition for C({n+1}) = osp(2|2{n})")
    print(f"="*60)
    
    # 1. Define basis elements of g = C(n+1)
    # Fermionic oscillators: a_1^+, a_1^-
    # Bosonic oscillators: b_k^+, b_k^- (k=1..n)
    
    # Even generators:
    # Z = a1+ a1- - 1/2
    # Bosonic sp(2n) generators:
    # B_{k,s; l,s'} = b_k^s b_l^{s'} (for (k,s) <= (l,s') in some order)
    
    bosonic_indices = []
    for k in range(1, n+1):
        bosonic_indices.append((k, '+'))
        bosonic_indices.append((k, '-'))
    
    # Sp(2n) basis generators (quadratic in b)
    # We can represent them as pairs (idx1, idx2) with idx1 <= idx2
    sp_basis = []
    for i in range(len(bosonic_indices)):
        for j in range(i, len(bosonic_indices)):
            sp_basis.append((bosonic_indices[i], bosonic_indices[j]))
            
    # Total even basis: ['Z'] + sp_basis
    even_basis = ['Z'] + [f"B({b1[0]}^{b1[1]},{b2[0]}^{b2[1]})" for b1, b2 in sp_basis]
    
    # Odd generators: O_{sigma, k, s} = a1^sigma b_k^s
    odd_basis = []
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                odd_basis.append(f"O_{sigma}_{k}^{s}")
                
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    print(f"n={n}: dim(even) = {dim_even}, dim(odd) = {dim_odd}, total = {dim_even + dim_odd}")
    
    # Deformation parameters: gb_{sigma, k, s}
    gb_params = {}
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                gb_params[(sigma, k, s)] = sp.Symbol(f"gb_{sigma}_{k}_{s}")
                
    gb_vars = list(gb_params.values())
    
    # Odd linear map f: g -> g
    # f(even) in odd_basis
    # f(odd) in even_basis
    
    f_even_vars = {}
    for e in even_basis:
        for o in odd_basis:
            f_even_vars[(e, o)] = sp.Symbol(f"phi_{e}_{o}")
            
    f_odd_vars = {}
    for o in odd_basis:
        for e in even_basis:
            f_odd_vars[(o, e)] = sp.Symbol(f"phi_{o}_{e}")
            
    all_f_vars = list(f_even_vars.values()) + list(f_odd_vars.values())
    
    # Let's define the bracket [, ]_0 on g, gamma_gb(X, Y), and delta f(X, Y).
    # To do this cleanly, let's implement normal ordering commutator logic in sympy.
    
    return even_basis, odd_basis, gb_vars, all_f_vars

even, odd, gbs, fs = solve_cn(1)
print("Even basis:", even)
print("Odd basis:", odd)
