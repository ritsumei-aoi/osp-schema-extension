import json
import sympy as sp
from collections import defaultdict
import os

def get_p(v): return 1 if v.startswith('a_') else 0

def omega_0(u, v):
    if u == 'a_1_m' and v == 'a_1_p': return 1
    if u == 'a_1_p' and v == 'a_1_m': return 1
    if u.startswith('b_') and v.startswith('b_'):
        u_idx, u_s = u.split('_')[1:3]
        v_idx, v_s = v.split('_')[1:3]
        if u_idx == v_idx:
            if u_s == 'm' and v_s == 'p': return 1
            if u_s == 'p' and v_s == 'm': return -1
    return 0

def omega_gamma(u, v):
    if u.startswith('b_') and v.startswith('a_'):
        u_idx, u_s = u.split('_')[1:3]
        v_s = v.split('_')[2]
        return sp.Symbol(f"gb_{v_s}_{u_idx}_{u_s}")
    if u.startswith('a_') and v.startswith('b_'):
        u_s = u.split('_')[2]
        v_idx, v_s = v.split('_')[1:3]
        return -sp.Symbol(f"gb_{u_s}_{v_idx}_{v_s}")
    return 0

def word_parity(w):
    return sum(get_p(v) for v in w) % 2

def normal_order_word_v3(w):
    def rank(v):
        if v == 'a_1_p': return 0
        if v == 'a_1_m': return 1
        return 2 * int(v.split('_')[1]) + (0 if v.split('_')[2]=='p' else 1)
        
    def order_kappa_0(words_dict):
        terms = dict(words_dict)
        final_terms = {}
        while terms:
            new_terms = {}
            for word, coeff in terms.items():
                word = list(word)
                swapped = False
                for i in range(len(word)-1):
                    u, v = word[i], word[i+1]
                    if get_p(u) == 1 and u == v:
                        swapped = True
                        break
                    if rank(u) > rank(v):
                        pu, pv = get_p(u), get_p(v)
                        om0 = omega_0(u, v)
                        if pu == 1 and pv == 1:
                            word[i], word[i+1] = v, u
                            new_terms[tuple(word)] = new_terms.get(tuple(word), 0) - coeff
                            if om0 != 0:
                                new_w = tuple(word[:i] + word[i+2:])
                                new_terms[new_w] = new_terms.get(new_w, 0) + coeff * om0
                        elif pu == 0 and pv == 0:
                            word[i], word[i+1] = v, u
                            new_terms[tuple(word)] = new_terms.get(tuple(word), 0) + coeff
                            if om0 != 0:
                                new_w = tuple(word[:i] + word[i+2:])
                                new_terms[new_w] = new_terms.get(new_w, 0) + coeff * om0
                        else:
                            word[i], word[i+1] = v, u
                            new_terms[tuple(word)] = new_terms.get(tuple(word), 0) + coeff
                        swapped = True
                        break
                if not swapped:
                    final_terms[tuple(word)] = final_terms.get(tuple(word), 0) + coeff
            terms = {k: v for k, v in new_terms.items() if v != 0}
        return {k: v for k, v in final_terms.items() if v != 0}

    terms = {tuple(w): 1}
    final_0 = {}
    raw_gamma_terms = {}
    
    while terms:
        new_terms = {}
        for word, coeff in terms.items():
            word = list(word)
            swapped = False
            for i in range(len(word)-1):
                u, v = word[i], word[i+1]
                if get_p(u) == 1 and u == v:
                    swapped = True
                    break
                if rank(u) > rank(v):
                    pu, pv = get_p(u), get_p(v)
                    om0 = omega_0(u, v)
                    om1 = omega_gamma(u, v)
                    
                    if pu == 1 and pv == 1:
                        word[i], word[i+1] = v, u
                        new_terms[tuple(word)] = new_terms.get(tuple(word), 0) - coeff
                        if om0 != 0:
                            new_w = tuple(word[:i] + word[i+2:])
                            new_terms[new_w] = new_terms.get(new_w, 0) + coeff * om0
                    elif pu == 0 and pv == 0:
                        word[i], word[i+1] = v, u
                        new_terms[tuple(word)] = new_terms.get(tuple(word), 0) + coeff
                        if om0 != 0:
                            new_w = tuple(word[:i] + word[i+2:])
                            new_terms[new_w] = new_terms.get(new_w, 0) + coeff * om0
                    else:
                        word[i], word[i+1] = v, u
                        new_terms[tuple(word)] = new_terms.get(tuple(word), 0) + coeff
                        if om1 != 0:
                            sign = -1 if word_parity(word[:i]) == 1 else 1
                            new_w = tuple(word[:i] + word[i+2:])
                            raw_gamma_terms[new_w] = raw_gamma_terms.get(new_w, 0) + coeff * om1 * sign
                    swapped = True
                    break
            if not swapped:
                final_0[tuple(word)] = final_0.get(tuple(word), 0) + coeff
        terms = {k: v for k, v in new_terms.items() if v != 0}
        
    final_0 = {k: v for k, v in final_0.items() if v != 0}
    final_gamma = order_kappa_0(raw_gamma_terms)
    
    return final_0, final_gamma

def multiply_gamma(t1, t2):
    # t1 and t2 are purely kappa^0 terms
    res_gamma = {}
    for w1, c1 in t1:
        for w2, c2 in t2:
            _, f_gamma = normal_order_word_v3(w1 + w2)
            for nw, nc in f_gamma.items():
                res_gamma[nw] = res_gamma.get(nw, 0) + c1 * c2 * nc
    return {w: c for w, c in res_gamma.items() if c != 0}

def generate_gamma(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema = json.load(f)
        
    gen_reals = schema['generator_realization']['realizations']
    parity = schema['parity']
    all_gen = schema['basis']['even'] + schema['basis']['odd']
    
    parsed = {}
    for g in all_gen:
        terms = []
        for term in gen_reals[g]['standard_form']:
            c = sp.Rational(term['coeff'])
            w = tuple(term['words'])
            terms.append((w, c))
        res_t = {}
        for w, c in terms:
            f0, _ = normal_order_word_v3(w)
            for nw, nc in f0.items():
                res_t[nw] = res_t.get(nw, 0) + c * nc
        parsed[g] = [(w, c) for w, c in res_t.items() if c != 0]

    all_gen.append("K")
    parsed["K"] = [((), 1)]
    parity["K"] = 0


    gamma_out = []
    
    gb_params = []
    for s_fermion in ['p', 'm']:
        for j in range(1, n+1):
            for s_boson in ['p', 'm']:
                gb_params.append(f"gb_{s_fermion}_{j}_{s_boson}")
                
    for i, X in enumerate(all_gen):
        for j in range(len(all_gen)):
            Y = all_gen[j]
            pX, pY = parity[X], parity[Y]
            
            gamma_XY = multiply_gamma(parsed[X], parsed[Y])
            gamma_YX = multiply_gamma(parsed[Y], parsed[X])
            
            sign = -1 if (pX == 1 and pY == 1) else 1
            
            comm_gamma = {}
            for w, c in gamma_XY.items(): comm_gamma[w] = comm_gamma.get(w, 0) + c
            for w, c in gamma_YX.items(): comm_gamma[w] = comm_gamma.get(w, 0) - sign * c
            comm_gamma = {w: c for w, c in comm_gamma.items() if c != 0}
            
            if not comm_gamma: continue
            
            words_in_eq = list(set(list(comm_gamma.keys()) + [w for g in all_gen for w, c in parsed[g]]))
            
            M = sp.Matrix([[next((c for w_, c in parsed[g] if w_ == word), 0) for g in all_gen] for word in words_in_eq])
            b = sp.Matrix([[comm_gamma.get(word, 0)] for word in words_in_eq])
            
            try:
                x = (M.T * M).inv() * M.T * b
            except sp.matrices.common.NonInvertibleMatrixError:
                x = M.pinv() * b
            
            residual = M * x - b
            # Because b has symbolic terms, residual is symbolic. We can just simplify.
            residual = sp.simplify(residual)
            if not all(val == 0 for val in residual):
                print(f"WARNING: gamma of {X} and {Y} not in span!")
                
            for k, coeff in enumerate(x):
                coeff = sp.simplify(coeff)
                if coeff != 0:
                    Z = all_gen[k]
                    gamma_out.append({
                        "X": X, "Y": Y, "Z": Z, "gamma_coeff": str(coeff)
                    })

    schema2 = {
        "schema_version": "5.0",
        "algebra": schema['algebra'],
        "gb_matrix": {
            "parameters": gb_params,
            "description": "Deformation parameters gb_{sigma, j, s}"
        },
        "inhomogeneous_deformation": gamma_out
    }
    
    with open(f"data/C_{n}_gamma.json", "w") as f:
        json.dump(schema2, f, indent=2)

if __name__ == "__main__":
    for n in [1, 2, 3]:
        generate_gamma(n)
        print(f"Generated data/C_{n}_gamma.json")
