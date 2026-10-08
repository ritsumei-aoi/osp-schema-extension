import json
from collections import defaultdict
import os

def operator_order():
    def priority(op):
        if op == 'ap': return 0
        if op == 'am': return 1
        if op.startswith('b') and op.endswith('p'):
            return 2 * int(op[1:-1])
        if op.startswith('b') and op.endswith('m'):
            return 2 * int(op[1:-1]) + 1
        return 999
    return priority

def parity(op):
    return 1 if op in ['ap', 'am'] else 0

def tuple_parity(ops):
    return sum(parity(op) for op in ops) % 2

def commute(op1, op2):
    if op1 == 'am' and op2 == 'ap':
        return 1, None
    if op1.startswith('b') and op1.endswith('m') and op2.startswith('b') and op2.endswith('p'):
        if op1[1:-1] == op2[1:-1]:
            return 1, None
    if op1.startswith('b') and op2.startswith('a'):
        # b a = a b - gb \kappa
        return -1, f"gb_{op2}_{op1}"
    return 0, None

def normalize(terms):
    prio = operator_order()
    changed = True
    while changed:
        changed = False
        new_terms = defaultdict(int)
        for (ops, gb_var, has_kappa), coeff in terms.items():
            if coeff == 0: continue
            ops = list(ops)
            
            has_nilpotent = False
            for i in range(len(ops) - 1):
                if (ops[i] == 'ap' and ops[i+1] == 'ap') or (ops[i] == 'am' and ops[i+1] == 'am'):
                    has_nilpotent = True
                    break
            if has_nilpotent:
                continue
                
            for i in range(len(ops) - 1):
                if prio(ops[i]) > prio(ops[i+1]):
                    op1, op2 = ops[i], ops[i+1]
                    p1, p2 = parity(op1), parity(op2)
                    sign = -1 if (p1 == 1 and p2 == 1) else 1
                    
                    swapped_ops = tuple(ops[:i] + [op2, op1] + ops[i+2:])
                    new_terms[(swapped_ops, gb_var, has_kappa)] += coeff * sign
                    
                    comm, new_gb = commute(op1, op2)
                    if comm != 0:
                        comm_ops = tuple(ops[:i] + ops[i+2:])
                        if new_gb is None:
                            new_terms[(comm_ops, gb_var, has_kappa)] += coeff * comm
                        else:
                            if has_kappa:
                                # kappa^2 = 0
                                pass
                            else:
                                L_parity = tuple_parity(ops[:i])
                                k_sign = -1 if L_parity == 1 else 1
                                new_terms[(comm_ops, new_gb, True)] += coeff * comm * k_sign
                    
                    changed = True
                    break
            else:
                new_terms[(tuple(ops), gb_var, has_kappa)] += coeff
        
        terms = {k: v for k, v in new_terms.items() if v != 0}
    return terms

def add_terms(t1, t2, c1=1, c2=1):
    res = defaultdict(int)
    for k, v in t1.items(): res[k] += v * c1
    for k, v in t2.items(): res[k] += v * c2
    return {k: v for k, v in res.items() if v != 0}

def mul_terms(t1, t2):
    res = defaultdict(int)
    for (ops1, gb1, k1), v1 in t1.items():
        for (ops2, gb2, k2), v2 in t2.items():
            if k1 and k2: continue # kappa^2 = 0
            if gb1 and gb2: continue
            
            # move k2 to front: past ops1
            sign = 1
            if k2:
                p1 = tuple_parity(ops1)
                if p1 == 1: sign = -1
                
            new_ops = ops1 + ops2
            new_gb = gb1 or gb2
            new_k = k1 or k2
            
            res[(new_ops, new_gb, new_k)] += v1 * v2 * sign
    return normalize(res)

def get_basis(n):
    # Same basis as C_generators.py, but structured for gamma
    basis = {}
    basis['K'] = {((), None, False): 1}
    
    basis['H_1'] = {(('ap', 'am'), None, False): 1, (('b1p', 'b1m'), None, False): 1}
    for k in range(2, n + 1):
        basis[f'H_{k}'] = {((f'b{k-1}p', f'b{k-1}m'), None, False): 1, ((f'b{k}p', f'b{k}m'), None, False): -1}
    basis[f'H_{n+1}'] = {((f'b{n}p', f'b{n}m'), None, False): -1, ((), None, False): -0.5}
    
    for k in range(1, n + 1):
        basis[f'E_2del{k}_p'] = {((f'b{k}p', f'b{k}p'), None, False): 1}
        basis[f'E_2del{k}_m'] = {((f'b{k}m', f'b{k}m'), None, False): 1}
        
        basis[f'E_eps1_del{k}_pp'] = {(('ap', f'b{k}p'), None, False): 1}
        basis[f'E_eps1_del{k}_pm'] = {(('ap', f'b{k}m'), None, False): 1}
        basis[f'E_eps1_del{k}_mp'] = {(('am', f'b{k}p'), None, False): 1}
        basis[f'E_eps1_del{k}_mm'] = {(('am', f'b{k}m'), None, False): 1}
        
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            basis[f'E_del{i}_del{j}_pp'] = {((f'b{i}p', f'b{j}p'), None, False): 1}
            basis[f'E_del{i}_del{j}_pm'] = {((f'b{i}p', f'b{j}m'), None, False): 1}
            basis[f'E_del{i}_del{j}_mp'] = {((f'b{i}m', f'b{j}p'), None, False): 1}
            basis[f'E_del{i}_del{j}_mm'] = {((f'b{i}m', f'b{j}m'), None, False): 1}
            
    for k in basis:
        basis[k] = normalize(basis[k])
        
    even = []
    for k in range(1, n + 2): even.append(f'H_{k}')
    for k in range(1, n + 1): even.append(f'E_2del{k}_p')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1): even.append(f'E_del{i}_del{j}_pp')
    for k in range(1, n + 1): even.append(f'E_2del{k}_m')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1): even.append(f'E_del{i}_del{j}_mm')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1): even.append(f'E_del{i}_del{j}_pm')
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1): even.append(f'E_del{i}_del{j}_mp')
        
    odd = []
    for sign in ['pp', 'pm', 'mp', 'mm']:
        for k in range(1, n + 1):
            odd.append(f'E_eps1_del{k}_{sign}')
            
    return basis, even, odd

def graded_commutator(X_name, Y_name, basis, odd_list):
    X = basis[X_name]
    Y = basis[Y_name]
    
    pX = 1 if X_name in odd_list else 0
    pY = 1 if Y_name in odd_list else 0
    
    XY = mul_terms(X, Y)
    YX = mul_terms(Y, X)
    
    sign = -1 if (pX == 1 and pY == 1) else 1
    res = add_terms(XY, YX, 1, -sign)
    return res

def decompose_gamma(terms, basis, ordered_names, n):
    # Only look at has_kappa == True terms
    # return dict: Z -> dict(gb_var -> coeff)
    kappa_terms = defaultdict(int)
    for (ops, gb_var, has_kappa), c in terms.items():
        if has_kappa:
            kappa_terms[(ops, gb_var)] += c
            
    # Group by gb_var
    grouped = defaultdict(lambda: defaultdict(int))
    for (ops, gb_var), c in kappa_terms.items():
        grouped[gb_var][ops] += c
        
    res = defaultdict(lambda: defaultdict(int))
    
    for gb_var, rem in grouped.items():
        # rem is a dict of ops -> coeff
        # we decompose rem into basis
        for name in ordered_names:
            if name.startswith('H_') or name == 'K': continue
            k = list(basis[name].keys())[0][0] # basis[name] is { (ops, None, False): c }
            if k in rem:
                c = rem[k] / basis[name][(k, None, False)]
                res[gb_var][name] += c
                # subtract
                for (b_ops, _, _), b_c in basis[name].items():
                    rem[b_ops] -= c * b_c
                    if abs(rem[b_ops]) < 1e-9: del rem[b_ops]
                    
        if ('ap', 'am') in rem:
            c = rem[('ap', 'am')]
            res[gb_var]['H_1'] += c
            for (b_ops, _, _), b_c in basis['H_1'].items():
                rem[b_ops] -= c * b_c
                if abs(rem[b_ops]) < 1e-9: del rem[b_ops]
                
        for k in range(1, n + 1):
            if (f'b{k}p', f'b{k}m') in rem:
                c = rem[(f'b{k}p', f'b{k}m')]
                if k < n:
                    res[gb_var][f'H_{k+1}'] += c
                    for (b_ops, _, _), b_c in basis[f'H_{k+1}'].items():
                        rem[b_ops] -= c * b_c
                        if abs(rem[b_ops]) < 1e-9: del rem[b_ops]
                else:
                    res[gb_var][f'H_{n+1}'] -= c
                    for (b_ops, _, _), b_c in basis[f'H_{n+1}'].items():
                        rem[b_ops] += c * b_c
                        if abs(rem[b_ops]) < 1e-9: del rem[b_ops]
                        
        if () in rem:
            c = rem[()]
            res[gb_var]['K'] += c
            rem[()] -= c
            if abs(rem[()]) < 1e-9: del rem[()]
            
        rem = {k: v for k, v in rem.items() if abs(v) > 1e-9}
        if rem:
            raise ValueError(f"Failed to decompose gamma: {rem}")
            
    # invert res to Z -> gb_var -> c
    final_res = defaultdict(dict)
    for gb_var, z_dict in res.items():
        for Z, c in z_dict.items():
            final_res[Z][gb_var] = c
            
    return final_res

def build_schema_2(n):
    basis, even, odd = get_basis(n)
    all_names = even + odd + ['K']
    ordered_basis = odd + even
    
    gamma_constants = []
    
    for i, X in enumerate(ordered_basis):
        for j, Y in enumerate(ordered_basis):
            if i > j: continue
            res = graded_commutator(X, Y, basis, odd)
            if not res: continue
            
            gamma_res = decompose_gamma(res, basis, all_names, n)
            
            for Z, gb_dict in gamma_res.items():
                terms = []
                for gb_var, c in gb_dict.items():
                    if int(c) == c: c = int(c)
                    terms.append({"gb": gb_var, "coeff": str(c)})
                
                gamma_constants.append({
                    "X": X,
                    "Y": Y,
                    "Z": Z,
                    "gamma_terms": terms
                })
                
    schema = {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n
        },
        "inhomogeneous_deformation": {
            "description": "Gamma structure constants for inhomogeneous deformation",
            "gamma_constants": gamma_constants
        },
        "metadata": {
            "generated_by": "C_gamma.py",
            "generation_date": "2026-10-08"
        }
    }
    return schema

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema_2(n)
        with open(f"data/C_{n}_gamma.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_gamma.json")
