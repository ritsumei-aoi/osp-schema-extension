import json
import sympy
import os

class Poly:
    def __init__(self, terms=None):
        self.terms = {}
        if terms:
            for w, c in terms.items():
                if abs(c) > 1e-9:
                    drop = False
                    for i in range(len(w)-1):
                        if w[i] == w[i+1] and 'a_1' in w[i]:
                            drop = True
                            break
                    if not drop:
                        self.terms[w] = self.terms.get(w, 0) + c

    def mul(self, other):
        res = {}
        for w1, c1 in self.terms.items():
            for w2, c2 in other.terms.items():
                w = w1 + w2
                res[w] = res.get(w, 0) + c1 * c2
        return Poly(res).normal_order()

    def normal_order(self):
        order = {'a_1_p': 1, 'a_1_m': 2}
        for i in range(1, 10):
            order[f'b_{i}_p'] = 2 + 2*i - 1
            order[f'b_{i}_m'] = 2 + 2*i

        res = dict(self.terms)
        changed = True
        while changed:
            changed = False
            new_res = {}
            for w, c in res.items():
                if abs(c) < 1e-9: continue
                swapped = False
                for i in range(len(w)-1):
                    if order[w[i]] > order[w[i+1]]:
                        o1, o2 = w[i], w[i+1]
                        w_swapped = w[:i] + (o2, o1) + w[i+2:]
                        if o1 == 'a_1_m' and o2 == 'a_1_p':
                            w_drop = w[:i] + w[i+2:]
                            new_res[w_drop] = new_res.get(w_drop, 0) + c
                            new_res[w_swapped] = new_res.get(w_swapped, 0) - c
                        elif o1.startswith('b_') and o1.endswith('_m') and o2.startswith('b_') and o2.endswith('_p') and o1[2:-2] == o2[2:-2]:
                            w_drop = w[:i] + w[i+2:]
                            new_res[w_drop] = new_res.get(w_drop, 0) + c
                            new_res[w_swapped] = new_res.get(w_swapped, 0) + c
                        else:
                            p1 = 1 if 'a_1' in o1 else 0
                            p2 = 1 if 'a_1' in o2 else 0
                            sign = -1 if (p1 == 1 and p2 == 1) else 1
                            if o1 == o2 and p1 == 1:
                                pass # drops
                            else:
                                new_res[w_swapped] = new_res.get(w_swapped, 0) + sign * c
                        swapped = True
                        changed = True
                        break
                    elif w[i] == w[i+1] and 'a_1' in w[i]:
                        swapped = True
                        changed = True
                        break
                if not swapped:
                    new_res[w] = new_res.get(w, 0) + c
            res = new_res
            
        final_res = {}
        for w, c in res.items():
            if abs(c) > 1e-9: final_res[w] = c
        return Poly(final_res)

def p(poly):
    for w, c in poly.terms.items():
        if abs(c) > 1e-9:
            return sum(1 for x in w if 'a_1' in x) % 2
    return 0

def bracket(X, Y):
    XY = X.mul(Y)
    YX = Y.mul(X)
    sign = -1 if (p(X) == 1 and p(Y) == 1) else 1
    res = {}
    for w, c in XY.terms.items():
        res[w] = res.get(w, 0) + c
    for w, c in YX.terms.items():
        res[w] = res.get(w, 0) - sign * c
    return Poly(res).normal_order()

def get_generators(n):
    gens = {}
    gens['H_1'] = Poly({('a_1_p', 'a_1_m'): 1, ('b_1_p', 'b_1_m'): 1})
    for k in range(2, n+1):
        gens[f'H_{k}'] = Poly({(f'b_{k-1}_p', f'b_{k-1}_m'): 1, (f'b_{k}_p', f'b_{k}_m'): -1})
    gens[f'H_{n+1}'] = Poly({(f'b_{n}_p', f'b_{n}_m'): -1, tuple(): -0.5})

    for k in range(1, n+1):
        gens[f'E_2del{k}_p'] = Poly({(f'b_{k}_p', f'b_{k}_p'): 1})
        gens[f'E_2del{k}_m'] = Poly({(f'b_{k}_m', f'b_{k}_m'): 1})

    for i in range(1, n+1):
        for j in range(i+1, n+1):
            gens[f'E_del{i}_del{j}_pp'] = Poly({(f'b_{i}_p', f'b_{j}_p'): 1})
            gens[f'E_del{i}_del{j}_mm'] = Poly({(f'b_{i}_m', f'b_{j}_m'): 1})
            gens[f'E_del{i}_del{j}_pm'] = Poly({(f'b_{i}_p', f'b_{j}_m'): 1})
            gens[f'E_del{i}_del{j}_mp'] = Poly({(f'b_{i}_m', f'b_{j}_p'): 1})

    for k in range(1, n+1):
        gens[f'E_eps1_del{k}_pp'] = Poly({('a_1_p', f'b_{k}_p'): 1})
        gens[f'E_eps1_del{k}_pm'] = Poly({('a_1_p', f'b_{k}_m'): 1})
        gens[f'E_eps1_del{k}_mp'] = Poly({('a_1_m', f'b_{k}_p'): 1})
        gens[f'E_eps1_del{k}_mm'] = Poly({('a_1_m', f'b_{k}_m'): 1})

    ordered_odd = []
    for k in range(1, n+1): ordered_odd.append(f'E_eps1_del{k}_pp')
    for k in range(1, n+1): ordered_odd.append(f'E_eps1_del{k}_pm')
    for k in range(1, n+1): ordered_odd.append(f'E_eps1_del{k}_mp')
    for k in range(1, n+1): ordered_odd.append(f'E_eps1_del{k}_mm')
    
    ordered_even_cartan = [f'H_{k}' for k in range(1, n+2)]
    
    ordered_even_pos = []
    for k in range(1, n+1): ordered_even_pos.append(f'E_2del{k}_p')
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            ordered_even_pos.extend([f'E_del{i}_del{j}_pp', f'E_del{i}_del{j}_pm'])
            
    ordered_even_neg = []
    for k in range(1, n+1): ordered_even_neg.append(f'E_2del{k}_m')
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            ordered_even_neg.extend([f'E_del{i}_del{j}_mp', f'E_del{i}_del{j}_mm'])

    pbw_order = ordered_odd + ordered_even_cartan + ordered_even_pos + ordered_even_neg
    return gens, pbw_order

def decompose(poly, gens, pbw):
    vars = pbw
    all_words = set(poly.terms.keys())
    for Z in gens.values():
        all_words.update(Z.terms.keys())
    all_words = list(all_words)
    word_to_idx = {w: i for i, w in enumerate(all_words)}
    
    M = sympy.zeros(len(all_words), len(vars))
    for j, Z_name in enumerate(vars):
        Z = gens[Z_name]
        for w, c in Z.terms.items():
            M[word_to_idx[w], j] = sympy.Rational(str(c)) if isinstance(c, float) else sympy.Rational(c)
            
    v = sympy.zeros(len(all_words), 1)
    for w, c in poly.terms.items():
        v[word_to_idx[w], 0] = sympy.Rational(str(c)) if isinstance(c, float) else sympy.Rational(c)
        
    res = sympy.linsolve((M, v), sympy.symbols('x0:%d' % len(vars)))
    if not res:
        return []
    x = list(list(res)[0])
    
    result = []
    for j, Z_name in enumerate(vars):
        val = x[j]
        if val != 0:
            if val.is_integer:
                sval = str(int(val))
            else:
                sval = f"{val.p}/{val.q}"
            result.append((sval, Z_name))
    return result

def get_structure_constants(n):
    gens, pbw = get_generators(n)
    sc = []
    for i, X_name in enumerate(pbw):
        for j, Y_name in enumerate(pbw):
            X = gens[X_name]
            Y = gens[Y_name]
            res = bracket(X, Y)
            if not res.terms:
                continue
            
            dec = decompose(res, gens, pbw)
            for coeff, Z_name in dec:
                sc.append({
                    "X": X_name,
                    "Y": Y_name,
                    "Z": Z_name,
                    "coeff": coeff,
                    "sign_rule": "graded"
                })
    return sc

def generate_json(n, output_dir="data"):
    gens, pbw = get_generators(n)
    sc = get_structure_constants(n)
    
    dim_even = 2*n**2 + n + 1
    dim_odd = 4*n
    dim_total = dim_even + dim_odd
    
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
                "total": dim_total,
                "even": dim_even,
                "odd": dim_odd
            }
        },
        "oscillator_generators": {
            "fermions": {
                "count": 2,
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair a_1^± satisfying CAR."
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": [f"b_{i}_{sign}" for i in range(1, n+1) for sign in ("p", "m")],
                "description": "Bosonic oscillators b_i^± with i=1,...,n"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for the standard fermionic pair.",
                "relations": {
                    "same_type": "{a_1^±, a_1^±} = 0",
                    "conjugate_pair": "{a_1^-, a_1^+} = 1"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
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
                "relation": "kappa^2 = 0",
                "description": "Formal odd central nilpotent element defining the inhomogeneous deformation."
            },
            "K": {
                "parity": 0,
                "relation": "K = 1",
                "description": "Even central element identified with the scalar identity."
            }
        },
        "basis": {
            "even": [g for g in pbw if p(gens[g]) == 0],
            "odd": [g for g in pbw if p(gens[g]) == 1],
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded)"
        },
        "parity": {g: p(gens[g]) for g in pbw},
        "structure_constants": sc
    }
    
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"C_{n}_structure.json")
    with open(file_path, "w") as f:
        json.dump(schema, f, indent=2)
    return file_path

if __name__ == "__main__":
    for n in [1, 2, 3]:
        print(f"Generating schema for C({n+1})...")
        generate_json(n)
