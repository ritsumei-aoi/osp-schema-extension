"""
Complete verification and artifact generation for n=1, 2, 3 of C(n+1) = osp(2|2n)
"""
import sympy as sp
import json
import os
from verify_cn1 import get_algebra
from verify_brackets import build_representation_map, compute_brackets
from solve_triviality import compute_delta_f

def run_full_analysis(n, output_dir="artifacts"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n=======================================================")
    print(f"       RUNNING FULL ANALYSIS FOR C({n+1}) = osp(2|{2*n})")
    print(f"=======================================================")
    
    alg = get_algebra(n)
    dim_g = alg['dim_g']
    generators = alg['generators']
    gen_names = [g['name'] for g in generators]
    p = [g['parity'] for g in generators]
    even_count = sum(1 for x in p if x == 0)
    odd_count = sum(1 for x in p if x == 1)
    
    print(f"Dimension: {dim_g} (Even: {even_count}, Odd: {odd_count})")
    
    bracket_0, gamma_def = compute_brackets(alg)
    
    # 1. Export structure constants bracket_0 in sparse format
    structure_constants = []
    for i in range(dim_g):
        for j in range(dim_g):
            for k in range(dim_g):
                val = bracket_0[i][j][k]
                if val != 0:
                    structure_constants.append({
                        'i': i, 'j': j, 'k': k,
                        'gen_i': gen_names[i], 'gen_j': gen_names[j], 'gen_k': gen_names[k],
                        'coeff': int(val) if val == int(val) else float(val)
                    })
                    
    # 2. Export gamma_def in sparse format
    gb_list = list(alg['gb_symbols'].values())
    gb_str_list = [str(s) for s in gb_list]
    
    gamma_entries = []
    for i in range(dim_g):
        for j in range(dim_g):
            for k in range(dim_g):
                val = gamma_def[i][j][k]
                if val != 0:
                    # Decompose val into linear combination of gb
                    decomp = {}
                    for sym in gb_list:
                        c = sp.diff(val, sym)
                        if c != 0:
                            decomp[str(sym)] = int(c) if c == int(c) else float(c)
                    gamma_entries.append({
                        'i': i, 'j': j, 'k': k,
                        'gen_i': gen_names[i], 'gen_j': gen_names[j], 'gen_k': gen_names[k],
                        'gb_linear_combination': decomp
                    })
                    
    pairs = [(i, j) for i in range(dim_g) for j in range(i, dim_g)]
    cochain_dim = len(pairs) * dim_g
    
    # 3. Construct Coboundary Matrix M_delta
    odd_map_basis = []
    for j in range(dim_g):
        for i in range(dim_g):
            if p[i] != p[j]:
                odd_map_basis.append((i, j))
    dim_f_space = len(odd_map_basis)
    print(f"Dimension of Hom(g, g)_odd (f parameters): {dim_f_space}")
    
    delta_cols = []
    for col_idx, (a, b) in enumerate(odd_map_basis):
        phi = sp.zeros(dim_g, dim_g)
        phi[a, b] = 1
        d_f = compute_delta_f(alg, phi, bracket_0)
        col_vec = []
        for i, j in pairs:
            for k in range(dim_g):
                col_vec.append(d_f[i][j][k])
        delta_cols.append(col_vec)
        
    M_delta = sp.Matrix(delta_cols).T
    rank_B2 = M_delta.rank()
    dim_Der = dim_f_space - rank_B2
    print(f"dim B^2(g, g)_odd = {rank_B2}, dim Der(g, g)_odd = {dim_Der}")
    
    # 4. Construct Gamma Matrix M_gamma
    gamma_cols = []
    for sym in gb_list:
        sub_dict = {s: (1 if s == sym else 0) for s in gb_list}
        col_vec = []
        for i, j in pairs:
            for k in range(dim_g):
                val = gamma_def[i][j][k].subs(sub_dict)
                col_vec.append(val)
        gamma_cols.append(col_vec)
        
    M_gamma = sp.Matrix(gamma_cols).T
    rank_gamma = M_gamma.rank()
    print(f"dim Im(gamma_gb) = {rank_gamma} (out of {len(gb_list)} parameters)")
    
    # 5. Augmented rank and intersection
    M_aug = M_delta.row_join(M_gamma)
    rank_aug = M_aug.rank()
    dim_intersection = rank_B2 + rank_gamma - rank_aug
    print(f"Rank([M_delta | M_gamma]) = {rank_aug}")
    print(f"dim( B^2(g, g)_odd INTERSECT Im(gamma_gb) ) = {dim_intersection}")
    
    # Save structured JSON data
    data = {
        'algebra': f'C({n+1}) = osp(2|{2*n})',
        'n': n,
        'dimension': {
            'total': dim_g,
            'even': even_count,
            'odd': odd_count
        },
        'generators': [{'id': idx, 'name': g['name'], 'parity': g['parity']} for idx, g in enumerate(generators)],
        'gb_parameters': gb_str_list,
        'cohomology_analysis': {
            'dim_Hom_g_g_odd': dim_f_space,
            'dim_B2_g_g_odd': int(rank_B2),
            'dim_Der_g_g_odd': int(dim_Der),
            'num_gb_parameters': len(gb_list),
            'rank_gamma_space': int(rank_gamma),
            'rank_augmented': int(rank_aug),
            'dim_intersection_with_coboundaries': int(dim_intersection),
            'is_trivial_only_at_zero': bool(dim_intersection == 0)
        },
        'structure_constants_count': len(structure_constants),
        'structure_constants_sample': structure_constants[:20],
        'gamma_entries_count': len(gamma_entries),
        'gamma_entries_sample': gamma_entries[:20]
    }
    
    json_path = os.path.join(output_dir, f'C{n+1}_analysis.json')
    with open(json_path, 'w') as fp:
        json.dump(data, fp, indent=2)
    print(f"Saved artifact to {json_path}")
    
    # Also save full structure constants & gamma entries to a separate file for complete connectivity
    full_data = {
        'algebra': f'C({n+1}) = osp(2|{2*n})',
        'n': n,
        'generators': gen_names,
        'parities': p,
        'gb_parameters': gb_str_list,
        'structure_constants': structure_constants,
        'gamma_entries': gamma_entries
    }
    full_json_path = os.path.join(output_dir, f'C{n+1}_full_structures.json')
    with open(full_json_path, 'w') as fp:
        json.dump(full_data, fp, indent=2)
    print(f"Saved full structures to {full_json_path}")
    
    return data

if __name__ == '__main__':
    for n in [1, 2, 3]:
        run_full_analysis(n)
