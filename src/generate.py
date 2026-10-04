import json
import sympy as sp
import itertools

def get_p(v): return 1 if v.startswith('a_') else 0

def omega(u, v):
    if u == 'a_1_m' and v == 'a_1_p': return 1
    if u == 'a_1_p' and v == 'a_1_m': return 1
    if u.startswith('b_') and v.startswith('b_'):
        u_idx, u_s = u.split('_')[1:3]
        v_idx, v_s = v.split('_')[1:3]
        if u_idx == v_idx:
            if u_s == 'm' and v_s == 'p': return 1
            if u_s == 'p' and v_s == 'm': return -1
    return 0

def normal_order_word_v2(w):
    def rank(v):
        if v == 'a_1_p': return 0
        if v == 'a_1_m': return 1
        return 2 * int(v.split('_')[1]) + (0 if v.split('_')[2]=='p' else 1)
    
    terms = {(tuple(w),): 1.0}
    final_terms = {}
    
    while terms:
        new_terms = {}
        for (word,), coeff in terms.items():
            word = list(word)
            swapped = False
            for i in range(len(word)-1):
                if rank(word[i]) > rank(word[i+1]):
                    u, v = word[i], word[i+1]
                    pu, pv = get_p(u), get_p(v)
                    om = omega(u, v)
                    
                    if pu == 1 and pv == 1:
                        word[i], word[i+1] = v, u
                        new_terms[(tuple(word),)] = new_terms.get((tuple(word),), 0) - coeff
                        if om != 0:
                            new_w = word[:i] + word[i+2:]
                            new_terms[(tuple(new_w),)] = new_terms.get((tuple(new_w),), 0) + coeff * om
                    elif pu == 0 and pv == 0:
                        word[i], word[i+1] = v, u
                        new_terms[(tuple(word),)] = new_terms.get((tuple(word),), 0) + coeff
                        if om != 0:
                            new_w = word[:i] + word[i+2:]
                            new_terms[(tuple(new_w),)] = new_terms.get((tuple(new_w),), 0) + coeff * om
                    else:
                        word[i], word[i+1] = v, u
                        new_terms[(tuple(word),)] = new_terms.get((tuple(word),), 0) + coeff
                    
                    swapped = True
                    break
            if not swapped:
                final_terms[tuple(word)] = final_terms.get(tuple(word), 0) + coeff
        terms = {k: v for k, v in new_terms.items() if abs(v) > 1e-9}
        
    return [(w, c) for w, c in final_terms.items() if abs(c) > 1e-9]

def multiply(t1, t2):
    res = {}
    for w1, c1 in t1:
        for w2, c2 in t2:
            for nw, nc in normal_order_word_v2(w1 + w2):
                res[nw] = res.get(nw, 0) + c1 * c2 * nc
    return [(w, c) for w, c in res.items() if abs(c) > 1e-9]

def format_c(c):
    if abs(c - int(c)) < 1e-9: return str(int(c))
    if abs(c - 0.5) < 1e-9: return "1/2"
    if abs(c + 0.5) < 1e-9: return "-1/2"
    if abs(c - 1.5) < 1e-9: return "3/2"
    if abs(c + 1.5) < 1e-9: return "-3/2"
    if abs(c - 2.0) < 1e-9: return "2"
    if abs(c + 2.0) < 1e-9: return "-2"
    return str(c)

def build_schema(n):
    even_dim = 2*n**2 + n + 1
    odd_dim = 4*n
    total_dim = even_dim + odd_dim
    
    even = [f"H_{k}" for k in range(1, n+2)]
    even += [f"E_2del{k}_p" for k in range(1, n+1)]
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            even.append(f"E_del{i}_del{j}_pp")
    even += [f"E_2del{k}_m" for k in range(1, n+1)]
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            even.append(f"E_del{i}_del{j}_mm")
            even.append(f"E_del{i}_del{j}_pm")
            even.append(f"E_del{i}_del{j}_mp")
            
    odd = []
    for k in range(1, n+1):
        odd.append(f"E_eps_del{k}_pp")
        odd.append(f"E_eps_del{k}_pm")
        odd.append(f"E_eps_del{k}_mp")
        odd.append(f"E_eps_del{k}_mm")
        
    parity = {g: 0 for g in even}
    for g in odd: parity[g] = 1
        
    realizations = {}
    realizations["H_1"] = {
        "standard_form": [
            {"words": ["a_1_p", "a_1_m"], "coeff": "1"},
            {"words": ["b_1_p", "b_1_m"], "coeff": "1"}
        ],
        "frappat_form": "a_1^+ a_1^- + b_1^+ b_1^-", "parity": 0
    }
    for k in range(2, n+1):
        realizations[f"H_{k}"] = {
            "standard_form": [
                {"words": [f"b_{k-1}_p", f"b_{k-1}_m"], "coeff": "1"},
                {"words": [f"b_{k}_p", f"b_{k}_m"], "coeff": "-1"}
            ],
            "frappat_form": f"b_{k-1}^+ b_{k-1}^- - b_{k}^+ b_{k}^-", "parity": 0
        }
    realizations[f"H_{n+1}"] = {
        "standard_form": [
            {"words": [f"b_{n}_p", f"b_{n}_m"], "coeff": "-1"},
            {"words": [], "coeff": "-1/2"}
        ],
        "frappat_form": f"-b_{n}^+ b_{n}^- - 1/2", "parity": 0
    }
    
    for k in range(1, n+1):
        realizations[f"E_2del{k}_p"] = {
            "standard_form": [{"words": [f"b_{k}_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^+)^2", "parity": 0
        }
        realizations[f"E_2del{k}_m"] = {
            "standard_form": [{"words": [f"b_{k}_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"(b_{k}^-)^2", "parity": 0
        }
        realizations[f"E_eps_del{k}_pp"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^+", "parity": 1
        }
        realizations[f"E_eps_del{k}_pm"] = {
            "standard_form": [{"words": ["a_1_p", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^+ b_{k}^-", "parity": 1
        }
        realizations[f"E_eps_del{k}_mp"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_p"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^+", "parity": 1
        }
        realizations[f"E_eps_del{k}_mm"] = {
            "standard_form": [{"words": ["a_1_m", f"b_{k}_m"], "coeff": "1"}],
            "frappat_form": f"a_1^- b_{k}^-", "parity": 1
        }
        
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            realizations[f"E_del{i}_del{j}_pp"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^+", "parity": 0
            }
            realizations[f"E_del{i}_del{j}_mm"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^-", "parity": 0
            }
            realizations[f"E_del{i}_del{j}_pm"] = {
                "standard_form": [{"words": [f"b_{i}_p", f"b_{j}_m"], "coeff": "1"}],
                "frappat_form": f"b_{i}^+ b_{j}^-", "parity": 0
            }
            realizations[f"E_del{i}_del{j}_mp"] = {
                "standard_form": [{"words": [f"b_{i}_m", f"b_{j}_p"], "coeff": "1"}],
                "frappat_form": f"b_{i}^- b_{j}^+", "parity": 0
            }

    all_gen = even + odd
    parsed = {}
    for g in all_gen:
        terms = []
        for term in realizations[g]['standard_form']:
            c = float(eval(term['coeff'])) if '/' in term['coeff'] else float(term['coeff'])
            w = tuple(term['words'])
            terms.append((w, c))
        res_t = {}
        for w, c in terms:
            for nw, nc in normal_order_word_v2(w):
                res_t[nw] = res_t.get(nw, 0) + c * nc
        parsed[g] = [(w, c) for w, c in res_t.items() if abs(c) > 1e-9]

    brackets_out = []
    for i, X in enumerate(all_gen):
        for j in range(i, len(all_gen)):
            Y = all_gen[j]
            pX, pY = parity[X], parity[Y]
            XY = multiply(parsed[X], parsed[Y])
            YX = multiply(parsed[Y], parsed[X])
            sign = -1 if (pX == 1 and pY == 1) else 1
            comm = {}
            for w, c in XY: comm[w] = comm.get(w, 0) + c
            for w, c in YX: comm[w] = comm.get(w, 0) - sign * c
            comm = {w: c for w, c in comm.items() if abs(c) > 1e-9}
            if not comm: continue
            
            words_in_eq = list(set(list(comm.keys()) + [w for g in all_gen for w, c in parsed[g]]))
            M = sp.Matrix([[next((c for w_, c in parsed[g] if w_ == word), 0) for g in all_gen] for word in words_in_eq])
            b = sp.Matrix([[comm.get(word, 0)] for word in words_in_eq])
            
            x = M.pinv() * b
            
            for k, coeff in enumerate(x):
                c = float(coeff)
                if abs(c) > 1e-9:
                    Z = all_gen[k]
                    brackets_out.append({
                        "X": X, "Y": Y, "Z": Z, "coeff": format_c(c), "sign_rule": "graded"
                    })

    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
            "alternative_notation": {"osp": f"osp(2|{2*n})", "dimension_formula": "osp(2m|2n) with m=1"},
            "dimension": {"total": total_dim, "even": even_dim, "odd": odd_dim}
        },
        "oscillator_generators": {
            "fermions": {"m": 1, "labels": ["a_1_p", "a_1_m"], "description": "Standard fermionic pair a_1^±"},
            "bosons": {"count": 2*n, "n": n, "labels": [f"b_{k}_{s}" for k in range(1, n+1) for s in ["p", "m"]], "description": "Bosonic oscillators b_i^± with i=1,...,n"}
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {"description": "Canonical anticommutation relations for fermionic pair (CAR)", "relation": "{a_1^-, a_1^+} = 1, {a_1^±, a_1^±} = 0"},
            "bosonic_commutators": {"description": "Canonical commutation relations for bosonic oscillators (CCR)", "relations": {"same_type": "[b_i^±, b_j^±] = 0 for all i, j", "conjugate_pair": "[b_i^-, b_j^+] = δ_{ij}"}},
            "mixed_commutators": {"boson_fermion": "[b_i^±, a_1^±] = 0"}
        },
        "central_elements": {
            "kappa": {"parity": 1, "relation": "kappa^2 = 0", "description": "Odd nilpotent central extension element"},
            "K": {"parity": 0, "description": "Even central identity element (usually set to 1)"}
        },
        "basis": {"even": even, "odd": odd, "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"},
        "parity": parity,
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, " + ", ".join([f"b_{k}_{s}" for k in range(1, n+1) for s in ["p", "m"]]),
            "realizations": realizations
        },
        "structure_constants": brackets_out,
        "metadata": {"generated_by": "generate.py", "generation_date": "2026-10-05", "references": ["Frappat et al. (2000)"]}
    }
    
    with open(f"data/C_{n}_structure.json", "w") as f:
        json.dump(schema, f, indent=2)

if __name__ == "__main__":
    for n in [1, 2, 3]:
        build_schema(n)
        print(f"Generated data/C_{n}_structure.json")
