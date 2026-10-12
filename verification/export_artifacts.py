"""
Generate structured JSON verification artifacts for n=1, 2, 3.
"""
import json
import sympy as sp
from collections import defaultdict
from verification.cn1_algebra import create_algebra, get_generators, superbracket
from verification.test_jacobi import decompose_into_basis

def generate_artifacts(n):
    print(f"Generating structured artifacts for n={n}...")
    gb, reduce_word = create_algebra(n)
    gens, parities = get_generators(n)
    gen_names = list(gens.keys())
    dim = len(gen_names)
    
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
    gb_names = [str(g) for g in gb_list]
    
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

    # Build M and rhs
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
                row_vec = delta_f_coeffs[r]
                val_rhs = gamma[(g1, g2)][r]
                if any(c != 0 for c in row_vec) or val_rhs != 0:
                    rows.append(row_vec)
                    rhs_list.append(val_rhs)
                    eq_labels.append((g1, g2, r))
                    
    M = sp.Matrix(rows)
    rank_M = M.rank()
    nullspace_left = M.T.nullspace()
    
    gb_constraints = []
    for v in nullspace_left:
        val = sp.simplify(sum(v[i] * rhs_list[i] for i in range(len(rows))))
        if val != 0:
            gb_constraints.append(val)
            
    C_matrix = sp.Matrix([[sp.diff(c, g) for g in gb_list] for c in gb_constraints])
    rank_C = C_matrix.rank()
    
    # Structure constants serialization (non-zero entries only)
    c0_serialized = {}
    for (g1, g2), targets in c0.items():
        for r, val in targets.items():
            if val != 0:
                c0_serialized[f"[{g1}, {g2}] -> {r}"] = str(val)
                
    gamma_serialized = {}
    for (g1, g2), targets in gamma.items():
        for r, val in targets.items():
            if val != 0:
                gamma_serialized[f"gamma({g1}, {g2}) -> {r}"] = str(val)

    # Convert constraints to strings
    constraints_serialized = [str(c) + " = 0" for c in gb_constraints]
    
    if rank_C == len(gb_list):
        triviality_conclusion = "Trivial if and only if gb = 0 (unconditionally non-trivial for any non-zero gb)"
    else:
        triviality_conclusion = f"Trivial on non-zero subspace of dimension {len(gb_list) - rank_C}"
        
    data = {
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "n": n,
        "superdimension": {
            "even": len(even_gens),
            "odd": len(odd_gens),
            "total": dim
        },
        "generators": {
            "even": even_gens,
            "odd": odd_gens
        },
        "deformation_parameters": {
            "count": len(gb_names),
            "parameters": gb_names
        },
        "coboundary_map_f": {
            "parameter_count": num_phi,
            "parameters": phi_vars
        },
        "linear_system": {
            "equations_count": len(rows),
            "phi_unknowns": num_phi,
            "matrix_rank": int(rank_M),
            "kernel_dim (odd derivations)": num_phi - int(rank_M),
            "left_nullspace_dim": len(nullspace_left),
            "constraints_on_gb_count": len(gb_constraints),
            "constraint_matrix_rank": int(rank_C),
            "triviality_conclusion": triviality_conclusion
        },
        "sample_structure_constants": dict(list(c0_serialized.items())[:50]),
        "total_nonzero_structure_constants": len(c0_serialized),
        "sample_gamma_entries": dict(list(gamma_serialized.items())[:50]),
        "total_nonzero_gamma_entries": len(gamma_serialized),
        "gb_constraints": constraints_serialized[:30]
    }
    
    filename = f"verification/artifacts_n{n}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved artifacts to {filename}")
    return data

if __name__ == '__main__':
    for n in (1, 2, 3):
        generate_artifacts(n)
