import sympy as sp
from sympy import symbols, Matrix, zeros, simplify, solve, Symbol

def solve_triviality_for_n(n):
    print(f"\n==================================================")
    print(f"  ANALYZING TRIVIALITY FOR C({n+1}) (n = {n})")
    print(f"==================================================")
    
    # 1. Indexing deformation parameters gb_{sigma, j, s}
    # sigma in {+1, -1}, j in {1..n}, s in {+1, -1}
    gb_syms = {}
    gb_list = []
    for sigma_val, sigma_str in [(1, '+'), (-1, '-')]:
        for j in range(1, n + 1):
            for s_val, s_str in [(1, '+'), (-1, '-')]:
                sym = Symbol(f"gb_{sigma_str}_{j}_{s_str}")
                gb_syms[(sigma_val, j, s_val)] = sym
                gb_list.append(sym)
                
    num_gb = len(gb_list)
    print(f"Number of gb parameters: {num_gb} (expected {4*n})")
    
    # 2. Basis of C(n+1)
    # Bosonic indices: (j, s) for j in 1..n, s in {+1, -1}
    bosons = []
    for j in range(1, n + 1):
        bosons.append((j, 1))   # b_j^+
        bosons.append((j, -1))  # b_j^-
    
    # Even basis:
    # J0 (index 0)
    # Bosonic quadratic generators B_{(j,s),(k,t)}:
    # We define B_{(j,s),(k,t)} = 1/2 (b_j^s b_k^t + b_k^t b_j^s)
    even_basis = ['J0']
    boson_pairs = []
    for i in range(len(bosons)):
        for k in range(i, len(bosons)):
            b1 = bosons[i]
            b2 = bosons[k]
            boson_pairs.append((b1, b2))
            even_basis.append((b1, b2))
            
    # Odd basis: F_{(sigma, j, s)} = a1^sigma b_j^s
    odd_basis = []
    for sigma_val in [1, -1]:
        for j in range(1, n + 1):
            for s_val in [1, -1]:
                odd_basis.append((sigma_val, j, s_val))
                
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    dim_total = dim_even + dim_odd
    print(f"Dimensions: dim_even = {dim_even}, dim_odd = {dim_odd}, total = {dim_total}")
    
    # Let's verify the commutator formulas algebraically:
    # For any basis elements X, Y:
    # We can evaluate [X, Y]_0 and \gamma_{gb}(X, Y).
    
    # Let's represent elements as vectors in C(n+1).
    # Since \gamma: g x g -> g preserves total parity mod 2 (with p(kappa)=1):
    # p(\gamma(X,Y)) = p(X) + p(Y) + 1 mod 2.
    # Case AA: X in g_0, Y in g_0 => \gamma(X,Y) in g_1. But \gamma(g_0, g_0) = 0.
    # Case BB: X in g_1, Y in g_1 => \gamma(X,Y) in g_1.
    # Case AB: X in g_0, Y in g_1 => \gamma(X,Y) in g_0 (up to scalar J0 / 1).
    
    # Let's inspect map f: g -> g (odd linear map).
    # f_0: g_0 -> g_1 (matrix of size dim_odd x dim_even)
    # f_1: g_1 -> g_0 (matrix of size dim_even x dim_odd)
    # Total unknown entries in f: dim_odd * dim_even + dim_even * dim_odd = 2 * dim_even * dim_odd.
    
    # Let's set up the coboundary operator \delta f:
    # (\delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    
    # We want to check if \gamma_{gb}(X, Y) = (\delta f)(X, Y) for all X, Y.
    # This is a system of linear equations in the entries of f!
    # The coefficients of the linear system depend linearly on gb parameters.
    # Solvability of \delta f = \gamma_{gb} for f implies conditions on gb!
    
    return gb_list, dim_even, dim_odd

if __name__ == '__main__':
    for n in [1, 2, 3]:
        solve_triviality_for_n(n)
