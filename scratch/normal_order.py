import sympy as sp
from collections import defaultdict

class Monomial:
    """
    Represents a normal ordered monomial:
    coef * (a1+)^u_plus * (a1-)^u_minus * product_k (bk+)^p_k (bk-)^m_k * kappa^w
    """
    def __init__(self, u_p=0, u_m=0, b_powers=None, kappa=0, coef=1):
        self.u_p = u_p # 0 or 1
        self.u_m = u_m # 0 or 1
        self.b_powers = tuple(b_powers) if b_powers else () # tuple of (k, '+') or (k, '-') powers
        self.kappa = kappa # 0 or 1
        self.coef = sp.sympify(coef)

    def is_zero(self):
        return self.coef == 0 or self.u_p > 1 or self.u_m > 1 or self.kappa > 1

def multiply_monomials(m1, m2, n, gb_params):
    """
    Multiplies two normal-ordered monomials m1 and m2 for C(n+1).
    Returns a dict mapping normal-ordered Monomial keys to sympy coefficients.
    """
    # Monomial m1 has (a1+)^{u1_p} (a1-)^{u1_m} B1 kappa^{k1}
    # Monomial m2 has (a2+)^{u2_p} (a2-)^{u2_m} B2 kappa^{k2}
    # Product: m1 * m2 = coef1 * coef2 * kappa^{k1+k2} * (a1+)^{u1_p} (a1-)^{u1_m} B1 (a1+)^{u2_p} (a2-)^{u2_m} B2
    
    if m1.kappa + m2.kappa > 1:
        return {} # kappa^2 = 0
        
    init_coef = m1.coef * m2.coef
    init_kappa = m1.kappa + m2.kappa
    
    # We need to reorder: B1 (a1+)^{u2_p} (a1-)^{u2_m} B2
    # First, commute B1 past a1+ and a1-.
    # B1 is a product of b_k^s operators.
    # When b_k^s commutes past a1^\sigma: b_k^s a1^\sigma = a1^\sigma b_k^s - gb_{\sigma, k, s} kappa
    
    # Let's do step-by-step reduction of a list of fundamental operators:
    # Operators in the list can be: ('a', '+'), ('a', '-'), ('b', k, s), ('kappa', 1)
    
    ops = []
    if m1.u_p: ops.append(('a', '+'))
    if m1.u_m: ops.append(('a', '-'))
    for op in m1.b_powers: ops.append(('b', op[0], op[1]))
    if m2.u_p: ops.append(('a', '+'))
    if m2.u_m: ops.append(('a', '-'))
    for op in m2.b_powers: ops.append(('b', op[0], op[1]))
    
    # We reduce the list of operators to normal order.
    # Normal order sequence: ('a', '+'), ('a', '-'), ('b', 1, '+'), ('b', 1, '-'), ..., ('b', n, '+'), ('b', n, '-'), ('kappa', 1)
    
    # We can represent state as a list of (coef, kappa_deg, list_of_ops)
    states = [(init_coef, init_kappa, ops)]
    
    # Helper to check if list is normal ordered
    def is_ordered(op_list):
        # Order precedence:
        # ('a', '+') < ('a', '-') < ('b', 1, '+') < ('b', 1, '-') < ...
        def rank(op):
            if op[0] == 'a':
                return 0 if op[1] == '+' else 1
            elif op[0] == 'b':
                k, s = op[1], op[2]
                return 2 + 2*(k-1) + (0 if s == '+' else 1)
            return 999
        for i in range(len(op_list)-1):
            if rank(op_list[i]) > rank(op_list[i+1]):
                return False
        return True

    final_terms = defaultdict(lambda: sp.sympify(0))
    
    while states:
        c, kap, op_list = states.pop()
        if c == 0 or kap > 1:
            continue
            
        if is_ordered(op_list):
            # Check for nilpotent a_1+ or a_1-
            c_count = op_list.count(('a', '+'))
            a_count = op_list.count(('a', '-'))
            if c_count > 1 or a_count > 1:
                continue
            
            u_p = 1 if ('a', '+') in op_list else 0
            u_m = 1 if ('a', '-') in op_list else 0
            b_ops = tuple((op[1], op[2]) for op in op_list if op[0] == 'b')
            
            key = (u_p, u_m, b_ops, kap)
            final_terms[key] += c
            continue
            
        # Find first out-of-order adjacent pair
        def rank(op):
            if op[0] == 'a':
                return 0 if op[1] == '+' else 1
            elif op[0] == 'b':
                k, s = op[1], op[2]
                return 2 + 2*(k-1) + (0 if s == '+' else 1)
            return 999
            
        idx = 0
        for i in range(len(op_list)-1):
            if rank(op_list[i]) > rank(op_list[i+1]):
                idx = i
                break
                
        left, right = op_list[idx], op_list[idx+1]
        prefix = op_list[:idx]
        suffix = op_list[idx+2:]
        
        # Swapping left and right:
        # Case 1: ('a', '-') before ('a', '+') -> {a-, a+} = 1 => a- a+ = 1 - a+ a-
        if left == ('a', '-') and right == ('a', '+'):
            # Term 1: 1 * prefix + suffix
            states.append((c, kap, prefix + suffix))
            # Term 2: - a+ a- * prefix + ...
            states.append((-c, kap, prefix + [('a', '+'), ('a', '-')] + suffix))
            
        # Case 2: ('b', k, s) before ('a', sigma) -> b_k^s a1^sigma = a1^sigma b_k^s - gb_{\sigma, k, s} kappa
        elif left[0] == 'b' and right[0] == 'a':
            k, s = left[1], left[2]
            sigma = right[1]
            gb = gb_params[(sigma, k, s)]
            # Term 1: a1^sigma b_k^s
            states.append((c, kap, prefix + [right, left] + suffix))
            # Term 2: - gb * kappa
            if kap + 1 <= 1:
                states.append((-c * gb, kap + 1, prefix + suffix))
                
        # Case 3: ('b', k, '-') before ('b', k, '+') -> [b_k-, b_k+] = 1 => b_k- b_k+ = b_k+ b_k- + 1
        elif left[0] == 'b' and right[0] == 'b' and left[1] == right[1] and left[2] == '-' and right[2] == '+':
            k = left[1]
            # Term 1: b_k+ b_k-
            states.append((c, kap, prefix + [('b', k, '+'), ('b', k, '-')] + suffix))
            # Term 2: + 1
            states.append((c, kap, prefix + suffix))
            
        # Case 4: ('b', k1, s1) before ('b', k2, s2) where k1 > k2, or k1 == k2 and s1 == s2
        # For different k or same (k,s), bosonic operators commute!
        elif left[0] == 'b' and right[0] == 'b':
            states.append((c, kap, prefix + [right, left] + suffix))
            
        else:
            raise ValueError(f"Unhandled swap: {left}, {right}")
            
    return final_terms

print("Normal ordering logic written successfully.")
