#!/usr/bin/env python3
"""Debug the linear system to find inconsistent equations."""
import sys
sys.path.insert(0, '.')
from fractions import Fraction as F
from verification.verify_triviality import C2Algebra

alg = C2Algebra()
odd_data = {'o1': ('+','+'), 'o2': ('+','-'), 'o3': ('-','+'), 'o4': ('-','-')}
gb = {('+',1,'+'): F(1), ('+',1,'-'): F(2), ('-',1,'+'): F(3), ('-',1,'-'): F(4)}

def gb_val(sigma, s):
    return gb[(sigma, 1, s)]

def bb_to_even(s1, s2):
    if s1 == '+' and s2 == '+': return {'e3': F(2)}
    if s1 == '-' and s2 == '-': return {'e4': F(2)}
    if s1 == '+' and s2 == '-': return {'e2': F(-1)}
    if s1 == '-' and s2 == '+': return {'e2': F(-1)}

def gamma_oo(oa, ob):
    sa, ss = odd_data[oa]
    sb, st = odd_data[ob]
    r = {}
    c1 = gb_val(sb, ss)
    c2 = gb_val(sa, st)
    t1 = [k for k, (s, t) in odd_data.items() if s == sa and t == st][0]
    t2 = [k for k, (s, t) in odd_data.items() if s == sb and t == ss][0]
    if c1 != 0: r[t1] = r.get(t1, F(0)) + c1
    if c2 != 0: r[t2] = r.get(t2, F(0)) + c2
    return {k: v for k, v in r.items() if v != 0}

def gamma_eo(ea, ok):
    sigma, s = odd_data[ok]
    g_sp = gb_val(sigma, '+')
    g_sm = gb_val(sigma, '-')
    g_ss = gb_val(sigma, s)
    if ea == 'e1':
        r = {}
        bb1 = bb_to_even('-', s)
        bb2 = bb_to_even('+', s)
        for k, v in bb1.items(): r[k] = r.get(k, F(0)) - g_sp * v
        for k, v in bb2.items(): r[k] = r.get(k, F(0)) - g_sm * v
        r['e1'] = r.get('e1', F(0)) - g_ss
        r['e2'] = r.get('e2', F(0)) - g_ss
        return {k: v for k, v in r.items() if v != 0}
    elif ea == 'e2':
        r = {}
        bb1 = bb_to_even('-', s)
        bb2 = bb_to_even('+', s)
        for k, v in bb1.items(): r[k] = r.get(k, F(0)) + g_sp * v
        for k, v in bb2.items(): r[k] = r.get(k, F(0)) + g_sm * v
        return {k: v for k, v in r.items() if v != 0}
    elif ea == 'e3':
        bb = bb_to_even('+', s)
        return {k: -g_sp * v for k, v in bb.items() if -g_sp * v != 0}
    elif ea == 'e4':
        bb = bb_to_even('-', s)
        return {k: -g_sm * v for k, v in bb.items() if -g_sm * v != 0}
    return {}

n_vars = 32
var_idx = {}
for j in range(4):
    for k in range(4):
        var_idx[(f'o{k+1}', f'e{j+1}')] = j * 4 + k
for k in range(4):
    for i in range(4):
        var_idx[(f'e{i+1}', f'o{k+1}')] = 16 + k * 4 + i

def g_map_symbolic(basis_j):
    terms = []
    if basis_j.startswith('e'):
        for k in range(4):
            target = f'o{k+1}'
            vi = var_idx[(target, basis_j)]
            terms.append((vi, target))
    else:
        for i in range(4):
            target = f'e{i+1}'
            vi = var_idx[(target, basis_j)]
            terms.append((vi, target))
    return terms

equations = []

# OO sector
for ii, oa in enumerate(alg.odd):
    for jj, ob in enumerate(alg.odd):
        if jj < ii: continue
        gamma = gamma_oo(oa, ob)
        lhs_coeffs = {}
        for vi, target in g_map_symbolic(ob):
            br = alg.bracket(oa, target)
            for out_label, coeff in br.items():
                lhs_coeffs.setdefault(out_label, {})
                lhs_coeffs[out_label][vi] = lhs_coeffs[out_label].get(vi, F(0)) - coeff
        for vi, target in g_map_symbolic(oa):
            br = alg.bracket(ob, target)
            for out_label, coeff in br.items():
                lhs_coeffs.setdefault(out_label, {})
                lhs_coeffs[out_label][vi] = lhs_coeffs[out_label].get(vi, F(0)) - coeff
        xy_br = alg.bracket(oa, ob)
        for mid_label, mid_coeff in xy_br.items():
            for vi, target in g_map_symbolic(mid_label):
                lhs_coeffs.setdefault(target, {})
                lhs_coeffs[target][vi] = lhs_coeffs[target].get(vi, F(0)) - mid_coeff
        all_labels = set(list(gamma.keys()))
        for lbl in lhs_coeffs: all_labels.add(lbl)
        for out_label in all_labels:
            coeffs = lhs_coeffs.get(out_label, {})
            rhs = gamma.get(out_label, F(0))
            if coeffs or rhs != 0:
                equations.append((dict(coeffs), rhs, f'oo({oa},{ob})[{out_label}]'))

# EE sector
for ii, ea in enumerate(alg.even):
    for jj, eb in enumerate(alg.even):
        if jj <= ii: continue
        lhs_coeffs = {}
        for vi, target in g_map_symbolic(eb):
            br = alg.bracket(ea, target)
            for out_label, coeff in br.items():
                lhs_coeffs.setdefault(out_label, {})
                lhs_coeffs[out_label][vi] = lhs_coeffs[out_label].get(vi, F(0)) + coeff
        for vi, target in g_map_symbolic(ea):
            br = alg.bracket(eb, target)
            for out_label, coeff in br.items():
                lhs_coeffs.setdefault(out_label, {})
                lhs_coeffs[out_label][vi] = lhs_coeffs[out_label].get(vi, F(0)) - coeff
        ab_br = alg.bracket(ea, eb)
        for mid_label, mid_coeff in ab_br.items():
            for vi, target in g_map_symbolic(mid_label):
                lhs_coeffs.setdefault(target, {})
                lhs_coeffs[target][vi] = lhs_coeffs[target].get(vi, F(0)) - mid_coeff
        for out_label, coeffs in lhs_coeffs.items():
            equations.append((coeffs, F(0), f'ee({ea},{eb})[{out_label}]'))

# EO sector
for ea in alg.even:
    for ok in alg.odd:
        gamma = gamma_eo(ea, ok)
        lhs_coeffs = {}
        for vi, target in g_map_symbolic(ok):
            br = alg.bracket(ea, target)
            for out_label, coeff in br.items():
                lhs_coeffs.setdefault(out_label, {})
                lhs_coeffs[out_label][vi] = lhs_coeffs[out_label].get(vi, F(0)) + coeff
        for vi, target in g_map_symbolic(ea):
            br = alg.bracket(ok, target)
            for out_label, coeff in br.items():
                lhs_coeffs.setdefault(out_label, {})
                lhs_coeffs[out_label][vi] = lhs_coeffs[out_label].get(vi, F(0)) + coeff
        ax_br = alg.bracket(ea, ok)
        for mid_label, mid_coeff in ax_br.items():
            for vi, target in g_map_symbolic(mid_label):
                lhs_coeffs.setdefault(target, {})
                lhs_coeffs[target][vi] = lhs_coeffs[target].get(vi, F(0)) - mid_coeff
        all_labels = set(list(gamma.keys()))
        for lbl in lhs_coeffs: all_labels.add(lbl)
        for out_label in all_labels:
            coeffs = lhs_coeffs.get(out_label, {})
            rhs = gamma.get(out_label, F(0))
            if coeffs or rhs != 0:
                equations.append((coeffs, rhs, f'eo({ea},{ok})[{out_label}]'))

n_eq = len(equations)
A = [[F(0)] * n_vars for _ in range(n_eq)]
b = [F(0)] * n_eq
labels = []
for i, (coeffs, rhs, label) in enumerate(equations):
    for vi, c in coeffs.items():
        A[i][vi] = c
    b[i] = rhs
    labels.append(label)

# Gaussian elimination with row tracking
M = [A[i][:] + [b[i]] for i in range(n_eq)]
m, n = n_eq, n_vars
pivot_cols = []
row_idx = 0
row_perm = list(range(m))

for col in range(n):
    pivot = None
    for r in range(row_idx, m):
        if M[r][col] != 0:
            pivot = r
            break
    if pivot is None:
        continue
    M[row_idx], M[pivot] = M[pivot], M[row_idx]
    row_perm[row_idx], row_perm[pivot] = row_perm[pivot], row_perm[row_idx]
    pivot_cols.append(col)
    pv = M[row_idx][col]
    for r in range(m):
        if r != row_idx and M[r][col] != 0:
            factor = M[r][col] / pv
            for c in range(n + 1):
                M[r][c] -= factor * M[row_idx][c]
    row_idx += 1

rank = len(pivot_cols)
print(f'Equations: {n_eq}, Variables: {n_vars}, Rank: {rank}')
print(f'Pivot columns: {pivot_cols}')

incon_count = 0
for r in range(rank, m):
    if M[r][n] != 0:
        orig = row_perm[r]
        print(f'INCONSISTENT row {r} (orig={orig}): {labels[orig]}, rhs_after_elim={M[r][n]}')
        incon_count += 1
        if incon_count >= 10:
            break

if incon_count == 0:
    print('System is CONSISTENT!')
    sol = [F(0)] * n_vars
    for i, col in enumerate(pivot_cols):
        sol[col] = M[i][n] / M[i][col]
    print('Solution found.')
    for j, ej in enumerate(alg.even):
        terms = []
        for k in range(4):
            vi = j * 4 + k
            if sol[vi] != 0:
                terms.append(f'{sol[vi]}*{alg.odd[k]}')
        if terms:
            print(f'  g({ej}) = {" + ".join(terms)}')
    for k, ok in enumerate(alg.odd):
        terms = []
        for i in range(4):
            vi = 16 + k * 4 + i
            if sol[vi] != 0:
                terms.append(f'{sol[vi]}*{alg.even[i]}')
        if terms:
            print(f'  g({ok}) = {" + ".join(terms)}')
