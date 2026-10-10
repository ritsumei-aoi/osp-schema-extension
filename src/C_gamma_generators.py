import os
import json
import sys

def p(op):
    return 1 if op in ('a+', 'a-') else 0

def add_coefs(c1, c2, multiplier=1.0):
    if isinstance(c1, dict) or isinstance(c2, dict):
        res = dict(c1) if isinstance(c1, dict) else {'1': c1} if c1 != 0 else {}
        c2_dict = c2 if isinstance(c2, dict) else {'1': c2} if c2 != 0 else {}
        for k, v in c2_dict.items():
            res[k] = res.get(k, 0.0) + v * multiplier
            if abs(res[k]) < 1e-9:
                del res[k]
        return res
    else:
        return c1 + c2 * multiplier

def mult_coef(c, multiplier):
    if multiplier == 0:
        return {} if isinstance(c, dict) else 0.0
    if isinstance(c, dict):
        return {k: v * multiplier for k, v in c.items() if v != 0}
    return c * multiplier

class Term:
    def __init__(self, coef, ops, has_kappa=False):
        self.coef = coef
        self.ops = tuple(ops)
        self.has_kappa = has_kappa

def sort_ops(ops_input, initial_coef=1.0, initial_has_kappa=False):
    order = {'a+': 1, 'a-': 2}
    for i in range(1, 10):
        order[f'b{i}+'] = 2 + 2*i - 1
        order[f'b{i}-'] = 2 + 2*i
        
    terms = [Term(initial_coef, ops_input, initial_has_kappa)]
    ordered_terms = []
    
    while terms:
        t = terms.pop()
        ops = list(t.ops)
        swapped = False
        for i in range(len(ops) - 1):
            o1, o2 = ops[i], ops[i+1]
            if order[o1] > order[o2]:
                if o1 == 'a-' and o2 == 'a+':
                    # a- a+ = 1 - a+ a-
                    terms.append(Term(t.coef, ops[:i] + ops[i+2:], t.has_kappa))
                    terms.append(Term(mult_coef(t.coef, -1), ops[:i] + ['a+', 'a-'] + ops[i+2:], t.has_kappa))
                elif o1.startswith('b') and o1.endswith('-') and o2.startswith('b') and o2.endswith('+') and o1[:-1] == o2[:-1]:
                    # b- b+ = 1 + b+ b-
                    terms.append(Term(t.coef, ops[:i] + ops[i+2:], t.has_kappa))
                    terms.append(Term(t.coef, ops[:i] + [o2, o1] + ops[i+2:], t.has_kappa))
                elif o1.startswith('b') and o2.startswith('a'):
                    # bj a = a bj - gb_{a, b} kappa
                    sign = -1 if p(o1) == 1 and p(o2) == 1 else 1
                    terms.append(Term(mult_coef(t.coef, sign), ops[:i] + [o2, o1] + ops[i+2:], t.has_kappa))
                    
                    if not t.has_kappa:
                        # Produce kappa term
                        sigma = 'p' if o2 == 'a+' else 'm'
                        j = o1[1:-1]
                        s = 'p' if o1.endswith('+') else 'm'
                        gb_name = f'gb_{sigma}_{j}_{s}'
                        
                        # Move kappa to front
                        num_odd = sum(p(x) for x in ops[:i])
                        kappa_sign = -1 if num_odd % 2 == 1 else 1
                        
                        # The relation is bj a = a bj - gb kappa
                        # So coefficient is -gb
                        new_coef = {gb_name: -kappa_sign}
                        # multiply by existing t.coef (which is a float since has_kappa=False)
                        new_coef = mult_coef(new_coef, t.coef)
                        
                        terms.append(Term(new_coef, ops[:i] + ops[i+2:], True))
                else:
                    sign = -1 if p(o1) == 1 and p(o2) == 1 else 1
                    terms.append(Term(mult_coef(t.coef, sign), ops[:i] + [o2, o1] + ops[i+2:], t.has_kappa))
                swapped = True
                break
            elif order[o1] == order[o2]:
                if p(o1) == 1:
                    t.coef = mult_coef(t.coef, 0) # 0
        if not swapped:
            if isinstance(t.coef, dict) and not t.coef:
                pass
            elif not isinstance(t.coef, dict) and t.coef == 0:
                pass
            else:
                ordered_terms.append(t)
                
    res = {}
    for t in ordered_terms:
        key = (t.ops, t.has_kappa)
        res[key] = add_coefs(res.get(key, 0.0), t.coef)
    return {k: v for k, v in res.items() if (isinstance(v, dict) and v) or (not isinstance(v, dict) and v != 0)}

def mult(A, B):
    res = {}
    for (opsA, has_kappaA), cA in A.items():
        for (opsB, has_kappaB), cB in B.items():
            if has_kappaA and has_kappaB:
                continue
            
            has_kappa = has_kappaA or has_kappaB
            
            # If B has kappa, move it to front of A
            sign = 1
            if has_kappaB:
                num_odd_A = sum(p(x) for x in opsA)
                if num_odd_A % 2 == 1:
                    sign = -1
                    
            if isinstance(cA, dict) and isinstance(cB, dict):
                continue # Kappa squared = 0
            
            if isinstance(cA, dict):
                c = mult_coef(cA, cB * sign)
            elif isinstance(cB, dict):
                c = mult_coef(cB, cA * sign)
            else:
                c = cA * cB * sign
                
            new_term = list(opsA) + list(opsB)
            ordered = sort_ops(new_term, c, has_kappa)
            
            for (ops, hk), c_ord in ordered.items():
                res[(ops, hk)] = add_coefs(res.get((ops, hk), 0.0), c_ord)
    return res

def add(A, B, coefB=1.0):
    res = dict(A)
    for k, v in B.items():
        res[k] = add_coefs(res.get(k, 0.0), v, coefB)
    return res

def supercomm(A, B, pA, pB):
    AB = mult(A, B)
    BA = mult(B, A)
    sign = -1 if pA == 1 and pB == 1 else 1
    return add(AB, BA, -sign)

def get_generators(n):
    # Just standard generators but converted to new tuple keys (ops, False)
    import C_generators
    gens_0, parities = C_generators.get_generators(n)
    gens = {}
    for g, terms in gens_0.items():
        gens[g] = { (ops, False): c for ops, c in terms.items() }
    return gens, parities

def find_linear_comb_dict(expr, gens_0):
    # expr is {(ops, True): {gb: coef}}
    # We want to match it to a linear combination of generators.
    # The coefficients will be dicts of gb parameters.
    if not expr: return {}
    res = {}
    remaining = dict(expr)
    
    # gens_0 are standard {ops: coef(float)}
    for g, g_expr in gens_0.items():
        if g.startswith('H_'): continue
        if len(g_expr) == 1:
            monom = list(g_expr.keys())[0]
            val = g_expr[monom]
            monom_key = (monom, True)
            if monom_key in remaining:
                # remaining[monom_key] is a dict of gb
                c = mult_coef(remaining[monom_key], 1.0 / val)
                res[g] = c
                
                # subtract c * g_expr
                g_expr_kappa = {(k, True): v for k, v in g_expr.items()}
                remaining = add(remaining, g_expr_kappa, -1.0, c)
                
    # Cartans
    c1 = remaining.get((('a+', 'a-'), True), {})
    if c1:
        res['H_1'] = c1
        remaining = add(remaining, {(k, True): v for k, v in gens_0['H_1'].items()}, -1.0, c1)
        
    n = len([x for x in gens_0 if x.startswith("H_")]) - 1
    for k in range(2, n+1):
        hk = f'H_{k}'
        monom = (f'b{k-1}+', f'b{k-1}-')
        ck = remaining.get((monom, True), {})
        if ck:
            res[hk] = ck
            remaining = add(remaining, {(k, True): v for k, v in gens_0[hk].items()}, -1.0, ck)
            
    monom = (f'b{n}+', f'b{n}-')
    cn = remaining.get((monom, True), {})
    if cn:
        c = mult_coef(cn, -1.0)
        res[f'H_{n+1}'] = c
        remaining = add(remaining, {(k, True): v for k, v in gens_0[f'H_{n+1}'].items()}, -1.0, c)

    if (tuple(), True) in remaining:
        res['K'] = remaining[(tuple(), True)]
        remaining.pop((tuple(), True))
        
    for k, v in remaining.items():
        if isinstance(v, dict) and v:
            for val in v.values():
                if abs(val) > 1e-9:
                    raise ValueError(f"Could not fully match expression. Remaining: {remaining}")
            
    return res

def add(A, B, coefB=1.0, coefB_dict=None):
    res = dict(A)
    for k, v in B.items():
        if coefB_dict is not None:
            # v is float, coefB_dict is dict -> result is dict
            term = mult_coef(coefB_dict, v * coefB)
            res[k] = add_coefs(res.get(k, 0.0), term)
        else:
            res[k] = add_coefs(res.get(k, 0.0), v, coefB)
    return {k: v for k, v in res.items() if (isinstance(v, dict) and v) or (not isinstance(v, dict) and v != 0)}

def build_schema_2(n):
    import C_generators
    gens_0, _ = C_generators.get_generators(n)
    gens, parities = get_generators(n)
    
    basis_odd = sorted([g for g in gens if parities[g] == 1])
    basis_even_H = [f'H_{k}' for k in range(1, n+2)]
    basis_even_2del = sorted([g for g in gens if '2del' in g])
    basis_even_del_del = sorted([g for g in gens if 'del' in g and 'eps' not in g and '2del' not in g])
    basis_even = basis_even_H + basis_even_2del + basis_even_del_del
    
    struct_consts = {}
    all_basis = basis_odd + basis_even
    
    for g1 in all_basis:
        for g2 in all_basis:
            comm = supercomm(gens[g1], gens[g2], parities[g1], parities[g2])
            
            # Extract kappa terms
            kappa_terms = {k: v for k, v in comm.items() if k[1] == True}
            if kappa_terms:
                res = find_linear_comb_dict(kappa_terms, gens_0)
                if res:
                    struct_consts[f"{g1},{g2}"] = res
                    
    gb_matrix_desc = [
        ["gb_p_1_p", "gb_p_1_m", "...", f"gb_p_{n}_m"],
        ["gb_m_1_p", "gb_m_1_m", "...", f"gb_m_{n}_m"]
    ]
    
    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n
        },
        "inhomogeneous_deformation": {
            "gb_matrix_description": "2 x 2n matrix of odd deformation parameters.",
            "gb_matrix": gb_matrix_desc,
            "gamma_structure_constants": struct_consts
        },
        "metadata": {
            "description": f"Schema 2 for C({n+1}) = osp(2|{2*n})"
        }
    }
    return schema

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema_2(n)
        with open(f'data/C_{n}_gamma.json', 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_gamma.json")

