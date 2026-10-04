"""
Find the single-bracket obstructions for all gb parameters!
"""
import sympy as sp
from collections import defaultdict
from verification.cn1_algebra import create_algebra, get_generators, superbracket
from verification.test_jacobi import decompose_into_basis

def find_single_bracket_obstructions(n=1):
    gb, reduce_word = create_algebra(n)
    gens, parities = get_generators(n)
    gen_names = list(gens.keys())
    
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
    
    # Compute c0
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

    print("Checking pairs (g1, g2) and target r where delta_f row is IDENTICALLY ZERO but gamma != 0:")
    
    found_params = set()
    for g1 in gen_names:
        p1 = parities[g1]
        for g2 in gen_names:
            p2 = parities[g2]
            
            delta_f_coeffs = defaultdict(lambda: [sp.Integer(0)] * num_phi)
            s1 = (-1)**p1
            for k in gen_names:
                if parities[k] == 1 - p2:
                    p_idx = phi_map[(k, g2)]
                    for r, c_val in c0[(g1, k)].items():
                        delta_f_coeffs[r][p_idx] += s1 * c_val
                        
            s2 = - (-1)**((p1 + 1) * p2)
            for k in gen_names:
                if parities[k] == 1 - p1:
                    p_idx = phi_map[(k, g1)]
                    for r, c_val in c0[(g2, k)].items():
                        delta_f_coeffs[r][p_idx] += s2 * c_val
                        
            for m, c_val in c0[(g1, g2)].items():
                for r in gen_names:
                    if parities[r] == 1 - parities[m]:
                        p_idx = phi_map[(r, m)]
                        delta_f_coeffs[r][p_idx] -= c_val
                        
            for r in gen_names:
                if all(c == 0 for c in delta_f_coeffs[r]):
                    val_rhs = gamma[(g1, g2)][r]
                    if val_rhs != 0:
                        print(f"PAIR ({g1}, {g2}) -> target {r}:")
                        print(f"  (delta f) = 0")
                        print(f"  gamma = {val_rhs}")
                        for sym in val_rhs.free_symbols:
                            found_params.add(sym)
                            
    print(f"\nParameters directly constrained to 0 by zero-coboundary channels: {found_params}")

if __name__ == '__main__':
    find_single_bracket_obstructions(1)
