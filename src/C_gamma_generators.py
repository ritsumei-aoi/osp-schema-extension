import os
import sys
import json
from fractions import Fraction
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.C_generators import (
    osc_key, Polynomial, get_basis_and_realizations, solve_linear_combination
)

def get_gb_params(n):
    params = []
    param_info = {}
    for k in range(1, n + 1):
        for f_label, f_sym in [("a1_p", "a_1_p"), ("a1_m", "a_1_m")]:
            for b_label, b_sym in [(f"b{k}_p", f"b_{k}_p"), (f"b{k}_m", f"b_{k}_m")]:
                name = f"gb_{f_label}_{b_label}"
                params.append(name)
                param_info[name] = {
                    "row": f_sym,
                    "col": b_sym,
                    "parity": 1
                }
    return params, param_info

def reduce_deformed_word(word):
    current = [(word, Fraction(1), None)]
    final_undeformed = Polynomial()
    final_gamma = {} # gb_param -> Polynomial

    while current:
        next_state = []
        for w, c, gb_p in current:
            if c == 0:
                continue
            
            w_list = list(w)
            reduced = False
            for i in range(len(w_list) - 1):
                s1, s2 = w_list[i], w_list[i+1]
                
                # Check duplicate fermion
                if s1 == s2 and s1 in ("a_1_p", "a_1_m"):
                    reduced = True
                    break # term drops
                
                if osc_key(s1) > osc_key(s2):
                    reduced = True
                    prefix = tuple(w_list[:i])
                    suffix = tuple(w_list[i+2:])
                    
                    if s1 == "a_1_m" and s2 == "a_1_p":
                        next_state.append((prefix + suffix, c, gb_p))
                        next_state.append((prefix + ("a_1_p", "a_1_m") + suffix, -c, gb_p))
                    elif s1.startswith("b_") and s2.startswith("b_") and s1.split("_")[1] == s2.split("_")[1] and s1.endswith("_m") and s2.endswith("_p"):
                        bk_p, bk_m = s2, s1
                        next_state.append((prefix + (bk_p, bk_m) + suffix, c, gb_p))
                        next_state.append((prefix + suffix, c, gb_p))
                    elif s1.startswith("b_") and s2.startswith("a_1_"):
                        # Deformed exchange: b_k^s * a_1^\sigma = a_1^\sigma * b_k^s - gb * kappa
                        f_label = "a1_p" if s2 == "a_1_p" else "a1_m"
                        parts = s1.split("_")
                        b_label = f"b{parts[1]}_{parts[2]}"
                        gb_name = f"gb_{f_label}_{b_label}"
                        
                        # Swapped term
                        next_state.append((prefix + (s2, s1) + suffix, c, gb_p))
                        
                        # Deformed kappa term
                        if gb_p is None:
                            next_state.append((prefix + suffix, -c, gb_name))
                    else:
                        # Commuting operators
                        next_state.append((prefix + (s2, s1) + suffix, c, gb_p))
                    break
            
            if not reduced:
                poly = Polynomial({w: c})
                if gb_p is None:
                    final_undeformed = final_undeformed.add(poly)
                else:
                    final_gamma[gb_p] = final_gamma.get(gb_p, Polynomial()).add(poly)

        current = next_state

    return final_undeformed, final_gamma

def generate_c_gamma(n):
    even, odd, parity, realizations, realizations_json = get_basis_and_realizations(n)
    all_basis = odd + even # PBW: odd < even
    gb_params, param_info = get_gb_params(n)

    # Add central element K to realizations for gamma solving
    extended_realizations = dict(realizations)
    extended_realizations["K"] = Polynomial({(): 1})
    extended_basis = all_basis + ["K"]

    gamma_coefficients = []

    for i in range(len(all_basis)):
        for j in range(i, len(all_basis)):
            name_X = all_basis[i]
            name_Y = all_basis[j]
            poly_X = realizations[name_X]
            poly_Y = realizations[name_Y]
            p_X = parity[name_X]
            p_Y = parity[name_Y]

            sign = -1 if (p_X == 1 and p_Y == 1) else 1

            gamma_bracket = {} # gb_param -> Polynomial

            # 1. X Y
            for wX, cX in poly_X.terms.items():
                for wY, cY in poly_Y.terms.items():
                    raw_word = wX + wY
                    c_prod = cX * cY
                    _, g_dict = reduce_deformed_word(raw_word)
                    for g_param, g_poly in g_dict.items():
                        gamma_bracket[g_param] = gamma_bracket.get(g_param, Polynomial()).add(g_poly.scale(c_prod))

            # 2. - sign * Y X
            for wY, cY in poly_Y.terms.items():
                for wX, cX in poly_X.terms.items():
                    raw_word = wY + wX
                    c_prod = -sign * cY * cX
                    _, g_dict = reduce_deformed_word(raw_word)
                    for g_param, g_poly in g_dict.items():
                        gamma_bracket[g_param] = gamma_bracket.get(g_param, Polynomial()).add(g_poly.scale(c_prod))

            # Resolve gamma_bracket[g_param] into basis generators
            for g_param, g_poly in gamma_bracket.items():
                if not g_poly.is_zero():
                    sol = solve_linear_combination(g_poly, extended_realizations, extended_basis)
                    for name_Z, coeff in sol.items():
                        c_str = str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}"
                        gamma_coefficients.append({
                            "X": name_X,
                            "Y": name_Y,
                            "Z": name_Z,
                            "gb_param": g_param,
                            "coeff": c_str
                        })

    cartan_type = f"C({n+1})"
    osp_name = f"osp(2|{2*n})"
    total_dim = 2*n*n + 5*n + 1
    even_dim = 2*n*n + n + 1
    odd_dim = 4*n

    boson_labels = []
    for k in range(1, n + 1):
        boson_labels.extend([f"b_{k}_p", f"b_{k}_m"])

    schema_data = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": cartan_type,
            "alternative_notation": {
                "osp": osp_name,
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": total_dim,
                "even": even_dim,
                "odd": odd_dim
            }
        },
        "gb_matrix": {
            "rows": ["a_1_p", "a_1_m"],
            "columns": boson_labels,
            "parameter_count": len(gb_params),
            "parameters": param_info
        },
        "inhomogeneous_deformation": {
            "description": "Symbolic gamma structure constants gamma(X, Y) = sum_Z gamma_{XY}^Z Z",
            "gamma_coefficients": gamma_coefficients
        },
        "metadata": {
            "generated_by": "src/C_gamma_generators.py",
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }

    return schema_data

def main():
    os.makedirs("data", exist_ok=True)
    for n in (1, 2, 3):
        data = generate_c_gamma(n)
        filename = f"data/C_{n}_gamma.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename}: gamma_coefficients={len(data['inhomogeneous_deformation']['gamma_coefficients'])}")

if __name__ == "__main__":
    main()
