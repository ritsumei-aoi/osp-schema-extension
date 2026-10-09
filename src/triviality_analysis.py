#!/usr/bin/env python3
"""Triviality analysis: compare Layer 3 (gamma) with Layer 4 (coboundary space)."""

import json
from fractions import Fraction
from collections import defaultdict
import re
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def load_structure(n):
    with open(os.path.join(DATA_DIR, f'C_{n}_structure.json')) as f:
        return json.load(f)


def build_bracket_map(data):
    parity = data['parity']
    basis = data['basis']['even'] + data['basis']['odd']
    bracket = {}
    for sc in data['structure_constants']:
        X, Y, Z = sc['X'], sc['Y'], sc['Z']
        c = Fraction(sc['coeff'])
        bracket.setdefault((X, Y), {})[Z] = bracket.get((X, Y), {}).get(Z, Fraction(0)) + c
    return bracket, parity, basis


def compute_delta_f_entry(phi_i, phi_j, basis, bracket, parity):
    """Compute (delta f)(X,Y) where f(phi_j) = 1*phi_i."""
    f_map = {phi_j: {phi_i: Fraction(1)}}

    def bf(X, Y):
        return bracket.get((X, Y), {})

    result = {}
    for X in basis:
        for Y in basis:
            pX, pY = parity[X], parity[Y]
            s1 = -1 if pX % 2 == 1 else 1
            s2 = -1 if ((pX + 1) * pY) % 2 == 1 else 1
            fY = f_map.get(Y, {})
            fX = f_map.get(X, {})
            XY = bf(X, Y)
            combined = defaultdict(Fraction)
            for z, cz in fY.items():
                for w, cw in bf(X, z).items():
                    combined[w] += s1 * cz * cw
            for z, cz in fX.items():
                for w, cw in bf(Y, z).items():
                    combined[w] -= s2 * cz * cw
            for z, cz in XY.items():
                for w, cw in f_map.get(z, {}).items():
                    combined[w] -= cz * cw
            for Z, val in combined.items():
                if val != 0:
                    result[(X, Y, Z)] = result.get((X, Y, Z), Fraction(0)) + val
    return {k: v for k, v in result.items() if v != 0}


def gauss_elim(mat, nrows, ncols):
    """Gaussian elimination over Q."""
    A = [row[:] for row in mat]
    pr = 0
    for pc in range(ncols):
        found = -1
        for r in range(pr, nrows):
            if A[r][pc] != 0:
                found = r
                break
        if found == -1:
            continue
        A[pr], A[found] = A[found], A[pr]
        piv = A[pr][pc]
        for c in range(ncols):
            A[pr][c] /= piv
        for r in range(nrows):
            if r != pr and A[r][pc] != 0:
                fac = A[r][pc]
                for c in range(ncols):
                    A[r][c] -= fac * A[pr][c]
        pr += 1
    return pr, A


def analyze_triviality(n):
    print(f'\n=== C({n+1}) n={n} ===')
    data = load_structure(n)
    bracket, parity, basis = build_bracket_map(data)

    even_gens = [g for g in basis if parity[g] == 0]
    odd_gens = [g for g in basis if parity[g] == 1]
    print(f'  even={len(even_gens)}, odd={len(odd_gens)}')

    # phi parameters for odd map f (maps even->odd and odd->even)
    phi_pairs = [(pi, pj) for pj in basis for pi in basis if parity[pi] != parity[pj]]
    print(f'  phi parameters: {len(phi_pairs)}')

    # Load gamma structure
    with open(os.path.join(DATA_DIR, f'C_{n}_gamma.json')) as f:
        gdata = json.load(f)
    gamma_terms = gdata['inhomogeneous_deformation']['gamma_coefficients']
    gb_params = gdata['inhomogeneous_deformation']['gb_matrix']['parameters']

    # Parse gamma by gb parameter
    gamma_by_gb = {gb: {} for gb in gb_params}
    for term in gamma_terms:
        X, Y, Z = term['X'], term['Y'], term['Z']
        expr = term['coeff_expr']
        triple = (X, Y, Z)
        for gb in gb_params:
            if gb in expr:
                m = re.search(r'(-?\d+\*)?' + re.escape(gb), expr)
                if m:
                    s = m.group()
                    if '*' in s:
                        c = Fraction(s.split('*')[0])
                    elif s.startswith('-'):
                        c = Fraction(-1)
                    else:
                        c = Fraction(1)
                    gamma_by_gb[gb][triple] = gamma_by_gb[gb].get(triple, Fraction(0)) + c

    # Collect all triples from both delta and gamma
    all_triples = set()
    for gb in gb_params:
        all_triples.update(gamma_by_gb[gb].keys())

    # Compute delta_f for each phi pair and collect triples
    print(f'  Computing coboundary space (this may take a moment)...')
    all_delta = {}
    for (pi, pj) in phi_pairs:
        df = compute_delta_f_entry(pi, pj, basis, bracket, parity)
        all_delta[(pi, pj)] = df
        all_triples.update(df.keys())

    triple_list = sorted(all_triples)
    triple_idx = {t: i for i, t in enumerate(triple_list)}
    m_rows = len(triple_list)
    m_cols = len(phi_pairs)
    print(f'  triple space dim={m_rows}, phi_dim={m_cols}')

    # Build delta matrix
    delta_mat = [[Fraction(0)] * m_cols for _ in range(m_rows)]
    for col, (pi, pj) in enumerate(phi_pairs):
        for triple, val in all_delta[(pi, pj)].items():
            delta_mat[triple_idx[triple]][col] = val

    rank_d, _ = gauss_elim(delta_mat, m_rows, m_cols)
    print(f'  rank(coboundary space delta): {rank_d}')

    # Check each gb direction
    trivial = []
    nontrivial = []
    for gb in gb_params:
        gamma_vec = [Fraction(0)] * m_rows
        for triple, val in gamma_by_gb[gb].items():
            if triple in triple_idx:
                gamma_vec[triple_idx[triple]] = val
        aug = [delta_mat[i][:] + [gamma_vec[i]] for i in range(m_rows)]
        rank_aug, _ = gauss_elim(aug, m_rows, m_cols + 1)
        if rank_aug == rank_d:
            trivial.append(gb)
        else:
            nontrivial.append(gb)

    print(f'  Trivial gb directions: {trivial}')
    print(f'  Non-trivial gb directions: {nontrivial}')
    return trivial, nontrivial


if __name__ == '__main__':
    # Analyze n=1 (fast), then n=2,3 if time permits
    results = {}
    for n in [1]:
        tv, ntv = analyze_triviality(n)
        results[n] = (tv, ntv)

    print('\n=== Summary (n=1 only; n=2,3 use structural argument) ===')
    for n, (tv, ntv) in results.items():
        print(f'C({n+1}): trivial_dirs={len(tv)}, nontrivial_dirs={len(ntv)}')
