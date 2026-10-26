#!/usr/bin/env python3
"""Scribe check for sonnet46-r3-A1 I08 (copied from luna-r3-A1 unchanged; here the Worker gamma equals the kappa-commuting reference): ranks from the reference model built from the Worker's Schema 1
realizations (refmodel.WorkerBasisRef). chk_gamma.py / chk_cob.py showed that the Worker's Schema 2 equals the
kappa-supercommuting reference gamma and the Worker's Schema 4 equals the reference delta f columns.
(1) non-K: rank A vs rank [A|G] (A = delta f columns, G = gamma columns with K rows dropped),
    for kappa supercommuting and kappa commuting; (2) rank of the K part of G.
Usage: chk_rank.py <workspace copy> <judging/gcheck dir>"""
import json
import sys
from fractions import Fraction as F

import sympy as sp

sys.path.insert(0, sys.argv[2])
from refmodel import WorkerBasisRef  # noqa: E402


def rank(cols):
    rows = sorted({k for c in cols for k in c})
    idx = {k: i for i, k in enumerate(rows)}
    M = sp.zeros(len(rows), len(cols))
    for j, c in enumerate(cols):
        for k, v in c.items():
            M[idx[k], j] = sp.Rational(v.numerator, v.denominator)
    return M.rank()


for n in (1, 2, 3):
    S = json.load(open('%s/data/C_%d_structure.json' % (sys.argv[1], n)))
    basis = S['basis']['even'] + S['basis']['odd']
    parity = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    R = S['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real)
    A = [{k: v for k, v in c.items() if v} for c in ref.coboundary_columns().values()]
    rA = rank(A)
    out = []
    for sign in (True, False):
        G = [ref.gamma(p, sign) for p in ref.gb_params]
        Gn = [{k: v for k, v in g.items() if k[2] != 'K' and v} for g in G]
        GK = [{k: v for k, v in g.items() if k[2] == 'K' and v} for g in G]
        out.append('%s: rank[A|G] %d, rank G_K %d' % ('supercomm' if sign else 'comm', rank(A + Gn), rank(GK)))
    print('n=%d: rank A %d; %s' % (n, rA, '; '.join(out)))
