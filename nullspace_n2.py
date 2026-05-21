import sympy as sp
from collections import defaultdict

n = 2

def p(i): return 1 if i in (0, 1) else 0

G = {}
G_vars = []
for B in (0, 1):
    for A in range(2, 2*n + 2):
        sym = sp.Symbol(f'G_{B}_{A}')
        G[(B, A)] = sym
        G_vars.append(sym)

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

basis = [{(0, 1): 1}]
basis_p = [0]
for k in range(1, n+1):
    for l in range(k, n+1):
        if k == l:
            basis.append({(2*k, 2*k): 1})
            basis_p.append(0)
            basis.append({(2*k+1, 2*k+1): 1})
            basis_p.append(0)
            basis.append({(2*k, 2*k+1): 1})
            basis_p.append(0)
        else:
            basis.append({(2*k, 2*l): 1})
            basis_p.append(0)
            basis.append({(2*k+1, 2*l+1): 1})
            basis_p.append(0)
            basis.append({(2*k, 2*l+1): 1})
            basis_p.append(0)
            basis.append({(2*k+1, 2*l): 1})
            basis_p.append(0)

for k in range(1, n+1):
    basis.append({(0, 2*k): 1})
    basis_p.append(1)
    basis.append({(0, 2*k+1): 1})
    basis_p.append(1)
    basis.append({(1, 2*k): 1})
    basis_p.append(1)
    basis.append({(1, 2*k+1): 1})
    basis_p.append(1)

def project(e):
    coeffs = [0] * len(basis)
    e_copy = dict(e)
    for i, b in enumerate(basis):
        k = list(b.keys())[0]
        if k in e_copy:
            coeffs[i] = e_copy[k]
    return coeffs

brackets_0 = {}
gamma = {}
for i in range(len(basis)):
    for j in range(len(basis)):
        res = bracket(basis[i], basis[j], basis_p[i], basis_p[j])
        res_0, res_gamma = {}, {}
        for w, c in res.items():
            c_0 = c.subs({g: 0 for g in G_vars})
            if c_0 != 0: res_0[w] = c_0
            c_gamma = c - c_0
            if c_gamma != 0: res_gamma[w] = c_gamma
        brackets_0[(i, j)] = project(res_0)
        gamma[(i, j)] = project(res_gamma)

phi_vars = []
phi_map = {}
for i in range(len(basis)):
    for j in range(len(basis)):
        if basis_p[i] != basis_p[j]:
            var = sp.Symbol(f'phi_{i}_{j}')
            phi_vars.append(var)
            phi_map[(i, j)] = var
        else:
            phi_map[(i, j)] = 0

equations = []
for i in range(len(basis)):
    for j in range(len(basis)):
        term1 = [0] * len(basis)
        for m in range(len(basis)):
            if basis_p[m] == 1 - basis_p[j]:
                for k in range(len(basis)): term1[k] += phi_map[(m, j)] * brackets_0[(i, m)][k]
        term2 = [0] * len(basis)
        for m in range(len(basis)):
            if basis_p[m] == 1 - basis_p[i]:
                for k in range(len(basis)): term2[k] += phi_map[(m, i)] * brackets_0[(j, m)][k]
        term3 = [0] * len(basis)
        for m in range(len(basis)):
            c_m = brackets_0[(i, j)][m]
            if c_m != 0:
                for k in range(len(basis)):
                    if basis_p[k] == 1 - basis_p[m]:
                        term3[k] += c_m * phi_map[(k, m)]
        sign1 = (-1)**basis_p[i]
        sign2 = (-1)**((basis_p[i] + 1) * basis_p[j])
        
        for k in range(len(basis)):
            delta_f_ijk = sign1 * term1[k] - sign2 * term2[k] - term3[k]
            gamma_ijk = gamma[(i, j)][k]
            eq = delta_f_ijk - gamma_ijk
            if eq != 0: equations.append(eq)

A = []
B = []
for eq in equations:
    row_A = []
    for var in phi_vars:
        row_A.append(eq.coeff(var))
    row_B = []
    for var in G_vars:
        row_B.append((-eq).coeff(var))
    A.append(row_A)
    B.append(row_B)

A_mat = sp.Matrix(A)
B_mat = sp.Matrix(B)

nullspace = A_mat.T.nullspace()
conditions = []
for vec in nullspace:
    cond = vec.T * B_mat
    expr = 0
    for i, g in enumerate(G_vars):
        expr += cond[0, i] * g
    if expr != 0:
        conditions.append(expr)

import json
cond_strs = [str(sp.simplify(c)) for c in conditions]
with open("triviality_n2.json", "w") as f:
    json.dump({"conditions": cond_strs}, f)
print("Finished. Wrote conditions to triviality_n2.json")
