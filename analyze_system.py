import sympy as sp
import numpy as np

# Let's inspect the linear system M * phi = rhs(gb)
from solve_osp22 import equations, phi_vars, gb_list, dim, parities, C, gamma

# Each equation is: sum_v A_{eq, v} phi_v = b_{eq}(gb)
# Let's separate into A * phi = B * gb
all_vars = phi_vars + gb_list
print(f"Total equations: {len(equations)}")

# Convert to matrix form
M, b_vec = sp.linear_eq_to_matrix(equations, phi_vars)
print(f"Matrix M shape: {M.shape}")
print(f"Rank of M: {M.rank()}")

# Let's check consistency: solve for phi and gb together or compute kernel/cokernel
aug = M.row_join(-b_vec) # M * phi + b_vec = 0 => M * phi = -b_vec
rref_aug, pivots = aug.rref()
print(f"Pivots of augmented matrix: {len(pivots)}")

# Look at rows where M is zero but RHS is non-zero
constraints = []
for r in range(aug.rows):
    if all(rref_aug[r, c] == 0 for c in range(M.cols)):
        rhs = rref_aug[r, M.cols]
        if rhs != 0:
            constraints.append(rhs)

print(f"Number of constraint equations on gb: {len(constraints)}")
print("Constraints on gb:")
for c in constraints:
    print(" ", sp.simplify(c), "= 0")

gb_sol = sp.solve(constraints, gb_list)
print("\nSolution to constraints on gb:")
print(gb_sol)
