#!/usr/bin/env python3
"""
Generate comprehensive structure constants and deformation data for C(n+1), n=1, 2, 3.
"""

import json
from collections import defaultdict
import sympy as sp
from fast_verify import build_algebra, osc_parity, osc_bracket_0, osc_bracket_gamma_basis, reduce_pair_0

def export_full_data():
    all_data = {}
    
    for n in [1, 2, 3]:
        basis, dim, canonical_to_basis = build_algebra(n)
        
        gb_keys = []
        for sigma in ('+', '-'):
            for j in range(1, n+1):
                for s in ('+', '-'):
                    gb_keys.append(f"gb_{sigma}_{j}_{s}")
                    
        basis_info = []
        for i, b in enumerate(basis):
            basis_info.append({
                'index': i,
                'name': b['name'],
                'parity': b['parity']
            })
            
        # Non-zero structure constants
        structure_constants = []
        # Non-zero gamma entries
        gamma_entries = []
        
        for i in range(dim):
            g1 = basis[i]
            for j in range(i, dim):
                g2 = basis[j]
                
                dict_0 = defaultdict(float)
                dict_gamma = [defaultdict(float) for _ in range(len(gb_keys))]
                
                for c1, ops1 in g1['terms']:
                    if len(ops1) == 0:
                        continue
                    u1, u2 = ops1
                    p_u1, p_u2 = osc_parity(u1), osc_parity(u2)
                    
                    for c2, ops2 in g2['terms']:
                        if len(ops2) == 0:
                            continue
                        v1, v2 = ops2
                        p_v1, p_v2 = osc_parity(v1), osc_parity(v2)
                        
                        sign1 = 1
                        sign2 = (-1)**(p_u2 * p_v1)
                        sign3 = (-1)**(p_u2 * (p_v1 + p_v2))
                        sign4 = (-1)**(p_u2 * (p_v1 + p_v2) + p_u1 * p_v1)
                        
                        pieces = [
                            (sign1, (u2, v1), (u1, v2)),
                            (sign2, (u2, v2), (u1, v1)),
                            (sign3, (u1, v1), (v2, u2)),
                            (sign4, (u1, v2), (v1, u2))
                        ]
                        
                        c1_val = float(c1)
                        c2_val = float(c2)
                        
                        for sign, (br_u, br_v), (rem_1, rem_2) in pieces:
                            b0 = osc_bracket_0(br_u, br_v)
                            if b0 != 0:
                                red = reduce_pair_0(rem_1, rem_2)
                                for r_coeff, r_ops in red:
                                    dict_0[r_ops] += c1_val * c2_val * sign * b0 * float(r_coeff)
                                    
                            for gb_idx, gb_name in enumerate(gb_keys):
                                parts = gb_name.split('_')
                                sig_req, j_req, s_req = parts[1], int(parts[2]), parts[3]
                                bg = osc_bracket_gamma_basis(br_u, br_v, sig_req, j_req, s_req)
                                if bg != 0:
                                    red = reduce_pair_0(rem_1, rem_2)
                                    for r_coeff, r_ops in red:
                                        dict_gamma[gb_idx][r_ops] += c1_val * c2_val * sign * bg * float(r_coeff)
                                        
                v0, _ = canonical_to_basis(dict_0)
                for k in range(dim):
                    if abs(v0[k]) > 1e-10:
                        structure_constants.append({
                            'i': i, 'j': j, 'k': k,
                            'name_i': basis[i]['name'],
                            'name_j': basis[j]['name'],
                            'name_k': basis[k]['name'],
                            'coeff': float(v0[k])
                        })
                        
                for gb_idx, gb_name in enumerate(gb_keys):
                    vg, _ = canonical_to_basis(dict_gamma[gb_idx])
                    for k in range(dim):
                        if abs(vg[k]) > 1e-10:
                            gamma_entries.append({
                                'gb_param': gb_name,
                                'i': i, 'j': j, 'k': k,
                                'name_i': basis[i]['name'],
                                'name_j': basis[j]['name'],
                                'name_k': basis[k]['name'],
                                'coeff': float(vg[k])
                            })
                            
        all_data[f"C{n+1}"] = {
            'n': n,
            'algebra': f"osp(2|{2*n})",
            'dimension': dim,
            'basis': basis_info,
            'gb_parameters': gb_keys,
            'num_structure_constants': len(structure_constants),
            'num_gamma_entries': len(gamma_entries),
            'structure_constants_sample': structure_constants[:20],
            'gamma_entries_sample': gamma_entries[:20]
        }
        
    with open('docs/artifacts/C_algebra_structure_constants.json', 'w') as f:
        json.dump(all_data, f, indent=2)
        
    print("Exported structure constants and deformation data to docs/artifacts/C_algebra_structure_constants.json")

if __name__ == '__main__':
    export_full_data()
