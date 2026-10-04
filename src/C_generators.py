import json
import os
from fractions import Fraction
from copy import deepcopy
from itertools import combinations

class Term:
    def __init__(self, coeff, words):
        self.coeff = Fraction(coeff)
        self.words = list(words) # list of strings

    def __repr__(self):
        return f"{self.coeff}*({','.join(self.words)})"

def normal_order(terms):
    # Order: a_1_p, a_1_m, b_1_p, b_1_m, b_2_p, b_2_m, ...
    def rank(w):
        if w == 'a_1_p': return 10
        if w == 'a_1_m': return 20
        if w.startswith('b_'):
            parts = w.split('_')
            idx = int(parts[1])
            is_m = parts[2] == 'm'
            return 100 + idx * 10 + (1 if is_m else 0)
        return 1000

    result = []
    stack = [Term(t.coeff, t.words) for t in terms]
    
    while stack:
        curr = stack.pop()
        if curr.coeff == 0:
            continue
            
        words = curr.words
        swapped = False
        for i in range(len(words)-1):
            w1 = words[i]
            w2 = words[i+1]
            if rank(w1) > rank(w2) or (w1 == w2 and w1.startswith('a_')):
                swapped = True
                # They are out of order or same fermion, swap or eliminate
                if w1 == 'a_1_m' and w2 == 'a_1_p':
                    # a_1_m a_1_p = 1 - a_1_p a_1_m
                    t1 = Term(curr.coeff, words[:i] + words[i+2:])
                    t2 = Term(-curr.coeff, words[:i] + ['a_1_p', 'a_1_m'] + words[i+2:])
                    stack.append(t1)
                    stack.append(t2)
                elif w1 == w2 and w1.startswith('a_'):
                    pass # term becomes 0
                elif w1.startswith('b_') and w2.startswith('b_') and w1.split('_')[1] == w2.split('_')[1] and w1.endswith('m') and w2.endswith('p'):
                    # b_i_m b_i_p = b_i_p b_i_m + 1
                    t1 = Term(curr.coeff, words[:i] + words[i+2:])
                    t2 = Term(curr.coeff, words[:i] + [w2, w1] + words[i+2:])
                    stack.append(t1)
                    stack.append(t2)
                else:
                    t_swap = Term(curr.coeff, words[:i] + [w2, w1] + words[i+2:])
                    stack.append(t_swap)
                break
        
        if not swapped:
            result.append(curr)
            
    # Collect like terms
    final_dict = {}
    for t in result:
        w_tuple = tuple(t.words)
        final_dict[w_tuple] = final_dict.get(w_tuple, Fraction(0)) + t.coeff
        
    return [Term(c, w) for w, c in final_dict.items() if c != 0]

def add_terms(t1, t2):
    return normal_order(t1 + t2)

def multiply_terms(list1, list2):
    res = []
    for t1 in list1:
        for t2 in list2:
            res.append(Term(t1.coeff * t2.coeff, t1.words + t2.words))
    return normal_order(res)

def scale_terms(terms, scalar):
    return normal_order([Term(t.coeff * Fraction(scalar), t.words) for t in terms])

def graded_commutator(X_terms, X_parity, Y_terms, Y_parity):
    XY = multiply_terms(X_terms, Y_terms)
    YX = multiply_terms(Y_terms, X_terms)
    
    sign = -1 if (X_parity == 1 and Y_parity == 1) else 1
    # [X, Y} = XY - (-1)^{p(X)p(Y)} YX => XY - sign * YX
    if sign == 1:
        minus_YX = scale_terms(YX, -1)
    else:
        minus_YX = scale_terms(YX, 1) # wait, if sign==-1, XY - (-YX) = XY + YX
    return normal_order(XY + minus_YX)

def generate_algebra(n):
    # Define generators
    gens = {}
    parities = {}
    
    # H_1
    gens['H_1'] = normal_order([Term(1, ['a_1_p', 'a_1_m']), Term(1, ['b_1_p', 'b_1_m'])])
    parities['H_1'] = 0
    
    # H_k for k=2..n
    for k in range(2, n+1):
        gens[f'H_{k}'] = normal_order([Term(1, [f'b_{k-1}_p', f'b_{k-1}_m']), Term(-1, [f'b_{k}_p', f'b_{k}_m'])])
        parities[f'H_{k}'] = 0
        
    # H_{n+1}
    gens[f'H_{n+1}'] = normal_order([Term(-1, [f'b_{n}_p', f'b_{n}_m']), Term(Fraction(-1,2), [])])
    parities[f'H_{n+1}'] = 0
    
    # Even roots (±2δ_k)
    for k in range(1, n+1):
        gens[f'E_2del{k}_p'] = normal_order([Term(Fraction(1,2), [f'b_{k}_p', f'b_{k}_p'])])
        parities[f'E_2del{k}_p'] = 0
        gens[f'E_2del{k}_m'] = normal_order([Term(Fraction(-1,2), [f'b_{k}_m', f'b_{k}_m'])]) # wait, equation says E_{-2d_n} = 1/2(b_n^-)^2. For k, is it 1/2 or -1/2? Let's use 1/2 for all! Wait, I01 says Frappat formula: E_{-2\delta_n} = 1/2(b_n^-)^2. B(0,n) formula: E_2del_m is -1/2 or 1/2? Let's use 1/2.
        gens[f'E_2del{k}_m'] = normal_order([Term(Fraction(1,2), [f'b_{k}_m', f'b_{k}_m'])])
        parities[f'E_2del{k}_m'] = 0

    # Even roots (±δ_k ± δ_l)
    for k in range(1, n+1):
        for l in range(k+1, n+1):
            gens[f'E_del{k}_del{l}_pp'] = normal_order([Term(1, [f'b_{k}_p', f'b_{l}_p'])])
            gens[f'E_del{k}_del{l}_mm'] = normal_order([Term(1, [f'b_{k}_m', f'b_{l}_m'])])
            gens[f'E_del{k}_del{l}_pm'] = normal_order([Term(1, [f'b_{k}_p', f'b_{l}_m'])])
            gens[f'E_del{k}_del{l}_mp'] = normal_order([Term(1, [f'b_{k}_m', f'b_{l}_p'])])
            parities[f'E_del{k}_del{l}_pp'] = 0
            parities[f'E_del{k}_del{l}_mm'] = 0
            parities[f'E_del{k}_del{l}_pm'] = 0
            parities[f'E_del{k}_del{l}_mp'] = 0

    # Odd roots (±ε ± δ_k)
    for k in range(1, n+1):
        gens[f'E_eps_del{k}_pp'] = normal_order([Term(1, ['a_1_p', f'b_{k}_p'])])
        gens[f'E_eps_del{k}_pm'] = normal_order([Term(1, ['a_1_p', f'b_{k}_m'])])
        gens[f'E_eps_del{k}_mp'] = normal_order([Term(1, ['a_1_m', f'b_{k}_p'])])
        gens[f'E_eps_del{k}_mm'] = normal_order([Term(1, ['a_1_m', f'b_{k}_m'])])
        parities[f'E_eps_del{k}_pp'] = 1
        parities[f'E_eps_del{k}_pm'] = 1
        parities[f'E_eps_del{k}_mp'] = 1
        parities[f'E_eps_del{k}_mm'] = 1
        
    # Basis ordering
    even_basis = []
    for k in range(1, n+2): even_basis.append(f'H_{k}')
    for k in range(1, n+1): even_basis.append(f'E_2del{k}_p')
    for k in range(1, n+1):
        for l in range(k+1, n+1): even_basis.append(f'E_del{k}_del{l}_pp')
    for k in range(1, n+1): even_basis.append(f'E_2del{k}_m')
    for k in range(1, n+1):
        for l in range(k+1, n+1): even_basis.append(f'E_del{k}_del{l}_mm')
    for k in range(1, n+1):
        for l in range(k+1, n+1):
            even_basis.append(f'E_del{k}_del{l}_pm')
            even_basis.append(f'E_del{k}_del{l}_mp')
            
    odd_basis = []
    for k in range(1, n+1):
        odd_basis.extend([f'E_eps_del{k}_pp', f'E_eps_del{k}_pm', f'E_eps_del{k}_mp', f'E_eps_del{k}_mm'])
        
    # Compute structure constants
    all_gens = odd_basis + even_basis
    sc = []
    
    def terms_to_gen_str(terms):
        if not terms: return None
        for name, gen_terms in gens.items():
            # Check if terms == gen_terms
            if len(terms) != len(gen_terms): continue
            
            t_dict = {tuple(t.words): t.coeff for t in terms}
            g_dict = {tuple(t.words): t.coeff for t in gen_terms}
            
            # Check linear dependence
            first_key = list(t_dict.keys())[0]
            if first_key not in g_dict: continue
            ratio = t_dict[first_key] / g_dict[first_key]
            
            match = True
            for k, v in t_dict.items():
                if k not in g_dict or g_dict[k] * ratio != v:
                    match = False
                    break
            if match:
                # also need to check g_dict has no extra keys
                if len(t_dict) == len(g_dict):
                    return name, ratio
        return None

    # Decompose commutator into basis
    for i, X in enumerate(all_gens):
        for j, Y in enumerate(all_gens):
            Z_terms = graded_commutator(gens[X], parities[X], gens[Y], parities[Y])
            if not Z_terms:
                continue
                
            # Z_terms could be a linear combination of generators
            # Try to decompose. Since generators are distinct monomials in oscillators,
            # this is simple.
            
            # Actually, H_k are linear combinations, but roots are single monomials!
            # Let's extract Cartans first.
            remaining = deepcopy(Z_terms)
            
            # Helper to subtract
            def sub_terms(t1, t2):
                return normal_order(t1 + scale_terms(t2, -1))

            decomposition = []
            
            # A bit tricky for Cartans because H_1 = a1+a1- + b1+b1-, H_k = b_{k-1}+ b_{k-1}- - b_k+b_k-.
            # But wait! Commutators of roots only produce Cartans when they are opposite roots!
            # Let's just find which generator matches the remaining terms.
            # In our basis, the Cartans have a1+a1-, bk+bk-.
            
            # This decomposition logic might be too simplistic for Cartans.
            # Let's write a proper solver for Cartans.
            # Cartans span the subspace of terms [a1+a1-, b1+b1-, b2+b2-, ..., 1]
            
            # To be robust, let's just use a dictionary for monomials to generators.
            # But H_k are not single monomials.
            
            # Let's identify the Cartan part.
            cartan_coeff = {}
            for t in remaining:
                if t.words == ['a_1_p', 'a_1_m']:
                    cartan_coeff['a'] = t.coeff
                elif len(t.words) == 2 and t.words[0].startswith('b_') and t.words[1].startswith('b_') and t.words[0].endswith('_p') and t.words[1].endswith('_m') and t.words[0][:-2] == t.words[1][:-2]:
                    cartan_coeff[t.words[0][:-2]] = t.coeff
                elif len(t.words) == 0:
                    cartan_coeff['1'] = t.coeff
            
            if cartan_coeff:
                # We need to express this in terms of H_1 ... H_{n+1}.
                # H_1 = a + b1
                # H_2 = b1 - b2
                # H_k = b_{k-1} - bk
                # H_{n+1} = -bn - 1/2
                # Wait, this is a basis.
                # Let's solve it.
                c = []
                # c_1 * H_1 + c_2 * H_2 ...
                # a coeff = c_1
                c_1 = cartan_coeff.get('a', Fraction(0))
                if c_1 != 0:
                    decomposition.append((str(c_1), 'H_1'))
                    remaining = sub_terms(remaining, scale_terms(gens['H_1'], c_1))
                
                # After H_1, b1_p b1_m has remaining coeff
                for k in range(2, n+1):
                    # b_{k-1} coeff comes from H_{k-1} (-1) and H_k (+1)
                    # So we need to match the current b_{k-1} coeff.
                    curr_b = next((t.coeff for t in remaining if t.words == [f'b_{k-1}_p', f'b_{k-1}_m']), Fraction(0))
                    if curr_b != 0:
                        c_k = curr_b # because H_k has +b_{k-1}
                        decomposition.append((str(c_k), f'H_{k}'))
                        remaining = sub_terms(remaining, scale_terms(gens[f'H_{k}'], c_k))
                        
                curr_bn = next((t.coeff for t in remaining if t.words == [f'b_{n}_p', f'b_{n}_m']), Fraction(0))
                if curr_bn != 0:
                    c_np1 = -curr_bn # H_{n+1} has -bn
                    decomposition.append((str(c_np1), f'H_{n+1}'))
                    remaining = sub_terms(remaining, scale_terms(gens[f'H_{n+1}'], c_np1))
                    
            # Now remaining should be only root vectors.
            if remaining:
                # Group into roots
                for r in all_gens:
                    if r.startswith('H_'): continue
                    g_terms = gens[r]
                    # Check if g_terms[0] is in remaining
                    first_word = tuple(g_terms[0].words)
                    for t in remaining:
                        if tuple(t.words) == first_word:
                            ratio = t.coeff / g_terms[0].coeff
                            decomposition.append((str(ratio), r))
                            remaining = sub_terms(remaining, scale_terms(g_terms, ratio))
                            break
                            
            if remaining:
                print(f"Failed to fully decompose [{X}, {Y}]: {remaining}")
                
            for coeff_str, Z in decomposition:
                sc.append({
                    "X": X,
                    "Y": Y,
                    "Z": Z,
                    "coeff": coeff_str,
                    "sign_rule": "graded"
                })

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1"
            },
            "dimension": {
                "total": 2*n**2 + 5*n + 1,
                "even": 2*n**2 + n + 1,
                "odd": 4*n
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair a_1^±"
            },
            "bosons": {
                "n": n,
                "labels": [f"b_{i}_p" for i in range(1, n+1)] + [f"b_{i}_m" for i in range(1, n+1)],
                "description": "Bosonic oscillators b_i^± with i=1,...,n"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations",
                "relation": "{a_1^-, a_1^+} = 1"
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0",
                    "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_1^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "description": "Odd central element"
            },
            "K": {
                "parity": 0,
                "description": "Even central element identified with scalar 1"
            }
        },
        "basis": {
            "even": even_basis,
            "odd": odd_basis,
            "ordering_convention": "PBW: κ < [odd] < [even]"
        },
        "parity": parities,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, b_1_p, b_1_m...",
            "realizations": {
                g: {
                    "standard_form": [{"words": t.words, "coeff": str(t.coeff)} for t in terms],
                    "parity": parities[g]
                }
                for g, terms in gens.items()
            }
        },
        "structure_constants": sc
    }
    
    with open(f"data/C_{n}_structure.json", "w") as f:
        json.dump(schema, f, indent=2)

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    generate_algebra(1)
    generate_algebra(2)
    generate_algebra(3)
    print("Done generating JSON schemas")
