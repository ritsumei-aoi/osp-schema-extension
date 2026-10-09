#!/usr/bin/env python3
"""Debug the gauge-formula linear system."""
import sys
sys.path.insert(0, '.')
from fractions import Fraction as F
from verification.verify_triviality import C2Algebra
from verification.operator_algebra import compute_all_gammas

alg = C2Algebra()
all_gammas = compute_all_gammas(1, 2, 3, 4)

n_vars = 32
var_idx = {}
for j in range(4):
    for k in range(4):
        var_idx[('o%d' % (k+1), 'e%d' % (j+1))] = j * 4 + k
for k in range(4):
    for i in range(4):
        var_idx[('e%d' % (i+1), 'o%d' % (k+1))] = 16 + k * 4 + i

def g_map_symbolic(basis_j):
    terms = []
    if basis_j.startswith('e'):
        for k in range(4):
            target = 'o%d' % (k+1)
            vi = var_idx[(target, basis_j)]
            terms.append((vi, target))
    else:
        for i in range(4):
            target = 'e%d' % (i+1)
            vi = var_idx[(target, basis_j)]
            terms.append((vi, target))
    return terms

equations = []
basis = ['e1','e2','e3','e4','o1','o2','o3','o4']

for ii, bx in enumerate(basis):
    for jj, by in enumerate(basis):
        if jj <= ii:
            continue
        px = 1 if bx.startswith('o') else 0
        py = 1 if by.startswith('o') else 0
        gamma = all_gammas.get((bx, by), {})
        sign1 = F(-1)
        sign2 = F(-(-1)**(px*py))
        lhs_coeffs = {}
        for vi, target in g_map_symbolic(by):
            br = alg.bracket(bx, target)
            for out_label, coeff in br.items():
                lhs_coeffs.setdefault(out_label, {})
                lhs_coeffs[out_label][vi] = lhs_coeffs[out_label].get(vi, F(0)) + sign1 * coeff
        for vi, target in g_map_symbolic(bx):
            br = alg.bracket(by, target)
            for out_label, coeff in br.items():
                lhs_coeffs.setdefault(out_label, {})
                lhs_coeffs[out_label][vi] = lhs_coeffs[out_label].get(vi, F(0)) + sign2 * coeff
        xy_br = alg.bracket(bx, by)
        for mid_label, mid_coeff in xy_br.items():
            for vi, target in g_map_symbolic(mid_label):
                lhs_coeffs.setdefault(target, {})
                lhs_coeffs[target][vi] = lhs_coeffs[target].get(vi, F(0)) + mid_coeff
        all_labels = set(list(gamma.keys()))
        for lbl in lhs_coeffs:
            all_labels.add(lbl)
        for out_label in all_labels:
            coeffs = lhs_coeffs.get(out_label, {})
            rhs = gamma.get(out_label, F(0))
            if coeffs or rhs != 0:
                equations.append((dict(coeffs), rhs, '(%s,%s)[%s]' % (bx, by, out_label)))

n_eq = len(equations)
A = [[F(0)] * n_vars for _ in range(n_eq)]
b = [F(0)] * n_eq
labels = []
for i, (coeffs, rhs, label) in enumerate(equations):
    for vi, c in coeffs.items():
        A[i][vi] = c
    b[i] = rhs
    labels.append(label)

M = [A[i][:] + [b[i]] for i in range(n_eq)]
m, n = n_eq, n_vars
pivot_cols = []
row_idx = 0
row_perm = list(range(m))
for col in range(n):
    pivot_row = None
    for r in range(row_idx, m):
        if M[r][col] != 0:
            pivot_row = r
            break
    if pivot_row is None:
        continue
    M[row_idx], M[pivot_row] = M[pivot_row], M[row_idx]
    row_perm[row_idx], row_perm[pivot_row] = row_perm[pivot_row], row_perm[row_idx]
    pivot_cols.append(col)
    pv = M[row_idx][col]
    for r in range(m):
        if r != row_idx and M[r][col] != 0:
            factor = M[r][col] / pv
            for c2 in range(n + 1):
                M[r][c2] -= factor * M[row_idx][c2]
    row_idx += 1

rank = len(pivot_cols)
print('Rank: %d, Equations: %d' % (rank, n_eq))

incon = 0
for r in range(rank, m):
    if M[r][n] != 0:
        orig = row_perm[r]
        print('INCON row %d (orig %d): %s, rhs=%s' % (r, orig, labels[orig], M[r][n]))
        incon += 1
        if incon >= 20:
            break

if incon == 0:
    print('CONSISTENT!')
    sol = [F(0)] * n_vars
    for i, col in enumerate(pivot_cols):
        sol[col] = M[i][n] / M[i][col]
    for j in range(4):
        terms = []
        for k in range(4):
            vi = j * 4 + k
            if sol[vi] != 0:
                terms.append('%s*o%d' % (sol[vi], k+1))
        if terms:
            print('  g(e%d) = %s' % (j+1, ' + '.join(terms)))
    for k in range(4):
        terms = []
        for i in range(4):
            vi = 16 + k * 4 + i
            if sol[vi] != 0:
                terms.append('%s*e%d' % (sol[vi], i+1))
        if terms:
            print('  g(o%d) = %s' % (k+1, ' + '.join(terms)))
