import sympy as sp
from itertools import product

class OperatorMonomial:
    """
    Represents a monomial of operators:
    coeff * (a_ops) * (b_ops) * (kappa_power)
    """
    def __init__(self, coeff=1, ops=None):
        self.coeff = sp.sympify(coeff)
        self.ops = list(ops) if ops else []

def multiply_monomials(m1, m2):
    return OperatorMonomial(m1.coeff * m2.coeff, m1.ops + m2.ops)

def normal_order(monomial, gb_dict):
    """
    Normal order a monomial to first order in kappa.
    Returns a list of normal ordered OperatorMonomials.
    """
    current_terms = [(monomial.coeff, list(monomial.ops))]
    
    def is_ordered(op1, op2):
        if op1[0] == 'kappa':
            return True
        if op2[0] == 'kappa':
            return False
        
        if op1[0] == 'a' and op2[0] == 'b':
            return True
        if op1[0] == 'b' and op2[0] == 'a':
            return False
        
        if op1[0] == 'a' and op2[0] == 'a':
            if op1[1] == '+' and op2[1] == '-':
                return True
            if op1[1] == '-' and op2[1] == '+':
                return False
            return True
            
        if op1[0] == 'b' and op2[0] == 'b':
            k1, s1 = op1[1], op1[2]
            k2, s2 = op2[1], op2[2]
            if k1 < k2:
                return True
            if k1 > k2:
                return False
            if s1 == '+' and s2 == '-':
                return True
            if s1 == '-' and s2 == '+':
                return False
            return True
            
        return True

    def swap_adjacent(op1, op2, gb_dict):
        if op1[0] == 'kappa':
            return [(1, [op1, op2])]
        if op2[0] == 'kappa':
            return [(1, [op2, op1])]
            
        if op1[0] == 'a' and op2[0] == 'a':
            s1, s2 = op1[1], op2[1]
            if s1 == '+' and s2 == '+':
                return []
            if s1 == '-' and s2 == '-':
                return []
            if s1 == '-' and s2 == '+':
                return [(1, []), (-1, [('a', '+'), ('a', '-')])]
            return [(1, [op1, op2])]
            
        if op1[0] == 'b' and op2[0] == 'a':
            k, s = op1[1], op1[2]
            sigma = op2[1]
            gb_param = gb_dict[(sigma, k, s)]
            return [
                (1, [op2, op1]),
                (-gb_param, [('kappa',)])
            ]
            
        if op1[0] == 'a' and op2[0] == 'b':
            return [(1, [op1, op2])]
            
        if op1[0] == 'b' and op2[0] == 'b':
            k1, s1 = op1[1], op1[2]
            k2, s2 = op2[1], op2[2]
            if k1 > k2 or (k1 == k2 and s1 == '-' and s2 == '+'):
                if k1 == k2 and s1 == '-' and s2 == '+':
                    return [(1, [op2, op1]), (1, [])]
                else:
                    return [(1, [op2, op1])]
            return [(1, [op1, op2])]

        return [(1, [op1, op2])]

    fully_ordered = []
    
    while current_terms:
        coeff, ops = current_terms.pop()
        if coeff == 0:
            continue

        # Check Fermi exclusion principle: (a+)^2 = 0, (a-)^2 = 0
        ap_count = sum(1 for op in ops if op[0] == 'a' and op[1] == '+')
        am_count = sum(1 for op in ops if op[0] == 'a' and op[1] == '-')
        if ap_count > 1 or am_count > 1:
            continue
            
        # Check kappa count > 1
        kappa_count = sum(1 for op in ops if op[0] == 'kappa')
        if kappa_count > 1:
            continue
            
        out_of_order_idx = -1
        for idx in range(len(ops) - 1):
            if not is_ordered(ops[idx], ops[idx+1]):
                out_of_order_idx = idx
                break
                
        if out_of_order_idx == -1:
            fully_ordered.append((coeff, ops))
        else:
            idx = out_of_order_idx
            op1, op2 = ops[idx], ops[idx+1]
            prefix = ops[:idx]
            suffix = ops[idx+2:]
            
            swapped_results = swap_adjacent(op1, op2, gb_dict)
            for s_coeff, s_ops in swapped_results:
                new_coeff = coeff * s_coeff
                new_ops = prefix + s_ops + suffix
                current_terms.append((new_coeff, new_ops))
                
    combined = {}
    for coeff, ops in fully_ordered:
        key = tuple(ops)
        combined[key] = combined.get(key, 0) + coeff
        
    res = []
    for ops_tuple, c in combined.items():
        c_simp = sp.simplify(c)
        if c_simp != 0:
            res.append(OperatorMonomial(c_simp, list(ops_tuple)))
            
    return res

if __name__ == '__main__':
    print("Test operator normal order code defined.")
