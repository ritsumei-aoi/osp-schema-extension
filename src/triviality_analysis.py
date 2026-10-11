#!/usr/bin/env python3
"""
triviality_analysis.py

Determine conditions on gb parameters for the C(n+1) inhomogeneous deformation
to be trivial (= a coboundary delta-f).

Linear system:  A * phi = B * gb
  A: (n_triples x n_phi)  coboundary matrix  [from Schema 4]
  B: (n_triples x n_gb)   gamma matrix        [from Schema 2]

Triviality condition on gb:  B*gb in Im(A).

Algorithm: RREF of augmented matrix [A | B]. Rows where A-block = 0
after reduction give independent linear conditions B_row * gb = 0.

Usage:
    python triviality_analysis.py [--data-dir <path>]
"""

import sys
import json
from fractions import Fraction
from collections import defaultdict
from pathlib import Path


def load_json(path):
    with open(path) as f:
        return json.load(f)


def rref_augmented(M_input, n_pivot_cols):
    """RREF of M_input pivoting on first n_pivot_cols columns."""
    M = [row[:] for row in M_input]
    n_rows = len(M)
    n_cols = len(M[0]) if M else 0
    rank = 0
    pivot_cols = []
    for col in range(n_pivot_cols):
        pivot = None
        for r in range(rank, n_rows):
            if M[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue
        M[rank], M[pivot] = M[pivot], M[rank]
        scale = M[rank][col]
        M[rank] = [x / scale for x in M[rank]]
        for r in range(n_rows):
            if r != rank and M[r][col] != 0:
                fac = M[r][col]
                M[r] = [M[r][c] - fac * M[rank][c] for c in range(n_cols)]
        pivot_cols.append(col)
        rank += 1
    return M, rank, pivot_cols


def rref_standalone(M_input):
    M = [row[:] for row in M_input]
    if not M:
        return M, 0, []
    n_rows = len(M)
    n_cols = len(M[0])
    rank = 0
    pivot_cols = []
    for col in range(n_cols):
        pivot = None
        for r in range(rank, n_rows):
            if M[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue
        M[rank], M[pivot] = M[pivot], M[rank]
        scale = M[rank][col]
        M[rank] = [x / scale for x in M[rank]]
        for r in range(n_rows):
            if r != rank and M[r][col] != 0:
                fac = M[r][col]
                M[r] = [M[r][c] - fac * M[rank][c] for c in range(n_cols)]
        pivot_cols.append(col)
        rank += 1
    return M, rank, pivot_cols


def analyze_triviality(n, data_dir):
    """
    Full triviality analysis for C(n+1).
    Returns dict with conditions, dimensions, and certificate evidence.
    """
    schema2 = load_json(data_dir / f'C_{n}_gamma.json')
    schema4 = load_json(data_dir / f'C_{n}_coboundary.json')

    gamma_map = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema2['gamma']:
        key = (entry['X'], entry['Y'], entry['Z'])
        gamma_map[key][entry['gb_label']] += Fraction(entry['coeff'])

    cob_map = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema4['coboundary']:
        key = (entry['X'], entry['Y'], entry['Z'])
        cob_map[key][entry['phi_label']] += Fraction(entry['coeff'])

    gb_labels = [p['label'] for p in schema2['gb_matrix']['parameters']]
    phi_labels = [p['label'] for p in schema4['phi_matrix']['parameters']]
    gb_idx = {lbl: i for i, lbl in enumerate(gb_labels)}
    phi_idx = {lbl: i for i, lbl in enumerate(phi_labels)}
    n_gb = len(gb_labels)
    n_phi = len(phi_labels)

    gamma_triples = set(gamma_map.keys())
    cob_triples = set(cob_map.keys())
    all_triples = sorted(gamma_triples | cob_triples)
    n_triples = len(all_triples)

    A = [[Fraction(0)] * n_phi for _ in range(n_triples)]
    B = [[Fraction(0)] * n_gb for _ in range(n_triples)]
    for t_idx, triple in enumerate(all_triples):
        for phi_lbl, c in cob_map.get(triple, {}).items():
            if phi_lbl in phi_idx:
                A[t_idx][phi_idx[phi_lbl]] += c
        for gb_lbl, c in gamma_map.get(triple, {}).items():
            if gb_lbl in gb_idx:
                B[t_idx][gb_idx[gb_lbl]] += c

    M = [A[r][:] + B[r][:] for r in range(n_triples)]
    M_rref, rank_A, _ = rref_augmented(M, n_phi)

    raw_conditions = []
    for r in range(rank_A, n_triples):
        b_part = M_rref[r][n_phi:]
        if any(c != 0 for c in b_part):
            raw_conditions.append(b_part[:])

    if raw_conditions:
        C_rref, rank_C, _ = rref_standalone(raw_conditions)
        reduced_conds = C_rref[:rank_C]
    else:
        reduced_conds = []
        rank_C = 0

    # K-triple certificates
    gamma_K_triples = defaultdict(list)
    for entry in schema2['gamma']:
        if entry['Z'] == 'K':
            gamma_K_triples[(entry['X'], entry['Y'])].append(
                (entry['gb_label'], entry['coeff']))
    cob_K_count = sum(1 for e in schema4['coboundary'] if e['Z'] == 'K')

    gb_certificate = {}
    for entry in schema2['gamma']:
        if entry['Z'] == 'K' and entry['gb_label'] not in gb_certificate:
            gb_certificate[entry['gb_label']] = (entry['X'], entry['Y'], entry['coeff'])

    return {
        'n': n,
        'n_triples': n_triples,
        'n_phi': n_phi,
        'n_gb': n_gb,
        'rank_A': rank_A,
        'n_independent_conditions': rank_C,
        'conditions': reduced_conds,
        'gb_labels': gb_labels,
        'gamma_K_triples': len(gamma_K_triples),
        'cob_K_count': cob_K_count,
        'gb_certificate': gb_certificate,
        'gamma_only_count': len(gamma_triples - cob_triples),
        'cob_only_count': len(cob_triples - gamma_triples),
        'both_count': len(gamma_triples & cob_triples),
    }


def format_condition(cond_row, gb_labels):
    terms = []
    for i, c in enumerate(cond_row):
        if c == 0:
            continue
        short = gb_labels[i].replace('gb_', '')
        if c == 1:
            terms.append(short)
        elif c == -1:
            terms.append(f'-{short}')
        else:
            terms.append(f'{c}*{short}')
    return (' + '.join(terms) + ' = 0') if terms else '0 = 0'


def main():
    if '--data-dir' in sys.argv:
        idx = sys.argv.index('--data-dir')
        data_dir = Path(sys.argv[idx + 1])
    else:
        data_dir = Path(__file__).parent.parent / 'data'

    for n in [1, 2, 3]:
        print(f'\n{"=" * 60}')
        print(f'TRIVIALITY ANALYSIS: C({n+1}) = osp(2|{2*n}), n={n}')
        print(f'{"=" * 60}')
        result = analyze_triviality(n, data_dir)

        print(f'  gb params: {result["n_gb"]}, phi params: {result["n_phi"]}')
        print(f'  triples (union): {result["n_triples"]}')
        print(f'  rank(coboundary matrix): {result["rank_A"]}')
        print(f'  gamma K-triples: {result["gamma_K_triples"]}, cob K-entries: {result["cob_K_count"]}')
        print(f'  independent triviality conditions: {result["n_independent_conditions"]}')

        if result['n_independent_conditions'] == result['n_gb']:
            print('  RESULT: Trivial IFF all gb = 0')
        elif result['n_independent_conditions'] == 0:
            print('  RESULT: Always trivial')
        else:
            free = result['n_gb'] - result['n_independent_conditions']
            print(f'  RESULT: Trivial on a {free}-dim subspace of gb-space')

        print('\n  Conditions:')
        for i, cond in enumerate(result['conditions']):
            print(f'    ({i+1})  {format_condition(cond, result["gb_labels"])}')

        print('\n  Non-triviality certificates (gamma K-component per gb param):')
        for gb_lbl in result['gb_labels']:
            cert = result['gb_certificate'].get(gb_lbl)
            if cert:
                print(f'    gamma({cert[0]}, {cert[1]})[K] = {cert[2]} * {gb_lbl}')


if __name__ == '__main__':
    main()
