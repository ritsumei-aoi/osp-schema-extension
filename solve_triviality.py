#!/usr/bin/env python3
"""
Triviality analysis for C(n+1) = osp(2|2n) inhomogeneous deformations.
Solves gamma_{gb} = delta f.
"""

import sympy as sp
from algebra_engine import get_basis, compute_supercommutator_bracket
import json

def analyze_triviality(n):
    print(f"============================================================")
    print(f"               ANALYZING TRIVIALITY FOR n = {n}")
    print(f"============================================================")
    
    basis = get_basis(n)
    basis_names = [b[0] for b in basis]
    dim = len(basis)
    even_indices = [i for i, b in enumerate(basis) if b[1] == 0]
    odd_indices = [i for i, b in enumerate(basis) if b[1] == 1]
    
    dim_even = len(even_indices)
    dim_odd = len(odd_indices)
    
    print(f"Algebra C({n+1}): dim = {dim} (even={dim_even}, odd={dim_odd})")
    
    # 1. Parameterize gb
    gb_vars = {}
    gb_list = []
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                var = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                gb_vars[(sigma, j, s)] = var
                gb_list.append(var)
    print(f"Number of gb deformation parameters: {len(gb_list)} (expected {4*n})")
    
    # 2. Parameterize odd map f: g -> g
    # f(even) in odd, f(odd) in even
    # phi[i, j] is the coefficient of basis[i] in f(basis[j])
    phi_vars = {}
    phi_list = []
    
    # f on even generators: maps even j to odd i
    for j in even_indices:
        for i in odd_indices:
            var = sp.Symbol(f"phi_{i}_{j}")
            phi_vars[(i, j)] = var
            phi_list.append(var)
            
    # f on odd generators: maps odd j to even i
    for j in odd_indices:
        for i in even_indices:
            var = sp.Symbol(f"phi_{i}_{j}")
            phi_vars[(i, j)] = var
            phi_list.append(var)
            
    print(f"Number of parameters in f: {len(phi_list)} ({dim_even}*{dim_odd}*2 = {2*dim_even*dim_odd})")
    
    # Precompute undeformed brackets between all basis pairs
    # bracket_table[i][j] = dict {k: coeff} for [basis[i], basis[j]]_0
    bracket_table = [[None for _ in range(dim)] for _ in range(dim)]
    gamma_table = [[None for _ in range(dim)] for _ in range(dim)]
    
    for i in range(dim):
        for j in range(dim):
            b0, gam = compute_supercommutator_bracket(basis[i], basis[j], basis_names, gb_vars)
            bracket_table[i][j] = b0
            gamma_table[i][j] = gam

    # Helper to compute [basis[i], f(basis[j])]
    # f(basis[j]) = sum_{k} phi_{(k, j)} * basis[k]
    # So [basis[i], f(basis[j])] = sum_{k} phi_{(k, j)} * [basis[i], basis[k]]
    def compute_bracket_with_f(i, j):
        res = {k: sp.Integer(0) for k in range(dim)}
        # depending on parity of j, k runs over odd or even
        target_k = odd_indices if basis[j][1] == 0 else even_indices
        for k in target_k:
            phi = phi_vars[(k, j)]
            b_ik = bracket_table[i][k]
            for bname, coeff in b_ik.items():
                k_idx = basis_names.index(bname)
                res[k_idx] += phi * coeff
        return res

    # Helper to compute f([basis[i], basis[j]])
    # [basis[i], basis[j]] = sum_m c_m * basis[m]
    # f(...) = sum_m c_m * f(basis[m]) = sum_m c_m * sum_k phi_{(k, m)} basis[k]
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

    # Now compute delta f (X, Y) for all pairs (i, j) with i <= j
    # Formula: (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    equations = []
    
    for i in range(dim):
        for j in range(i, dim):
            px, py = basis[i][1], basis[j][1]
            
            # [X, f(Y)]
            X_fY = compute_bracket_with_f(i, j)
            # [Y, f(X)]
            Y_fX = compute_bracket_with_f(j, i)
            # f([X, Y])
            f_XY = compute_f_of_bracket(i, j)
            
            sign1 = (-1)**px
            sign2 = - ((-1)**((px + 1) * py))
            
            # delta_f_ij on basis element k
            gam_ij = gamma_table[i][j]
            
            for k in range(dim):
                delta_f_k = sign1 * X_fY[k] + sign2 * Y_fX[k] - f_XY[k]
                k_name = basis_names[k]
                gam_k = gam_ij.get(k_name, sp.Integer(0))
                
                # Equation: delta_f_k - gam_k == 0
                eq = sp.simplify(delta_f_k - gam_k)
                if eq != 0:
                    equations.append(eq)
                    
    print(f"Total non-trivial scalar equations generated: {len(equations)}")
    
    # 3. Solve the linear system for phi_vars and constraints on gb_vars
    print("Solving linear system for phi in terms of gb...")
    sol = sp.solve(equations, phi_list, dict=True)
    
    print(f"Solution result count: {len(sol)}")
    if len(sol) == 0:
        print("NO SOLUTION for arbitrary gb! Checking constraints on gb...")
        # Solve for both phi and gb
        all_vars = phi_list + gb_list
        sol_all = sp.solve(equations, all_vars, dict=True)
        print(f"Joint solution for (phi, gb): {sol_all}")
    else:
        sol_phi = sol[0]
        # Check if there are any remaining equations (constraints on gb)
        remaining_eqs = []
        for eq in equations:
            subbed = sp.simplify(eq.subs(sol_phi))
            if subbed != 0:
                remaining_eqs.append(subbed)
        print(f"Remaining constraint equations on gb: {len(remaining_eqs)}")
        if len(remaining_eqs) == 0:
            print("SUCCESS! gamma_{gb} is a coboundary for ALL gb configurations without any constraint on gb!")
            print("A sample solution for f in terms of gb:")
            # Print non-zero entries of f
            non_zero_phi = {str(k): v for k, v in sol_phi.items() if v != 0}
            print(f"Number of non-zero phi components: {len(non_zero_phi)}")
            for k, v in list(non_zero_phi.items())[:10]:
                print(f"  {k} = {v}")
        else:
            print("Constraints on gb:")
            gb_sol = sp.solve(remaining_eqs, gb_list, dict=True)
            print(f"gb constraints: {gb_sol}")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        analyze_triviality(n)
