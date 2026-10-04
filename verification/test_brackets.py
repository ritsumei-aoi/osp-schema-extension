"""
Compute [X, Y] for all generators of C(2) = osp(2|2).
"""
import sympy as sp
from collections import defaultdict
from verification.test_norm import create_algebra

# For n=1:
# Generators of C(2) = osp(2|2):
# Even generators (4):
# H1 = a+ a- + b1+ b1-
# H2 = - b1+ b1- - 1/2
# E_2delta = 1/2 (b1+)^2
# E_-2delta = 1/2 (b1-)^2

# Odd generators (4):
# E_{eps + delta} = a+ b1+
# E_{eps - delta} = a+ b1-
# E_{-eps + delta} = a- b1+
# E_{-eps - delta} = a- b1-

def get_generators(n=1):
    gens = {}
    parities = {}
    
    # Odd generators:
    # E_{eps + delta_j} = a+ bj+
    # E_{eps - delta_j} = a+ bj-
    # E_{-eps + delta_j} = a- bj+
    # E_{-eps - delta_j} = a- bj-
    for j in range(1, n+1):
        gens[f"F_p_{j}_p"] = [('a+', ('b+', j), sp.Integer(1))]
        gens[f"F_p_{j}_m"] = [('a+', ('b-', j), sp.Integer(1))]
        gens[f"F_m_{j}_p"] = [('a-', ('b+', j), sp.Integer(1))]
        gens[f"F_m_{j}_m"] = [('a-', ('b-', j), sp.Integer(1))]
        for s1 in ['p', 'm']:
            for s2 in ['p', 'm']:
                parities[f"F_{s1}_{j}_{s2}"] = 1
                
    # Even generators:
    # Cartan:
    # H1 = a+ a- + b1+ b1-
    gens["H_1"] = [
        (('a+', 'a-'), sp.Integer(1)),
        ((('b+', 1), ('b-', 1)), sp.Integer(1))
    ]
    parities["H_1"] = 0
    
    for k in range(2, n+1):
        # Hk = b_{k-1}+ b_{k-1}- - bk+ bk-
        gens[f"H_{k}"] = [
            ((('b+', k-1), ('b-', k-1)), sp.Integer(1)),
            ((('b+', k), ('b-', k)), sp.Integer(-1))
        ]
        parities[f"H_{k}"] = 0
        
    # H_{n+1} = - bn+ bn- - 1/2
    gens[f"H_{n+1}"] = [
        ((('b+', n), ('b-', n)), sp.Integer(-1)),
        ((), sp.Rational(-1, 2))
    ]
    parities[f"H_{n+1}"] = 0
    
    # Root generators of sp(2n):
    # E_{2 delta_k} = 1/2 (bk+)^2
    # E_{-2 delta_k} = 1/2 (bk-)^2
    for k in range(1, n+1):
        gens[f"E_2d_{k}"] = [((('b+', k), ('b+', k)), sp.Rational(1, 2))]
        gens[f"E_-2d_{k}"] = [((('b-', k), ('b-', k)), sp.Rational(1, 2))]
        parities[f"E_2d_{k}"] = 0
        parities[f"E_-2d_{k}"] = 0
        
    # E_{delta_k - delta_l}, E_{delta_k + delta_l}, E_{-delta_k - delta_l} for k != l
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
    # el1 and el2 are lists of (word, coeff)
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
    sign = -1 if (p1 == 1 and p2 == 1) else 1 # [X, Y] = XY - (-1)^{p1 p2} YX
    
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
    print("Generators count:", len(gens))
    for name, p in parities.items():
        print(f"{name} (parity {p}): {gens[name]}")
        
    print("\n--- Testing superbracket [F_p_1_m, F_m_1_p] ---")
    br = superbracket("F_p_1_m", "F_m_1_p", gens, parities, reduce_word)
    print(br)
