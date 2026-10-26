#!/usr/bin/env python3
"""Scribe check for luna-A2 I07: Schema 4 (C_n_coboundary.json, coboundary.structure,
coefficients 'c*phi_<out>_from_<in>') against the reference delta f columns
(judging/gcheck/refmodel.WorkerBasisRef.coboundary_columns, built from the
Worker's realizations; formula of C_coboundary_definition.md). Reads only."""
import json
import re
import sys
from fractions import Fraction as F

sys.path.insert(0, sys.argv[2])
from refmodel import WorkerBasisRef  # noqa: E402

TERM = re.compile(r'\s*([+-]?)\s*(?:(\d+(?:/\d+)?)\s*\*\s*)?(phi_\S+?)(?=\s*[+-]|\s*$)')


def parse(coeff):
    out, pos = {}, 0
    for m in TERM.finditer(coeff):
        assert coeff[pos:m.start()].strip() == '', (coeff, pos)
        pos = m.end()
        c = F(m[2]) if m[2] else F(1)
        if m[1] == '-':
            c = -c
        t, s = m[3][4:].split('_from_')
        out[(t, s)] = out.get((t, s), 0) + c
    assert coeff[pos:].strip() == '', coeff
    return out


def main(ws, n):
    S = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    basis = S['basis']['even'] + S['basis']['odd']
    parity = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    R = S['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real).coboundary_columns()
    C = json.load(open('%s/data/C_%d_coboundary.json' % (ws, n)))
    params = C['odd_linear_map']['parameter_order']
    w = {}
    for e in C['coboundary']['structure']:
        for ph, c in parse(e['coeff']).items():
            w.setdefault(ph, {})[(e['X'], e['Y'], e['Z'])] = w.setdefault(ph, {}).get((e['X'], e['Y'], e['Z']), 0) + c
    w = {ph: {k: v for k, v in d.items() if v} for ph, d in w.items()}
    wp = {tuple(p[4:].split('_from_')) for p in params}
    eq = sum(1 for ph in ref if w.get(ph, {}) == ref[ph])
    print('n=%d: map parameters %d (reference %d, same set %s); delta f columns equal %d/%d; records %d' % (
        n, len(params), len(ref), wp == set(ref), eq, len(ref), len(C['coboundary']['structure'])))


if __name__ == '__main__':
    for n in (1, 2, 3):
        main(sys.argv[1], n)
