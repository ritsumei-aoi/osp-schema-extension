#!/usr/bin/env python3
"""Scribe check for luna-r2-A1 I06 (adapted from luna-A2): Schema 3 (C_n_evaluated.json) against the
independent reference: structure_constants = chk_sc reference, gamma at the
recorded gb assignment = sum_p gb_p * refmodel gamma(p, kappa supercommuting),
incl. K entries. Reads only."""
import json
import sys
from fractions import Fraction as F

sys.path.insert(0, sys.argv[2])
from refmodel import WorkerBasisRef  # noqa: E402
import re  # noqa: E402


def gbparse(s):
    m = re.fullmatch(r'gb_a1([pm])_b(\d+)([pm])', s)
    return ('+' if m[1] == 'p' else '-', int(m[2]), '+' if m[3] == 'p' else '-')


def entries(lst):
    out = {}
    for e in lst:
        k = (e['X'], e['Y'], e['Z'])
        out[k] = out.get(k, 0) + F(e['coeff'])
    return {k: v for k, v in out.items() if v}


def main(ws, n):
    S = json.load(open('%s/data/C_%d_structure.json' % (ws, n)))
    basis = S['basis']['even'] + S['basis']['odd']
    parity = {x: 0 for x in S['basis']['even']} | {x: 1 for x in S['basis']['odd']}
    R = S['generator_realization']['realizations']
    real = {g: [(F(t['coeff']), list(t['words'])) for t in R[g]['standard_form']] for g in basis}
    ref = WorkerBasisRef(n, basis, parity, real)
    E = json.load(open('%s/data/C_%d_evaluated.json' % (ws, n)))
    vals = {gbparse(k): F(str(v)) for k, v in E['inhomogeneous_deformation']['evaluation_profile']['parameter_values'].items()}
    sc_ref = {(X, Y, Z): c for (X, Y), zs in ref.structure_constants().items() for Z, c in zs.items() if c}
    g_ref = {}
    for p in ref.gb_params:
        for k, c in ref.gamma(p, True).items():
            g_ref[k] = g_ref.get(k, 0) + vals.get(p, 0) * c
    g_ref = {k: v for k, v in g_ref.items() if v}
    sc_w = entries(E['structure_constants'])
    g_w = entries(E['inhomogeneous_deformation']['evaluated_gamma_coefficients'])
    print('n=%d: gb values %s; structure constants equal %s (%d terms); gamma equal %s (%d terms, K terms %d)' % (
        n, sorted(set(vals.values())), sc_w == sc_ref, len(sc_w), g_w == g_ref, len(g_w),
        sum(1 for k in g_w if k[2] == 'K')))


if __name__ == '__main__':
    for n in (1, 2, 3):
        main(sys.argv[1], n)
