"""
Schema 2 (Gamma Structure / Inhomogeneous Deformation) Generator for C(n+1) = osp(2|2n)
"""

import os
import sys
import json
import datetime
from fractions import Fraction

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.C_generators import get_C_basis, get_generator_realizations
from src.oscillator_engine import op_key, op_parity

def swap_adjacent_deformed(word, i):
    """
    Swaps word[i] and word[i+1] under deformed oscillator relations containing kappa * gb.
    Returns list of (coeff, gb_param_or_None, new_word).
    """
    A = word[i]
    B = word[i+1]
    prefix = word[:i]
    suffix = word[i+2:]
    
    pA = op_parity(A)
    pB = op_parity(B)
    
    if pA == 1 and pB == 1:
        anticomm = 0
        if (A == "a_1_m" and B == "a_1_p") or (A == "a_1_p" and B == "a_1_m"):
            anticomm = 1
        terms = []
        if anticomm != 0:
            terms.append((Fraction(anticomm), None, prefix + suffix))
        terms.append((Fraction(-1), None, prefix + (B, A) + suffix))
        return terms
    elif pA == 0 and pB == 0:
        comm = 0
        if A.startswith("b_") and B.startswith("b_"):
            kA, sA = int(A.split("_")[1]), A.split("_")[2]
            kB, sB = int(B.split("_")[1]), B.split("_")[2]
            if kA == kB:
                if sA == 'm' and sB == 'p': comm = 1
                elif sA == 'p' and sB == 'm': comm = -1
        terms = []
        if comm != 0:
            terms.append((Fraction(comm), None, prefix + suffix))
        terms.append((Fraction(1), None, prefix + (B, A) + suffix))
        return terms
    else:
        # Mixed fermion/boson: [b_j^s, a_1^\sigma] = - gb_{\sigma, j, s} * kappa
        # b_j^s a_1^\sigma = a_1^\sigma b_j^s - gb * kappa
        # a_1^\sigma b_j^s = b_j^s a_1^\sigma + gb * kappa
        terms = []
        if A.startswith("b_") and B.startswith("a_"):
            # A is boson, B is fermion
            gb_param = f"gb_{B}_{A}"
            terms.append((Fraction(-1), gb_param, prefix + suffix))
            terms.append((Fraction(1), None, prefix + (B, A) + suffix))
        elif A.startswith("a_") and B.startswith("b_"):
            # A is fermion, B is boson
            gb_param = f"gb_{A}_{B}"
            terms.append((Fraction(1), gb_param, prefix + suffix))
            terms.append((Fraction(1), None, prefix + (B, A) + suffix))
        return terms

def reduce_word_deformed(word):
    """
    Reduces tuple of operator labels to dict of {(word_tuple, gb_param_or_None): Fraction_coeff}.
    At most one gb_param per term (since kappa^2 = 0).
    """
    state = {(tuple(word), None): Fraction(1)}
    
    while True:
        next_state = {}
        all_sorted = True
        
        for (w, gb), c in state.items():
            out_of_order_i = -1
            for i in range(len(w) - 1):
                if op_key(w[i]) > op_key(w[i+1]):
                    out_of_order_i = i
                    break
            if out_of_order_i != -1:
                all_sorted = False
                expanded = swap_adjacent_deformed(w, out_of_order_i)
                for coeff_factor, new_gb, new_w in expanded:
                    # If term already has a gb and new_gb is present, kappa^2 = 0 so it vanishes!
                    if gb is not None and new_gb is not None:
                        continue
                    final_gb = gb if new_gb is None else new_gb
                    key = (new_w, final_gb)
                    next_state[key] = next_state.get(key, Fraction(0)) + c * coeff_factor
            else:
                key = (w, gb)
                next_state[key] = next_state.get(key, Fraction(0)) + c
                
        state = {k: c for k, c in next_state.items() if c != 0}
        if all_sorted:
            break
            
    return state

def compute_deformed_bracket_terms(poly1, poly2):
    """
    Computes [poly1, poly2]_gamma.
    Returns dict of {(reduced_word, gb_param_or_None): Fraction_coeff}.
    """
    res = {}
    for term1 in poly1:
        w1, c1 = tuple(term1["words"]), Fraction(term1["coeff"])
        p1 = sum(op_parity(op) for op in w1) % 2
        for term2 in poly2:
            w2, c2 = tuple(term2["words"]), Fraction(term2["coeff"])
            p2 = sum(op_parity(op) for op in w2) % 2
            
            sign = -1 if (p1 == 1 and p2 == 1) else 1
            
            # term1 * term2
            red12 = reduce_word_deformed(w1 + w2)
            for (w, gb), c in red12.items():
                key = (w, gb)
                res[key] = res.get(key, Fraction(0)) + c1 * c2 * c
                
            # - (-1)^(p1*p2) term2 * term1
            red21 = reduce_word_deformed(w2 + w1)
            for (w, gb), c in red21.items():
                key = (w, gb)
                res[key] = res.get(key, Fraction(0)) - Fraction(sign) * c1 * c2 * c
                
    return {k: c for k, c in res.items() if c != 0}

def get_gamma_structure(n):
    """
    Generates Schema 2 (C_{n}_gamma.json) data structure.
    """
    basis_info = get_C_basis(n)
    even_basis = basis_info["even"]
    odd_basis = basis_info["odd"]
    all_basis = even_basis + odd_basis
    realizations = get_generator_realizations(n)
    
    # Build gb_matrix specification
    rows = ["a_1_p", "a_1_m"]
    cols = []
    for k in range(1, n + 1):
        cols.extend([f"b_{k}_p", f"b_{k}_m"])
        
    gb_params_matrix = []
    for r in rows:
        row_params = [f"gb_{r}_{c}" for c in cols]
        gb_params_matrix.append(row_params)
        
    gamma_coeffs = []
    
    for i, X in enumerate(all_basis):
        polyX = realizations[X]["standard_form"]
        for j, Y in enumerate(all_basis):
            polyY = realizations[Y]["standard_form"]
            
            deformed_terms = compute_deformed_bracket_terms(polyX, polyY)
            
            # Isolate terms with gb != None
            gb_dict = {}
            for (w, gb), c in deformed_terms.items():
                if gb is not None:
                    gb_dict[(w, gb)] = c
                    
            # Map reduced words to basis generators Z
            # Each word w of length 2 or 1 maps to basis generators
            for (w, gb), c in gb_dict.items():
                if len(w) == 2:
                    o1, o2 = w[0], w[1]
                    if o1 == "a_1_p" and o2 == "a_1_m":
                        gamma_coeffs.append({"X": X, "Y": Y, "Z": "H_0", "gb_param": gb, "coeff": str(c)})
                    elif o1.startswith("b_") and o2.startswith("b_"):
                        k1, s1 = int(o1.split("_")[1]), o1.split("_")[2]
                        k2, s2 = int(o2.split("_")[1]), o2.split("_")[2]
                        if k1 == k2:
                            if s1 == 'p' and s2 == 'm':
                                gen_name = f"H_{k1}"
                                gamma_coeffs.append({"X": X, "Y": Y, "Z": gen_name, "gb_param": gb, "coeff": str(c)})
                            elif s1 == 'p' and s2 == 'p':
                                gen_name = f"E_2del{k1}_p"
                                gamma_coeffs.append({"X": X, "Y": Y, "Z": gen_name, "gb_param": gb, "coeff": str(c)})
                            elif s1 == 'm' and s2 == 'm':
                                gen_name = f"E_2del{k1}_m"
                                gamma_coeffs.append({"X": X, "Y": Y, "Z": gen_name, "gb_param": gb, "coeff": str(c)})
                        else:
                            gen_name = f"E_del{k1}_del{k2}_{s1}{s2}"
                            gamma_coeffs.append({"X": X, "Y": Y, "Z": gen_name, "gb_param": gb, "coeff": str(c)})
                    elif o1.startswith("a_") and o2.startswith("b_"):
                        s1 = o1.split("_")[2]
                        k2, s2 = int(o2.split("_")[1]), o2.split("_")[2]
                        gen_name = f"E_eps1_del{k2}_{s1}{s2}"
                        gamma_coeffs.append({"X": X, "Y": Y, "Z": gen_name, "gb_param": gb, "coeff": str(c)})
                elif len(w) == 1:
                    # Single operator word (not a standard Lie basis element unless mapped)
                    pass

    schema_2 = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})"
        },
        "gb_matrix": {
            "dim": [2, 2 * n],
            "rows": rows,
            "cols": cols,
            "parameters": gb_params_matrix,
            "total_parameters": 4 * n
        },
        "basis": basis_info,
        "inhomogeneous_deformation": {
            "description": "Symbolic gamma coefficients gamma_abc for [X_a, Y_b]_gamma = [X_a, Y_b]_0 + kappa * sum_c gamma_{abc} Z_c",
            "coefficients": gamma_coeffs
        },
        "metadata": {
            "generated_by": "src/C_gamma_generators.py",
            "generation_date": datetime.date.today().isoformat()
        }
    }
    return schema_2

def generate_all_C_gammas(data_dir="data"):
    os.makedirs(data_dir, exist_ok=True)
    for n in [1, 2, 3]:
        data = get_gamma_structure(n)
        filename = os.path.join(data_dir, f"C_{n}_gamma.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Generated {filename} (gb_count={data['gb_matrix']['total_parameters']}, gamma_terms_count={len(data['inhomogeneous_deformation']['coefficients'])})")

if __name__ == "__main__":
    generate_all_C_gammas()
