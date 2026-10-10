import json
import os
import sys
import sympy

def check_triviality(n):
    gamma_path = f'data/C_{n}_gamma.json'
    coboundary_path = f'data/C_{n}_coboundary.json'
    
    with open(gamma_path) as f:
        gamma_data = json.load(f)['inhomogeneous_deformation']['gamma_structure_constants']
        
    with open(coboundary_path) as f:
        coboundary_data = json.load(f)['coboundary_structure']['delta_f_constants']
        
    # Variables: phi_... and gb_...
    phi_vars = set()
    for xy, out_expr in coboundary_data.items():
        for z, terms in out_expr.items():
            for phi_name in terms:
                phi_vars.add(phi_name)
                
    gb_vars = set()
    for xy, out_expr in gamma_data.items():
        for z, terms in out_expr.items():
            for gb_name in terms:
                gb_vars.add(gb_name)
                
    phi_syms = {p: sympy.Symbol(p) for p in phi_vars}
    gb_syms = {gb: sympy.Symbol(gb) for gb in gb_vars}
    
    equations = []
    
    # We want gamma(X, Y) = delta_f(X, Y)
    # i.e. gamma(X, Y) - delta_f(X, Y) = 0
    
    # Collect all pairs X, Y
    all_pairs = set(gamma_data.keys()).union(set(coboundary_data.keys()))
    
    for xy in all_pairs:
        gamma_expr = gamma_data.get(xy, {})
        delta_f_expr = coboundary_data.get(xy, {})
        
        all_z = set(gamma_expr.keys()).union(set(delta_f_expr.keys()))
        for z in all_z:
            gamma_terms = gamma_expr.get(z, {})
            delta_f_terms = delta_f_expr.get(z, {})
            
            eq = 0
            for gb_name, coef in gamma_terms.items():
                eq += coef * gb_syms[gb_name]
                
            for phi_name, coef in delta_f_terms.items():
                eq -= coef * phi_syms[phi_name]
                
            if eq != 0:
                equations.append(eq)
                
    # We want to know: under what conditions on gb_syms does there exist a solution for phi_syms?
    # This is equivalent to checking if the system of equations in phi_syms (with gb_syms as constants) is consistent.
    # We can form a matrix A for phi_syms, and a vector b for gb_syms. A * phi = b.
    # The condition is that b is in the column space of A.
    
    phi_list = list(phi_syms.values())
    gb_list = list(gb_syms.values())
    
    # We can just use sympy.linsolve
    # Wait, we want to eliminate phi_vars and see what equations remain for gb_vars.
    # We can use Gaussian elimination.
    
    # Let's extract the matrix A and b
    # eq: sum A_{i, j} phi_j - sum B_{i, k} gb_k = 0
    # A * phi = B * gb
    
    import numpy as np
    
    A_rows = []
    b_rows = []
    
    for eq in equations:
        a_row = []
        for phi in phi_list:
            a_row.append(float(eq.coeff(phi)))
        b_row = []
        for gb in gb_list:
            # Note: eq is A*phi - B*gb = 0 => A*phi = B*gb. So B_k = -coeff(gb_k)
            b_row.append(float(-eq.coeff(gb)))
            
        A_rows.append(a_row)
        b_rows.append(b_row)
        
    A = sympy.Matrix(A_rows)
    B = sympy.Matrix(b_rows)
    
    # We want to find conditions on B*gb such that it's in the column space of A.
    # We can compute the left null space of A.
    # For every vector v in left_nullspace(A), we must have v * B * gb = 0.
    
    left_null = A.T.nullspace()
    
    conditions = []
    for v in left_null:
        cond_vec = v.T * B
        # cond_vec is 1 x len(gb)
        cond_expr = 0
        for k, gb in enumerate(gb_list):
            cond_expr += cond_vec[0, k] * gb
        if cond_expr != 0:
            conditions.append(cond_expr)
            
    print(f"--- Analysis for C({n+1}) ---")
    if not conditions:
        print("Deformation is ALWAYS trivial (no conditions on gb parameters).")
    else:
        print("Deformation is trivial IF AND ONLY IF the following conditions hold:")
        for cond in conditions:
            # simplify expression
            print(f"  {sympy.simplify(cond)} == 0")
            
    return conditions

if __name__ == '__main__':
    for n in [1, 2]:
        check_triviality(n)
