import sympy as sp
from solve_osp22 import equations, phi_vars, gb_list

M, b_vec = sp.linear_eq_to_matrix(equations, phi_vars)

print(f"M shape: {M.shape}, Rank: {M.rank()}")
# Left nullspace of M: vectors v such that v^T * M = 0 <=> M^T * v = 0
left_null = M.T.nullspace()
print(f"Dimension of left nullspace (cokernel): {len(left_null)}")

constraints = []
for v in left_null:
    c = sum(v[i] * b_vec[i, 0] for i in range(len(v)))
    c_simp = sp.simplify(c)
    if c_simp != 0:
        constraints.append(c_simp)

print(f"Number of non-trivial constraints on gb: {len(constraints)}")
print("Constraints on gb:")
for c in set(constraints):
    print(" ", c, "= 0")

gb_sol = sp.solve(constraints, gb_list)
print("\nSolution to constraints on gb:")
print(gb_sol)
