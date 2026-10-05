#!/usr/bin/env python3
"""
Inspect the mathematical mechanism that forces gb = 0.
"""

import sympy as sp
from algebra_engine import get_basis, compute_supercommutator_bracket

def explain_obstruction(n=1):
    basis = get_basis(n)
    basis_names = [b[0] for b in basis]
    dim = len(basis)
    even_indices = [i for i, b in enumerate(basis) if b[1] == 0]
    odd_indices = [i for i, b in enumerate(basis) if b[1] == 1]
    
    gb_vars = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb_vars[(sigma, j, s)] = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                
    # Let's inspect gamma(X, Y) for all pairs:
    print(f"--- Non-zero gamma(X, Y) pairs for n={n} ---")
    for i in range(dim):
        for j in range(i, dim):
            _, gam = compute_supercommutator_bracket(basis[i], basis[j], basis_names, gb_vars)
            if gam:
                print(f"gamma({basis[i][0]}, {basis[j][0]}) = {gam}")

explain_obstruction(1)
