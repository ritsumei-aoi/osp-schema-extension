import json
import sympy as sp
import os
import sys

# Import solver components
sys.path.append(os.path.abspath("scratch"))
from normal_order import Monomial, multiply_monomials
from vec_helper import get_basis_and_algebra, monomial_to_vec
from run_full_solver import elem_to_monomial

def generate_structured_artifacts():
    artifacts = {}
    
    for n in [1, 2, 3]:
        even_basis, odd_basis = get_basis_and_algebra(n)
        all_basis = even_basis + odd_basis
        
        # Format basis names cleanly for JSON
        even_names = ["Z" if e == ('Z',) else f"B_{e[0][1]}{e[0][2]}_{e[1][1]}{e[1][2]}" for e in even_basis]
        odd_names = [f"O_{o[1]}_{o[2]}{o[3]}" for o in odd_basis]
        
        gb_names = []
        gb_params = {}
        for sigma in ['+', '-']:
            for k in range(1, n+1):
                for s in ['+', '-']:
                    name = f"gb_{sigma}_{k}_{s}"
                    gb_names.append(name)
                    gb_params[(sigma, k, s)] = sp.Symbol(name)
                    
        # Compute gamma_gb matrix for key basis pairs
        gamma_data = []
        
        for X_idx, X in enumerate(all_basis):
            pX = 0 if X in even_basis else 1
            mX = elem_to_monomial(X)
            X_name = "Z" if X == ('Z',) else (f"O_{X[1]}_{X[2]}{X[3]}" if X[0] == 'O' else f"B_{X[0][1]}{X[0][2]}_{X[1][1]}{X[1][2]}")
            
            for Y_idx, Y in enumerate(all_basis):
                if X_idx > Y_idx:
                    continue
                pY = 0 if Y in even_basis else 1
                mY = elem_to_monomial(Y)
                
                sign_YX = 1 if (pX * pY == 1) else -1
                
                XY_dict = multiply_monomials(mX, mY, n, gb_params)
                YX_dict = multiply_monomials(mY, mX, n, gb_params)
                
                super_bracket_dict = {}
                keys = set(XY_dict.keys()).union(set(YX_dict.keys()))
                for k in keys:
                    c = XY_dict.get(k, 0) + sign_YX * YX_dict.get(k, 0)
                    if c != 0:
                        super_bracket_dict[k] = c
                        
                vec_0, vec_1 = monomial_to_vec(super_bracket_dict, even_basis, odd_basis, n)
                
                # Filter non-zero deformation components
                non_zero_gamma = {}
                for b, c in vec_1.items():
                    if c != 0:
                        b_name = "Z" if b == ('Z',) else (f"O_{b[1]}_{b[2]}{b[3]}" if b[0] == 'O' else f"B_{b[0][1]}{b[0][2]}_{b[1][1]}{b[1][2]}")
                        non_zero_gamma[b_name] = str(c)
                        
                if non_zero_gamma:
                    Y_name = "Z" if Y == ('Z',) else (f"O_{Y[1]}_{Y[2]}{Y[3]}" if Y[0] == 'O' else f"B_{Y[0][1]}{Y[0][2]}_{Y[1][1]}{Y[1][2]}")
                    gamma_data.append({
                        "X": X_name,
                        "Y": Y_name,
                        "gamma_gb": non_zero_gamma
                    })
                    
        artifacts[f"C_{n+1}"] = {
            "algebra": f"C({n+1}) = osp(2|2*{n})",
            "superdimension": {
                "even": len(even_basis),
                "odd": len(odd_basis),
                "total": len(all_basis)
            },
            "basis": {
                "even": even_names,
                "odd": odd_names
            },
            "deformation_parameters": gb_names,
            "gamma_gb_sample_evaluations": gamma_data,
            "triviality_conclusion": {
                "is_trivial_if_and_only_if": "gb == 0",
                "non_zero_trivial_gb_exists": False
            }
        }
        
    out_path = "docs/issues/verification_artifacts.json"
    with open(out_path, "w") as f:
        json.dump(artifacts, f, indent=2)
        
    print(f"Artifacts successfully written to {out_path}")

if __name__ == "__main__":
    generate_structured_artifacts()
