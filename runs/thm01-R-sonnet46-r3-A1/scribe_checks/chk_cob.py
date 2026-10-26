#!/usr/bin/env python3
"""Scribe check for sonnet46-r3-A1 I07: Worker Schema 4 (data/C_n_coboundary.json, "coboundary":
[{X, Y, phi_label, Z, coeff}], phi_matrix maps phi_<out>_<in> to labels) vs
judging/gcheck/refmodel.WorkerBasisRef.coboundary_columns() (built from the Worker's realizations),
compared on the ordered pairs the Worker recorded. Also: rank of the full coboundary matrix (all
ordered pairs, reference) and of the Worker matrix. Reads only.
Usage: chk_cob.py <workspace copy> <judging/gcheck>"""
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
    ref = WorkerBasisRef(n, basis, parity, real)
    Cj = json.load(open('%s/data/C_%d_coboundary.json' % (ws, n)))
    lab = {p['label']: (p['output_lbl'], p['input_lbl']) for p in Cj['phi_matrix']['parameters']}
    W, pairs = {}, set()
    for e in Cj['coboundary']:
        ph = lab[e['phi_label']]
        k = (e['X'], e['Y'], e['Z'])
        W.setdefault(ph, {})[k] = W.setdefault(ph, {}).get(k, 0) + F(e['coeff'])
        pairs.add((e['X'], e['Y']))
    D = ref.coboundary_columns()
    eq = 0
    for ph in D:
        r = {k: v for k, v in D[ph].items() if (k[0], k[1]) in pairs and v}
        w = {k: v for k, v in W.get(ph, {}).items() if v}
        eq += r == w
    extra = set(W) - set(D)
    full = ref.rank([D[ph] for ph in D])
    wr = ref.rank([W.get(ph, {}) for ph in D])
    print('n=%d: phi %d (ref %d, extra %d), records %d, pairs %d; columns equal on recorded pairs %d/%d; rank ref(all pairs) %d, rank worker %d'
          % (n, len(lab), len(D), len(extra), len(Cj['coboundary']), len(pairs), eq, len(D), full, wr))


if __name__ == '__main__':
    for n in (1, 2, 3):
        main(sys.argv[1], n)
