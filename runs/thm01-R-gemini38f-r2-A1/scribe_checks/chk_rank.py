#!/usr/bin/env python3
"""Scribe check for gemini38f-r2-A1 I07 (adapted from luna-r3-A1/scribe_checks/chk_rank.py; exact sparse
Fraction elimination instead of sympy). A = reference delta f columns (chk_cob.py: equal to the Worker's
Schema 4). Reports rank A and rank [A|...] for: the Worker's gamma at the Schema 3 profile (gb = +1) with and
without K rows; the Worker's per-gb gamma columns (Schema 2) with and without K rows; the reference gamma
columns (kappa commuting / supercommuting) without K rows, and rank of their K parts.
Usage: chk_rank.py <workspace copy> <judging/gcheck dir>"""
import json
import re
import sys
from fractions import Fraction as F

sys.path.insert(0, sys.argv[2])
from refmodel import WorkerBasisRef  # noqa: E402


def rank(cols):
    piv = {}  # pivot row -> reduced column (dict)
    r = 0
    for c in cols:
        v = {k: x for k, x in c.items() if x}
        while v:
            k = min(v)
            if k in piv:
                p = piv[k]; f = v[k] / p[k]
                for kk, x in p.items():
                    y = v.get(kk, 0) - f * x
                    if y: v[kk] = y
                    else: v.pop(kk, None)
            else:
                piv[k] = v; r += 1; break
    return r


ws = sys.argv[1]
for n in (1, 2, 3):
    S = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    basis = S['basis']['even'] + S['basis']['odd']
    parity = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    R = S['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real)
    A = [{k: v for k, v in c.items() if v} for c in ref.coboundary_columns().values()]
    rA = rank(A)
    E = json.load(open('%s/data/C_%d_evaluated.json' % (ws, n)))['evaluated_deformation']['evaluated_gamma_constants']
    ge = {}
    for e in E:
        k = (e['X'], e['Y'], e['Z']); ge[k] = ge.get(k, 0) + F(e['coeff'])
    geN = {k: v for k, v in ge.items() if k[2] != 'K'}
    G2 = json.load(open('%s/data/C_%d_gamma.json' % (ws, n)))['inhomogeneous_deformation']['gamma_constants']
    wg = {}
    for e in G2:
        d = wg.setdefault(e['param'], {}); k = (e['X'], e['Y'], e['Z']); d[k] = d.get(k, 0) + F(e['coeff'])
    WG = list(wg.values()); WGN = [{k: v for k, v in g.items() if k[2] != 'K'} for g in WG]
    out = ['worker gamma_eval: rank[A|g] %d (no K: %d)' % (rank(A + [ge]), rank(A + [geN])),
           'worker per-gb: rank[A|G] %d (no K: %d)' % (rank(A + WG), rank(A + WGN))]
    for sign in (False, True):
        G = [ref.gamma(p, sign) for p in ref.gb_params]
        Gn = [{k: v for k, v in g.items() if k[2] != 'K'} for g in G]
        GK = [{k: v for k, v in g.items() if k[2] == 'K'} for g in G]
        out.append('ref %s: rank[A|G no K] %d, rank G_K %d' % ('supercomm' if sign else 'comm', rank(A + Gn), rank(GK)))
    print('n=%d: rank A %d; %s' % (n, rA, '; '.join(out)))
