import sympy as sp
from collections import defaultdict

# Let's define the oscillator algebra symbolically
# An oscillator is represented by a tuple (type, index, sign):
# ('a', 1, 1) for a1+
# ('a', 1, -1) for a1-
# ('b', j, 1) for bj+
# ('b', j, -1) for bj-

# A monomial is a tuple of oscillators, e.g. (('a', 1, 1), ('b', 1, 1))
# An element of the algebra is a linear combination of normal-ordered monomials,
# with coefficients being expressions in symbols (numbers, gb's, kappa).

# Standard normal order:
# 1. a1+ (at most power 1)
# 2. a1- (at most power 1)
# 3. bj+ (any power)
# 4. bj- (any power)
# ordering by j: b1+, b1-, b2+, b2-, ...

def oscillator_key(osc):
    typ, idx, sgn = osc
    if typ == 'a':
        return (0, idx, -sgn) # a+ comes before a-
    else:
        return (1, idx, -sgn) # b+ comes before b-

def normal_order_monomial(monomial, gb_params):
    # monomial is a tuple of oscillators
    # We will sort by bubble-like adjacent swaps using the commutation relations.
    # Returns a dict: {monomial: coeff}
    # where monomial is a sorted tuple, and coeff is sympy expression
    
    # We'll use a queue of terms
    current = {monomial: sp.Integer(1)}
    
    # Helper to check if a monomial is sorted
    def is_sorted(m):
        for i in range(len(m) - 1):
            k1 = oscillator_key(m[i])
            k2 = oscillator_key(m[i+1])
            if k1 > k2:
                return False
            if k1 == k2 and m[i][0] == 'a':
                # (a+)^2 = 0 or (a-)^2 = 0
                return False
        return True

    while True:
        all_done = True
        next_dict = defaultdict(lambda: sp.Integer(0))
        for m, c in current.items():
            if c == 0:
                continue
            # find first inversion
            inversion_idx = -1
            for i in range(len(m) - 1):
                k1 = oscillator_key(m[i])
                k2 = oscillator_key(m[i+1])
                if k1 > k2 or (k1 == k2 and m[i][0] == 'a'):
                    inversion_idx = i
                    break
            
            if inversion_idx == -1:
                next_dict[m] += c
            else:
                all_done = False
                i = inversion_idx
                o1 = m[i]
                o2 = m[i+1]
                prefix = m[:i]
                suffix = m[i+2:]
                
                # Case 1: same fermionic oscillator (a+ a+ or a- a-)
                if o1 == o2 and o1[0] == 'a':
                    # (a+)^2 = 0, (a-)^2 = 0
                    continue # term vanishes
                
                # Case 2: a- a+ -> 1 - a+ a-
                elif o1 == ('a', 1, -1) and o2 == ('a', 1, 1):
                    # a- a+ = 1 - a+ a-
                    # term 1: - a+ a-
                    m_swap = prefix + (o2, o1) + suffix
                    next_dict[m_swap] += -c
                    # term 2: + 1
                    m_scalar = prefix + suffix
                    next_dict[m_scalar] += c
                
                # Case 3: b_j^- b_k^+ -> b_k^+ b_j^- + delta_{jk}
                elif o1[0] == 'b' and o2[0] == 'b':
                    # If o1 > o2 in key, then o1 must be b^- and o2 must be b^+, or diff indices
                    # CCR: [b_j^s, b_k^s'] = 0 unless j=k, s=-1, s'=+1
                    # [b_j^-, b_j^+] = 1 => b_j^- b_j^+ = b_j^+ b_j^- + 1
                    m_swap = prefix + (o2, o1) + suffix
                    next_dict[m_swap] += c
                    if o1[1] == o2[1] and o1[2] == -1 and o2[2] == 1:
                        m_scalar = prefix + suffix
                        next_dict[m_scalar] += c
                
                # Case 4: b_j^s and a_1^sigma
                # We have o1 = ('b', j, s) and o2 = ('a', 1, sigma)
                # Relation: [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa
                # => b_j^s a_1^sigma = a_1^sigma b_j^s - gb_{sigma, j, s} * kappa
                elif o1[0] == 'b' and o2[0] == 'a':
                    sigma = '+' if o2[2] == 1 else '-'
                    j = o1[1]
                    s = '+' if o1[2] == 1 else '-'
                    gb_val = gb_params.get((sigma, j, s), sp.Symbol(f"gb_{sigma}{j}{s}"))
                    kappa = sp.Symbol('kappa')
                    
                    # term 1: a_1^sigma b_j^s
                    m_swap = prefix + (o2, o1) + suffix
                    next_dict[m_swap] += c
                    # term 2: - gb * kappa
                    m_scalar = prefix + suffix
                    next_dict[m_scalar] += -c * gb_val * kappa
                else:
                    # other swaps commute trivially
                    m_swap = prefix + (o2, o1) + suffix
                    next_dict[m_swap] += c
        current = next_dict
        if all_done:
            break
            
    return {m: sp.expand(c) for m, c in current.items() if sp.expand(c) != 0}

print('Normal order function defined successfully')
