import json
import sympy as sp
from collections import defaultdict
import sys

def main(n):
    with open(f"data/C_{n}_gamma.json") as f:
        gamma_data = json.load(f)
    with open(f"data/C_{n}_coboundary.json") as f:
        coboundary_data = json.load(f)
        
    gb_labels = gamma_data["inhomogeneous_deformation"]["gb_labels"]
    
    eqs_G = defaultdict(lambda: defaultdict(int))
    for entry in gamma_data["gamma_structure"]:
        X, Y, Z, gb, coeff = entry["X"], entry["Y"], entry["Z"], entry["gb"], int(entry["coeff"])
        eqs_G[(X, Y, Z)][gb] += coeff

    eqs_M = defaultdict(lambda: defaultdict(int))
    phi_labels = set()
    for entry in coboundary_data["coboundary_structure"]:
        X, Y, Z, f_in, f_out, coeff = entry["X"], entry["Y"], entry["Z"], entry["f_in"], entry["f_out"], int(entry["coeff"])
        phi = f"phi_{f_in}_{f_out}"
        phi_labels.add(phi)
        eqs_M[(X, Y, Z)][phi] += coeff

    all_triples = set(eqs_G.keys()).union(set(eqs_M.keys()))
    
    gb_syms = sp.symbols(' '.join(gb_labels))
    if not isinstance(gb_syms, tuple): gb_syms = (gb_syms,)
    gb_dict = dict(zip(gb_labels, gb_syms))
    
    phi_list = list(phi_labels)
    matrix_rows = []
    rhs_rows = []
    
    for t in sorted(all_triples):
        row = []
        for phi in phi_list:
            row.append(eqs_M[t][phi])
        matrix_rows.append(row)
        
        rhs = 0
        for gb in gb_labels:
            rhs += eqs_G[t][gb] * gb_dict[gb]
        rhs_rows.append(rhs)
        
    M = sp.Matrix(matrix_rows)
    RHS = sp.Matrix(rhs_rows)
    augmented = M.row_join(RHS)
    print("Computing rref...")
    reduced_augmented, pivots = augmented.rref()
    
    print("Checking zero rows...")
    for i in range(reduced_augmented.shape[0]):
        is_zero = True
        for j in range(len(phi_list)):
            if reduced_augmented[i, j] != 0:
                is_zero = False
                break
        if is_zero:
            val = reduced_augmented[i, -1]
            if val != 0:
                print("Found non-zero RHS for zero row:")
                print(repr(val))

if __name__ == "__main__":
    main(1)
