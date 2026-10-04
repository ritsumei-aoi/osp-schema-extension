"""
Find sparse null vectors to give simple algebraic derivations of gb = 0.
"""
import sympy as sp
from collections import defaultdict
from verification.cn1_algebra import create_algebra, get_generators, superbracket
from verification.test_jacobi import decompose_into_basis

def find_sparse_obstructions(n=1):
    gb, reduce_word = create_algebra(n)
    gens, parities = get_generators(n)
    gen_names = list(gens.keys())
    dim = len(gen_names)
    
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
    
    rows = []
    rhs_list = []
    eq_labels = []
    
    for i, g1 in enumerate(gen_names):
        p1 = parities[g1]
        for j in range(i, dim):
            g2 = gen_names[j]
            p2 = parities[g2]
            
            delta_f_coeffs = defaultdict(lambda: [sp.Integer(0)] * num_phi)
            
            s1 = (-1)**p1
            target_par_g2 = 1 - p2
            for k in gen_names:
                if parities[k] == target_par_g2:
                    p_idx = phi_map[(k, g2)]
                    for r, c_val in c0[(g1, k)].items():
                        delta_f_coeffs[r][p_idx] += s1 * c_val
                        
            s2 = - (-1)**((p1 + 1) * p2)
            target_par_g1 = 1 - p1
            for k in gen_names:
                if parities[k] == target_par_g1:
                    p_idx = phi_map[(k, g1)]
                    for r, c_val in c0[(g2, k)].items():
                        delta_f_coeffs[r][p_idx] += s2 * c_val
                        
            for m, c_val in c0[(g1, g2)].items():
                target_par_m = 1 - parities[m]
                for r in gen_names:
                    if parities[r] == target_par_m:
                        p_idx = phi_map[(r, m)]
                        delta_f_coeffs[r][p_idx] -= c_val
                        
            for r in gen_names:
                row_vec = delta_f_coeffs[r]
                val_rhs = gamma[(g1, g2)][r]
                if any(c != 0 for c in row_vec) or val_rhs != 0:
                    rows.append(row_vec)
                    rhs_list.append(val_rhs)
                    eq_labels.append((g1, g2, r))
                    
    M = sp.Matrix(rows)
    
    # Let's search for equations that directly relate phi and gb
    # For example, let's find the RREF of [M | b]
    # We can write b in terms of gb_list
    b_sym = sp.Matrix(rhs_list)
    aug = M.row_join(b_sym)
    
    # RREF of aug with respect to phi_vars:
    # We can do rref on M first:
    rref_M, pivots = M.rref()
    
    # Look at non-pivot rows of the augmented matrix:
    # For row i not in pivots:
    # That gives a direct constraint!
    print("Finding simple relations from non-pivot rows...")
    # Let's express each row of M in terms of pivot rows
    # M = P * R where R is rref
    # Or just use the left nullspace
    left_null = M.T.nullspace()
    
    # Find combinations with minimum support (fewest non-zero entries)
    # Let's inspect the first few left null vectors:
    for idx_n, v in enumerate(left_null):
        val = sp.simplify(sum(v[i] * rhs_list[i] for i in range(len(rows))))
        if val != 0:
            supp = [i for i, c in enumerate(v) if c != 0]
            if len(supp) <= 6:
                print(f"\nNull vector {idx_n} with support size {len(supp)}:")
                print(f"  Constraint: {val} = 0")
                for s in supp:
                    g1, g2, r = eq_labels[s]
                    print(f"    Eq ({g1}, {g2} -> {r}): coeff = {v[s]}, rhs = {rhs_list[s]}")

if __name__ == '__main__':
    find_sparse_obstructions(1)
