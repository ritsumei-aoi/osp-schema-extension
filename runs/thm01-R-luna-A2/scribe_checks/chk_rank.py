#!/usr/bin/env python3
"""Scribe check for luna-A2 I08: ranks from the Worker's own Schema 2 (gamma, non-K)
and Schema 4 (delta f) data: rank A vs rank [A|G] (G = gamma columns per gb, K dropped)."""
import json, sys
from fractions import Fraction as F
sys.path.insert(0, sys.argv[2])
from refmodel import WorkerBasisRef
from chk_gamma import parse as gparse
from chk_cob import parse as cparse

def main(ws, n):
    S = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    basis = S['basis']['even'] + S['basis']['odd']
    parity = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    R = S['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real)
    A = {}
    for e in json.load(open('%s/data/C_%d_coboundary.json' % (ws, n)))['coboundary']['structure']:
        for ph, c in cparse(e['coeff']).items():
            A.setdefault(ph, {})[(e['X'], e['Y'], e['Z'])] = c
    G = {}
    for e in json.load(open('%s/data/C_%d_gamma.json' % (ws, n)))['inhomogeneous_deformation']['gamma_structure']:
        if e['Z'] == 'K':
            continue
        for p, c in gparse(e['coeff']).items():
            G.setdefault(p, {})[(e['X'], e['Y'], e['Z'])] = c
    ra = ref.rank(list(A.values()))
    rag = ref.rank(list(A.values()) + list(G.values()))
    print('n=%d: rank A = %d, rank [A|G] (Worker gamma, K dropped) = %d, gb columns %d' % (n, ra, rag, len(G)))

for n in (1, 2, 3):
    main(sys.argv[1], n)
