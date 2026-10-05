import json
import os
from fractions import Fraction
from C_generators import parity, build_generators, get_basis_lists, format_coeff, get_osc_parity, normal_order_monomial

def get_K1(X, Y):
    # returns dict of {gb_param: coeff}
    # K1(b, a) = - gb_{a, b}
    # K1(a, b) = gb_{a, b}
    
    px = get_osc_parity(X)
    py = get_osc_parity(Y)
    
    if px == 0 and py == 1: # b, a
        gb_param = f"gb_{Y}_{X}"
        return {gb_param: Fraction(-1)}
    elif px == 1 and py == 0: # a, b
        gb_param = f"gb_{X}_{Y}"
        return {gb_param: Fraction(1)}
    
    return {}

def compute_gamma_term(A, B, C, D):
    # Returns a list of dicts: {"gb_param": name, "coeff": val, "term": (O1, O2)}
    pA = get_osc_parity(A)
    pB = get_osc_parity(B)
    pC = get_osc_parity(C)
    pD = get_osc_parity(D)
    
    res = []
    
    # Term 1: (-1)^pA K1(B,C) A D
    k1 = get_K1(B, C)
    for gb, c in k1.items():
        res.append({
            "gb_param": gb,
            "coeff": c * ((-1)**pA),
            "term": (A, D)
        })
        
    # Term 2: (-1)^{pB pC} K1(A,C) B D
    k1 = get_K1(A, C)
    for gb, c in k1.items():
        res.append({
            "gb_param": gb,
            "coeff": c * ((-1)**(pB * pC)),
            "term": (B, D)
        })
        
    # Term 3: (-1)^{pA pC + pB pC + pC + pA} K1(B,D) C A
    k1 = get_K1(B, D)
    sign = (-1)**(pA*pC + pB*pC + pC + pA)
    for gb, c in k1.items():
        res.append({
            "gb_param": gb,
            "coeff": c * sign,
            "term": (C, A)
        })
        
    # Term 4: (-1)^{pA pC + pB pC + pC + pB pD} K1(A,D) C B
    k1 = get_K1(A, D)
    sign = (-1)**(pA*pC + pB*pC + pC + pB*pD)
    for gb, c in k1.items():
        res.append({
            "gb_param": gb,
            "coeff": c * sign,
            "term": (C, B)
        })
        
    return res

def generate_schema2(n):
    gens = build_generators(n)
    even, odd = get_basis_lists(n, gens)
    all_basis = odd + even
    
    # helper for express_in_basis from C_generators
    terms_set = set()
    for k in gens:
        terms_set.update(gens[k].keys())
    terms_list = list(terms_set)
    
    M = [[Fraction(0) for _ in range(len(all_basis))] for _ in range(len(terms_list))]
    for j, b in enumerate(all_basis):
        b_poly = gens[b]
        for t, c in b_poly.items():
            M[terms_list.index(t)][j] = c
            
    def express_in_basis(poly):
        target = [poly.get(t, Fraction(0)) for t in terms_list]
        aug = [row[:] + [target[i]] for i, row in enumerate(M)]
        rows = len(aug)
        cols = len(aug[0]) - 1
        pivot_row = 0
        for c in range(cols):
            for r in range(pivot_row, rows):
                if aug[r][c] != 0:
                    aug[pivot_row], aug[r] = aug[r], aug[pivot_row]
                    break
            else:
                continue
            pivot_val = aug[pivot_row][c]
            for j in range(c, cols + 1):
                aug[pivot_row][j] /= pivot_val
            for r in range(rows):
                if r != pivot_row and aug[r][c] != 0:
                    factor = aug[r][c]
                    for j in range(c, cols + 1):
                        aug[r][j] -= factor * aug[pivot_row][j]
            pivot_row += 1
        coeffs = {}
        for c in range(cols):
            val = Fraction(0)
            for r in range(rows):
                if aug[r][c] == 1:
                    is_pivot = True
                    for j in range(cols):
                        if j != c and aug[r][j] != 0:
                            is_pivot = False
                    if is_pivot:
                        val = aug[r][-1]
            if val != 0:
                coeffs[all_basis[c]] = val
        return coeffs
        
    gb_params = []
    for f in ["a_1_p", "a_1_m"]:
        for b_idx in range(1, n+1):
            for s in ["p", "m"]:
                gb_params.append(f"gb_{f}_b_{b_idx}_{s}")
                
    gamma_sc = []
    
    for i in range(len(all_basis)):
        for j in range(i, len(all_basis)):
            X = all_basis[i]
            Y = all_basis[j]
            
            X_poly = gens[X]
            Y_poly = gens[Y]
            
            # gamma(X, Y) is sum of gb_param * poly
            gamma_accum = {gb: {} for gb in gb_params}
            
            for termX, cx in X_poly.items():
                for termY, cy in Y_poly.items():
                    if not termX or not termY:
                        continue # scalars have no commutator
                        
                    A, B = termX
                    C, D = termY
                    
                    terms = compute_gamma_term(A, B, C, D)
                    for t in terms:
                        gb = t["gb_param"]
                        c = t["coeff"] * cx * cy
                        # normal order the quadratic
                        no_terms = normal_order_monomial(list(t["term"]))
                        for no_c, no_t in no_terms:
                            gamma_accum[gb][no_t] = gamma_accum[gb].get(no_t, Fraction(0)) + c * no_c
                            
            # Now express each gb's poly in terms of basis
            z_accum = {}
            for gb in gb_params:
                poly = {k: v for k, v in gamma_accum[gb].items() if v != 0}
                if not poly:
                    continue
                basis_coeffs = express_in_basis(poly)
                for Z, coeff in basis_coeffs.items():
                    if Z not in z_accum:
                        z_accum[Z] = {}
                    z_accum[Z][gb] = coeff
                    
            for Z, gb_dict in z_accum.items():
                formatted_gb = {gb: format_coeff(c) for gb, c in gb_dict.items() if c != 0}
                if formatted_gb:
                    gamma_sc.append({
                        "X": X,
                        "Y": Y,
                        "Z": Z,
                        "gb_terms": formatted_gb,
                        "sign_rule": "graded"
                    })
                    
    schema = {
        "schema_version": "5.0",
        "layer": "Schema 2: Gamma structure",
        "algebra": {
            "family": "C",
            "n": n
        },
        "gb_matrix": {
            "parameters": gb_params,
            "description": "Deformation parameters gb_{fermion}_{boson}"
        },
        "gamma_structure_constants": gamma_sc
    }
    
    return schema

if __name__ == "__main__":
    for n in [1, 2, 3]:
        sch = generate_schema2(n)
        with open(f"data/C_{n}_gamma.json", "w") as f:
            json.dump(sch, f, indent=2)
        print(f"Generated data/C_{n}_gamma.json with {len(sch['gamma_structure_constants'])} gamma brackets.")
