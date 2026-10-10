import json
import sympy as sp
from collections import defaultdict

def analyze_triviality(n):
    with open(f"data/C_{n}_gamma.json") as f:
        gamma_data = json.load(f)
    with open(f"data/C_{n}_coboundary.json") as f:
        coboundary_data = json.load(f)
        
    with open(f"data/C_{n}_structure.json") as f:
        struct_data = json.load(f)
    parities = struct_data["parity"]
        
    gb_labels = gamma_data["inhomogeneous_deformation"]["gb_labels"]
    
    eqs_G = defaultdict(lambda: defaultdict(int))
    for entry in gamma_data["gamma_structure"]:
        X, Y, Z, gb, coeff = entry["X"], entry["Y"], entry["Z"], entry["gb"], int(entry["coeff"])
        # canonicalize X, Y order alphabetically
        if X > Y:
            sign = -1 if parities[X] * parities[Y] == 1 else 1
            X, Y = Y, X
            coeff = -sign * coeff
        eqs_G[(X, Y, Z)][gb] += coeff

    eqs_M = defaultdict(lambda: defaultdict(int))
    phi_labels = set()
    for entry in coboundary_data["coboundary_structure"]:
        X, Y, Z, f_in, f_out, coeff = entry["X"], entry["Y"], entry["Z"], entry["f_in"], entry["f_out"], int(entry["coeff"])
        if X > Y:
            sign = -1 if parities[X] * parities[Y] == 1 else 1
            X, Y = Y, X
            coeff = -sign * coeff
        phi = f"phi_{f_in}_{f_out}"
        phi_labels.add(phi)
        eqs_M[(X, Y, Z)][phi] += coeff

    all_triples = set(eqs_G.keys()).union(set(eqs_M.keys()))
    all_triples = sorted(list(all_triples))
    
    phi_list = list(phi_labels)
    matrix_rows = []
    rhs_rows = []
    
    gb_syms = sp.symbols(' '.join(gb_labels))
    if not isinstance(gb_syms, tuple): gb_syms = (gb_syms,)
    gb_dict = dict(zip(gb_labels, gb_syms))
    
    for t in all_triples:
        row = []
        for phi in phi_list:
            row.append(eqs_M[t][phi])
        matrix_rows.append(row)
        
        rhs = 0
        for gb in gb_labels:
            rhs += eqs_G[t][gb] * gb_dict[gb]
        rhs_rows.append(rhs)
        
    M = sp.Matrix(matrix_rows)
    # Find left nullspace of M
    nullspace_vectors = M.T.nullspace()
    
    conditions = []
    for v in nullspace_vectors:
        cond = 0
        for i in range(len(all_triples)):
            if v[i] != 0:
                cond += v[i] * rhs_rows[i]
        cond = sp.simplify(cond)
        if cond != 0:
            conditions.append(cond)
            
    print(f"--- Analysis for n={n} ---")
    if len(conditions) == 0:
        print("Trivial for ALL gb assignments! (No conditions)")
        return []
    else:
        cond_matrix = []
        for cond in conditions:
            row = []
            for gb in gb_syms:
                row.append(cond.coeff(gb))
            cond_matrix.append(row)
        
        CM = sp.Matrix(cond_matrix)
        CM_rref, _ = CM.rref()
        
        final_conds = []
        for i in range(CM_rref.shape[0]):
            is_zero = True
            expr = 0
            for j in range(len(gb_syms)):
                if CM_rref[i, j] != 0:
                    expr += CM_rref[i, j] * gb_syms[j]
                    is_zero = False
            if not is_zero:
                final_conds.append(expr)
                
        print("Conditions for triviality:")
        for c in final_conds:
            print(f"{c} == 0")
        return final_conds

if __name__ == "__main__":
    for n in [1, 2, 3]:
        analyze_triviality(n)
