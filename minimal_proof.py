#!/usr/bin/env python3
"""
Find minimal inconsistent subsystem of equations to give a clean, transparent analytical proof.
"""

import sympy as sp
from algebra_engine import get_basis, compute_supercommutator_bracket

def find_minimal_proof(n=1):
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
            
    bracket_table = [[None for _ in range(dim)] for _ in range(dim)]
    gamma_table = [[None for _ in range(dim)] for _ in range(dim)]
    
    for i in range(dim):
        for j in range(dim):
            b0, gam = compute_supercommutator_bracket(basis[i], basis[j], basis_names, gb_vars)
            bracket_table[i][j] = b0
            gamma_table[i][j] = gam

    def compute_bracket_with_f(i, j):
        res = {k: sp.Integer(0) for k in range(dim)}
        target_k = odd_indices if basis[j][1] == 0 else even_indices
        for k in target_k:
            phi = phi_vars[(k, j)]
            b_ik = bracket_table[i][k]
            for bname, coeff in b_ik.items():
                k_idx = basis_names.index(bname)
                res[k_idx] += phi * coeff
        return res

    def compute_f_of_bracket(i, j):
        res = {k: sp.Integer(0) for k in range(dim)}
        b_ij = bracket_table[i][j]
        for bname, coeff in b_ij.items():
            m = basis_names.index(bname)
            target_k = odd_indices if basis[m][1] == 0 else even_indices
            for k in target_k:
                phi = phi_vars[(k, m)]
                res[k] += coeff * phi
        return res

    all_eqs = []
    # Let's collect equations with tags indicating their origin (pair (X, Y) and component Z)
    for i in range(dim):
        for j in range(i, dim):
            px, py = basis[i][1], basis[j][1]
            X_fY = compute_bracket_with_f(i, j)
            Y_fX = compute_bracket_with_f(j, i)
            f_XY = compute_f_of_bracket(i, j)
            sign1 = (-1)**px
            sign2 = - ((-1)**((px + 1) * py))
            gam_ij = gamma_table[i][j]
            for k in range(dim):
                delta_f_k = sign1 * X_fY[k] + sign2 * Y_fX[k] - f_XY[k]
                k_name = basis_names[k]
                gam_k = gam_ij.get(k_name, sp.Integer(0))
                eq = sp.simplify(delta_f_k - gam_k)
                if eq != 0:
                    all_eqs.append((f"({basis[i][0]}, {basis[j][0]}) -> {k_name}", eq))
                    
    print(f"Total equations: {len(all_eqs)}")
    
    # Let's focus on a specific gb parameter, e.g. gb_+_1_+
    gb_param = gb_vars[('+', 1, '+')]
    
    # Let's select a small subset of equations involving gb_+_1_+
    selected_eqs = []
    selected_vars = set()
    for tag, eq in all_eqs:
        if gb_param in eq.free_symbols:
            selected_eqs.append((tag, eq))
            selected_vars.update(eq.free_symbols)
            
    print(f"Equations containing gb_+_1_+ directly: {len(selected_eqs)}")
    for tag, eq in selected_eqs:
        print(f"  {tag}: {eq} = 0")
        
    # Let's add equations involving these phi variables until we get a closed system forcing gb_+_1_+ = 0
    curr_eqs = list(selected_eqs)
    curr_vars = set(selected_vars) - {gb_param}
    
    for tag, eq in all_eqs:
        if (tag, eq) not in curr_eqs:
            # Check if this equation only uses currently active phi variables
            eq_phi = eq.free_symbols - set(gb_vars.values())
            if eq_phi and eq_phi.issubset(curr_vars):
                curr_eqs.append((tag, eq))
                
    print(f"\nExpanded small system size: {len(curr_eqs)}")
    eq_list = [eq for tag, eq in curr_eqs]
    sol = sp.solve(eq_list, list(phi_vars.values()) + list(gb_vars.values()), dict=True)
    print("Solution of small subsystem for gb:")
    for s in sol:
        for k in gb_vars.values():
            if k in s:
                print(f"  {k} = {s[k]}")

find_minimal_proof(1)
