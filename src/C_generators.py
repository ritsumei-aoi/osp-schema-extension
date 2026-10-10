import itertools
import json
import os

class Term:
    def __init__(self, coef, ops):
        self.coef = coef
        self.ops = tuple(ops)

def p(op):
    if op in ('a+', 'a-'):
        return 1
    return 0

def sort_ops(ops):
    # order: a+, a-, b1+, b1-, b2+, b2-, ...
    order = {'a+': 1, 'a-': 2}
    for i in range(1, 10):
        order[f'b{i}+'] = 2 + 2*i - 1
        order[f'b{i}-'] = 2 + 2*i
    
    # We will bubble sort to keep track of signs and commutators
    terms = [Term(1, ops)]
    ordered_terms = []
    
    while terms:
        t = terms.pop()
        ops_list = list(t.ops)
        swapped = False
        for i in range(len(ops_list) - 1):
            o1 = ops_list[i]
            o2 = ops_list[i+1]
            if order[o1] > order[o2]:
                # Need to swap
                if o1 == 'a-' and o2 == 'a+':
                    # a- a+ = 1 - a+ a-
                    # Term 1: 1 (remove a-, a+)
                    new_ops_1 = ops_list[:i] + ops_list[i+2:]
                    terms.append(Term(t.coef, new_ops_1))
                    # Term 2: - a+ a-
                    new_ops_2 = ops_list[:i] + ['a+', 'a-'] + ops_list[i+2:]
                    terms.append(Term(-t.coef, new_ops_2))
                elif o1.startswith('b') and o1.endswith('-') and o2.startswith('b') and o2.endswith('+') and o1[:-1] == o2[:-1]:
                    # bk- bk+ = 1 + bk+ bk-
                    new_ops_1 = ops_list[:i] + ops_list[i+2:]
                    terms.append(Term(t.coef, new_ops_1))
                    new_ops_2 = ops_list[:i] + [o2, o1] + ops_list[i+2:]
                    terms.append(Term(t.coef, new_ops_2))
                else:
                    # just swap, check sign
                    sign = -1 if p(o1) == 1 and p(o2) == 1 else 1
                    new_ops = ops_list[:i] + [o2, o1] + ops_list[i+2:]
                    terms.append(Term(t.coef * sign, new_ops))
                swapped = True
                break
            elif order[o1] == order[o2]:
                if p(o1) == 1:
                    # a+ a+ = 0, a- a- = 0
                    t.coef = 0
                else:
                    # bk+ bk+ is fine
                    pass
        if not swapped:
            if t.coef != 0:
                ordered_terms.append(t)
                
    # collect terms
    res = {}
    for t in ordered_terms:
        res[t.ops] = res.get(t.ops, 0) + t.coef
    return {k: v for k, v in res.items() if v != 0}

def mult(A, B):
    res = {}
    for opsA, cA in A.items():
        for opsB, cB in B.items():
            new_term = list(opsA) + list(opsB)
            ordered = sort_ops(new_term)
            for ops, c in ordered.items():
                res[ops] = res.get(ops, 0) + cA * cB * c
    return {k: v for k, v in res.items() if v != 0}

def add(A, B, coefB=1):
    res = dict(A)
    for k, v in B.items():
        res[k] = res.get(k, 0) + v * coefB
    return {k: v for k, v in res.items() if v != 0}

def supercomm(A, B, pA, pB):
    AB = mult(A, B)
    BA = mult(B, A)
    sign = -1 if pA == 1 and pB == 1 else 1
    return add(AB, BA, -sign)

def get_generators(n):
    gens = {}
    parities = {}
    
    # Even generators
    # Cartan
    gens['H_1'] = sort_ops(['a+', 'a-'])
    gens['H_1'] = add(gens['H_1'], sort_ops(['b1+', 'b1-']))
    parities['H_1'] = 0
    
    for k in range(2, n+1):
        h = sort_ops([f'b{k-1}+', f'b{k-1}-'])
        h = add(h, sort_ops([f'b{k}+', f'b{k}-']), -1)
        gens[f'H_{k}'] = h
        parities[f'H_{k}'] = 0
        
    gens[f'H_{n+1}'] = add(sort_ops([f'b{n}+', f'b{n}-']), {tuple(): 0.5}, -1) # -bn+ bn- - 1/2
    # Wait, the definition says H_{n+1} = -bn+ bn- - 1/2.
    # The normal_order gives H_{n+1} = -bn+ bn- - 0.5.
    gens[f'H_{n+1}'] = sort_ops([]) # empty
    gens[f'H_{n+1}'] = { (f'b{n}+', f'b{n}-'): -1, tuple(): -0.5 }
    parities[f'H_{n+1}'] = 0

    for k in range(1, n+1):
        gens[f'E_2del{k}_p'] = sort_ops([f'b{k}+', f'b{k}+'])
        gens[f'E_2del{k}_m'] = sort_ops([f'b{k}-', f'b{k}-'])
        parities[f'E_2del{k}_p'] = 0
        parities[f'E_2del{k}_m'] = 0

    for i in range(1, n+1):
        for j in range(i+1, n+1):
            gens[f'E_del{i}_del{j}_pp'] = sort_ops([f'b{i}+', f'b{j}+'])
            gens[f'E_del{i}_del{j}_pm'] = sort_ops([f'b{i}+', f'b{j}-'])
            gens[f'E_del{i}_del{j}_mp'] = sort_ops([f'b{i}-', f'b{j}+'])
            gens[f'E_del{i}_del{j}_mm'] = sort_ops([f'b{i}-', f'b{j}-'])
            parities[f'E_del{i}_del{j}_pp'] = 0
            parities[f'E_del{i}_del{j}_pm'] = 0
            parities[f'E_del{i}_del{j}_mp'] = 0
            parities[f'E_del{i}_del{j}_mm'] = 0

    # Odd generators
    for k in range(1, n+1):
        gens[f'E_eps_del{k}_pp'] = sort_ops(['a+', f'b{k}+'])
        gens[f'E_eps_del{k}_pm'] = sort_ops(['a+', f'b{k}-'])
        gens[f'E_eps_del{k}_mp'] = sort_ops(['a-', f'b{k}+'])
        gens[f'E_eps_del{k}_mm'] = sort_ops(['a-', f'b{k}-'])
        parities[f'E_eps_del{k}_pp'] = 1
        parities[f'E_eps_del{k}_pm'] = 1
        parities[f'E_eps_del{k}_mp'] = 1
        parities[f'E_eps_del{k}_mm'] = 1

    return gens, parities

def format_realization(gen_dict):
    res = {}
    for g, terms in gen_dict.items():
        desc = []
        for ops, c in terms.items():
            if not ops:
                desc.append(f"{c}")
            else:
                c_str = f"{c} " if c != 1 and c != -1 else ("- " if c == -1 else "")
                desc.append(f"{c_str}" + " ".join(ops))
        res[g] = " + ".join(desc).replace("+ -", "- ")
    return res

def find_linear_comb(expr, gens):
    # expr is a dict of terms. gens is a dict of generators.
    # We want to express expr as sum c_i * G_i.
    # For oscillator realization of degree 2, they form a basis.
    if not expr:
        return {}
    
    # We can just match term by term.
    res = {}
    remaining = dict(expr)
    
    # We'll just do a greedy match because the basis is orthogonal in terms of monomials,
    # except H_k which share b_k+ b_k-.
    # Actually, it's easier to just invert the linear system, but for our specific basis,
    # off-diagonal terms uniquely identify roots.
    
    # first, extract off-diagonal (degree 2 mixed or squared)
    for g, g_expr in gens.items():
        if g.startswith('H_'): continue
        # root vectors have exactly 1 monomial
        if len(g_expr) == 1:
            monom = list(g_expr.keys())[0]
            val = g_expr[monom]
            if monom in remaining:
                c = remaining[monom] / val
                res[g] = c
                remaining = add(remaining, g_expr, -c)
    
    # now remaining should be diagonal terms and constants
    # H_1 = a+ a- + b1+ b1-
    # H_k = b_{k-1}+ b_{k-1}- - bk+ bk-
    # H_{n+1} = -bn+ bn- - 1/2
    
    # Let's see coefficient of a+ a- to find c_1 for H_1
    c1 = remaining.get(('a+', 'a-'), 0)
    if c1 != 0:
        res['H_1'] = c1
        remaining = add(remaining, gens['H_1'], -c1)
        
    n = len([x for x in gens if x.startswith("H_")]) - 1
    for k in range(2, n+1):
        hk = f'H_{k}'
        if hk not in gens: break
        monom = (f'b{k-1}+', f'b{k-1}-')
        ck = remaining.get(monom, 0)
        if ck != 0:
            res[hk] = ck
            remaining = add(remaining, gens[hk], -ck)
            
    monom = (f'b{n}+', f'b{n}-')
    cn = remaining.get(monom, 0)
    if cn != 0:
        c = cn / (-1.0)
        res[f'H_{n+1}'] = c
        remaining = add(remaining, gens[f'H_{n+1}'], -c)

    # Now if remaining has empty tuple, it's the central element K (which is just 1)
    if tuple() in remaining:
        res['K'] = remaining[tuple()]
        remaining.pop(tuple())
        
    # Check if remaining is zero
    for k, v in remaining.items():
        if abs(v) > 1e-9:
            raise ValueError(f"Could not fully match expression. Remaining: {remaining}")
            
    return res

def build_schema(n):
    gens, parities = get_generators(n)
    
    # Order basis as per PBW: odd then even
    basis_odd = sorted([g for g in gens if parities[g] == 1], key=lambda x: x)
    
    # For even: H_k, E_2del, E_del_del
    basis_even_H = [f'H_{k}' for k in range(1, n+2)]
    basis_even_2del = sorted([g for g in gens if '2del' in g])
    basis_even_del_del = sorted([g for g in gens if 'del' in g and 'eps' not in g and '2del' not in g])
    basis_even = basis_even_H + basis_even_2del + basis_even_del_del
    
    struct_consts = {}
    all_basis = basis_odd + basis_even
    
    for i, g1 in enumerate(all_basis):
        for j, g2 in enumerate(all_basis):
            comm = supercomm(gens[g1], gens[g2], parities[g1], parities[g2])
            res = find_linear_comb(comm, gens)
            if res:
                key = f"{g1},{g2}"
                struct_consts[key] = res
                
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
                "total": 2*n*n + 5*n + 1,
                "even": 2*n*n + n + 1,
                "odd": 4*n
            }
        },
        "oscillator_generators": {
            "fermions": {
                "m": 1,
                "count": 2,
                "labels": ["a_1_p", "a_1_m"],
                "description": "Fermionic oscillators a_i^± with i=1,...,m"
            },
            "bosons": {
                "n": n,
                "count": 2*n,
                "labels": [f"b_{k}_p" if sign == "+" else f"b_{k}_m" for k in range(1, n+1) for sign in ("+", "-")],
                "description": "Bosonic oscillators b_j^± with j=1,...,n"
            }
        },
        "oscillator_relations": {
            "fermionic_anticommutators": {
                "description": "Canonical anticommutation relations (CAR) for fermionic oscillators",
                "relations": {
                    "same_type": "{a_i^±, a_j^±} = 0 for all i, j",
                    "conjugate_pair": "{a_i^-, a_j^+} = \\delta_{ij}"
                }
            },
            "bosonic_commutators": {
                "description": "Canonical commutation relations (CCR) for bosonic oscillators",
                "relations": {
                    "same_type": "[b_i^±, b_j^±] = 0 for all i, j",
                    "conjugate_pair": "[b_i^-, b_j^+] = \\delta_{ij}"
                }
            },
            "mixed_commutators": {
                "boson_fermion": "[b_i^±, a_j^±] = 0"
            }
        },
        "central_elements": {
            "kappa": {
                "parity": 1,
                "description": "Odd central element (nilpotent: kappa^2 = 0) used for the inhomogeneous deformation."
            },
            "K": {
                "parity": 0,
                "description": "Even central element, identified with scalar 1 in applications."
            }
        },
        "basis": {
            "even": basis_even,
            "odd": basis_odd,
            "ordering_convention": "PBW: κ < [odd] < [even]"
        },
        "parity": parities,
        "generator_realization": format_realization(gens),
        "structure_constants": struct_consts,
        "metadata": {
            "description": f"Schema 1 for C({n+1}) = osp(2|{2*n})"
        }
    }
    return schema

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    for n in [1, 2, 3]:
        schema = build_schema(n)
        with open(f'data/C_{n}_structure.json', 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"Generated data/C_{n}_structure.json")
