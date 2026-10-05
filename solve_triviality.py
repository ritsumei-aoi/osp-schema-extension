"""
Solve triviality condition gamma_{gb} = delta f for C(n+1)
"""
import sympy as sp
from itertools import product
from verify_cn1 import get_algebra
from verify_brackets import compute_brackets

def compute_delta_f(alg, phi_matrix, bracket_0):
    dim_g = alg['dim_g']
    generators = alg['generators']
    p = [g['parity'] for g in generators]
    
    # delta_f[i][j] = vector in g
    delta_f = [[sp.zeros(dim_g, 1) for _ in range(dim_g)] for _ in range(dim_g)]
    
    # f(Z_j) = sum_i phi[i, j] Z_i
    # Note: phi[i, j] != 0 only if p[i] = 1 - p[j]
    
    for i in range(dim_g):
        for j in range(dim_g):
            # Term 1: (-1)^p(X) [X, f(Y)] = (-1)^p[i] sum_m phi[m, j] [Z_i, Z_m]
            term1 = sp.zeros(dim_g, 1)
            for m in range(dim_g):
                if phi_matrix[m, j] != 0:
                    term1 += phi_matrix[m, j] * bracket_0[i][m]
            term1 *= (-1)**p[i]
            
            # Term 2: - (-1)^((p(X)+1)p(Y)) [Y, f(X)] = - (-1)^((p[i]+1)p[j]) sum_m phi[m, i] [Z_j, Z_m]
            term2 = sp.zeros(dim_g, 1)
            for m in range(dim_g):
                if phi_matrix[m, i] != 0:
                    term2 += phi_matrix[m, i] * bracket_0[j][m]
            term2 *= - ((-1)**((p[i] + 1) * p[j]))
            
            # Term 3: - f([X, Y]) = - sum_k [Z_i, Z_j]_k f(Z_k) = - sum_k bracket_0[i][j][k] sum_m phi[m, k] Z_m
            term3 = sp.zeros(dim_g, 1)
            for k in range(dim_g):
                b_ijk = bracket_0[i][j][k]
                if b_ijk != 0:
                    for m in range(dim_g):
                        if phi_matrix[m, k] != 0:
                            term3[m] -= b_ijk * phi_matrix[m, k]
                            
            delta_f[i][j] = term1 + term2 + term3
            
    return delta_f

def test_triviality(n):
    print(f"\n=================== Testing Triviality for n = {n} ===================")
    alg = get_algebra(n)
    dim_g = alg['dim_g']
    generators = alg['generators']
    p = [g['parity'] for g in generators]
    
    bracket_0, gamma_def = compute_brackets(alg)
    
    # Create generic odd phi parameters
    phi_symbols = []
    phi_matrix = sp.zeros(dim_g, dim_g)
    
    for j in range(dim_g):
        for i in range(dim_g):
            if p[i] == 1 - p[j]:
                sym = sp.Symbol(f'phi_{i}_{j}')
                phi_symbols.append(sym)
                phi_matrix[i, j] = sym
                
    print(f"Number of phi parameters: {len(phi_symbols)}")
    print(f"Number of gb parameters: {len(alg['gb_symbols'])}")
    
    delta_f = compute_delta_f(alg, phi_matrix, bracket_0)
    
    # Check graded skew-symmetry of delta_f
    skew_delta_ok = True
    for i in range(dim_g):
        for j in range(dim_g):
            expected = - ((-1)**(p[i]*p[j])) * delta_f[i][j]
            diff = delta_f[j][i] - expected
            if any(sp.simplify(val) != 0 for val in diff):
                print(f"Skew-symmetry failed for delta_f between {generators[i]['name']} and {generators[j]['name']}")
                skew_delta_ok = False
                break
        if not skew_delta_ok:
            break
    print(f"delta_f graded skew-symmetry: {'PASSED' if skew_delta_ok else 'FAILED'}")
    
    # Set up equations: gamma_def[i][j][k] - delta_f[i][j][k] == 0 for all i <= j, k
    equations = []
    for i in range(dim_g):
        for j in range(i, dim_g):
            for k in range(dim_g):
                eq = gamma_def[i][j][k] - delta_f[i][j][k]
                eq_sim = sp.simplify(eq)
                if eq_sim != 0:
                    equations.append(eq_sim)
                    
    print(f"Number of non-trivial scalar equations: {len(equations)}")
    
    # Solve linear equations for phi in terms of gb
    sol = sp.solve(equations, phi_symbols)
    print("Solve result type:", type(sol))
    if isinstance(sol, dict):
        print(f"Found solution for {len(sol)} parameters!")
        # Check if there are remaining unconstrained equations
        # Substitute solution back into equations
        remaining = [sp.simplify(eq.subs(sol)) for eq in equations]
        remaining_nonzero = [eq for eq in remaining if eq != 0]
        print(f"Remaining non-zero equations after substituting phi solution: {len(remaining_nonzero)}")
        if len(remaining_nonzero) > 0:
            print("Constraints on gb:")
            gb_constraints = sp.solve(remaining_nonzero, list(alg['gb_symbols'].values()))
            print("gb constraints:", gb_constraints)
        else:
            print(">>> EXACT MATCH: gamma_gb IS A COBOUNDARY FOR ALL gb VALUES! <<<")
    elif isinstance(sol, list):
        print(f"Solution list length: {len(sol)}")
        if len(sol) == 0:
            print("No solution for phi! Checking constraints on gb...")
            # Solve for both phi and gb
            all_syms = phi_symbols + list(alg['gb_symbols'].values())
            sol_all = sp.solve(equations, all_syms)
            print("sol_all:", sol_all)
            
    return alg, bracket_0, gamma_def, delta_f, phi_symbols, equations

test_triviality(1)
