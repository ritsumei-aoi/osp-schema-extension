#!/usr/bin/env python3
"""Scribe check for luna-r2-A1 I08 (adapted from luna-A2): ranks from the Worker's own
Schema 2 (gamma) and Schema 4 (delta f) data.
(1) non-K part: rank A vs rank [A|G] (A = delta f columns per phi, G = gamma columns
    per gb with K entries dropped) -> is the non-K part of gamma a coboundary?
(2) K part: rank of the K-coefficient matrix (rows (X,Y), columns gb).
Usage: chk_rank.py <workspace copy> <judging/gcheck dir>  (run from scribe_checks/)."""
import json
import sys
from fractions import Fraction as F
sys.path.insert(0, sys.argv[2])
from refmodel import WorkerBasisRef  # noqa: E402
from chk_gamma import parse as gparse  # noqa: E402
from chk_cob import parse as cparse  # noqa: E402


def main(ws, n):
    S = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    basis = S['basis']['even'] + S['basis']['odd']
    parity = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    R = S['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real)
    A = {}
    for e in json.load(open('%s/data/C_%d_coboundary.json' % (ws, n)))['coboundary']['delta_f_coefficients']:
        for ph, c in cparse(e['coeff']).items():
            A.setdefault(ph, {})[(e['X'], e['Y'], e['Z'])] = c
    G, GK = {}, {}
    for e in json.load(open('%s/data/C_%d_gamma.json' % (ws, n)))['inhomogeneous_deformation']['gamma_coefficients']:
        tgt = GK if e['Z'] == 'K' else G
        for p, c in gparse(e['coeff']).items():
            tgt.setdefault(p, {})[(e['X'], e['Y'], e['Z'])] = c
    ra = ref.rank(list(A.values()))
    rag = ref.rank(list(A.values()) + list(G.values()))
    rk = ref.rank(list(GK.values()))
    print('n=%d: rank A = %d, rank [A|G] (gamma, K dropped) = %d, gb columns %d; rank of K part = %d' % (
        n, ra, rag, len(G), rk))


for n in (1, 2, 3):
    main(sys.argv[1], n)
