#!/usr/bin/env python3
"""[gemini38f-A1 copy of luna-r3-A1: E_2del coefficient 1] Scribe check for luna-r2-A1 I03 (copied from luna-A2): independent oscillator realization of C(n+1)
(docs/json_schema_specification.md after I02: E_{±2δ_k} = (b_k^±)^2 for all k, coefficient 1), brackets computed
by normal ordering, decomposed on the basis; compared with the Worker's JSON
(realizations and structure_constants). Reads the JSON only; writes nothing."""
import json
import sys
from fractions import Fraction as F
from itertools import product

# symbols: ('a', s) fermion, ('b', i, s) boson; s = +1 / -1
def key(x):
    if x[0] == 'a':
        return (0, 0 if x[1] > 0 else 1)
    return (1 if x[2] > 0 else 2, x[1])

def normal(word):
    """word (tuple) -> dict normal-ordered word -> coeff"""
    out = {}
    stack = [(tuple(word), F(1))]
    while stack:
        w, c = stack.pop()
        for k in range(len(w) - 1):
            x, y = w[k], w[k + 1]
            if x[0] == 'a' and y[0] == 'a' and x[1] == y[1]:
                break  # a^± a^± = 0
            if key(x) > key(y):
                if x[0] == 'a' and y[0] == 'a':          # a- a+ = 1 - a+ a-
                    stack.append((w[:k] + w[k + 2:], c))
                    stack.append((w[:k] + (y, x) + w[k + 2:], -c))
                elif x[0] == 'b' and y[0] == 'b' and x[1] == y[1] and x[2] < 0 < y[2]:
                    stack.append((w[:k] + w[k + 2:], c))   # b- b+ = b+ b- + 1
                    stack.append((w[:k] + (y, x) + w[k + 2:], c))
                else:                                      # commuting (boson-boson, boson-fermion)
                    stack.append((w[:k] + (y, x) + w[k + 2:], c))
                break
        else:
            out[w] = out.get(w, 0) + c
            continue
    return {w: c for w, c in out.items() if c}

def mul(p, q):
    r = {}
    for (w1, c1), (w2, c2) in product(p.items(), q.items()):
        for w, c in normal(w1 + w2).items():
            r[w] = r.get(w, 0) + c1 * c2 * c
    return {w: c for w, c in r.items() if c}

def add(p, q, s=1):
    r = dict(p)
    for w, c in q.items():
        r[w] = r.get(w, 0) + s * c
    return {w: c for w, c in r.items() if c}

A = lambda s: ('a', s)
B = lambda i, s: ('b', i, s)

def realizations(n):
    R, par = {}, {}
    def put(name, terms, p):
        poly = {}
        for c, w in terms:
            for ww, cc in normal(tuple(w)).items():
                poly[ww] = poly.get(ww, 0) + F(c) * cc
        R[name] = {w: c for w, c in poly.items() if c}
        par[name] = p
    put('H_1', [(1, [A(1), A(-1)]), (1, [B(1, 1), B(1, -1)])], 0)
    for k in range(2, n + 1):
        put('H_%d' % k, [(1, [B(k - 1, 1), B(k - 1, -1)]), (-1, [B(k, 1), B(k, -1)])], 0)
    put('H_%d' % (n + 1), [(-1, [B(n, 1), B(n, -1)]), (F(-1, 2), [])], 0)
    for i in range(1, n + 1):
        c = 1  # luna-r2-A1: coefficient 1 for every k (I02)
        put('E_2del%d_p' % i, [(c, [B(i, 1), B(i, 1)])], 0)
        put('E_2del%d_m' % i, [(c, [B(i, -1), B(i, -1)])], 0)
        for j in range(i + 1, n + 1):
            put('E_del%d_del%d_pp' % (i, j), [(1, [B(i, 1), B(j, 1)])], 0)
            put('E_del%d_del%d_mm' % (i, j), [(1, [B(i, -1), B(j, -1)])], 0)
            put('E_del%d_del%d_pm' % (i, j), [(1, [B(i, 1), B(j, -1)])], 0)
            put('E_del%d_del%d_mp' % (i, j), [(1, [B(i, -1), B(j, 1)])], 0)
        for fs, bs in (('p', 'p'), ('p', 'm'), ('m', 'p'), ('m', 'm')):
            put('E_eps1_del%d_%s%s' % (i, fs, bs),
                [(1, [A(1 if fs == 'p' else -1), B(i, 1 if bs == 'p' else -1)])], 1)
    return R, par

def solve(target, basis_polys):
    """express target as rational combination of basis_polys (dict name -> poly); exact Gauss."""
    names = list(basis_polys)
    words = sorted({w for p in list(basis_polys.values()) + [target] for w in p}, key=str)
    rows = [[basis_polys[nm].get(w, F(0)) for nm in names] + [target.get(w, F(0))] for w in words]
    m, ncol = len(rows), len(names)
    piv, r = [], 0
    for c in range(ncol):
        pr = next((k for k in range(r, m) if rows[k][c]), None)
        if pr is None:
            continue
        rows[r], rows[pr] = rows[pr], rows[r]
        pv = rows[r][c]
        rows[r] = [x / pv for x in rows[r]]
        for k in range(m):
            if k != r and rows[k][c]:
                f = rows[k][c]
                rows[k] = [a - f * b for a, b in zip(rows[k], rows[r])]
        piv.append(c)
        r += 1
    if any(row[-1] for row in rows[r:]):
        return None
    return {names[c]: rows[i][-1] for i, c in enumerate(piv) if rows[i][-1]}

def main(path, n):
    d = json.load(open(path))
    R, par = realizations(n)
    names = d['basis']['even'] + d['basis']['odd']
    issues = []
    if sorted(names) != sorted(R):
        issues.append('basis names differ: %s' % sorted(set(names) ^ set(R)))
    sym = {'a_1_p': A(1), 'a_1_m': A(-1)}
    for i in range(1, n + 1):
        sym['b_%d_p' % i] = B(i, 1)
        sym['b_%d_m' % i] = B(i, -1)
    for nm, r in d['generator_realization']['realizations'].items():
        poly = {}
        for t in r['standard_form']:
            for w, c in normal(tuple(sym[s] for s in t['words'])).items():
                poly[w] = poly.get(w, 0) + F(t['coeff']) * c
        poly = {w: c for w, c in poly.items() if c}
        if poly != R.get(nm):
            issues.append('realization differs: %s' % nm)
        if r['parity'] != par.get(nm) or d['parity'].get(nm) != par.get(nm):
            issues.append('parity differs: %s' % nm)
    ref = {}
    for X, Y in product(names, names):
        s = -1 if par[X] and par[Y] else 1
        br = add(mul(R[X], R[Y]), mul(R[Y], R[X]), -s)
        if not br:
            continue
        sol = solve(br, R)
        if sol is None:
            issues.append('bracket outside span: [%s,%s]' % (X, Y))
            continue
        for Z, c in sol.items():
            ref[(X, Y, Z)] = c
    got = {}
    for e in d['structure_constants']:
        k = (e['X'], e['Y'], e['Z'])
        if k in got:
            issues.append('duplicate entry %s' % (k,))
        got[k] = F(e['coeff'])
    miss = [k for k in ref if k not in got]
    extra = [k for k in got if k not in ref]
    diff = [k for k in ref if k in got and got[k] != ref[k]]
    print('n=%d: ref terms %d, json terms %d, missing %d, extra %d, coeff diff %d, other issues %d'
          % (n, len(ref), len(got), len(miss), len(extra), len(diff), len(issues)))
    for k in (miss[:5] + extra[:5] + diff[:5]):
        print('   ', k, 'ref', ref.get(k), 'json', got.get(k))
    for x in issues[:10]:
        print('   ', x)

if __name__ == '__main__':
    ws = sys.argv[1]
    for n in (1, 2, 3):
        main('%s/data/C_%d_structure.json' % (ws, n), n)
