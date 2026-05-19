import json
import sympy
import os
from collections import defaultdict

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def check_triviality(n):
    l2_path = f"data/C_{n}_gamma.json"
    l4_path = f"data/C_{n}_coboundary.json"
    
    if not os.path.exists(l2_path) or not os.path.exists(l4_path):
        print(f"Files for n={n} missing.")
        return
        
    s2 = load_json(l2_path)
    s4 = load_json(l4_path)
    
    # Extract gb variables
    gb_matrix = s2["inhomogeneous_deformation"]["gb_matrix"]
    gb_vars = set()
    for gb_list in gb_matrix.values():
        for gb_name in gb_list:
            gb_vars.add(sympy.Symbol(gb_name))
            
    gb_vars = sorted(list(gb_vars), key=lambda x: str(x))
            
    # Extract gamma_matrix: (X, Y, Z) -> expr(gb)
    gamma_eval = defaultdict(lambda: 0)
    for entry in s2["inhomogeneous_deformation"]["gamma_matrix"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        local_dict = {str(s): s for s in gb_vars}
        expr = sympy.sympify(entry["gamma_coeff"], locals=local_dict)
        gamma_eval[(X, Y, Z)] += expr

    # Extract coboundary_matrix: (X, Y, Z) -> expr(phi)
    gamma_cob = defaultdict(lambda: 0)
    phi_vars = set()
    for entry in s4["coboundary_matrix"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        expr = sympy.sympify(entry["coboundary_coeff"])
        phi_vars.update(expr.free_symbols)
        gamma_cob[(X, Y, Z)] += expr
        
    phi_vars = sorted(list(phi_vars), key=lambda x: str(x))
        
    all_keys = sorted(list(set(gamma_eval.keys()).union(set(gamma_cob.keys()))))
    
    # We want to solve A * phi = b(gb)
    # A is numeric. b is a vector of linear combinations of gb.
    num_eqs = len(all_keys)
    num_phi = len(phi_vars)
    
    A = sympy.zeros(num_eqs, num_phi)
    b = sympy.zeros(num_eqs, 1)
    
    key_to_row = {}
    
    for i, k in enumerate(all_keys):
        key_to_row[k] = i
        cob_expr = gamma_cob[k]
        eval_expr = gamma_eval[k]
        
        # Populate A
        if cob_expr != 0:
            cob_poly = cob_expr.as_coefficients_dict()
            for var, coeff in cob_poly.items():
                if var in phi_vars:
                    A[i, phi_vars.index(var)] = coeff
                    
        # Populate b
        b[i, 0] = eval_expr
        
    print(f"--- Analyzing C({n+1}) ---")
    print(f"Matrix A dimensions: {A.rows} x {A.cols}")
    
    # Calculate Left Nullspace of A
    # V * A = 0 => V^T is in nullspace of A^T
    print("Computing left nullspace of A...")
    left_nullspace = A.transpose().nullspace()
    
    print(f"Left nullspace dimension: {len(left_nullspace)}")
    
    # For A * phi = b to have a solution, we must have V * b = 0 for all V in left_nullspace.
    conditions = []
    for V in left_nullspace:
        # V is a column vector of size (num_eqs x 1)
        # We need V^T * b = 0
        constraint = (V.transpose() * b)[0, 0]
        constraint = sympy.simplify(constraint)
        if constraint != 0:
            conditions.append(constraint)
            
    if not conditions:
        print("Deformation is ALWAYS TRIVIAL (no constraints on gb).")
    else:
        print(f"Deformation is NON-TRIVIAL in general. Found {len(conditions)} constraint equations on gb.")
        
        # Let's reduce the conditions to find independent ones
        cond_matrix = sympy.zeros(len(conditions), len(gb_vars))
        for i, cond in enumerate(conditions):
            poly = cond.as_coefficients_dict()
            for var, coeff in poly.items():
                if var in gb_vars:
                    cond_matrix[i, gb_vars.index(var)] = coeff
                    
        reduced_cond, _ = cond_matrix.rref()
        
        independent_conds = []
        for i in range(reduced_cond.rows):
            if not all(reduced_cond[i, j] == 0 for j in range(reduced_cond.cols)):
                expr = 0
                for j in range(reduced_cond.cols):
                    expr += reduced_cond[i, j] * gb_vars[j]
                independent_conds.append(expr)
                
        print(f"Reduced to {len(independent_conds)} independent constraints:")
        for c in independent_conds:
            print(f"  {c} == 0")
            
        # Check Option A: all gb = 1
        optA_subs = {v: 1 for v in gb_vars}
        optA_fails = False
        for c in independent_conds:
            if c.subs(optA_subs) != 0:
                optA_fails = True
                break
        print(f"Option A (all gb=+1) trivial? {'NO' if optA_fails else 'YES'}")

        # Let's find specific non-trivial discrepancy
        print("Example of discrepancy causing non-triviality:")
        # Look at the first condition's corresponding left nullspace vector
        for V in left_nullspace:
            constraint = sympy.simplify((V.transpose() * b)[0, 0])
            if constraint != 0:
                print(f"  Constraint: {constraint} == 0")
                print("  This comes from the linear combination of the following brackets:")
                for i in range(V.rows):
                    if V[i, 0] != 0:
                        k = all_keys[i]
                        print(f"    {V[i, 0]} * bracket({k[0]}, {k[1]})|_({k[2]})  [Eval: {gamma_eval[k]}]")
                break
                
    print()

if __name__ == "__main__":
    for n in [1, 2, 3]:
        check_triviality(n)
