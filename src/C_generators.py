import json
import os
from collections import defaultdict
from fractions import Fraction

class Term:
    def __init__(self, coeff, words):
        self.coeff = coeff
        self.words = tuple(words)
    def __repr__(self):
        return f"{self.coeff}*{self.words}"
    def __eq__(self, other):
        return self.coeff == other.coeff and self.words == other.words
    def __hash__(self):
        return hash((self.coeff, self.words))

def parity(w):
    return 1 if w.startswith('a') else 0

def sort_adjacent(words, i):
    w1, w2 = words[i], words[i+1]
    p1, p2 = parity(w1), parity(w2)
    sign = -1 if (p1 == 1 and p2 == 1) else 1
    
    if w1 == 'a_1_m' and w2 == 'a_1_p':
        return [(sign, (w2, w1)), (1, ())]
    elif w1.startswith('b_') and w1.endswith('_m') and w2.startswith('b_') and w2.endswith('_p'):
        idx1, idx2 = w1.split('_')[1], w2.split('_')[1]
        if idx1 == idx2:
            return [(sign, (w2, w1)), (1, ())]
    return [(sign, (w2, w1))]

def normal_order_term(coeff, words):
    terms = [(coeff, tuple(words))]
    final_terms = defaultdict(Fraction)
    
    while terms:
        c, w = terms.pop()
        changed = False
        for i in range(len(w)-1):
            w1, w2 = w[i], w[i+1]
            def rank(x):
                if x.endswith('_p'):
                    return 0, x
                else:
                    return 1, x
            
            if rank(w1) > rank(w2):
                changed = True
                res = sort_adjacent(w, i)
                for new_c, new_sub in res:
                    new_w = w[:i] + new_sub + w[i+2:]
                    terms.append((c * new_c, new_w))
                break
        if not changed:
            final_terms[w] += c
            
    return [(c, w) for w, c in final_terms.items() if c != 0]

def add_expr(expr1, expr2):
    res = defaultdict(Fraction)
    for c, w in expr1: res[w] += c
    for c, w in expr2: res[w] += c
    return [(c, w) for w, c in res.items() if c != 0]

def mult_expr(expr1, expr2):
    res = []
    for c1, w1 in expr1:
        for c2, w2 in expr2:
            res.extend(normal_order_term(c1 * c2, w1 + w2))
    d = defaultdict(Fraction)
    for c, w in res: d[w] += c
    return [(c, w) for w, c in d.items() if c != 0]

def get_parity(expr):
    if not expr: return 0
    c, w = expr[0]
    return sum(parity(x) for x in w) % 2

def supercommutator(expr1, expr2):
    p1 = get_parity(expr1)
    p2 = get_parity(expr2)
    term1 = mult_expr(expr1, expr2)
    term2 = mult_expr(expr2, expr1)
    sign = -1 if (p1 == 1 and p2 == 1) else 1
    # [X, Y} = X Y - (-1)^{p(X)p(Y)} Y X
    # wait, standard commutator is [X, Y} = XY - (-1)^{p1 p2} YX
    res = add_expr(term1, [( -sign * c, w) for c, w in term2])
    # Ignore constant terms (w == ()) since they belong to the center in the universal enveloping algebra but not in the Lie algebra.
    return [(c, w) for c, w in res if len(w) > 0]

def get_generators(n):
    gens = {}
    
    # Cartans
    gens["H_1"] = add_expr(normal_order_term(1, ("a_1_p", "a_1_m")), normal_order_term(1, ("b_1_p", "b_1_m")))
    for k in range(2, n+1):
        gens[f"H_{k}"] = add_expr(normal_order_term(1, (f"b_{k-1}_p", f"b_{k-1}_m")), normal_order_term(-1, (f"b_{k}_p", f"b_{k}_m")))
    gens[f"H_{n+1}"] = normal_order_term(-1, (f"b_{n}_p", f"b_{n}_m")) # -1/2 is constant, omitted
    
    # Even roots
    for k in range(1, n+1):
        gens[f"E_2del{k}_p"] = normal_order_term(Fraction(1, 2), (f"b_{k}_p", f"b_{k}_p"))
        gens[f"E_2del{k}_m"] = normal_order_term(Fraction(-1, 2) if False else Fraction(1, 2), (f"b_{k}_m", f"b_{k}_m")) # wait, E_{-2del_k} is 1/2(b_k^-)^2
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            gens[f"E_del{i}_del{j}_pp"] = normal_order_term(1, (f"b_{i}_p", f"b_{j}_p"))
            gens[f"E_del{i}_del{j}_mm"] = normal_order_term(1, (f"b_{i}_m", f"b_{j}_m"))
            gens[f"E_del{i}_del{j}_pm"] = normal_order_term(1, (f"b_{i}_p", f"b_{j}_m"))
            gens[f"E_del{i}_del{j}_mp"] = normal_order_term(1, (f"b_{i}_m", f"b_{j}_p"))
            
    # Odd roots
    for k in range(1, n+1):
        gens[f"E_eps1_del{k}_pp"] = normal_order_term(1, ("a_1_p", f"b_{k}_p"))
        gens[f"E_eps1_del{k}_pm"] = normal_order_term(1, ("a_1_p", f"b_{k}_m"))
        gens[f"E_eps1_del{k}_mp"] = normal_order_term(1, ("a_1_m", f"b_{k}_p"))
        gens[f"E_eps1_del{k}_mm"] = normal_order_term(1, ("a_1_m", f"b_{k}_m"))
        
    return gens

def get_basis_order(n):
    gens = get_generators(n)
    even = []
    odd = []
    for g, expr in gens.items():
        if get_parity(expr) == 0:
            even.append(g)
        else:
            odd.append(g)
    return sorted(odd) + sorted(even)

def expr_to_json(expr):
    res = []
    for c, w in expr:
        res.append({"words": list(w), "coeff": str(c)})
    return res

def generate_schema(n):
    gens = get_generators(n)
    order = get_basis_order(n)
    
    # Compute structure constants
    sc = []
    for i in range(len(order)):
        for j in range(len(order)):
            X = order[i]
            Y = order[j]
            comm = supercommutator(gens[X], gens[Y])
            if comm:
                # find expansion in basis
                # For quadratic polynomials, it must be a linear combination of generators
                # We can just match terms.
                rem = defaultdict(Fraction, ((w, c) for c, w in comm))
                for Z in order:
                    Z_expr = gens[Z]
                    if not Z_expr: continue
                    # heuristic: find coeff of first word of Z_expr in rem
                    Z_c, Z_w = Z_expr[0]
                    if Z_w in rem and rem[Z_w] != 0:
                        factor = rem[Z_w] / Z_c
                        # subtract factor * Z_expr
                        for ec, ew in Z_expr:
                            rem[ew] -= factor * ec
                            if rem[ew] == 0: del rem[ew]
                        sc.append({
                            "X": X,
                            "Y": Y,
                            "Z": Z,
                            "coeff": str(factor),
                            "sign_rule": "graded"
                        })
                        if not any(v != 0 for v in rem.values()): break

    even_keys = [k for k in order if get_parity(gens[k]) == 0]
    odd_keys = [k for k in order if get_parity(gens[k]) == 1]
    
    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "dimension": {
                "even": 2*n*n + n + 1,
                "odd": 4*n,
                "total": 2*n*n + 5*n + 1
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"]
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": [f"b_{k}_{s}" for k in range(1, n+1) for s in ["p", "m"]]
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "relation": "{a_1^-, a_1^+} = 1"
            },
            "bosonic_commutators": {
                "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"
            }
        },
        "central_elements": {
            "kappa": {"parity": 1},
            "K": {"parity": 0}
        },
        "basis": {
            "even": even_keys,
            "odd": odd_keys,
            "ordering_convention": "PBW: κ < [odd] < [even]"
        },
        "parity": {k: get_parity(gens[k]) for k in order},
        "generator_realization": {
            "realizations": {k: {"standard_form": expr_to_json(gens[k]), "parity": get_parity(gens[k])} for k in order}
        },
        "structure_constants": sc,
        "metadata": {
            "generated_by": "C_generators.py",
            "references": ["Frappat et al. (2000)"]
        }
    }
    return schema

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        with open(f"data/C_{n}_structure.json", "w") as f:
            json.dump(generate_schema(n), f, indent=2)
    print("Generated Schema JSONs in data/")
