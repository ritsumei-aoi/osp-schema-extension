import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
from itertools import product

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from C_generators import get_generators, get_basis_order, normal_order_term, get_parity, add_expr

def get_c(x, y):
    if x.startswith('b_') and y.startswith('a_1_'):
        s = x.split('_')[-1]
        sigma = y.split('_')[-1]
        j = x.split('_')[1]
        return -1, f"gb_{sigma}_{j}_{s}"
    elif x.startswith('a_1_') and y.startswith('b_'):
        s = y.split('_')[-1]
        sigma = x.split('_')[-1]
        j = y.split('_')[1]
        return 1, f"gb_{sigma}_{j}_{s}"
    return 0, None

def gamma_bracket_words(w1, w2):
    # w1 = (A, B), w2 = (C, D)
    if len(w1) != 2 or len(w2) != 2:
        return []
    A, B = w1
    C, D = w2
    pA, pB, pC, pD = get_parity([(1, (A,))]), get_parity([(1, (B,))]), get_parity([(1, (C,))]), get_parity([(1, (D,))])
    
    terms = []
    
    # 1: A c(B, C) D
    v, gb = get_c(B, C)
    if v != 0:
        terms.append((v, gb, (A, D)))
        
    # 2: (-1)^{p_B p_C} A C c(B, D)  -- wait, A c(B,D) C = (-1)^{p_B p_C} c(B,D) A C?
    # Original: A C [B, D] -> A C c(B, D)
    v, gb = get_c(B, D)
    if v != 0:
        sign = -1 if (pB == 1 and pC == 1) else 1
        terms.append((sign * v, gb, (A, C)))
        
    # 3: (-1)^{p_B(p_C+p_D)} c(A, C) D B
    v, gb = get_c(A, C)
    if v != 0:
        sign = -1 if (pB == 1 and (pC + pD) % 2 == 1) else 1
        terms.append((sign * v, gb, (D, B)))
        
    # 4: (-1)^{p_B(p_C+p_D) + p_A p_C} C c(A, D) B
    v, gb = get_c(A, D)
    if v != 0:
        sign = -1 if ((pB * (pC + pD) + pA * pC) % 2 == 1) else 1
        terms.append((sign * v, gb, (C, B)))
        
    return terms

def gamma_bracket(expr1, expr2):
    res = []
    for c1, w1 in expr1:
        for c2, w2 in expr2:
            if len(w1) == 0 or len(w2) == 0: continue
            raw_terms = gamma_bracket_words(w1, w2)
            for v, gb, w in raw_terms:
                # normal order w
                no_w = normal_order_term(c1 * c2 * v, w)
                for no_c, no_word in no_w:
                    res.append((no_c, gb, no_word))
    return res

def expand_in_basis(terms, gens, order):
    # terms is list of (coeff, gb, word)
    grouped = defaultdict(list)
    for c, gb, w in terms:
        if len(w) > 0:
            grouped[gb].append((c, w))
            
    expansion = []
    for gb, expr in grouped.items():
        # group by word
        expr_dict = defaultdict(Fraction)
        for c, w in expr:
            expr_dict[w] += c
        rem = {w: c for w, c in expr_dict.items() if c != 0}
        
        for Z in order:
            Z_expr = gens[Z]
            if not Z_expr: continue
            Z_c, Z_w = Z_expr[0]
            if Z_w in rem and rem[Z_w] != 0:
                factor = rem[Z_w] / Z_c
                for ec, ew in Z_expr:
                    rem[ew] = rem.get(ew, Fraction(0)) - factor * ec
                    if rem[ew] == 0: del rem[ew]
                expansion.append({
                    "Z": Z,
                    "gb_param": gb,
                    "coeff": str(factor)
                })
                if not any(v != 0 for v in rem.values()): break
    return expansion

def generate_schema2(n):
    gens = get_generators(n)
    order = get_basis_order(n)
    
    gamma = []
    for i in range(len(order)):
        for j in range(len(order)):
            X = order[i]
            Y = order[j]
            gb_terms = gamma_bracket(gens[X], gens[Y])
            if gb_terms:
                expansion = expand_in_basis(gb_terms, gens, order)
                if expansion:
                    gamma.append({
                        "X": X,
                        "Y": Y,
                        "gamma_expansion": expansion
                    })
                    
    schema2 = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n
        },
        "inhomogeneous_deformation": {
            "gb_matrix": {
                "description": "Deformation parameters gb_{sigma, j, s}",
                "parameters": [f"gb_{sigma}_{j}_{s}" for sigma in ["p", "m"] for j in range(1, n+1) for s in ["p", "m"]]
            }
        },
        "gamma_structure": gamma,
        "metadata": {
            "generated_by": "C_gamma.py"
        }
    }
    return schema2

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_gamma.json", "w") as f:
            json.dump(generate_schema2(n), f, indent=2)
    print("Generated Schema 2 JSONs in data/")
