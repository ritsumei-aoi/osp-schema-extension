import sympy as sp
from collections import defaultdict
from itertools import combinations_with_replacement, product

# We will build a complete, self-contained solver for C(n+1) triviality.

def get_basis_and_algebra(n):
    """
    Constructs the basis of g = C(n+1) = osp(2|2n) and all bracket operations modulo scalar identity 1.
    """
    # Bosonic indices (k, s)
    b_indices = []
    for k in range(1, n+1):
        b_indices.append((k, '+'))
        b_indices.append((k, '-'))
        
    # 1. Even basis elements
    # Z = a1+ a1-
    even_basis = [('Z',)]
    
    # sp(2n) basis:
    # We can index sp(2n) generators by sorted pairs of (k, s)
    # To be precise, let's use:
    # - (b_k+, b_l+) for 1 <= k <= l <= n
    # - (b_k-, b_l-) for 1 <= k <= l <= n
    # - (b_k+, b_l-) for 1 <= k, l <= n
    sp_basis = []
    for k in range(1, n+1):
        for l in range(k, n+1):
            sp_basis.append(( ('b', k, '+'), ('b', l, '+') ))
            sp_basis.append(( ('b', k, '-'), ('b', l, '-') ))
    for k in range(1, n+1):
        for l in range(1, n+1):
            sp_basis.append(( ('b', k, '+'), ('b', l, '-') ))
            
    # Remove duplicate representation if any:
    # Notice ('b', k, '+'), ('b', l, '+') with k <= l are unique.
    # ('b', k, '-'), ('b', l, '-') with k <= l are unique.
    # ('b', k, '+'), ('b', l, '-') for all 1 <= k, l <= n are n^2 unique generators.
    # Total count = n(n+1)/2 + n(n+1)/2 + n^2 = n^2 + n + n^2 = 2n^2 + n. Perfect!
    
    even_basis.extend(sp_basis)
    
    # 2. Odd basis elements: ('O', sigma, k, s)
    odd_basis = []
    for sigma in ['+', '-']:
        for k in range(1, n+1):
            for s in ['+', '-']:
                odd_basis.append(('O', sigma, k, s))
                
    return even_basis, odd_basis

def monomial_to_vec(mon_dict, even_basis, odd_basis, n):
    """
    Converts a normal-ordered polynomial (dict of Monomial keys -> coeffs)
    into a vector over g = C(n+1) modulo scalar 1, separated by kappa=0 and kappa=1.
    
    Key format in mon_dict: (u_p, u_m, b_ops, kap)
    - u_p: 0 or 1 for a1+
    - u_m: 0 or 1 for a1-
    - b_ops: tuple of (k, s)
    - kap: 0 or 1 for kappa
    """
    vec_0 = {b: sp.sympify(0) for b in even_basis + odd_basis} # kappa^0 part
    vec_1 = {b: sp.sympify(0) for b in even_basis + odd_basis} # kappa^1 part
    scalar_0 = sp.sympify(0)
    scalar_1 = sp.sympify(0)
    
    for (u_p, u_m, b_ops, kap), c in mon_dict.items():
        if c == 0:
            continue
            
        target_vec = vec_1 if kap == 1 else vec_0
        
        # Determine element:
        # Case A: u_p=0, u_m=0 -> pure bosonic
        if u_p == 0 and u_m == 0:
            if len(b_ops) == 0: # scalar 1
                if kap == 1: scalar_1 += c
                else: scalar_0 += c
            elif len(b_ops) == 2: # quadratic in b
                op1, op2 = b_ops[0], b_ops[1]
                # Match with sp_basis representation:
                # sp_basis elements:
                # 1. ( ('b', k, '+'), ('b', l, '+') ) for k <= l
                # 2. ( ('b', k, '-'), ('b', l, '-') ) for k <= l
                # 3. ( ('b', k, '+'), ('b', l, '-') ) for 1 <= k, l <= n
                if op1[1] == '+' and op2[1] == '+':
                    k, l = min(op1[0], op2[0]), max(op1[0], op2[0])
                    b_elem = ( ('b', k, '+'), ('b', l, '+') )
                    target_vec[b_elem] += c
                elif op1[1] == '-' and op2[1] == '-':
                    k, l = min(op1[0], op2[0]), max(op1[0], op2[0])
                    b_elem = ( ('b', k, '-'), ('b', l, '-') )
                    target_vec[b_elem] += c
                elif op1[1] == '+' and op2[1] == '-':
                    b_elem = ( ('b', op1[0], '+'), ('b', op2[0], '-') )
                    target_vec[b_elem] += c
                elif op1[1] == '-' and op2[1] == '+':
                    # b_k- b_l+ = b_l+ b_k- + delta_{kl}
                    b_elem = ( ('b', op2[0], '+'), ('b', op1[0], '-') )
                    target_vec[b_elem] += c
                    if op1[0] == op2[0]:
                        if kap == 1: scalar_1 += c
                        else: scalar_0 += c
                else:
                    raise ValueError(f"Unknown b_ops quadratic: {b_ops}")
            else:
                raise ValueError(f"Unexpected b_ops degree: {b_ops}")
                
        # Case B: u_p=1, u_m=1 -> a1+ a1- * (b_ops)
        elif u_p == 1 and u_m == 1:
            if len(b_ops) == 0: # Z = a1+ a1-
                target_vec[('Z',)] += c
            else:
                # Higher order term? Should not occur in g
                raise ValueError(f"Higher order element in g: a1+ a1- {b_ops}")
                
        # Case C: (u_p, u_m) = (1, 0) or (0, 1) -> odd generator
        elif (u_p == 1 and u_m == 0) or (u_p == 0 and u_m == 1):
            sigma = '+' if u_p == 1 else '-'
            if len(b_ops) == 1:
                k, s = b_ops[0][0], b_ops[0][1]
                target_vec[('O', sigma, k, s)] += c
            else:
                raise ValueError(f"Unexpected odd element: a1^{sigma} {b_ops}")
                
    return vec_0, vec_1

print("Helper functions defined.")
