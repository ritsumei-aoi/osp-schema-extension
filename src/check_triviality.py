import json
import sympy as sp

def check_triviality(n):
    with open(f"data/C_{n}_gamma.json", "r") as f:
        gamma_json = json.load(f)
        gamma_data = gamma_json["inhomogeneous_deformation"]["constants"] \
            if "constants" in gamma_json["inhomogeneous_deformation"] \
            else gamma_json["inhomogeneous_deformation"]["gamma_constants"]
            
    with open(f"data/C_{n}_coboundary.json", "r") as f:
        coboundary_data = json.load(f)["coboundary_structure"]["constants"]
        
    equations = []
    variables = set()
    gb_vars = set()
    
    # Organize data by (X, Y, Z)
    gamma_dict = {}
    for entry in gamma_data:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        gamma_dict[(X, Y, Z)] = entry["gamma_terms"]
        for term in entry["gamma_terms"]:
            gb_vars.add(term["gb"])
            
    coboundary_dict = {}
    for entry in coboundary_data:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        coboundary_dict[(X, Y, Z)] = entry["coboundary_terms"]
        for term in entry["coboundary_terms"]:
            variables.add(term["phi"])
            
    # Combine keys
    all_keys = set(gamma_dict.keys()).union(set(coboundary_dict.keys()))
    
    gb_syms = {gb: sp.Symbol(gb) for gb in gb_vars}
    phi_syms = {phi: sp.Symbol(phi) for phi in variables}
    
    eqs = []
    
    for (X, Y, Z) in all_keys:
        gamma_expr = 0
        if (X, Y, Z) in gamma_dict:
            for term in gamma_dict[(X, Y, Z)]:
                gamma_expr += float(term["coeff"]) * gb_syms[term["gb"]]
                
        coboundary_expr = 0
        if (X, Y, Z) in coboundary_dict:
            for term in coboundary_dict[(X, Y, Z)]:
                coboundary_expr += float(term["coeff"]) * phi_syms[term["phi"]]
                
        if gamma_expr != 0 or coboundary_expr != 0:
            eqs.append(coboundary_expr - gamma_expr)
            
    # Try to solve for phi_syms in terms of gb_syms
    phi_list = list(phi_syms.values())
    solution = sp.solve(eqs, phi_list, dict=True)
    
    print(f"\n--- Triviality Check for C({n+1}) ---")
    if not solution:
        print("No solution exists for arbitrary gb. The deformation is generally non-trivial.")
        # We want to eliminate phi from the system. 
        # Using sympy to find the relations among gb
        # We can form a matrix and find its left null space.
        phi_vars = list(phi_syms.values())
        M, b = sp.linear_eq_to_matrix(eqs, phi_vars)
        # M * phi = -b => M * phi + b = 0
        # The equations are M * phi + b = 0, where b is a vector of linear combos of gb
        # Left null space of M:
        left_null = M.T.nullspace()
        
        print(f"Number of constraints on gb: {len(left_null)}")
        for vec in left_null:
            # vec is a column vector
            # vec.T * (M * phi + b) = 0 => vec.T * b = 0
            constraint = (vec.T * b)[0]
            if constraint != 0:
                print(f"Constraint: {constraint} = 0")
    else:
        print("Solution exists! The deformation is always trivial (a coboundary).")
        print("A possible parameterization for f:")
        for k, v in solution[0].items():
            if v != 0:
                print(f"  {k} = {v}")

if __name__ == "__main__":
    for n in [1, 2, 3]:
        check_triviality(n)
