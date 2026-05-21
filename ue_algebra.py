import sympy as sp
from collections import defaultdict
import sys

def get_n():
    return 1 # Start with n=1

n = get_n()

# Oscillators: 
# 0: a+ (odd)
# 1: a- (odd)
# 2k: b+_k (even)
# 2k+1: b-_k (even)

def p(i):
    return 1 if i in (0, 1) else 0

# G variables: G[B, A] corresponds to gb_{B, A} * \kappa
G = {}
for B in (0, 1):
    for A in range(2, 2*n + 2):
        G[(B, A)] = sp.Symbol(f'G_{B}_{A}')

def multiply_basis(word1, word2):
    # concatenate words and normal order
    word = list(word1 + word2)
    
    # We maintain a sum of (coefficient, word)
    # coefficient is a sympy expression
    terms = {tuple(word): 1}
    
    changed = True
    while changed:
        changed = False
        new_terms = defaultdict(lambda: 0)
        for w, c in terms.items():
            if c == 0:
                continue
            
            # find first inversion
            inv = -1
            for i in range(len(w)-1):
                if w[i] > w[i+1]:
                    inv = i
                    break
            
            if inv == -1:
                # check for adjacent identical fermions
                zeroed = False
                for i in range(len(w)-1):
                    if w[i] == w[i+1] and p(w[i]) == 1:
                        zeroed = True
                        break
                if not zeroed:
                    new_terms[w] += c
            else:
                changed = True
                A = w[inv]
                B = w[inv+1]
                
                prefix = w[:inv]
                suffix = w[inv+2:]
                
                if A == 1 and B == 0:
                    # a- a+ = 1 - a+ a-
                    new_terms[prefix + suffix] += c
                    new_terms[prefix + (0, 1) + suffix] -= c
                elif A >= 2 and A % 2 == 1 and B == A - 1:
                    # b- b+ = 1 + b+ b-
                    new_terms[prefix + suffix] += c
                    new_terms[prefix + (B, A) + suffix] += c
                elif A >= 2 and B in (0, 1):
                    # b a = a b - G
                    new_terms[prefix + (B, A) + suffix] += c
                    new_terms[prefix + suffix] -= c * G[(B, A)]
                else:
                    # O_A O_B = (-1)^{p(A)p(B)} O_B O_A
                    sign = -1 if (p(A) == 1 and p(B) == 1) else 1
                    new_terms[prefix + (B, A) + suffix] += c * sign
                    
        terms = new_terms
        
    # remove zeros
    return {w: c for w, c in terms.items() if sp.expand(c) != 0}

def add_elements(e1, e2):
    res = defaultdict(lambda: 0)
    for w, c in e1.items():
        res[w] += c
    for w, c in e2.items():
        res[w] += c
    return {w: sp.expand(c) for w, c in res.items() if sp.expand(c) != 0}

def scale_element(e, scalar):
    return {w: sp.expand(c * scalar) for w, c in e.items() if sp.expand(c * scalar) != 0}

def bracket(e1, e2, p1, p2):
    # [e1, e2] = e1 e2 - (-1)^{p1 p2} e2 e1
    res = defaultdict(lambda: 0)
    
    for w1, c1 in e1.items():
        for w2, c2 in e2.items():
            prod1 = multiply_basis(w1, w2)
            for w, c in prod1.items():
                res[w] += c1 * c2 * c

            prod2 = multiply_basis(w2, w1)
            sign = -1 if (p1 == 1 and p2 == 1) else 1
            for w, c in prod2.items():
                res[w] -= c1 * c2 * c * sign
                
    return {w: sp.expand(c) for w, c in res.items() if sp.expand(c) != 0}

# test
e1 = {(0, 2): 1} # a+ b+ (odd)
e2 = {(1, 3): 1} # a- b- (odd)
# [e1, e2] = a+ b+ a- b- + a- b- a+ b+
res = bracket(e1, e2, 1, 1)
for w, c in res.items():
    print(w, c)

