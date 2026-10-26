#!/usr/bin/env python3
"""Scribe check for luna-r3-A1 I07 (adapted from luna-r2-A1: keys odd_linear_map.coefficients /
coboundary_structure, symbols phi_<out>__from__<in>, coefficients parsed with sympy): Schema 4 against the
reference delta f columns (judging/gcheck/refmodel.WorkerBasisRef.coboundary_columns, built from the Worker's
realizations; formula of C_coboundary_definition.md). Reads only.
Usage: chk_cob.py <workspace copy> <judging/gcheck dir>"""
import json
import sys
from fractions import Fraction as F

import sympy as sp

sys.path.insert(0, sys.argv[2])
from refmodel import WorkerBasisRef  # noqa: E402


def main(ws, n):
    S = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    basis = S['basis']['even'] + S['basis']['odd']
    parity = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    R = S['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real).coboundary_columns()
    C = json.load(open('%s/data/C_%d_coboundary.json' % (ws, n)))
    coefs = C['odd_linear_map']['coefficients']
    sym = {e['symbol']: (e['output'], e['input']) for e in coefs}
    w = {}
    for e in C['coboundary_structure']:
        expr = sp.expand(sp.sympify(e['coeff'], locals={s: sp.Symbol(s) for s in sym}))
        assert expr.free_symbols <= {sp.Symbol(s) for s in sym}, e
        for s in expr.free_symbols:
            ph = sym[str(s)]
            k = (e['X'], e['Y'], e['Z'])
            w.setdefault(ph, {})[k] = w.setdefault(ph, {}).get(k, 0) + F(str(expr.coeff(s)))
    w = {ph: {k: v for k, v in d.items() if v} for ph, d in w.items()}
    eq = sum(1 for ph in ref if w.get(ph, {}) == ref[ph])
    print('n=%d: map parameters %d (reference %d, same set %s); delta f columns equal %d/%d; records %d' % (
        n, len(coefs), len(ref), set(sym.values()) == set(ref), eq, len(ref), len(C['coboundary_structure'])))


if __name__ == '__main__':
    for n in (1, 2, 3):
        main(sys.argv[1], n)
