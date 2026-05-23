import sympy as sp
from nullspace_n1 import A_mat, B_mat, G_vars, basis, basis_p, brackets_0, gamma, phi_map

equations_info = []
for i in range(len(basis)):
    for j in range(len(basis)):
        term1 = [0] * len(basis)
        for m in range(len(basis)):
            if basis_p[m] == 1 - basis_p[j]:
                for k in range(len(basis)): term1[k] += phi_map[(m, j)] * brackets_0[(i, m)][k]
        term2 = [0] * len(basis)
        for m in range(len(basis)):
            if basis_p[m] == 1 - basis_p[i]:
                for k in range(len(basis)): term2[k] += phi_map[(m, i)] * brackets_0[(j, m)][k]
        term3 = [0] * len(basis)
        for m in range(len(basis)):
            c_m = brackets_0[(i, j)][m]
            if c_m != 0:
                for k in range(len(basis)):
                    if basis_p[k] == 1 - basis_p[m]:
                        term3[k] += c_m * phi_map[(k, m)]
        sign1 = (-1)**basis_p[i]
        sign2 = (-1)**((basis_p[i] + 1) * basis_p[j])
        
        for k in range(len(basis)):
            delta_f_ijk = sign1 * term1[k] - sign2 * term2[k] - term3[k]
            gamma_ijk = gamma[(i, j)][k]
            eq = delta_f_ijk - gamma_ijk
            if eq != 0: equations_info.append((eq, i, j, k))

# Eq 2, 12, 43
for idx in [2, 12, 43]:
    eq, i, j, k = equations_info[idx]
    print(f"Eq {idx}: i={i}, j={j}, k={k}")
    print(f"  X_i = {basis[i]}")
    print(f"  X_j = {basis[j]}")
    print(f"  X_k = {basis[k]}")
    print(f"  equation: {eq} = 0")
