import json
import itertools
from collections import defaultdict

def operator_order():
    # Return a function that gives the priority of an operator. Lower is earlier.
    # Order: ap, am, b1p, b1m, b2p, b2m...
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

def commute(op1, op2):
    # Returns the scalar from [op1, op2] or {op1, op2} if they don't simply commute/anticommute
    # Returns None if they just commute (or anticommute for two fermions) without extra terms
    if op1 == 'am' and op2 == 'ap':
        return 1 # {am, ap} = 1 => am ap = -ap am + 1
    if op1.startswith('b') and op1.endswith('m') and op2.startswith('b') and op2.endswith('p'):
        if op1[1:-1] == op2[1:-1]:
            return 1 # [bm, bp] = 1 => bm bp = bp bm + 1
    return 0

def normalize(terms):
    prio = operator_order()
    changed = True
    while changed:
        changed = False
        new_terms = defaultdict(int)
        for ops, coeff in terms.items():
            if coeff == 0: continue
            ops = list(ops)
            
            # Check for nilpotent fermions
            has_nilpotent = False
            for i in range(len(ops) - 1):
                if (ops[i] == 'ap' and ops[i+1] == 'ap') or (ops[i] == 'am' and ops[i+1] == 'am'):
                    has_nilpotent = True
                    break
            if has_nilpotent:
                continue # this term is 0
                
            # Find first out-of-order pair
            for i in range(len(ops) - 1):
                if prio(ops[i]) > prio(ops[i+1]):
                    # Swap them
                    op1, op2 = ops[i], ops[i+1]
                    p1, p2 = parity(op1), parity(op2)
                    sign = -1 if (p1 == 1 and p2 == 1) else 1
                    
                    # add swapped term
                    swapped_ops = tuple(ops[:i] + [op2, op1] + ops[i+2:])
                    new_terms[swapped_ops] += coeff * sign
                    
                    # add commutator term if non-zero
                    comm = commute(op1, op2)
                    if comm != 0:
                        comm_ops = tuple(ops[:i] + ops[i+2:])
                        new_terms[comm_ops] += coeff * comm
                    
                    changed = True
                    break
            else:
                new_terms[tuple(ops)] += coeff
        
        terms = {k: v for k, v in new_terms.items() if v != 0}
    return terms

def add_terms(t1, t2, c1=1, c2=1):
    res = defaultdict(int)
    for k, v in t1.items(): res[k] += v * c1
    for k, v in t2.items(): res[k] += v * c2
    return {k: v for k, v in res.items() if v != 0}

def mul_terms(t1, t2):
    res = defaultdict(int)
    for k1, v1 in t1.items():
        for k2, v2 in t2.items():
            res[k1 + k2] += v1 * v2
    return normalize(res)

def get_basis(n):
    basis = {}
    basis['K'] = {(): 1}
    
    basis['H_1'] = {('ap', 'am'): 1, ('b1p', 'b1m'): 1}
    for k in range(2, n + 1):
        basis[f'H_{k}'] = {(f'b{k-1}p', f'b{k-1}m'): 1, (f'b{k}p', f'b{k}m'): -1}
    basis[f'H_{n+1}'] = {(f'b{n}p', f'b{n}m'): -1, (): -0.5}
    
    for k in range(1, n + 1):
        basis[f'E_2del{k}_p'] = {(f'b{k}p', f'b{k}p'): 1}
        basis[f'E_2del{k}_m'] = {(f'b{k}m', f'b{k}m'): 1}
        
        basis[f'E_eps1_del{k}_pp'] = {('ap', f'b{k}p'): 1}
        basis[f'E_eps1_del{k}_pm'] = {('ap', f'b{k}m'): 1}
        basis[f'E_eps1_del{k}_mp'] = {('am', f'b{k}p'): 1}
        basis[f'E_eps1_del{k}_mm'] = {('am', f'b{k}m'): 1}
        
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            basis[f'E_del{i}_del{j}_pp'] = {(f'b{i}p', f'b{j}p'): 1}
            basis[f'E_del{i}_del{j}_pm'] = {(f'b{i}p', f'b{j}m'): 1}
            basis[f'E_del{i}_del{j}_mp'] = {(f'b{i}m', f'b{j}p'): 1}
            basis[f'E_del{i}_del{j}_mm'] = {(f'b{i}m', f'b{j}m'): 1}
            
    # Normalize all basis elements just in case
    for k in basis:
        basis[k] = normalize(basis[k])
        
    # Ordering
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

def decompose(terms, basis, ordered_names, n):
    rem = {k: v for k, v in terms.items() if v != 0}
    coeffs = defaultdict(int)
    
    # Extract roots
    for name in ordered_names:
        if name.startswith('H_') or name == 'K': continue
        k = list(basis[name].keys())[0]
        if k in rem:
            c = rem[k] / basis[name][k]
            coeffs[name] += c
            rem = add_terms(rem, basis[name], c1=1, c2=-c)
            
    # Extract Cartans
    # H_1 = ap am + b1p b1m
    if ('ap', 'am') in rem:
        c = rem[('ap', 'am')]
        coeffs['H_1'] += c
        rem = add_terms(rem, basis['H_1'], c1=1, c2=-c)
        
    for k in range(1, n + 1):
        if (f'b{k}p', f'b{k}m') in rem:
            c = rem[(f'b{k}p', f'b{k}m')]
            if k < n:
                # H_{k+1} = bkp bkm - bk+1p bk+1m
                coeffs[f'H_{k+1}'] += c
                rem = add_terms(rem, basis[f'H_{k+1}'], c1=1, c2=-c)
            else:
                # H_{n+1} = -bnp bnm - 1/2
                # to cancel c * (bnp bnm), we need -c * H_{n+1}
                coeffs[f'H_{n+1}'] -= c
                rem = add_terms(rem, basis[f'H_{n+1}'], c1=1, c2=c)
                
    if () in rem:
        c = rem[()]
        coeffs['K'] += c
        rem = add_terms(rem, basis['K'], c1=1, c2=-c)
        
    for k, v in rem.items():
        if abs(v) > 1e-9:
            raise ValueError(f"Failed to decompose: remainder {rem}")
            
    return {k: v for k, v in coeffs.items() if v != 0}

def build_schema(n):
    basis, even, odd = get_basis(n)
    all_names = even + odd + ['K']
    
    structure_constants = []
    
    ordered_basis = odd + even
    
    for i, X in enumerate(ordered_basis):
        for j, Y in enumerate(ordered_basis):
            if i > j: continue # graded commutator has symmetry
            res = graded_commutator(X, Y, basis, odd)
            if not res: continue
            
            coeffs = decompose(res, basis, all_names, n)
            for Z, c in coeffs.items():
                if int(c) == c: c = int(c)
                structure_constants.append({
                    "X": X,
                    "Y": Y,
                    "Z": Z,
                    "coeff": str(c),
                    "sign_rule": "graded"
                })
                
    dim_even = 2*n**2 + n + 1
    dim_odd = 4*n
    
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
                "total": dim_even + dim_odd,
                "even": dim_even,
                "odd": dim_odd
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Standard fermionic pair"
            },
            "bosons": {
                "count": 2*n,
                "n": n,
                "labels": [f"b_{i}_{s}" for i in range(1, n+1) for s in ['p', 'm']],
                "description": "Bosonic oscillators b_i^± with i=1,...,n"
            }
        },
        "oscillator_relations": {
            "standard_fermion_anticommutators": {
                "description": "CAR for standard fermions",
                "relation": "{a_1^-, a_1^+} = 1"
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
                "description": "Nilpotent odd central element"
            },
            "K": {
                "parity": 0,
                "description": "Identity central element"
            }
        },
        "basis": {
            "even": even,
            "odd": odd,
            "ordering_convention": "PBW: κ < [odd] < [even]  (K = 1 is excluded; see note below)"
        },
        "parity": {gen: 1 if gen in odd else 0 for gen in even + odd},
        "generator_realization": {
            "description": "Standard form with PBW ordering",
            "ordering": "a_1_p, a_1_m, " + ", ".join([f"b_{i}_{s}" for i in range(1, n+1) for s in ['p', 'm']]),
            "realizations": {}
        },
        "structure_constants": structure_constants,
        "metadata": {
            "generated_by": "C_generators.py",
            "generation_date": "2026-10-08",
            "references": [
                "Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras"
            ]
        }
    }
    
    # fill generator_realization
    for gen in even + odd:
        real_terms = []
        for term, c in basis[gen].items():
            words = []
            for op in term:
                if op == 'ap': words.append('a_1_p')
                elif op == 'am': words.append('a_1_m')
                else: words.append(f"b_{op[1:-1]}_{op[-1]}")
            if int(c) == c: c = int(c)
            real_terms.append({"words": words, "coeff": str(c)})
        schema["generator_realization"]["realizations"][gen] = {
            "standard_form": real_terms,
            "parity": 1 if gen in odd else 0
        }
        
    return schema

if __name__ == "__main__":
    for n in [1, 2, 3]:
        schema = build_schema(n)
        with open(f"data/C_{n}_structure.json", "w") as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_structure.json")
