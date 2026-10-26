#!/usr/bin/env python3
"""Scribe check for gemini38f-r2-A1 I07 (adapted from luna-r3-A1/scribe_checks/chk_cob.py: key
coboundary_structure.coboundary_constants, one record per (X, Y, param, Z) with a rational coeff, parameter
labels phi_<A>__<B>): Schema 4 against the reference delta f columns (judging/gcheck/refmodel, built from the
Worker's realizations). Both readings of phi_<A>__<B> (A = output, B = input, and the reverse) are tried.
Also reports whether both orders (X,Y), (Y,X) are recorded. Reads only.
Usage: chk_cob.py <workspace copy> <judging/gcheck dir>"""
import json
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
    ref = WorkerBasisRef(n, basis, parity, real).coboundary_columns()
    ref = {ph: {k: v for k, v in d.items() if v} for ph, d in ref.items()}
    C = json.load(open('%s/data/C_%d_coboundary.json' % (ws, n)))['coboundary_structure']
    labels = C['linear_map']['parameter_labels']
    recs = C['coboundary_constants']
    pairs = {(e['X'], e['Y']) for e in recs}
    both = sum(1 for (x, y) in pairs if (y, x) in pairs or x == y)
    res = []
    for rev in (False, True):
        w = {}
        for e in recs:
            a, b = e['param'][len('phi_'):].split('__')
            ph = (b, a) if rev else (a, b)
            d = w.setdefault(ph, {}); k = (e['X'], e['Y'], e['Z'])
            d[k] = d.get(k, 0) + F(e['coeff'])
        w = {ph: {k: v for k, v in d.items() if v} for ph, d in w.items()}
        eq = sum(1 for ph in ref if w.get(ph, {}) == ref[ph])
        res.append('%s: same set %s, columns equal %d/%d' % ('A=input,B=output' if rev else 'A=output,B=input',
                   set(w) <= set(ref) and len(labels) == len(ref), eq, len(ref)))
    print('n=%d: parameters %d (reference %d), records %d, pairs %d (reverse recorded %d); %s' % (
        n, len(labels), len(ref), len(recs), len(pairs), both, '; '.join(res)))


if __name__ == '__main__':
    for n in (1, 2, 3):
        main(sys.argv[1], n)
