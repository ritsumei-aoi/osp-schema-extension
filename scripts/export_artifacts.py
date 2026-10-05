import numpy as np
import json
import os
from scratch.verify_cn1_deformation import build_cn1_algebra, analyze_triviality

def export_all_artifacts():
    output_data = {
        "metadata": {
            "algebra": "C(n+1) = osp(2|2n)",
            "problem": "Triviality of inhomogeneous deformation gamma_{gb}",
            "author": "Antigravity AI Researcher",
            "date": "2026-10-05"
        },
        "results_by_n": {}
    }
    
    for n in [1, 2, 3]:
        basis, C_tensor, gamma_tensor, gb_params = build_cn1_algebra(n)
        res = analyze_triviality(n)
        
        # Convert basis to JSON serializable format
        basis_json = []
        for b in basis:
            basis_json.append({
                "name": b["name"],
                "parity": b["parity"]
            })
            
        # Structure constants non-zero entries
        dim = len(basis)
        C_nonzero = []
        for a in range(dim):
            for b in range(dim):
                for c in range(dim):
                    if C_tensor[a, b, c] != 0:
                        C_nonzero.append({
                            "a": basis[a]["name"],
                            "b": basis[b]["name"],
                            "c": basis[c]["name"],
                            "val": float(C_tensor[a, b, c])
                        })
                        
        # Gamma tensor non-zero entries
        gamma_nonzero = []
        for a in range(dim):
            for b in range(dim):
                for c in range(dim):
                    for p_idx, p_name in enumerate(gb_params):
                        val = gamma_tensor[a, b, c, p_idx]
                        if val != 0:
                            gamma_nonzero.append({
                                "a": basis[a]["name"],
                                "b": basis[b]["name"],
                                "c": basis[c]["name"],
                                "param": p_name,
                                "val": float(val)
                            })
                            
        output_data["results_by_n"][f"n={n}"] = {
            "summary": res,
            "basis": basis_json,
            "gb_params": gb_params,
            "num_nonzero_structure_constants": len(C_nonzero),
            "num_nonzero_gamma_entries": len(gamma_nonzero),
            "sample_structure_constants": C_nonzero[:20],
            "sample_gamma_entries": gamma_nonzero[:20]
        }
        
    os.makedirs("docs/issues", exist_ok=True)
    out_path = "docs/issues/cn1_triviality_artifacts.json"
    with open(out_path, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"Exported verification artifacts to {out_path}")

if __name__ == "__main__":
    export_all_artifacts()
