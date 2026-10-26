"""
Scratch script to examine the coboundary and gamma structure.
"""
from collections import defaultdict
from fractions import Fraction
import sympy as sp
from src.C_generators import build_c_basis, compute_structure_constants

# Let's inspect the coboundary operator delta f: g x g -> g
# from docs/math/C_coboundary_definition.md:
# (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
# where f: g -> g is an odd linear map (so p(f(X)) = 1 - p(X)).

def compute_coboundary_matrix(n):
    even_basis, odd_basis, gens = build_c_basis(n)
    full_basis = even_basis + odd_basis
    dim = len(full_basis)
    parity = {g: gens[g]["parity"] for g in full_basis}
    
    # Structure constants
    sc_list, _ = compute_structure_constants(n)
    bracket_dict = defaultdict(dict)
    for sc in sc_list:
        bracket_dict[(sc["X"], sc["Y"])][sc["Z"]] = Fraction(sc["coeff"])
        
    print(f"n={n}: dim={dim}, even={len(even_basis)}, odd={len(odd_basis)}")
    # f is an odd linear map:
    # f maps even generators to odd subspace (dim_even * dim_odd parameters)
    # f maps odd generators to even subspace (dim_odd * dim_even parameters)
    # Total parameters of f: 2 * dim_even * dim_odd.
    n_params = 2 * len(even_basis) * len(odd_basis)
    print(f"Total parameters for odd linear map f: {n_params}")
    
    return full_basis, parity, bracket_dict

if __name__ == "__main__":
    compute_coboundary_matrix(1)
