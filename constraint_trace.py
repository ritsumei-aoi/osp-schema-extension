import sympy as sp
from nullspace_n1 import A_mat, B_mat, G_vars, basis, basis_p, brackets_0, gamma, phi_map, equations

nullspace = A_mat.T.nullspace()
for vec in nullspace:
    cond = vec.T * B_mat
    expr = 0
    for i, g in enumerate(G_vars):
        expr += cond[0, i] * g
    if expr == 4 * G_vars[0] or expr == -4 * G_vars[0] or sp.simplify(expr) == 4*G_vars[0] or sp.simplify(expr) == -4*G_vars[0]:
        print("Found vector giving 4 * G_0_2")
        # Which equations are involved?
        # vec is a vector of length len(equations)
        for i, val in enumerate(vec):
            if val != 0:
                eq = equations[i]
                print(f"Eq {i} (weight {val}): {eq}")
        print("---")
