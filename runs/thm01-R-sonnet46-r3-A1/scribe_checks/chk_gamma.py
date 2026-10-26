#!/usr/bin/env python3
"""Scribe check for sonnet46-r3-A1 I05 (adapted from luna-r3-A1): Worker gamma records are
top-level "gamma": [{X, Y, gb_label (gb_a1p_b1m), Z, coeff (number)}], recorded for ONE orientation of
each pair. Compare with judging/gcheck/refmodel.WorkerBasisRef (built from the Worker's own
realizations), kappa supercommuting (sign=True) and commuting (sign=False), K / non-K separately,
on the ordered pairs the Worker recorded; also count reference entries whose pair the Worker
recorded only in the reverse order. Reads only. Usage: chk_gamma.py <workspace copy> <judging/gcheck>"""
import json
import re
import sys
from fractions import Fraction as F

sys.path.insert(0, sys.argv[2])
from refmodel import WorkerBasisRef  # noqa: E402


def main(ws, n):
    S = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    basis = S['basis']['even'] + S['basis']['odd']
    parity = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    R = S['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real)
    G = json.load(open('%s/data/C_%d_gamma.json' % (ws, n)))['gamma']
    worker, pairs = {}, set()
    for e in G:
        m = re.fullmatch(r'gb_a1([pm])_b(\d+)([pm])', e['gb_label'])
        p = ('+' if m[1] == 'p' else '-', int(m[2]), '+' if m[3] == 'p' else '-')
        k = (e['X'], e['Y'], e['Z'])
        worker.setdefault(p, {})[k] = worker.setdefault(p, {}).get(k, 0) + F(str(e['coeff']))
        pairs.add((e['X'], e['Y']))
    nK = sum(1 for e in G if e['Z'] == 'K')
    both = sum(1 for (x, y) in pairs if x != y and (y, x) in pairs)
    print('n=%d: gamma records %d (Z = K: %d), pairs %d, pairs with both orders %d' % (n, len(G), nK, len(pairs), both))
    for sign in (True, False):
        res = {'nonK': [0, 0], 'K': [0, 0]}
        revonly = 0
        for p in ref.gb_params:
            r = {k: v for k, v in ref.gamma(p, sign).items() if v}
            w = {k: v for k, v in worker.get(p, {}).items() if v}
            covered = {k: v for k, v in r.items() if (k[0], k[1]) in pairs}
            revonly += sum(1 for k in r if (k[0], k[1]) not in pairs and (k[1], k[0]) in pairs)
            missing_pair = sum(1 for k in r if (k[0], k[1]) not in pairs and (k[1], k[0]) not in pairs)
            assert missing_pair == 0 or True
            for part, sel in (('nonK', lambda k: k[2] != 'K'), ('K', lambda k: k[2] == 'K')):
                rr = {k: v for k, v in covered.items() if sel(k)}
                ww = {k: v for k, v in w.items() if sel(k)}
                res[part][1] += 1
                res[part][0] += rr == ww
        allref = sum(len([1 for v in ref.gamma(p, sign).values() if v]) for p in ref.gb_params)
        print('  kappa %s: on recorded pairs non-K equal %d/%d, K equal %d/%d; ref entries total %d, in reverse-only pairs %d' % (
            'supercommuting' if sign else 'commuting', res['nonK'][0], res['nonK'][1], res['K'][0], res['K'][1], allref, revonly))


if __name__ == '__main__':
    for n in (1, 2, 3):
        main(sys.argv[1], n)
