#!/usr/bin/env python3
"""Scribe check for luna-r3-A1 I05 (adapted from luna-r2-A1: key gamma_structure, parameter names gb_a1_p_b1_p): compare the Worker's gamma
(data/C_n_gamma.json, inhomogeneous_deformation.gamma_coefficients, coefficients as
linear expressions in gb_a1{p,m}_b{j}{p,m}) with the independent reference
(judging/gcheck/refmodel.WorkerBasisRef, built from the Worker's own realizations),
for kappa supercommuting (sign=True) and kappa commuting (sign=False); K entries and
non-K entries separately. Up to an overall sign is also reported. Reads only.
Usage: chk_gamma.py <workspace copy> <judging/gcheck dir>"""
import json
import re
import sys
from fractions import Fraction as F

import sympy as sp

GC = sys.argv[2]
sys.path.insert(0, GC)
from refmodel import WorkerBasisRef  # noqa: E402


def parse(coeff):
    expr = sp.expand(sp.sympify(coeff))
    out = {}
    for sym in expr.free_symbols:
        name = str(sym)  # gb_a1_p_b1_p
        m = re.fullmatch(r'gb_a1_([pm])_b(\d+)_([pm])', name)
        s, j, t = m[1], int(m[2]), m[3]
        c = expr.coeff(sym)
        out[('+' if s == 'p' else '-', j, '+' if t == 'p' else '-')] = F(str(c))
    assert sp.expand(expr - sum(sp.Rational(str(v)) * sp.Symbol('gb_a1_%s_b%d_%s' % (
        'p' if k[0] == '+' else 'm', k[1], 'p' if k[2] == '+' else 'm')) for k, v in out.items())) == 0, coeff
    return out


def main(ws, n):
    S = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    basis = S['basis']['even'] + S['basis']['odd']
    parity = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    R = S['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real)
    G = json.load(open('%s/data/C_%d_gamma.json' % (ws, n)))['inhomogeneous_deformation']['gamma_structure']
    worker = {}
    for e in G:
        for p, c in parse(e['coeff']).items():
            k = (e['X'], e['Y'], e['Z'])
            worker.setdefault(p, {})[k] = worker.setdefault(p, {}).get(k, 0) + c
    nK = sum(1 for e in G if e['Z'] == 'K')
    print('n=%d: gamma records %d (Z = K: %d)' % (n, len(G), nK))
    for sign in (True, False):
        res = {'nonK': [0, 0, 0], 'K': [0, 0, 0]}  # equal, equal up to -1, total params
        for p in ref.gb_params:
            r = ref.gamma(p, sign)
            w = {k: v for k, v in worker.get(p, {}).items() if v}
            for part, sel in (('nonK', lambda k: k[2] != 'K'), ('K', lambda k: k[2] == 'K')):
                rr = {k: v for k, v in r.items() if sel(k) and v}
                ww = {k: v for k, v in w.items() if sel(k)}
                res[part][2] += 1
                res[part][0] += rr == ww
                res[part][1] += rr == {k: -v for k, v in ww.items()}
        print('  kappa %s: non-K equal %d/%d (up to -1: %d), K equal %d/%d (up to -1: %d)' % (
            'supercommuting' if sign else 'commuting', res['nonK'][0], res['nonK'][2], res['nonK'][1],
            res['K'][0], res['K'][2], res['K'][1]))


if __name__ == '__main__':
    for n in (1, 2, 3):
        main(sys.argv[1], n)
