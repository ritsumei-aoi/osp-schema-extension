import json
import os
from fractions import Fraction
from copy import deepcopy

class Term:
    def __init__(self, coeff, words):
        self.coeff = Fraction(coeff)
        self.words = list(words)

class GammaTerm:
    def __init__(self, coeff, gb_name, words):
        self.coeff = Fraction(coeff)
        self.gb_name = gb_name
        self.words = list(words)

def rank(w):
    if w == 'a_1_p': return 10
    if w == 'a_1_m': return 20
    if w.startswith('b_'):
        parts = w.split('_')
        return 100 + int(parts[1]) * 10 + (1 if parts[2] == 'm' else 0)
    return 1000

def normal_order_base(terms):
    # Standard normal ordering without deformation
    result = []
    stack = [Term(t.coeff, t.words) for t in terms]
    while stack:
        curr = stack.pop()
        if curr.coeff == 0: continue
        words = curr.words
        swapped = False
        for i in range(len(words)-1):
            w1, w2 = words[i], words[i+1]
            if rank(w1) > rank(w2) or (w1 == w2 and w1.startswith('a_')):
                swapped = True
                if w1 == 'a_1_m' and w2 == 'a_1_p':
                    stack.append(Term(curr.coeff, words[:i] + words[i+2:]))
                    stack.append(Term(-curr.coeff, words[:i] + ['a_1_p', 'a_1_m'] + words[i+2:]))
                elif w1 == w2 and w1.startswith('a_'):
                    pass
                elif w1.startswith('b_') and w2.startswith('b_') and w1[:-2] == w2[:-2] and w1.endswith('m') and w2.endswith('p'):
                    stack.append(Term(curr.coeff, words[:i] + words[i+2:]))
                    stack.append(Term(curr.coeff, words[:i] + [w2, w1] + words[i+2:]))
                else:
                    stack.append(Term(curr.coeff, words[:i] + [w2, w1] + words[i+2:]))
                break
        if not swapped:
            result.append(curr)
    
    final_dict = {}
    for t in result:
        w_tuple = tuple(t.words)
        final_dict[w_tuple] = final_dict.get(w_tuple, Fraction(0)) + t.coeff
    return [Term(c, w) for w, c in final_dict.items() if c != 0]

def normal_order_deformed(terms):
    # Returns (normal_ordered_terms, gamma_terms)
    result = []
    gamma_result = []
    stack = [Term(t.coeff, t.words) for t in terms]
    
    while stack:
        curr = stack.pop()
        if curr.coeff == 0: continue
        words = curr.words
        swapped = False
        for i in range(len(words)-1):
            w1, w2 = words[i], words[i+1]
            if rank(w1) > rank(w2) or (w1 == w2 and w1.startswith('a_')):
                swapped = True
                if w1.startswith('b_') and w2.startswith('a_'):
                    # Deformation: b_j^s a_1^sigma = a_1^sigma b_j^s - gb * kappa
                    # Swap term
                    stack.append(Term(curr.coeff, words[:i] + [w2, w1] + words[i+2:]))
                    # Gamma term
                    sigma = 'p' if w2.endswith('p') else 'm'
                    s = 'p' if w1.endswith('p') else 'm'
                    j = w1.split('_')[1]
                    gb_name = f"gb_{sigma}_{j}_{s}"
                    
                    # count fermions before i to move kappa to front
                    F = sum(1 for w in words[:i] if w.startswith('a_'))
                    sign = -1 if F % 2 == 1 else 1
                    
                    # coeff is curr.coeff * (-1) * sign
                    g_coeff = curr.coeff * (-1) * sign
                    gamma_result.append(GammaTerm(g_coeff, gb_name, words[:i] + words[i+2:]))
                    
                elif w1 == 'a_1_m' and w2 == 'a_1_p':
                    stack.append(Term(curr.coeff, words[:i] + words[i+2:]))
                    stack.append(Term(-curr.coeff, words[:i] + ['a_1_p', 'a_1_m'] + words[i+2:]))
                elif w1 == w2 and w1.startswith('a_'):
                    pass
                elif w1.startswith('b_') and w2.startswith('b_') and w1[:-2] == w2[:-2] and w1.endswith('m') and w2.endswith('p'):
                    stack.append(Term(curr.coeff, words[:i] + words[i+2:]))
                    stack.append(Term(curr.coeff, words[:i] + [w2, w1] + words[i+2:]))
                else:
                    stack.append(Term(curr.coeff, words[:i] + [w2, w1] + words[i+2:]))
                break
        if not swapped:
            result.append(curr)
            
    final_dict = {}
    for t in result:
        w_tuple = tuple(t.words)
        final_dict[w_tuple] = final_dict.get(w_tuple, Fraction(0)) + t.coeff
    normal_terms = [Term(c, w) for w, c in final_dict.items() if c != 0]
    
    # Process gamma terms: they are just normal ordered using base relations
    gamma_final = []
    # Group by gb_name
    gb_groups = {}
    for gt in gamma_result:
        gb_groups.setdefault(gt.gb_name, []).append(Term(gt.coeff, gt.words))
        
    for gb_name, g_terms in gb_groups.items():
        ordered = normal_order_base(g_terms)
        for t in ordered:
            gamma_final.append(GammaTerm(t.coeff, gb_name, t.words))
            
    return normal_terms, gamma_final

def multiply_terms(list1, list2):
    res = []
    for t1 in list1:
        for t2 in list2:
            res.append(Term(t1.coeff * t2.coeff, t1.words + t2.words))
    return res # Not normal ordered yet

def scale_terms(terms, scalar):
    return [Term(t.coeff * Fraction(scalar), t.words) for t in terms]

def graded_commutator_gamma(X_terms, X_parity, Y_terms, Y_parity):
    XY = multiply_terms(X_terms, Y_terms)
    YX = multiply_terms(Y_terms, X_terms)
    sign = -1 if (X_parity == 1 and Y_parity == 1) else 1
    
    if sign == 1:
        minus_YX = scale_terms(YX, -1)
    else:
        minus_YX = scale_terms(YX, 1)
        
    combined = XY + minus_YX
    _, gamma_terms = normal_order_deformed(combined)
    return gamma_terms

def generate_gamma(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema1 = json.load(f)
        
    gens = {}
    for name, data in schema1['generator_realization']['realizations'].items():
        terms = []
        for t in data['standard_form']:
            terms.append(Term(Fraction(t['coeff']), t['words']))
        gens[name] = terms
        
    parities = schema1['parity']
    all_gens = schema1['basis']['even'] + schema1['basis']['odd']
    
    gamma_constants = []
    
    # Helper to decompose into generators
    def decompose(gamma_terms):
        # gamma_terms is a list of GammaTerm
        # Group by gb_name
        gb_dict = {}
        for gt in gamma_terms:
            gb_dict.setdefault(gt.gb_name, []).append(Term(gt.coeff, gt.words))
            
        decomp = {}
        for gb_name, g_terms in gb_dict.items():
            remaining = g_terms
            
            # Decompose Cartans
            cartan_coeff = {}
            for t in remaining:
                if t.words == ['a_1_p', 'a_1_m']: cartan_coeff['a'] = t.coeff
                elif len(t.words) == 2 and t.words[0].startswith('b_') and t.words[1].startswith('b_') and t.words[0].endswith('_p') and t.words[1].endswith('_m') and t.words[0][:-2] == t.words[1][:-2]:
                    cartan_coeff[t.words[0][:-2]] = t.coeff
                elif len(t.words) == 0: cartan_coeff['1'] = t.coeff
                
            def sub_terms(t1, t2):
                return normal_order_base(t1 + scale_terms(t2, -1))
                
            if cartan_coeff:
                c_1 = cartan_coeff.get('a', Fraction(0))
                if c_1 != 0:
                    decomp.setdefault(gb_name, {})['H_1'] = c_1
                    remaining = sub_terms(remaining, scale_terms(gens['H_1'], c_1))
                
                for k in range(2, n+1):
                    curr_b = next((t.coeff for t in remaining if t.words == [f'b_{k-1}_p', f'b_{k-1}_m']), Fraction(0))
                    if curr_b != 0:
                        decomp.setdefault(gb_name, {})[f'H_{k}'] = curr_b
                        remaining = sub_terms(remaining, scale_terms(gens[f'H_{k}'], curr_b))
                        
                curr_bn = next((t.coeff for t in remaining if t.words == [f'b_{n}_p', f'b_{n}_m']), Fraction(0))
                if curr_bn != 0:
                    c_np1 = -curr_bn
                    decomp.setdefault(gb_name, {})[f'H_{n+1}'] = c_np1
                    remaining = sub_terms(remaining, scale_terms(gens[f'H_{n+1}'], c_np1))
                    
                curr_1 = next((t.coeff for t in remaining if len(t.words) == 0), Fraction(0))
                if curr_1 != 0:
                    decomp.setdefault(gb_name, {})['K'] = curr_1
                    remaining = sub_terms(remaining, [Term(curr_1, [])])
                    
            if remaining:
                for r in all_gens:
                    if r.startswith('H_'): continue
                    g_terms = gens[r]
                    first_word = tuple(g_terms[0].words)
                    for t in remaining:
                        if tuple(t.words) == first_word:
                            ratio = t.coeff / g_terms[0].coeff
                            decomp.setdefault(gb_name, {})[r] = ratio
                            remaining = sub_terms(remaining, scale_terms(g_terms, ratio))
                            break
            if remaining:
                print(f"Warning: Failed to decompose gamma for {gb_name}: {remaining}")
                
        return decomp

    for X in all_gens:
        for Y in all_gens:
            gamma_terms = graded_commutator_gamma(gens[X], parities[X], gens[Y], parities[Y])
            if not gamma_terms: continue
            
            decomp = decompose(gamma_terms)
            for gb_name, z_dict in decomp.items():
                for Z, coeff in z_dict.items():
                    if coeff != 0:
                        gamma_constants.append({
                            "X": X, "Y": Y, "Z": Z,
                            "gb_param": gb_name,
                            "coeff": str(coeff)
                        })

    schema2 = {
        "schema_version": "5.0",
        "algebra": schema1["algebra"],
        "inhomogeneous_deformation": {
            "gb_matrix_size": f"2 x {2*n}",
            "gb_parameters": [f"gb_{sigma}_{j}_{s}" for sigma in ['p', 'm'] for j in range(1, n+1) for s in ['p', 'm']],
            "gamma_structure_constants": gamma_constants
        }
    }
    
    with open(f"data/C_{n}_gamma.json", "w") as f:
        json.dump(schema2, f, indent=2)

if __name__ == '__main__':
    for n in [1, 2, 3]:
        generate_gamma(n)
    print("Done generating Schema 2 JSON files")
