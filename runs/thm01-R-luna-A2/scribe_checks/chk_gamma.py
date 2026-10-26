#!/usr/bin/env python3
"""Scribe check for luna-A2 I05: compare the Worker's gamma (data/C_n_gamma.json,
inhomogeneous_deformation.gamma_structure, coefficients 'c*gb_a1_s_bj_t') with
the independent reference (judging/gcheck/refmodel.WorkerBasisRef, built from
the Worker's own realizations), for kappa supercommuting (sign=True) and
kappa commuting (sign=False); K entries and non-K entries separately.
Up to an overall sign is also reported. Reads only."""
import json
import re
import sys
from fractions import Fraction as F

GC = sys.argv[2]
sys.path.insert(0, GC)
from refmodel import WorkerBasisRef  # noqa: E402

TERM = re.compile(r'\s*([+-]?)\s*(?:(\d+(?:/\d+)?)\s*\*\s*)?(gb_a1_([pm])_b(\d+)_([pm]))')


def parse(coeff):
    out = {}
    pos = 0
    for m in TERM.finditer(coeff):
        assert coeff[pos:m.start()].strip() == '', coeff
        pos = m.end()
        c = F(m[2]) if m[2] else F(1)
        if m[1] == '-':
            c = -c
        key = ('+' if m[4] == 'p' else '-', int(m[5]), '+' if m[6] == 'p' else '-')
        out[key] = out.get(key, 0) + c
    assert coeff[pos:].strip() == '', coeff
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
        print('n=%d kappa %s: non-K equal %d/%d (up to -1: %d), K equal %d/%d (up to -1: %d)' % (
            n, 'supercommuting' if sign else 'commuting', res['nonK'][0], res['nonK'][2], res['nonK'][1],
            res['K'][0], res['K'][2], res['K'][1]))


if __name__ == '__main__':
    for n in (1, 2, 3):
        main(sys.argv[1], n)
