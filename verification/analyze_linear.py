"""
Detailed linear algebra analysis of M * phi = b(gb).
"""
import sympy as sp
from collections import defaultdict
from verification.cn1_algebra import create_algebra, get_generators, superbracket
from verification.test_jacobi import decompose_into_basis

def analyze_linear_system(n=1):
    gb, reduce_word = create_algebra(n)
    gens, parities = get_generators(n)
    gen_names = list(gens.keys())
    dim = len(gen_names)
    
    # Structure constants and gamma
    c0 = defaultdict(lambda: defaultdict(lambda: sp.Integer(0)))
    gamma = defaultdict(lambda: defaultdict(lambda: sp.Integer(0)))
    
    for g1 in gen_names:
        for g2 in gen_names:
            br = superbracket(g1, g2, gens, parities, reduce_word)
            t0 = {k: v[0] for k, v in br.items() if v[0] != 0}
            tk = {k: v[1] for k, v in br.items() if v[1] != 0}
            dec0, _ = decompose_into_basis(t0, gens, n)
            deck, _ = decompose_into_basis(tk, gens, n)
            for k_gen, val in dec0.items():
                c0[(g1, g2)][k_gen] = val
            for k_gen, val in deck.items():
                gamma[(g1, g2)][k_gen] = val

    even_gens = [g for g in gen_names if parities[g] == 0]
    odd_gens = [g for g in gen_names if parities[g] == 1]
    
    phi_vars = []
    phi_map = {}
    idx = 0
    for o in odd_gens:
        for e in even_gens:
            phi_map[(o, e)] = idx
            phi_vars.append(f"phi_{o}_{e}")
            idx += 1
            phi_map[(e, o)] = idx
            phi_vars.append(f"phi_{e}_{o}")
            idx += 1
            
    num_phi = len(phi_vars)
    gb_list = list(gb.values())
    
    # We build rows of equations:
    # (delta f)(g1, g2)_r = gamma(g1, g2)_r
    # Left hand side is sum_k M_{row, k} phi_k
    # Right hand side is gamma(g1, g2)_r
    
    rows = []
    rhs_list = []
    eq_labels = []
    
    for i, g1 in enumerate(gen_names):
        p1 = parities[g1]
        for j in range(i, dim):
            g2 = gen_names[j]
            p2 = parities[g2]
            
            # Compute delta f(g1, g2)
            # Row vector for each target r
            delta_f_coeffs = defaultdict(lambda: [sp.Integer(0)] * num_phi)
            
            # Term 1: (-1)^p1 [g1, f(g2)]
            s1 = (-1)**p1
            target_par_g2 = 1 - p2
            for k in gen_names:
                if parities[k] == target_par_g2:
                    p_idx = phi_map[(k, g2)]
                    for r, c_val in c0[(g1, k)].items():
                        delta_f_coeffs[r][p_idx] += s1 * c_val
                        
            # Term 2: - (-1)^{(p1 + 1) p2} [g2, f(g1)]
            s2 = - (-1)**((p1 + 1) * p2)
            target_par_g1 = 1 - p1
            for k in gen_names:
                if parities[k] == target_par_g1:
                    p_idx = phi_map[(k, g1)]
                    for r, c_val in c0[(g2, k)].items():
                        delta_f_coeffs[r][p_idx] += s2 * c_val
                        
            # Term 3: - f([g1, g2])
            for m, c_val in c0[(g1, g2)].items():
                target_par_m = 1 - parities[m]
                for r in gen_names:
                    if parities[r] == target_par_m:
                        p_idx = phi_map[(r, m)]
                        delta_f_coeffs[r][p_idx] -= c_val
                        
            for r in gen_names:
                row_vec = delta_f_coeffs[r]
                val_rhs = gamma[(g1, g2)][r]
                # If both row_vec is all zeros and val_rhs is 0, skip
                if any(c != 0 for c in row_vec) or val_rhs != 0:
                    rows.append(row_vec)
                    rhs_list.append(val_rhs)
                    eq_labels.append((g1, g2, r))
                    
    M = sp.Matrix(rows)
    b = sp.Matrix(rhs_list)
    
    print(f"Matrix M shape: {M.shape}")
    print(f"Rank of M: {M.rank()}")
    
    # We want to find conditions on gb such that M * phi = b has a solution.
    # By Rouché-Capelli theorem, a solution exists iff rank(M) == rank([M | b]).
    # Equivalently, for any vector v in left nullspace of M (v^T M = 0), we must have v^T b = 0.
    
    nullspace_left = M.T.nullspace()
    print(f"Dimension of left nullspace of M: {len(nullspace_left)}")
    
    gb_constraints = []
    for v in nullspace_left:
        # v is a column vector of length len(rows)
        # constraint is v.dot(b) == 0
        val = sp.simplify(sum(v[i] * rhs_list[i] for i in range(len(rows))))
        if val != 0:
            gb_constraints.append(val)
            
    print(f"Number of non-zero constraints on gb: {len(gb_constraints)}")
    
    # Eliminate redundant constraints
    independent_constraints = []
    if gb_constraints:
        C_matrix = sp.Matrix([[sp.diff(c, g) for g in gb_list] for c in gb_constraints])
        print(f"Constraint matrix shape on gb: {C_matrix.shape}")
        print(f"Rank of constraint matrix on gb: {C_matrix.rank()}")
        print(f"Total gb variables: {len(gb_list)}")
        
        # Solve the constraints for gb
        gb_sol = sp.solve(gb_constraints, gb_list)
        print("Explicit solution for gb constraints:")
        print(gb_sol)
        
    return M, b, gb_constraints, gb_list

if __name__ == '__main__':
    analyze_linear_system(1)
