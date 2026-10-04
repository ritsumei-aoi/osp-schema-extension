import json
import sympy as sp

def find_conditions(n):
    with open(f"data/C_{n}_gamma.json") as f:
        gamma_data = json.load(f)
    with open(f"data/C_{n}_coboundary.json") as f:
        coboundary_data = json.load(f)
        
    gb_symbols = []
    for sigma in ['p', 'm']:
        for j in range(1, n+1):
            for s in ['p', 'm']:
                gb_symbols.append(sp.Symbol(f"gb_{sigma}_{j}_{s}"))
    
    phi_symbols = set()
    for entry in coboundary_data["coboundary_structure"]:
        for term in entry["coboundary_expansion"]:
            phi_symbols.add(sp.Symbol(term["phi_param"]))
    phi_list = list(phi_symbols)
    
    eq_keys = set()
    for entry in gamma_data["gamma_structure"]:
        for term in entry["gamma_expansion"]:
            eq_keys.add((entry["X"], entry["Y"], term["Z"]))
    for entry in coboundary_data["coboundary_structure"]:
        for term in entry["coboundary_expansion"]:
            eq_keys.add((entry["X"], entry["Y"], term["Z"]))
            
    eq_list = list(eq_keys)
    M = sp.zeros(len(eq_list), len(phi_list))
    A = sp.zeros(len(eq_list), len(gb_symbols))
    
    # Fill A (gamma part, RHS)
    for entry in gamma_data["gamma_structure"]:
        X, Y = entry["X"], entry["Y"]
        for term in entry["gamma_expansion"]:
            Z, gb, c = term["Z"], term["gb_param"], sp.Rational(term["coeff"])
            row = eq_list.index((X, Y, Z))
            col = gb_symbols.index(sp.Symbol(gb))
            A[row, col] += c
            
    # Fill M (coboundary part, LHS)
    for entry in coboundary_data["coboundary_structure"]:
        X, Y = entry["X"], entry["Y"]
        for term in entry["coboundary_expansion"]:
            Z, phi, c = term["Z"], term["phi_param"], sp.Rational(term["coeff"])
            row = eq_list.index((X, Y, Z))
            col = phi_list.index(sp.Symbol(phi))
            M[row, col] += c
            
    print(f"n={n}: Matrix M is {M.shape[0]}x{M.shape[1]}, Matrix A is {A.shape[0]}x{A.shape[1]}")
    
    # We want conditions on gb:  M * phi = A * gb
    # Calculate row space of M nullspace. Actually, we can augment M with A and do rref.
    Aug = M.row_join(A)
    R, pivots = Aug.rref()
    
    conditions = []
    # Any row in R that has zeros in the first len(phi_list) columns but non-zeros in the rest
    for i in range(R.shape[0]):
        # check if all phi coeffs are 0
        if all(R[i, j] == 0 for j in range(len(phi_list))):
            # check gb coeffs
            expr = sum(R[i, len(phi_list) + k] * gb_symbols[k] for k in range(len(gb_symbols)))
            if expr != 0:
                conditions.append(expr)
                
    # simplify conditions
    if not conditions:
        print(f"n={n}: Trivial for ALL gb parameters.")
    else:
        # Find basis for conditions
        print(f"n={n}: Conditions for triviality:")
        cond_matrix = sp.zeros(len(conditions), len(gb_symbols))
        for i, expr in enumerate(conditions):
            for j, sym in enumerate(gb_symbols):
                cond_matrix[i, j] = expr.coeff(sym)
        CR, _ = cond_matrix.rref()
        for i in range(CR.shape[0]):
            expr = sum(CR[i, j] * gb_symbols[j] for j in range(len(gb_symbols)))
            if expr != 0:
                print(f"  {expr} == 0")

if __name__ == "__main__":
    for n in [1, 2]:
        find_conditions(n)
