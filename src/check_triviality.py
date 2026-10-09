import json
import sympy
from collections import defaultdict

def check_triviality(n):
    print(f"\n--- Checking Triviality for C({n+1}) ---")
    
    with open(f"data/C_{n}_gamma.json") as f:
        schema2 = json.load(f)
        
    with open(f"data/C_{n}_coboundary.json") as f:
        schema4 = json.load(f)
        
    gb_params = schema2["inhomogeneous_deformation"]["gb_matrix"]["parameters"]
    phi_params = schema4["f_parameters"]
    
    # Create sympy symbols
    gb_syms = {p: sympy.Symbol(p) for p in gb_params}
    phi_syms = {p: sympy.Symbol(p) for p in phi_params}
    
    # build equations: for each (X, Y, Z), gamma(X, Y)|_Z = delta_f(X, Y)|_Z
    # We will build LHS = gamma, RHS = delta_f
    
    eqs_dict = defaultdict(lambda: sympy.S.Zero)
    
    for entry in schema2["inhomogeneous_deformation"]["gamma_structure"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        param = entry["gb_param"]
        c = float(entry["coeff"])
        eqs_dict[(x, y, z)] += c * gb_syms[param]
        
    for entry in schema4["coboundary_evaluated"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        param = entry["phi_param"]
        c = float(entry["coeff"])
        eqs_dict[(x, y, z)] -= c * phi_syms[param] # RHS moved to LHS, so it's gamma - delta_f = 0
        
    # The equations are linear in phi and gb.
    # We want to solve for phi in terms of gb.
    # If a solution exists for ALL gb, then the deformation is always trivial.
    # If a solution exists only when some linear combination of gb is 0, those are the conditions!
    
    equations = list(eqs_dict.values())
    
    # Extract the matrix of coefficients for phi variables
    # M * Phi = N * gb
    # We can just ask sympy to solve the linear system for phi_syms.
    # If the system is underdetermined, it will give parametric solutions.
    # If it is overdetermined and inconsistent, it will give conditions.
    
    # We will compute the row echelon form of the augmented matrix.
    # Actually sympy.linsolve is easier, but to extract the conditions on gb:
    # Let's write the system as A * phi + B * gb = 0
    phi_vars = list(phi_syms.values())
    gb_vars = list(gb_syms.values())
    
    M, _ = sympy.linear_eq_to_matrix(equations, phi_vars + gb_vars)
    
    # RREF
    M_rref, pivots = M.rref()
    
    conditions = []
    
    num_phi = len(phi_vars)
    # Check rows where all phi coefficients are 0
    for row in range(M_rref.shape[0]):
        # if the row has 0 for all phi_vars, but non-zero for some gb_vars,
        # then this row is a condition on gb.
        is_phi_zero = True
        for col in range(num_phi):
            if M_rref[row, col] != 0:
                is_phi_zero = False
                break
                
        if is_phi_zero:
            cond = sympy.S.Zero
            for i, gb in enumerate(gb_vars):
                cond += M_rref[row, num_phi + i] * gb
            if cond != 0:
                conditions.append(cond)
                
    if not conditions:
        print("Deformation is ALWAYS trivial (no conditions on gb).")
    else:
        print(f"Deformation is trivial ONLY IF the following {len(conditions)} conditions hold:")
        # We can simplify the conditions
        # Convert to a set of independent conditions
        cond_matrix, _ = sympy.linear_eq_to_matrix(conditions, gb_vars)
        cond_rref, _ = cond_matrix.rref()
        
        indep_conds = []
        for row in range(cond_rref.shape[0]):
            expr = sum(cond_rref[row, col] * gb_vars[col] for col in range(len(gb_vars)))
            if expr != 0:
                indep_conds.append(expr)
                
        for expr in indep_conds:
            print(f"  {expr} == 0")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        check_triviality(n)
