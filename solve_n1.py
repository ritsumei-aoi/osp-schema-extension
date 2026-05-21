import sympy as sp
from collections import defaultdict
import sys

n = 1

def p(i):
    return 1 if i in (0, 1) else 0

G = {}
# B in (0,1), A in (2, 3)
for B in (0, 1):
    for A in range(2, 2*n + 2):
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
            for w, c in prod1.items():
                res[w] += c1 * c2 * c
            prod2 = multiply_basis(w2, w1)
            sign = -1 if (p1 == 1 and p2 == 1) else 1
            for w, c in prod2.items():
                res[w] -= c1 * c2 * c * sign
    return {w: sp.expand(c) for w, c in res.items() if sp.expand(c) != 0}

# Define basis of C(2)
basis = []
basis_p = []

# Even
basis.append({(0, 1): 1}) # a+ a-
basis_p.append(0)
basis.append({(2, 2): 1}) # b+ b+
basis_p.append(0)
basis.append({(3, 3): 1}) # b- b-
basis_p.append(0)
basis.append({(2, 3): 1}) # b+ b-
basis_p.append(0)

# Odd
basis.append({(0, 2): 1}) # a+ b+
basis_p.append(1)
basis.append({(0, 3): 1}) # a+ b-
basis_p.append(1)
basis.append({(1, 2): 1}) # a- b+
basis_p.append(1)
basis.append({(1, 3): 1}) # a- b-
basis_p.append(1)

# Helper to project an element onto the basis
def project(e):
    coeffs = [0] * len(basis)
    e_copy = dict(e)
    
    # We might have scalar terms like () : c
    # But basis doesn't have (). 
    # Let's check if the basis spans the non-scalar part.
    # Actually, generators of Lie algebra shouldn't produce scalars in brackets,
    # except maybe central extensions.
    # Let's just match the keys exactly.
    for i, b in enumerate(basis):
        k = list(b.keys())[0]
        if k in e_copy:
            coeffs[i] = e_copy[k]
            del e_copy[k]
    
    # Check if there are any non-scalar terms left (ignore G terms that are scalar, etc.)
    # wait, G terms will have keys like (0,2), which match basis!
    # Any pure scalars like () should be central, we can ignore them if they are constant.
    return coeffs

# Precompute [X_i, X_j]_0 and \gamma(X_i, X_j)
brackets_0 = {}
gamma = {}

for i in range(len(basis)):
    for j in range(len(basis)):
        res = bracket(basis[i], basis[j], basis_p[i], basis_p[j])
        
        # separate res into part without G and part with G
        res_0 = {}
        res_gamma = {}
        for w, c in res.items():
            # evaluate at G=0
            c_0 = c.subs({G[k]: 0 for k in G})
            if c_0 != 0:
                res_0[w] = c_0
            c_gamma = c - c_0
            if c_gamma != 0:
                res_gamma[w] = c_gamma
                
        brackets_0[(i, j)] = project(res_0)
        gamma[(i, j)] = project(res_gamma)

# f is odd map. f(X_j) = sum \phi_{k, j} X_k
phi = sp.MatrixSymbol('phi', len(basis), len(basis))
# phi[k, j] is coefficient of X_k in f(X_j)
# p(X_k) must be 1 - p(X_j) for phi[k, j] to be non-zero

# \delta f(X_i, X_j) = (-1)^{p_i} [X_i, f(X_j)] - (-1)^{(p_i+1)p_j} [X_j, f(X_i)] - f([X_i, X_j]_0)
# We equate this to gamma(X_i, X_j)

equations = []
# For each pair (i, j) and each basis component k
for i in range(len(basis)):
    for j in range(len(basis)):
        # f(X_j) = sum_{m} phi_{m, j} X_m
        # [X_i, f(X_j)] = sum_m phi_{m, j} [X_i, X_m]_0
        term1 = [0] * len(basis)
        for m in range(len(basis)):
            if basis_p[m] != 1 - basis_p[j]: continue
            for k in range(len(basis)):
                term1[k] += phi[m, j] * brackets_0[(i, m)][k]
                
        # [X_j, f(X_i)]
        term2 = [0] * len(basis)
        for m in range(len(basis)):
            if basis_p[m] != 1 - basis_p[i]: continue
            for k in range(len(basis)):
                term2[k] += phi[m, i] * brackets_0[(j, m)][k]
                
        # f([X_i, X_j]_0)
        term3 = [0] * len(basis)
        for m in range(len(basis)):
            # [X_i, X_j]_0 component m
            c_m = brackets_0[(i, j)][m]
            if c_m != 0:
                # f(X_m) = sum_k phi_{k, m} X_k
                for k in range(len(basis)):
                    if basis_p[k] == 1 - basis_p[m]:
                        term3[k] += c_m * phi[k, m]
                        
        sign1 = (-1)**basis_p[i]
        sign2 = (-1)**((basis_p[i] + 1) * basis_p[j])
        
        for k in range(len(basis)):
            delta_f_ijk = sign1 * term1[k] - sign2 * term2[k] - term3[k]
            gamma_ijk = gamma[(i, j)][k]
            eq = delta_f_ijk - gamma_ijk
            if eq != 0:
                equations.append(eq)

# Variables to solve for
vars_to_solve = []
for i in range(len(basis)):
    for j in range(len(basis)):
        if basis_p[i] != basis_p[j]:
            vars_to_solve.append(phi[i, j])

sol = sp.solve(equations, vars_to_solve)
print("Solution:")
print(sol)

# Let's check if the system is solvable for ALL G.
# The equations are linear in phi and G.
# sp.solve will treat G as constants and solve for phi in terms of G.
# If sol is empty dict or doesn't exist, it means no solution.
