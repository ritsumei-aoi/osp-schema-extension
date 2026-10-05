from solve_osp22 import equations, phi_vars, gb_list
import sympy as sp

print("Checking equations:")
const_eqs = []
for eq in equations:
    # check free symbols
    free = eq.free_symbols
    has_gb = any(g in free for g in gb_list)
    has_phi = any(p in free for p in phi_vars)
    if not has_gb and not has_phi:
        const_eqs.append(eq)
        print("Pure constant equation:", eq)

print(f"Total pure constant equations: {len(const_eqs)}")

# Let's inspect b_vec properly
M, b_vec = sp.linear_eq_to_matrix(equations, phi_vars)
print("b_vec free symbols:")
for i in range(b_vec.rows):
    if any(g in b_vec[i,0].free_symbols for g in gb_list):
        pass
    else:
        if b_vec[i,0] != 0:
            print(f"b_vec[{i}] has no gb: {b_vec[i,0]}")
