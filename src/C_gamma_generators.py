import json
import sympy
import os
from fractions import Fraction

class PolyGamma:
    def __init__(self, terms0=None, terms1=None):
        self.terms0 = {}
        self.terms1 = {}
        if terms0:
            for w, c in terms0.items():
                if abs(c) > 1e-9:
                    drop = False
                    for i in range(len(w)-1):
                        if w[i] == w[i+1] and 'a_1' in w[i]:
                            drop = True
                            break
                    if not drop:
                        self.terms0[w] = self.terms0.get(w, 0) + c
        if terms1:
            for w, expr in terms1.items():
                if expr != 0:
                    drop = False
                    for i in range(len(w)-1):
                        if w[i] == w[i+1] and 'a_1' in w[i]:
                            drop = True
                            break
                    if not drop:
                        self.terms1[w] = self.terms1.get(w, 0) + expr

    def mul(self, other):
        res0 = {}
        res1 = {}
        for w1, c1 in self.terms0.items():
            for w2, c2 in other.terms0.items():
                w = w1 + w2
                res0[w] = res0.get(w, 0) + c1 * c2
                
        for w1, c1 in self.terms0.items():
            for w2, expr2 in other.terms1.items():
                w = w1 + w2
                res1[w] = res1.get(w, 0) + c1 * expr2
                
        for w1, expr1 in self.terms1.items():
            for w2, c2 in other.terms0.items():
                w = w1 + w2
                res1[w] = res1.get(w, 0) + expr1 * c2
        return PolyGamma(res0, res1).normal_order()

    def normal_order(self):
        order = {'a_1_p': 1, 'a_1_m': 2}
        for i in range(1, 10):
            order[f'b_{i}_p'] = 2 + 2*i - 1
            order[f'b_{i}_m'] = 2 + 2*i

        res0 = dict(self.terms0)
        res1 = dict(self.terms1)
        
        changed = True
        while changed:
            changed = False
            new_res0 = {}
            new_res1 = dict(res1)
            
            for w, c in res0.items():
                if abs(c) < 1e-9: continue
                swapped = False
                for i in range(len(w)-1):
                    if order[w[i]] > order[w[i+1]]:
                        o1, o2 = w[i], w[i+1]
                        w_swapped = w[:i] + (o2, o1) + w[i+2:]
                        
                        if o1 == 'a_1_m' and o2 == 'a_1_p':
                            w_drop = w[:i] + w[i+2:]
                            new_res0[w_drop] = new_res0.get(w_drop, 0) + c
                            new_res0[w_swapped] = new_res0.get(w_swapped, 0) - c
                        elif o1.startswith('b_') and o1.endswith('_m') and o2.startswith('b_') and o2.endswith('_p') and o1[2:-2] == o2[2:-2]:
                            w_drop = w[:i] + w[i+2:]
                            new_res0[w_drop] = new_res0.get(w_drop, 0) + c
                            new_res0[w_swapped] = new_res0.get(w_swapped, 0) + c
                        elif o1.startswith('b_') and o2.startswith('a_1'):
                            # [o1, o2] = - gb_o2_o1 * kappa
                            # o1 o2 = o2 o1 - gb_o2_o1 * kappa
                            new_res0[w_swapped] = new_res0.get(w_swapped, 0) + c
                            w_drop = w[:i] + w[i+2:]
                            o2_name = o2.replace('_', '')
                            o1_name = o1.replace('_', '')
                            gb_sym = sympy.Symbol(f"gb_{o2_name}_{o1_name}")
                            new_res1[w_drop] = new_res1.get(w_drop, 0) - c * gb_sym
                        else:
                            p1 = 1 if 'a_1' in o1 else 0
                            p2 = 1 if 'a_1' in o2 else 0
                            sign = -1 if (p1 == 1 and p2 == 1) else 1
                            if o1 == o2 and p1 == 1:
                                pass
                            else:
                                new_res0[w_swapped] = new_res0.get(w_swapped, 0) + sign * c
                        swapped = True
                        changed = True
                        break
                    elif w[i] == w[i+1] and 'a_1' in w[i]:
                        swapped = True
                        changed = True
                        break
                if not swapped:
                    new_res0[w] = new_res0.get(w, 0) + c
            res0 = new_res0
            res1 = new_res1
            
        changed = True
        while changed:
            changed = False
            new_res1 = {}
            for w, expr in res1.items():
                if expr == 0: continue
                swapped = False
                for i in range(len(w)-1):
                    if order[w[i]] > order[w[i+1]]:
                        o1, o2 = w[i], w[i+1]
                        w_swapped = w[:i] + (o2, o1) + w[i+2:]
                        
                        if o1 == 'a_1_m' and o2 == 'a_1_p':
                            w_drop = w[:i] + w[i+2:]
                            new_res1[w_drop] = new_res1.get(w_drop, 0) + expr
                            new_res1[w_swapped] = new_res1.get(w_swapped, 0) - expr
                        elif o1.startswith('b_') and o1.endswith('_m') and o2.startswith('b_') and o2.endswith('_p') and o1[2:-2] == o2[2:-2]:
                            w_drop = w[:i] + w[i+2:]
                            new_res1[w_drop] = new_res1.get(w_drop, 0) + expr
                            new_res1[w_swapped] = new_res1.get(w_swapped, 0) + expr
                        elif o1.startswith('b_') and o2.startswith('a_1'):
                            new_res1[w_swapped] = new_res1.get(w_swapped, 0) + expr
                        else:
                            p1 = 1 if 'a_1' in o1 else 0
                            p2 = 1 if 'a_1' in o2 else 0
                            sign = -1 if (p1 == 1 and p2 == 1) else 1
                            if o1 == o2 and p1 == 1:
                                pass
                            else:
                                new_res1[w_swapped] = new_res1.get(w_swapped, 0) + sign * expr
                        swapped = True
                        changed = True
                        break
                    elif w[i] == w[i+1] and 'a_1' in w[i]:
                        swapped = True
                        changed = True
                        break
                if not swapped:
                    new_res1[w] = new_res1.get(w, 0) + expr
            res1 = new_res1
            
        final_res0 = {w: c for w, c in res0.items() if abs(c) > 1e-9}
        final_res1 = {w: e for w, e in res1.items() if e != 0}
        return PolyGamma(final_res0, final_res1)

def p(poly):
    for w, c in poly.terms0.items():
        if abs(c) > 1e-9:
            return sum(1 for x in w if 'a_1' in x) % 2
    return 0

def bracket_gamma(X, Y):
    XY = X.mul(Y)
    YX = Y.mul(X)
    sign = -1 if (p(X) == 1 and p(Y) == 1) else 1
    
    res1 = {}
    for w, expr in XY.terms1.items():
        res1[w] = res1.get(w, 0) + expr
    for w, expr in YX.terms1.items():
        res1[w] = res1.get(w, 0) - sign * expr
        
    res0 = {}
    for w, c in XY.terms0.items():
        res0[w] = res0.get(w, 0) + c
    for w, c in YX.terms0.items():
        res0[w] = res0.get(w, 0) - sign * c
        
    return PolyGamma(res0, res1).normal_order()

def get_generators(n):
    gens = {}
    gens['H_1'] = PolyGamma({('a_1_p', 'a_1_m'): 1, ('b_1_p', 'b_1_m'): 1})
    for k in range(2, n+1):
        gens[f'H_{k}'] = PolyGamma({(f'b_{k-1}_p', f'b_{k-1}_m'): 1, (f'b_{k}_p', f'b_{k}_m'): -1})
    gens[f'H_{n+1}'] = PolyGamma({(f'b_{n}_p', f'b_{n}_m'): -1, tuple(): -0.5})

    for k in range(1, n+1):
        gens[f'E_2del{k}_p'] = PolyGamma({(f'b_{k}_p', f'b_{k}_p'): 1})
        gens[f'E_2del{k}_m'] = PolyGamma({(f'b_{k}_m', f'b_{k}_m'): 1})

    for i in range(1, n+1):
        for j in range(i+1, n+1):
            gens[f'E_del{i}_del{j}_pp'] = PolyGamma({(f'b_{i}_p', f'b_{j}_p'): 1})
            gens[f'E_del{i}_del{j}_mm'] = PolyGamma({(f'b_{i}_m', f'b_{j}_m'): 1})
            gens[f'E_del{i}_del{j}_pm'] = PolyGamma({(f'b_{i}_p', f'b_{j}_m'): 1})
            gens[f'E_del{i}_del{j}_mp'] = PolyGamma({(f'b_{i}_m', f'b_{j}_p'): 1})

    for k in range(1, n+1):
        gens[f'E_eps1_del{k}_pp'] = PolyGamma({('a_1_p', f'b_{k}_p'): 1})
        gens[f'E_eps1_del{k}_pm'] = PolyGamma({('a_1_p', f'b_{k}_m'): 1})
        gens[f'E_eps1_del{k}_mp'] = PolyGamma({('a_1_m', f'b_{k}_p'): 1})
        gens[f'E_eps1_del{k}_mm'] = PolyGamma({('a_1_m', f'b_{k}_m'): 1})

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
    
    # Add K for gamma decomposition
    gens['K'] = PolyGamma({tuple(): 1})
    pbw_order.append('K')
    
    return gens, pbw_order

def decompose_gamma(terms1, gens, pbw):
    vars = pbw
    all_words = set(terms1.keys())
    for Z in gens.values():
        all_words.update(Z.terms0.keys())
    all_words = list(all_words)
    word_to_idx = {w: i for i, w in enumerate(all_words)}
    
    M = sympy.zeros(len(all_words), len(vars))
    for j, Z_name in enumerate(vars):
        Z = gens[Z_name]
        for w, c in Z.terms0.items():
            M[word_to_idx[w], j] = sympy.Rational(str(c)) if isinstance(c, float) else sympy.Rational(c)
            
    v = sympy.zeros(len(all_words), 1)
    for w, expr in terms1.items():
        v[word_to_idx[w], 0] = expr
        
    res = sympy.linsolve((M, v), sympy.symbols('x0:%d' % len(vars)))
    if not res:
        return []
    x = list(list(res)[0])
    
    result = []
    for j, Z_name in enumerate(vars):
        val = x[j]
        if val != 0:
            result.append((str(sympy.expand(val)), Z_name))
    return result

def get_gamma_constants(n):
    gens, pbw = get_generators(n)
    gamma_matrix = []
    for i, X_name in enumerate(pbw):
        for j, Y_name in enumerate(pbw):
            X = gens[X_name]
            Y = gens[Y_name]
            res = bracket_gamma(X, Y)
            if not res.terms1:
                continue
            
            dec = decompose_gamma(res.terms1, gens, pbw)
            if not dec:
                print(f"Warning: Could not decompose [{X_name}, {Y_name}]_gamma = {res.terms1}")
            for coeff_expr, Z_name in dec:
                # To enforce Option B, we just log all pairs that are non-zero.
                # Because of anti-symmetry [X,Y] = -(-1) [Y,X], if X!=Y or p(X)=1, we'll get both stored.
                gamma_matrix.append({
                    "X": X_name,
                    "Y": Y_name,
                    "Z": Z_name,
                    "gamma_coeff": coeff_expr
                })
    return gamma_matrix

def generate_schema2(n, output_dir="data"):
    gens, pbw = get_generators(n)
    gamma_matrix = get_gamma_constants(n)
    
    gb_matrix = {
        "a_1_p": [f"gb_a1p_b{i}p" for i in range(1, n+1)] + [f"gb_a1p_b{i}m" for i in range(1, n+1)],
        "a_1_m": [f"gb_a1m_b{i}p" for i in range(1, n+1)] + [f"gb_a1m_b{i}m" for i in range(1, n+1)]
    }
    # Rearrange to match description: b1p, b1m, b2p, b2m...
    gb_matrix["a_1_p"] = []
    gb_matrix["a_1_m"] = []
    for i in range(1, n+1):
        gb_matrix["a_1_p"].extend([f"gb_a1p_b{i}p", f"gb_a1p_b{i}m"])
        gb_matrix["a_1_m"].extend([f"gb_a1m_b{i}p", f"gb_a1m_b{i}m"])

    schema2 = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})"
        },
        "inhomogeneous_deformation": {
            "exchange_relation": "[b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa",
            "gb_matrix": gb_matrix,
            "gamma_matrix": gamma_matrix
        }
    }
    
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"C_{n}_gamma.json")
    with open(file_path, "w") as f:
        json.dump(schema2, f, indent=2)
    return file_path

if __name__ == "__main__":
    for n in [1, 2, 3]:
        print(f"Generating Schema 2 for C({n+1})...")
        generate_schema2(n)
