"""
Normal ordering reduction in U(A) for C(n+1).
"""
import sympy as sp
from collections import defaultdict

def create_algebra(n=1):
    # Oscillators representation:
    # 'a+': fermion a_1^+
    # 'a-': fermion a_1^-
    # ('b+', j): boson b_j^+
    # ('b-', j): boson b_j^-
    
    # Symbols for gb parameters:
    # gb(sigma, j, s) where sigma in ['+', '-'], s in ['+', '-'], j in 1..n
    gb = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                gb[(sigma, j, s)] = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                
    # Normal order priority (lower index comes first):
    # a+, a-, then b1+, b1-, b2+, b2-, ...
    priority = {'a+': 0, 'a-': 1}
    for j in range(1, n + 1):
        priority[('b+', j)] = 2 * j
        priority[('b-', j)] = 2 * j + 1
        
    def parity(osc):
        if osc in ('a+', 'a-'):
            return 1
        return 0

    def word_parity(word):
        return sum(parity(o) for o in word) % 2

    # A state is a dict: tuple of oscillators -> (coeff_0, coeff_kappa)
    # where coeff_0 is undeformed, coeff_kappa is coefficient of kappa.
    
    def reduce_word(word):
        # We perform adjacent swaps until sorted or zeroed out
        # Queue of (list_of_osc, coeff_0, coeff_kappa)
        terms = defaultdict(lambda: [sp.Integer(0), sp.Integer(0)])
        
        queue = [(list(word), sp.Integer(1), sp.Integer(0))]
        
        while queue:
            w, c0, ck = queue.pop()
            if c0 == 0 and ck == 0:
                continue
                
            # Check for adjacent violations
            # First check if any (a+)^2 or (a-)^2 exists
            # Wait, they might not be adjacent yet, but let's just do bubble sort style swaps
            swapped = False
            for i in range(len(w) - 1):
                o1, o2 = w[i], w[i+1]
                
                # Check (a+)^2 = 0, (a-)^2 = 0
                if o1 == o2 and o1 in ('a+', 'a-'):
                    c0, ck = sp.Integer(0), sp.Integer(0)
                    swapped = True
                    break
                
                # Check if out of order
                if priority[o1] > priority[o2]:
                    # Need to swap o1 and o2
                    # What is o1 o2 in terms of o2 o1?
                    # Case 1: a- a+ = 1 - a+ a-
                    if o1 == 'a-' and o2 == 'a+':
                        # w[:i] + ['a-', 'a+'] + w[i+2:]
                        # = w[:i] + w[i+2:] (coeff 1) - w[:i] + ['a+', 'a-'] + w[i+2:]
                        w_comm = w[:i] + w[i+2:]
                        w_swap = w[:i] + ['a+', 'a-'] + w[i+2:]
                        queue.append((w_comm, c0, ck))
                        queue.append((w_swap, -c0, -ck))
                        swapped = True
                        break
                    
                    # Case 2: b_j- b_k+
                    elif isinstance(o1, tuple) and isinstance(o2, tuple):
                        # Both are bosons
                        s1, j1 = o1
                        s2, j2 = o2
                        if s1 == 'b-' and s2 == 'b+' and j1 == j2:
                            # b_j- b_j+ = b_j+ b_j- + 1
                            w_comm = w[:i] + w[i+2:]
                            w_swap = w[:i] + [o2, o1] + w[i+2:]
                            queue.append((w_comm, c0, ck))
                            queue.append((w_swap, c0, ck))
                            swapped = True
                            break
                        else:
                            # All other bosons commute!
                            w_swap = w[:i] + [o2, o1] + w[i+2:]
                            queue.append((w_swap, c0, ck))
                            swapped = True
                            break
                            
                    # Case 3: boson o1 and fermion o2
                    elif isinstance(o1, tuple) and o2 in ('a+', 'a-'):
                        # o1 is ('b+', j) or ('b-', j)
                        # o2 is 'a+' or 'a-'
                        # b_j^s a_1^sigma = a_1^sigma b_j^s - gb_{sigma, j, s} * kappa
                        s_b, j_b = o1
                        s_b_sign = '+' if s_b == 'b+' else '-'
                        sigma = '+' if o2 == 'a+' else '-'
                        param = gb[(sigma, j_b, s_b_sign)]
                        
                        # Swapped term: o2 o1
                        w_swap = w[:i] + [o2, o1] + w[i+2:]
                        queue.append((w_swap, c0, ck))
                        
                        # Commutator term: - param * kappa * w[:i] + w[i+2:]
                        # Note: this contributes to ck with factor -c0 * param (since c0 * kappa * param)
                        if c0 != 0:
                            w_comm = w[:i] + w[i+2:]
                            queue.append((w_comm, sp.Integer(0), -c0 * param))
                        swapped = True
                        break
                        
                    else:
                        raise ValueError(f"Unhandled pair {o1}, {o2}")
                        
            if not swapped:
                # Also check if there are two identical fermions anywhere
                num_ap = sum(1 for o in w if o == 'a+')
                num_am = sum(1 for o in w if o == 'a-')
                if num_ap > 1 or num_am > 1:
                    continue
                terms[tuple(w)][0] += c0
                terms[tuple(w)][1] += ck
                
        # Clean up zero terms
        res = {}
        for k, v in terms.items():
            c0 = sp.simplify(v[0])
            ck = sp.simplify(v[1])
            if c0 != 0 or ck != 0:
                res[k] = (c0, ck)
        return res

    return gb, reduce_word

if __name__ == '__main__':
    gb, reduce_word = create_algebra(1)
    print("Testing a- a+:")
    print(reduce_word(['a-', 'a+']))
    print("Testing b1- b1+:")
    print(reduce_word([('b-', 1), ('b+', 1)]))
    print("Testing b1+ a+:")
    print(reduce_word([('b+', 1), 'a+']))
