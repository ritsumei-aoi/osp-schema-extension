import sympy as sp
from collections import defaultdict

def p(i): return 1 if i in (0, 1) else 0

G = {}
for B in (0, 1):
    for A in (2, 3):
        G[(B, A)] = sp.Symbol(f'G_{B}_{A}')

def multiply_basis(word1, word2):
    word = list(word1 + word2)
    terms = {tuple(word): 1}
    changed = True
    while changed:
        changed = False
        new_terms = defaultdict(lambda: 0)
        for w, c in terms.items():
            if c == 0: continue
            inv = -1
            for i in range(len(w)-1):
                if w[i] > w[i+1]:
                    inv = i; break
            if inv == -1:
                zeroed = False
                for i in range(len(w)-1):
                    if w[i] == w[i+1] and p(w[i]) == 1:
                        zeroed = True; break
                if not zeroed: new_terms[w] += c
            else:
                changed = True
                A, B = w[inv], w[inv+1]
                prefix, suffix = w[:inv], w[inv+2:]
                if A == 1 and B == 0:
                    new_terms[prefix + suffix] += c
                    new_terms[prefix + (0, 1) + suffix] -= c
                elif A >= 2 and A % 2 == 1 and B == A - 1:
                    new_terms[prefix + suffix] += c
                    new_terms[prefix + (B, A) + suffix] += c
                elif A >= 2 and B in (0, 1):
                    new_terms[prefix + (B, A) + suffix] += c
                    new_terms[prefix + suffix] -= c * G[(B, A)]
                else:
                    sign = -1 if (p(A) == 1 and p(B) == 1) else 1
                    new_terms[prefix + (B, A) + suffix] += c * sign
        terms = new_terms
    return {w: sp.expand(c) for w, c in terms.items() if sp.expand(c) != 0}

def bracket(e1, e2, p1, p2):
    res = defaultdict(lambda: 0)
    for w1, c1 in e1.items():
        for w2, c2 in e2.items():
            prod1 = multiply_basis(w1, w2)
            for w, c in prod1.items(): res[w] += c1 * c2 * c
            prod2 = multiply_basis(w2, w1)
            sign = -1 if (p1 == 1 and p2 == 1) else 1
            for w, c in prod2.items(): res[w] -= c1 * c2 * c * sign
    return {w: sp.expand(c) for w, c in res.items() if sp.expand(c) != 0}

# 0: a+, 1: a-, 2: b+, 3: b-
# H1 = a+ a- + b+ b- = {(0, 1): 1, (2, 3): 1}
H1 = {(0, 1): 1, (2, 3): 1}
# E_{eps+d1} = a+ b+ = {(0, 2): 1}
E = {(0, 2): 1}

res = bracket(H1, E, 0, 1)
print("Bracket [H1, E]:")
for w, c in res.items():
    print(w, c)

