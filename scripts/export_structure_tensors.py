import sympy as sp
import json
import os
from analyzer import run_analysis

def export_tensors(n):
    basis_names, basis_parity, bracket_0, gamma_gb, gb_syms = run_analysis(n)
    
    # Structure constants: [Z_i, Z_j]_0 = sum_k C0_{ij}^k Z_k
    # We store as list of non-zero entries: {"i": name_i, "j": name_j, "k": name_k, "val": coeff}
    c0_entries = []
    for (name_X, name_Y), b_dict in bracket_0.items():
        for name_Z, val in b_dict.items():
            if val != 0:
                c0_entries.append({
                    "i": name_X,
                    "j": name_Y,
                    "k": name_Z,
                    "coeff": str(val)
                })
                
    # Deformation 2-cocycle: gamma(Z_i, Z_j) = sum_k gamma_{ij}^k(gb) Z_k
    # Each coeff is a linear combination of gb parameters: {"gb_param": coeff}
    gamma_entries = []
    for (name_X, name_Y), g_dict in gamma_gb.items():
        for name_Z, val in g_dict.items():
            if val != 0:
                # Decompose into linear coeffs of gb_syms
                gb_decomp = {}
                for sym in gb_syms.values():
                    c = sp.diff(val, sym)
                    if c != 0:
                        gb_decomp[str(sym)] = str(c)
                if gb_decomp:
                    gamma_entries.append({
                        "i": name_X,
                        "j": name_Y,
                        "k": name_Z,
                        "expr": str(val),
                        "linear_terms": gb_decomp
                    })
                    
    tensor_data = {
        "n": n,
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "dimension": len(basis_names),
        "even_dimension": sum(1 for name in basis_names if basis_parity[name] == 0),
        "odd_dimension": sum(1 for name in basis_names if basis_parity[name] == 1),
        "basis_names": basis_names,
        "basis_parity": {name: basis_parity[name] for name in basis_names},
        "num_c0_nonzero_entries": len(c0_entries),
        "structure_constants_c0": c0_entries,
        "num_gamma_nonzero_entries": len(gamma_entries),
        "deformation_cocycle_gamma": gamma_entries
    }
    
    os.makedirs("data", exist_ok=True)
    out_path = f"data/structure_constants_C{n+1}.json"
    with open(out_path, "w") as f:
        json.dump(tensor_data, f, indent=2)
    print(f"Exported {out_path}: {len(c0_entries)} C0 entries, {len(gamma_entries)} gamma entries.")

if __name__ == '__main__':
    for n in [1, 2, 3]:
        export_tensors(n)
