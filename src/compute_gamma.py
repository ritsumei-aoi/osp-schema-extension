#!/usr/bin/env python3
"""
compute_gamma.py: Gamma structure (Schema 2) generator for C(n+1) = osp(2|2n).

Sign Convention A: gb_{sigma,j,s} = (a_1^sigma | b_j^s) from the skew-supersymmetric
bilinear form. Deformed exchange relation: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.

Outputs Schema 2 JSON files: data/C_{n}_gamma.json for n=1, 2, 3.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fractions import Fraction
import json
from datetime import date

from C_generators import (
    build_algebra, build_word_map, get_osc_order,
    osc_parity, _elementary_bracket, _norm_word, decompose,
    generate_schema,
)


# ─── GB label utilities ───────────────────────────────────────────────────────

def gb_label(sigma_osc, bs_osc):
    """
    Return the gb parameter label for the Gram matrix entry (a_1^sigma | b_j^s).
    sigma_osc: 'a_1_p' or 'a_1_m'
    bs_osc:    'b_{j}_p' or 'b_{j}_m'
    """
    return f"gb_{sigma_osc}_{bs_osc}"


def gb_labels_for_n(n):
    """Return all 4n gb parameter labels for C(n+1), grouped as (sigma, j, s)."""
    labels = []
    for sigma in ['a_1_p', 'a_1_m']:
        for j in range(1, n + 1):
            for s in ['p', 'm']:
                labels.append(gb_label(sigma, f'b_{j}_{s}'))
    return labels


# ─── Deformed normal ordering ─────────────────────────────────────────────────

def _norm_word_with_kappa(word, coeff, osc_idx, n):
    """
    Normalize a single oscillator word to PBW order, tracking the kappa-coefficient
    at first order in gb (Sign Convention A).

    When a bosonic oscillator b_j^s (higher PBW index) passes a fermionic oscillator
    a_1^sigma (lower PBW index), the deformed relation contributes:
        b_j^s * a_1^sigma = a_1^sigma * b_j^s  -  gb_{sigma,j,s} * kappa

    Returns:
        osc_part   : {word_tuple: Fraction}            -- kappa-free part
        kappa_part : {(gb_label, word_tuple): Fraction} -- kappa-coefficient, linear in gb
    """
    for i in range(len(word) - 1):
        a, b = word[i], word[i + 1]
        if osc_idx[a] > osc_idx[b]:
            pa, pb = osc_parity(a), osc_parity(b)
            sign = Fraction((-1) ** (pa * pb))
            comm = _elementary_bracket(a, b, n)

            # --- swap ---
            swapped = word[:i] + [b, a] + word[i + 2:]
            osc_swap, kappa_swap = _norm_word_with_kappa(swapped, coeff * sign, osc_idx, n)

            osc_result = dict(osc_swap)
            kappa_result = dict(kappa_swap)

            # --- undeformed bracket terms ---
            for cw, cv in comm.items():
                surrounding = word[:i] + list(cw) + word[i + 2:]
                osc_s, kappa_s = _norm_word_with_kappa(surrounding, coeff * cv, osc_idx, n)
                for w, v in osc_s.items():
                    osc_result[w] = osc_result.get(w, Fraction(0)) + v
                for k, v in kappa_s.items():
                    kappa_result[k] = kappa_result.get(k, Fraction(0)) + v

            # --- deformed kappa contribution (Option A) ---
            # Only when a = b_j^s (bosonic, pa=0) passes b = a_1^sigma (fermionic, pb=1).
            # [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
            # => b_j^s * a_1^sigma = a_1^sigma * b_j^s  -  gb_{sigma,j,s} * kappa
            # kappa contribution: -gb_{sigma,j,s} * (remaining words, normalized undeformed)
            if pa == 0 and pb == 1:
                sigma_osc = b    # the fermionic oscillator a_1^sigma
                bs_osc = a       # the bosonic oscillator b_j^s
                gb_lbl = gb_label(sigma_osc, bs_osc)
                remaining = word[:i] + word[i + 2:]
                rem_norm = _norm_word(remaining, coeff * Fraction(-1), osc_idx, n)
                for w, v in rem_norm.items():
                    key = (gb_lbl, w)
                    kappa_result[key] = kappa_result.get(key, Fraction(0)) + v

            osc_result = {w: v for w, v in osc_result.items() if v != 0}
            kappa_result = {k: v for k, v in kappa_result.items() if v != 0}
            return osc_result, kappa_result

    # Word is in PBW order; check fermionic nilpotency
    for i in range(len(word) - 1):
        if word[i] == word[i + 1] and osc_parity(word[i]) == 1:
            return {}, {}

    return {tuple(word): coeff}, {}


def poly_mul_kappa(p, q, osc_idx, n):
    """
    Multiply two oscillator polynomials with deformed normal ordering.
    Returns (osc_part, kappa_part) aggregated over all word pairs.
    """
    osc_out = {}
    kappa_out = {}
    for w1, c1 in p.items():
        for w2, c2 in q.items():
            osc_s, kappa_s = _norm_word_with_kappa(list(w1 + w2), c1 * c2, osc_idx, n)
            for w, v in osc_s.items():
                osc_out[w] = osc_out.get(w, Fraction(0)) + v
            for k, v in kappa_s.items():
                kappa_out[k] = kappa_out.get(k, Fraction(0)) + v
    return (
        {w: v for w, v in osc_out.items() if v != 0},
        {k: v for k, v in kappa_out.items() if v != 0},
    )


def compute_gamma_kappa(X_poly, Y_poly, px, py, osc_idx, n):
    """
    Compute the kappa-coefficient gamma(X,Y) of
        [X, Y]_deformed = [X, Y]_0  +  kappa * gamma(X, Y)

    Returns: {(gb_label, word_tuple): Fraction}  (linear in gb parameters)
    """
    _, XY_kappa = poly_mul_kappa(X_poly, Y_poly, osc_idx, n)
    _, YX_kappa = poly_mul_kappa(Y_poly, X_poly, osc_idx, n)
    sign = Fraction((-1) ** (px * py))

    kappa = dict(XY_kappa)
    for k, v in YX_kappa.items():
        kappa[k] = kappa.get(k, Fraction(0)) - sign * v

    return {k: v for k, v in kappa.items() if v != 0}


# ─── Schema 2 generation ──────────────────────────────────────────────────────

def generate_gamma_schema(n):
    """Generate the Schema 2 dict for C(n+1) = osp(2|2n)."""
    basis_odd, basis_even, parity, gen_poly, osc_idx = build_algebra(n)
    all_basis = basis_odd + basis_even
    word_map = build_word_map(gen_poly, basis_odd, basis_even)

    # Compute gamma structure for all basis pairs X < Y (PBW order)
    gamma_structure = []
    for i in range(len(all_basis)):
        for j in range(i + 1, len(all_basis)):
            X_lbl, Y_lbl = all_basis[i], all_basis[j]
            px, py = parity[X_lbl], parity[Y_lbl]

            kappa_raw = compute_gamma_kappa(
                gen_poly[X_lbl], gen_poly[Y_lbl], px, py, osc_idx, n
            )
            if not kappa_raw:
                continue

            # Group kappa terms by gb_label, then decompose each oscillator poly
            gb_to_poly = {}
            for (gb_lbl, word), coeff in kappa_raw.items():
                if gb_lbl not in gb_to_poly:
                    gb_to_poly[gb_lbl] = {}
                gb_to_poly[gb_lbl][word] = (
                    gb_to_poly[gb_lbl].get(word, Fraction(0)) + coeff
                )

            gamma_terms = []
            for gb_lbl in sorted(gb_to_poly):
                poly = {w: v for w, v in gb_to_poly[gb_lbl].items() if v != 0}
                if not poly:
                    continue
                terms = decompose(poly, gen_poly, basis_odd, basis_even, n, word_map)
                for Z_lbl, c in terms:
                    gamma_terms.append({
                        'gb_label': gb_lbl,
                        'Z': Z_lbl,
                        'coeff': str(c),
                    })

            if gamma_terms:
                gamma_structure.append({
                    'X': X_lbl,
                    'Y': Y_lbl,
                    'gamma_terms': gamma_terms,
                })

    # Build gb_matrix metadata
    fermionic_labels = ['a_1_p', 'a_1_m']
    bosonic_labels = []
    for j in range(1, n + 1):
        bosonic_labels.extend([f'b_{j}_p', f'b_{j}_m'])

    gb_entries = {}
    for sigma in fermionic_labels:
        for bs in bosonic_labels:
            lbl = gb_label(sigma, bs)
            gb_entries[lbl] = {
                'fermionic': sigma,
                'bosonic': bs,
                'definition': f'({sigma} | {bs}) in the skew-supersymmetric bilinear form',
                'parity': 1,
            }

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    return {
        'schema_version': '5.0',
        'schema_layer': 2,
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {
                'osp': f'osp(2|{2 * n})',
                'dimension_formula': 'osp(2m|2n) with m=1',
            },
            'dimension': {
                'total': even_dim + odd_dim,
                'even': even_dim,
                'odd': odd_dim,
            },
        },
        'sign_convention': {
            'label': 'A',
            'description': (
                'gb_{sigma,j,s} = (a_1^sigma | b_j^s) from the skew-supersymmetric bilinear form. '
                'Deformed exchange relation: [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa. '
                'Equivalently: b_j^s * a_1^sigma = a_1^sigma * b_j^s - gb_{sigma,j,s} * kappa '
                'under PBW normalization.'
            ),
            'deformed_relation': '[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa',
        },
        'gb_matrix': {
            'description': (
                'Gram matrix of the deformation parameters. '
                'Rows: fermionic oscillator labels (a_1^sigma). '
                'Cols: bosonic oscillator labels (b_j^s). '
                'Entry gb_{sigma,j,s} = (a_1^sigma | b_j^s).'
            ),
            'size': f'2 x {2 * n} = {4 * n} parameters',
            'rows': fermionic_labels,
            'cols': bosonic_labels,
            'entries': gb_entries,
        },
        'gamma_structure': gamma_structure,
        'metadata': {
            'generated_by': 'compute_gamma.py',
            'generation_date': str(date.today()),
            'notes': (
                'Each entry encodes: [X, Y]_deformed = [X, Y]_0 + kappa * gamma(X, Y). '
                'gamma(X, Y) = sum_terms (coeff * gb_label) * Z. '
                'Only non-zero gamma pairs (X < Y in PBW order) are listed. '
                'gamma coefficients are linear in the gb parameters (first-order deformation).'
            ),
            'references': [
                'Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras',
                'docs/math/C_inhomogeneous_definition.md',
            ],
        },
    }


# ─── Consistency check ────────────────────────────────────────────────────────

def check_consistency(gamma_schema, structure_schema):
    """
    Verify consistency between Schema 2 (gamma) and Schema 1 (structure constants).

    Checks:
    1. Every generator referenced in gamma_structure appears in Schema 1 basis.
    2. Parity: gamma(X, Y) has parity p(X) + p(Y) + 1 (mod 2).
    3. gamma coefficients are linear in gb (no gb-squared).
    """
    parity = structure_schema['parity']
    basis_set = set(structure_schema['basis']['odd'] + structure_schema['basis']['even'])
    errors = []

    for entry in gamma_schema['gamma_structure']:
        X, Y = entry['X'], entry['Y']
        px, py = parity[X], parity[Y]
        expected_parity_gamma = (px + py + 1) % 2

        for term in entry['gamma_terms']:
            Z = term['Z']
            if Z not in basis_set:
                errors.append(f"Unknown generator {Z} in gamma({X},{Y})")
                continue
            pz = parity[Z]
            if pz != expected_parity_gamma:
                errors.append(
                    f"Parity mismatch in gamma({X},{Y}): Z={Z} has parity {pz}, "
                    f"expected {expected_parity_gamma}"
                )

    return errors


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate C(n+1) Schema 2 (gamma structure) JSON'
    )
    parser.add_argument('--n', type=int, nargs='+', default=[1, 2, 3])
    parser.add_argument('--output-dir', default='data')
    parser.add_argument('--check', action='store_true', help='Run consistency check')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    for n in args.n:
        print(f'Generating gamma structure for C({n + 1}) = osp(2|{2 * n})...')
        gamma_schema = generate_gamma_schema(n)
        fname = os.path.join(args.output_dir, f'C_{n}_gamma.json')
        with open(fname, 'w') as f:
            json.dump(gamma_schema, f, indent=2)

        ng = len(gamma_schema['gamma_structure'])
        nt = sum(len(e['gamma_terms']) for e in gamma_schema['gamma_structure'])
        print(f'  Written: {fname}')
        print(f'  Non-zero gamma pairs: {ng}')
        print(f'  Total gamma terms (before grouping): {nt}')

        if args.check:
            struct_fname = os.path.join(args.output_dir, f'C_{n}_structure.json')
            if not os.path.exists(struct_fname):
                print(f'  Skipping consistency check: {struct_fname} not found.')
                continue
            with open(struct_fname) as f:
                struct = json.load(f)
            errors = check_consistency(gamma_schema, struct)
            if errors:
                print(f'  CONSISTENCY ERRORS:')
                for e in errors:
                    print(f'    {e}')
            else:
                print(f'  Consistency check PASSED.')


if __name__ == '__main__':
    main()
