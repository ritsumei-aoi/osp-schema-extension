#!/usr/bin/env python3
"""
Detailed algebraic analysis of coboundary vs gamma.
"""

import sympy as sp
from algebra_engine import get_basis, compute_supercommutator_bracket

def analyze_system(n=1):
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
                
    phi_vars = {}
    for j in even_indices:
        for i in odd_indices:
            phi_vars[(i, j)] = sp.Symbol(f"phi_{i}_{j}")
    for j in odd_indices:
        for i in even_indices:
            phi_vars[(i, j)] = sp.Symbol(f"phi_{i}_{j}")
            
    # For each odd generator X_k (k in odd_indices):
    # gamma(X_k, X_k) = -2 * gb_{sigma, j, s} * X_k
    # delta f(X_k, X_k) = -2 * [X_k, f(X_k)] = 2 * [f(X_k), X_k]
    print("Examining (X_k, X_k) for odd generators:")
    for k in odd_indices:
        X = basis[k]
        name = X[0]
        _, gam = compute_supercommutator_bracket(X, X, basis_names, gb_vars)
        print(f"X = {name}:")
        print(f"  gamma({name}, {name}) = {gam}")
        
        # compute [f(X), X]
        # f(X) = sum_{e in even_indices} phi_{(e, k)} basis[e]
        f_X_bracket_X = {b: sp.Integer(0) for b in basis_names}
        for e in even_indices:
            phi = phi_vars[(e, k)]
            b0 = compute_supercommutator_bracket(basis[e], X, basis_names)
            for bname, coeff in b0.items():
                f_X_bracket_X[bname] += phi * coeff
                
        delta_f_XX = {b: 2 * coeff for b, coeff in f_X_bracket_X.items() if coeff != 0}
        print(f"  delta f({name}, {name}) = {delta_f_XX}")

analyze_system(1)
