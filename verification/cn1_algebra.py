"""
Comprehensive algebra and deformation computation for C(n+1) = osp(2|2n).
"""
import sys
import sympy as sp
from collections import defaultdict

def create_algebra(n=1):
    gb = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb[(sigma, j, s)] = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                
    priority = {'a+': 0, 'a-': 1}
    for j in range(1, n + 1):
        priority[('b+', j)] = 2 * j
        priority[('b-', j)] = 2 * j + 1
        
    def parity(osc):
        return 1 if osc in ('a+', 'a-') else 0

    def reduce_word(word):
        terms = defaultdict(lambda: [sp.Integer(0), sp.Integer(0)])
        queue = [(list(word), sp.Integer(1), sp.Integer(0))]
        
        while queue:
            w, c0, ck = queue.pop()
            if c0 == 0 and ck == 0:
                continue
                
            swapped = False
            for i in range(len(w) - 1):
                o1, o2 = w[i], w[i+1]
                
                # Check (a+)^2 = 0, (a-)^2 = 0
                if o1 == o2 and o1 in ('a+', 'a-'):
                    c0, ck = sp.Integer(0), sp.Integer(0)
                    swapped = True
                    break
                
                if priority[o1] > priority[o2]:
                    # Case 1: a- a+ = 1 - a+ a-
                    if o1 == 'a-' and o2 == 'a+':
                        w_comm = w[:i] + w[i+2:]
                        w_swap = w[:i] + ['a+', 'a-'] + w[i+2:]
                        queue.append((w_comm, c0, ck))
                        queue.append((w_swap, -c0, -ck))
                        swapped = True
                        break
                    
                    # Case 2: both bosons
                    elif isinstance(o1, tuple) and isinstance(o2, tuple):
                        s1, j1 = o1
                        s2, j2 = o2
                        if s1 == 'b-' and s2 == 'b+' and j1 == j2:
                            w_comm = w[:i] + w[i+2:]
                            w_swap = w[:i] + [o2, o1] + w[i+2:]
                            queue.append((w_comm, c0, ck))
                            queue.append((w_swap, c0, ck))
                            swapped = True
                            break
                        else:
                            w_swap = w[:i] + [o2, o1] + w[i+2:]
                            queue.append((w_swap, c0, ck))
                            swapped = True
                            break
                            
                    # Case 3: boson o1 and fermion o2
                    elif isinstance(o1, tuple) and o2 in ('a+', 'a-'):
                        s_b, j_b = o1
                        s_b_sign = '+' if s_b == 'b+' else '-'
                        sigma = '+' if o2 == 'a+' else '-'
                        param = gb[(sigma, j_b, s_b_sign)]
                        
                        # b_j^s a_1^sigma = a_1^sigma b_j^s - gb * kappa
                        w_swap = w[:i] + [o2, o1] + w[i+2:]
                        queue.append((w_swap, c0, ck))
                        
                        if c0 != 0:
                            w_comm = w[:i] + w[i+2:]
                            queue.append((w_comm, sp.Integer(0), -c0 * param))
                        swapped = True
                        break
                    else:
                        raise ValueError(f"Unhandled pair {o1}, {o2}")
                        
            if not swapped:
                num_ap = sum(1 for o in w if o == 'a+')
                num_am = sum(1 for o in w if o == 'a-')
                if num_ap > 1 or num_am > 1:
                    continue
                terms[tuple(w)][0] += c0
                terms[tuple(w)][1] += ck
                
        res = {}
        for k, v in terms.items():
            c0 = sp.simplify(v[0])
            ck = sp.simplify(v[1])
            if c0 != 0 or ck != 0:
                res[k] = (c0, ck)
        return res

    return gb, reduce_word

def get_generators(n=1):
    gens = {}
    parities = {}
    
    # Odd generators (4n total):
    for j in range(1, n+1):
        gens[f"F_p_{j}_p"] = [(('a+', ('b+', j)), sp.Integer(1))]
        gens[f"F_p_{j}_m"] = [(('a+', ('b-', j)), sp.Integer(1))]
        gens[f"F_m_{j}_p"] = [(('a-', ('b+', j)), sp.Integer(1))]
        gens[f"F_m_{j}_m"] = [(('a-', ('b-', j)), sp.Integer(1))]
        for s1 in ['p', 'm']:
            for s2 in ['p', 'm']:
                parities[f"F_{s1}_{j}_{s2}"] = 1
                
    # Even generators: 2n^2 + n + 1 total
    # Cartan:
    gens["H_1"] = [
        (('a+', 'a-'), sp.Integer(1)),
        ((('b+', 1), ('b-', 1)), sp.Integer(1))
    ]
    parities["H_1"] = 0
    
    for k in range(2, n+1):
        gens[f"H_{k}"] = [
            ((('b+', k-1), ('b-', k-1)), sp.Integer(1)),
            ((('b+', k), ('b-', k)), sp.Integer(-1))
        ]
        parities[f"H_{k}"] = 0
        
    gens[f"H_{n+1}"] = [
        ((('b+', n), ('b-', n)), sp.Integer(-1)),
        ((), sp.Rational(-1, 2))
    ]
    parities[f"H_{n+1}"] = 0
    
    # Root generators of sp(2n):
    for k in range(1, n+1):
        gens[f"E_2d_{k}"] = [((('b+', k), ('b+', k)), sp.Rational(1, 2))]
        gens[f"E_-2d_{k}"] = [((('b-', k), ('b-', k)), sp.Rational(1, 2))]
        parities[f"E_2d_{k}"] = 0
        parities[f"E_-2d_{k}"] = 0
        
    for k in range(1, n+1):
        for l in range(k+1, n+1):
            gens[f"E_dp_d_{k}_{l}"] = [((('b+', k), ('b+', l)), sp.Integer(1))]
            gens[f"E_dm_d_{k}_{l}"] = [((('b-', k), ('b-', l)), sp.Integer(1))]
            gens[f"E_pm_d_{k}_{l}"] = [((('b+', k), ('b-', l)), sp.Integer(1))]
            gens[f"E_mp_d_{k}_{l}"] = [((('b-', k), ('b+', l)), sp.Integer(1))]
            parities[f"E_dp_d_{k}_{l}"] = 0
            parities[f"E_dm_d_{k}_{l}"] = 0
            parities[f"E_pm_d_{k}_{l}"] = 0
            parities[f"E_mp_d_{k}_{l}"] = 0
            
    return gens, parities

def multiply_elements(el1, el2, reduce_word):
    res = defaultdict(lambda: [sp.Integer(0), sp.Integer(0)])
    for w1, c1 in el1:
        for w2, c2 in el2:
            prod_w = list(w1) + list(w2)
            terms = reduce_word(prod_w)
            for k, (c0, ck) in terms.items():
                res[k][0] += c1 * c2 * c0
                res[k][1] += c1 * c2 * ck
                
    clean_res = {}
    for k, v in res.items():
        c0 = sp.simplify(v[0])
        ck = sp.simplify(v[1])
        if c0 != 0 or ck != 0:
            clean_res[k] = (c0, ck)
    return clean_res

def superbracket(g1_name, g2_name, gens, parities, reduce_word):
    p1 = parities[g1_name]
    p2 = parities[g2_name]
    sign = -1 if (p1 == 1 and p2 == 1) else 1
    
    el1 = gens[g1_name]
    el2 = gens[g2_name]
    
    xy = multiply_elements(el1, el2, reduce_word)
    yx = multiply_elements(el2, el1, reduce_word)
    
    res = defaultdict(lambda: [sp.Integer(0), sp.Integer(0)])
    for k, (c0, ck) in xy.items():
        res[k][0] += c0
        res[k][1] += ck
    for k, (c0, ck) in yx.items():
        res[k][0] -= sign * c0
        res[k][1] -= sign * ck
        
    clean_res = {}
    for k, v in res.items():
        c0 = sp.simplify(v[0])
        ck = sp.simplify(v[1])
        if c0 != 0 or ck != 0:
            clean_res[k] = (c0, ck)
    return clean_res

if __name__ == '__main__':
    gb, reduce_word = create_algebra(1)
    gens, parities = get_generators(1)
    print(f"Total generators for n=1: {len(gens)}")
    br = superbracket("F_p_1_m", "F_m_1_p", gens, parities, reduce_word)
    print("Bracket [F_p_1_m, F_m_1_p]:")
    print(br)
