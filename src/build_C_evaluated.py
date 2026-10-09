#!/usr/bin/env python3
"""
build_C_evaluated.py
Construct Schema 3 (Evaluated Structure) for C(n+1) = osp(2|2n).

All gb parameters are set to +1 (Option A: uniform positive, human-approved).

Schema 3 = Schema 1 base brackets  +  evaluated κ·γ(X,Y) from Schema 2.

Z label convention in Schema 3 evaluated_brackets:
  type='base'  : Z is a basis generator name (same as Schema 1).
  type='kappa' : Z is 'kappa' (= κ·K = κ·1) or 'kappa·{gen}'.
"""
from __future__ import annotations
import json
import os
import sys
from collections import defaultdict
from datetime import date
from fractions import Fraction

SCHEMA_VERSION = "5.0"
GB_PROFILE = "uniform_plus1"
GB_DESCRIPTION = "All gb_{σ,j,s} = +1 (Option A: uniform positive)"


# ── helpers ──────────────────────────────────────────────────────────────────

def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def parse_frac(s: str) -> Fraction:
    if '/' in s:
        num, den = s.split('/')
        return Fraction(int(num), int(den))
    return Fraction(int(s))


def frac_str(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    return f'{f.numerator}/{f.denominator}'


def basis_order(schema1: dict) -> dict[str, int]:
    return {g: i for i, g in enumerate(
        schema1['basis']['even'] + schema1['basis']['odd'])}


# ── evaluation ───────────────────────────────────────────────────────────────

def evaluate_n(n: int, data_dir: str) -> dict:
    schema1 = load_json(os.path.join(data_dir, f'C_{n}_structure.json'))
    schema2 = load_json(os.path.join(data_dir, f'C_{n}_gamma.json'))

    gb_labels: list[str] = schema2['gb_parameters']['labels']
    gb_values: dict[str, Fraction] = {gb: Fraction(1) for gb in gb_labels}

    # ── base brackets (Schema 1) ──────────────────────────────────────────
    base_entries = [
        {'X': e['X'], 'Y': e['Y'], 'Z': e['Z'],
         'coeff': e['coeff'], 'type': 'base'}
        for e in schema1['structure_constants']
    ]

    # ── kappa brackets: evaluate γ(X,Y) at gb = 1 ───────────────────────
    # Accumulate: (X, Y, Z_schema2) → total coefficient
    kappa_acc: dict[tuple[str,str,str], Fraction] = defaultdict(Fraction)
    for e in schema2['inhomogeneous_deformation']:
        coeff = parse_frac(e['coeff']) * gb_values[e['gb']]
        kappa_acc[(e['X'], e['Y'], e['Z'])] += coeff

    kappa_entries = []
    for (X, Y, Z2), total in kappa_acc.items():
        if not total:
            continue
        # Map Schema 2 Z to Schema 3 Z label
        z3 = 'kappa' if Z2 == 'K' else f'kappa·{Z2}'
        kappa_entries.append(
            {'X': X, 'Y': Y, 'Z': z3, 'coeff': frac_str(total), 'type': 'kappa'})

    # ── sort entries by (X, Y, type, Z) ──────────────────────────────────
    order = basis_order(schema1)
    type_order = {'base': 0, 'kappa': 1}

    def sort_key(e):
        return (order.get(e['X'], 9999), order.get(e['Y'], 9999),
                type_order[e['type']], e['Z'])

    all_entries = sorted(base_entries + kappa_entries, key=sort_key)

    # ── consistency checks ────────────────────────────────────────────────
    _check_consistency(schema1, schema2, gb_values, kappa_acc)

    d = schema1['algebra']['dimension']
    return {
        'schema_version': SCHEMA_VERSION,
        'schema_layer': 3,
        'algebra': schema1['algebra'],
        'basis': schema1['basis'],
        'parity': schema1['parity'],
        'central_elements': schema2['central_elements'],
        'gb_assignment': {
            'profile': GB_PROFILE,
            'description': GB_DESCRIPTION,
            'values': {gb: '1' for gb in gb_labels},
        },
        'evaluated_brackets': all_entries,
        'metadata': {
            'description': (
                'Schema 3: evaluated deformed bracket [X,Y]_γ = [X,Y]_0 + κ·γ(X,Y) '
                'with all gb parameters set to +1 (Option A). '
                'type="base" entries reproduce Schema 1 structure constants. '
                'type="kappa" entries give κ·Z contributions from γ(X,Y)|_{gb=1}. '
                'Z="kappa" denotes κ·K = κ (since K=1).'
            ),
            'generated_by': 'build_C_evaluated.py',
            'generation_date': str(date.today()),
            'references': ['Frappat, Sciarrino, Sorba (2000)'],
        },
    }


# ── consistency checks ────────────────────────────────────────────────────────

def _check_consistency(schema1, schema2, gb_values, kappa_acc):
    parity = {k: int(v) for k, v in schema1['parity'].items()}
    basis_parity = parity.copy()
    basis_parity['K'] = 0  # K is even central element

    # 1. Every gb label in Schema 2 is in the assignment
    s2_gbs = {e['gb'] for e in schema2['inhomogeneous_deformation']}
    unknown = s2_gbs - set(gb_values)
    assert not unknown, f'Unknown gb labels in Schema 2: {unknown}'

    # 2. Parity of Z in kappa entries.
    #    [X,Y]_γ = [X,Y]_0 + κ·γ(X,Y).  κ has parity 1, so κ·Z has parity
    #    (1 + p(Z)) mod 2.  For the full bracket to be graded, κ·γ(X,Y) must
    #    have parity (p(X)+p(Y)) mod 2, which means p(Z) = (p(X)+p(Y)+1) mod 2.
    for (X, Y, Z2), total in kappa_acc.items():
        if not total or X not in parity or Y not in parity:
            continue
        pX, pY = parity[X], parity[Y]
        pZ2 = basis_parity.get(Z2)
        if pZ2 is None:
            raise AssertionError(f'Unknown Z={Z2!r} in γ({X},{Y})')
        expected_pZ2 = (pX + pY + 1) % 2
        assert pZ2 == expected_pZ2, (
            f'Parity mismatch in γ({X},{Y}): Z={Z2} has p={pZ2}, '
            f'expected {expected_pZ2} (p(X)+p(Y)+1 mod 2)')

    # 3. Every Schema 2 entry maps X,Y,Z to known basis elements (or K)
    known_Z = set(parity) | {'K'}
    for e in schema2['inhomogeneous_deformation']:
        assert e['X'] in parity, f'Unknown X={e["X"]!r}'
        assert e['Y'] in parity, f'Unknown Y={e["Y"]!r}'
        assert e['Z'] in known_Z, f'Unknown Z={e["Z"]!r}'


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root, 'data')

    print('C(n+1) Schema 3 — evaluated deformed bracket build')
    print('=' * 60)
    print(f'gb assignment: {GB_DESCRIPTION}')
    print()

    overall_pass = True
    for n in [1, 2, 3]:
        print(f'n={n}  C({n+1}) = osp(2|{2*n})')
        try:
            result = evaluate_n(n, data_dir)
            entries = result['evaluated_brackets']
            base_cnt = sum(1 for e in entries if e['type'] == 'base')
            kappa_cnt = sum(1 for e in entries if e['type'] == 'kappa')
            print(f'  Base entries  (from Schema 1) : {base_cnt}')
            print(f'  Kappa entries (from Schema 2) : {kappa_cnt}')
            print(f'  Total entries                 : {len(entries)}')
            print(f'  Consistency checks            : PASS')

            out_path = os.path.join(data_dir, f'C_{n}_evaluated.json')
            with open(out_path, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f'  Written : {out_path}')
        except Exception as exc:
            overall_pass = False
            print(f'  FAIL: {exc}')
        print()

    print('=' * 60)
    if overall_pass:
        print('ALL CHECKS PASSED')
    else:
        print('FAILURES DETECTED — see above')
        sys.exit(1)


if __name__ == '__main__':
    main()
