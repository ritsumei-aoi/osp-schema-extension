import sympy as sp
from itertools import product

def solve_deformation(n_val=1):
    print(f"=== Running analysis for n = {n_val} ===")
    
    # Let's define the basis of oscillators:
    # Fermions: a^+, a^-
    # Bosons: b_j^+, b_j^- for j in 1..n
    # And kappa (odd central parameter)
    
    # gb parameters:
    # gb_{sigma, j, s} where sigma in {+, -}, s in {+, -}, j in 1..n
    gb_symbols = {}
    for sigma in ['+', '-']:
        for j in range(1, n_val + 1):
            for s in ['+', '-']:
                name = f"gb_{sigma}_{j}_{s}"
                gb_symbols[(sigma, j, s)] = sp.Symbol(name)
                
    print(f"gb parameters ({len(gb_symbols)}): {list(gb_symbols.keys())}")
    
    # Basis of C(n+1):
    # Even basis:
    # 1. J_0 = a^+ a^- - 1/2
    # 2. b_j^+ b_k^+ (1 <= j <= k <= n)
    # 3. b_j^- b_k^- (1 <= j <= k <= n)
    # 4. 1/2 (b_j^+ b_k^- + b_k^- b_j^+) = b_j^+ b_k^- + 1/2 delta_jk (1 <= j, k <= n)
    
    even_basis = []
    # J0
    even_basis.append(('J0',))
    # B++
    for j in range(1, n_val + 1):
        for k in range(j, n_val + 1):
            even_basis.append(('B++', j, k))
    # B--
    for j in range(1, n_val + 1):
        for k in range(j, n_val + 1):
            even_basis.append(('B--', j, k))
    # B+-
    for j in range(1, n_val + 1):
        for k in range(1, n_val + 1):
            even_basis.append(('B+-', j, k))
            
    odd_basis = []
    # F_{sigma, j, s} = a^sigma b_j^s
    for sigma in ['+', '-']:
        for j in range(1, n_val + 1):
            for s in ['+', '-']:
                odd_basis.append(('F', sigma, j, s))
                
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    print(f"dim even = {dim_even}, dim odd = {dim_odd}, total = {dim_even + dim_odd}")
    
    # Let's represent elements in universal enveloping algebra as polynomials in standard normal ordered monomials.
    # Normal ordering:
    # Order of operators:
    # a^+, a^-, b_1^+, ..., b_n^+, b_1^-, ..., b_n^-, kappa
    # Note: for quadratic elements and their commutators, we can also write an exact rewrite rule for any product of two basis elements!
    
    # Let's define the basis elements as linear combinations of ordered monomials.
    # An ordered monomial is (n_a_plus, n_a_minus, tuple(n_b_plus), tuple(n_b_minus), n_kappa)
    # where n_a_plus, n_a_minus in {0, 1}, n_kappa in {0, 1}.
    
    return even_basis, odd_basis, gb_symbols

if __name__ == "__main__":
    solve_deformation(1)
    solve_deformation(2)
    solve_deformation(3)
