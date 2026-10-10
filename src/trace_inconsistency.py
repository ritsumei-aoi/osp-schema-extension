import json
from collections import defaultdict
import sympy as sp

with open("data/C_1_gamma.json") as f:
    gamma_data = json.load(f)
with open("data/C_1_coboundary.json") as f:
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
all_triples = sorted(list(all_triples))

phi_list = list(phi_labels)
matrix_rows = []
rhs_rows = []

for t in all_triples:
    row = []
    for phi in phi_list:
        row.append(eqs_M[t][phi])
    matrix_rows.append(row)
    
    rhs = 0
    for gb in gb_labels:
        # only keep gb_p_1_p
        if gb == 'gb_p_1_p':
            rhs += eqs_G[t][gb]
    rhs_rows.append(rhs)
    
M = sp.Matrix(matrix_rows)
nullspace = M.T.nullspace()

for v in nullspace:
    cond = 0
    for i in range(len(all_triples)):
        if v[i] != 0:
            cond += v[i] * rhs_rows[i]
    if cond != 0:
        print("Found inconsistent condition!")
        print(f"Condition value: {cond}")
        print("Involved equations:")
        for i in range(len(all_triples)):
            if v[i] != 0:
                print(f"{v[i]} * eq for {all_triples[i]}")
                print(f"   gamma = {rhs_rows[i]}, coboundary = {[ (phi_list[j], M[i, j]) for j in range(len(phi_list)) if M[i,j] != 0 ]}")
        break
