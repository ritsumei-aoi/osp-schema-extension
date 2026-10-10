#!/usr/bin/env python3
"""
evaluate_gamma.py: Schema 3 (Evaluated Structure) generator for C(n+1) = osp(2|2n).

Reads Schema 2 gamma JSON files and substitutes concrete numeric values for the
gb deformation parameters, producing evaluated structure constants.

Outputs Schema 3 JSON files: data/C_{n}_evaluated_{profile}.json for n=1, 2, 3.

Profile "allplus": all 4n gb parameters set to +1.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
from fractions import Fraction
from datetime import date


# ─── Profile definitions ──────────────────────────────────────────────────────

PROFILES = {
    'allplus': {
        'name': 'allplus',
        'description': 'All 4n gb parameters set to +1 (maximal deformation).',
        'value_fn': lambda gb_label: 1,
    },
}


def build_gb_values(gb_entries, profile):
    """Return {gb_label: numeric_value} for all entries in gb_matrix."""
    value_fn = PROFILES[profile]['value_fn']
    return {lbl: value_fn(lbl) for lbl in gb_entries}


# ─── Evaluation logic ─────────────────────────────────────────────────────────

def evaluate_gamma_structure(gamma_structure, gb_values):
    """
    Substitute gb values into the symbolic gamma structure.

    For each pair (X, Y), the gamma terms are:
        gamma(X, Y) = sum_terms coeff * gb_label * Z

    After substitution:
        gamma(X, Y) = sum_Z  (sum_{terms for Z} coeff * gb_value)  * Z

    Returns a list of evaluated entries:
        [{ 'X': X, 'Y': Y, 'gamma_terms': [{'Z': Z, 'coeff': str}] }]
    Only entries with at least one non-zero evaluated term are included.
    """
    evaluated = []
    for entry in gamma_structure:
        X, Y = entry['X'], entry['Y']
        # Accumulate numeric coefficients per Z
        z_coeff = {}
        for term in entry['gamma_terms']:
            gb_lbl = term['gb_label']
            Z = term['Z']
            sym_coeff = Fraction(term['coeff'])
            gb_val = Fraction(gb_values.get(gb_lbl, 0))
            contrib = sym_coeff * gb_val
            z_coeff[Z] = z_coeff.get(Z, Fraction(0)) + contrib

        # Filter zero terms
        nonzero_terms = [
            {'Z': Z, 'coeff': str(c)}
            for Z, c in z_coeff.items()
            if c != 0
        ]
        if nonzero_terms:
            evaluated.append({'X': X, 'Y': Y, 'gamma_terms': nonzero_terms})

    return evaluated


# ─── Schema 3 generation ──────────────────────────────────────────────────────

def generate_evaluated_schema(gamma_schema, structure_schema, profile):
    """
    Generate Schema 3 dict by evaluating Schema 2 with the given gb profile.
    """
    gb_entries = gamma_schema['gb_matrix']['entries']
    gb_values = build_gb_values(gb_entries, profile)

    profile_meta = PROFILES[profile]

    evaluated_gamma = evaluate_gamma_structure(
        gamma_schema['gamma_structure'], gb_values
    )

    n = gamma_schema['algebra']['n']
    fermionic_labels = gamma_schema['gb_matrix']['rows']
    bosonic_labels = gamma_schema['gb_matrix']['cols']

    # Record gb values in matrix form (rows x cols)
    gb_value_matrix = {}
    for sigma in fermionic_labels:
        row = {}
        for bs in bosonic_labels:
            lbl = f'gb_{sigma}_{bs}'
            row[bs] = gb_values.get(lbl, 0)
        gb_value_matrix[sigma] = row

    return {
        'schema_version': '5.0',
        'schema_layer': 3,
        'algebra': gamma_schema['algebra'],
        'sign_convention': gamma_schema['sign_convention'],
        'gb_profile': {
            'name': profile_meta['name'],
            'description': profile_meta['description'],
            'fermionic_labels': fermionic_labels,
            'bosonic_labels': bosonic_labels,
            'values': {lbl: gb_values[lbl] for lbl in sorted(gb_values)},
            'value_matrix': gb_value_matrix,
        },
        'evaluated_gamma': evaluated_gamma,
        'metadata': {
            'generated_by': 'evaluate_gamma.py',
            'generation_date': str(date.today()),
            'source_schema2': f'C_{n}_gamma.json',
            'source_schema1': f'C_{n}_structure.json',
            'notes': (
                'Each entry encodes the evaluated gamma coefficient: '
                '[X, Y]_deformed = [X, Y]_0 + kappa * gamma(X, Y). '
                'gamma(X, Y) = sum_Z coeff * Z, where coeff is a rational number '
                'obtained by substituting the gb profile values into the Schema 2 '
                'symbolic expression. Only non-zero pairs are listed.'
            ),
            'references': [
                'Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras',
                'docs/math/C_inhomogeneous_definition.md',
            ],
        },
    }


# ─── Consistency check ────────────────────────────────────────────────────────

def check_consistency(eval_schema, gamma_schema, structure_schema, gb_values):
    """
    Verify Schema 3 consistency against Schema 2 and Schema 1.

    Checks:
    1. Every Z in evaluated_gamma appears in Schema 1 basis.
    2. Evaluated coefficients match manual substitution of gb values into Schema 2.
    3. Parity: gamma(X, Y) has parity p(X) + p(Y) + 1 (mod 2).
    """
    parity = structure_schema['parity']
    basis_set = set(structure_schema['basis']['odd'] + structure_schema['basis']['even'])
    errors = []

    # Build lookup from evaluated_gamma for comparison
    eval_lookup = {}
    for entry in eval_schema['evaluated_gamma']:
        key = (entry['X'], entry['Y'])
        eval_lookup[key] = {t['Z']: Fraction(t['coeff']) for t in entry['gamma_terms']}

    # Manually substitute gb values into Schema 2 and compare
    gamma_structure = gamma_schema['gamma_structure']
    for entry in gamma_structure:
        X, Y = entry['X'], entry['Y']
        px, py = parity.get(X, -1), parity.get(Y, -1)
        expected_parity_gamma = (px + py + 1) % 2

        expected_z_coeff = {}
        for term in entry['gamma_terms']:
            gb_lbl = term['gb_label']
            Z = term['Z']
            sym_coeff = Fraction(term['coeff'])
            gb_val = Fraction(gb_values.get(gb_lbl, 0))
            contrib = sym_coeff * gb_val
            expected_z_coeff[Z] = expected_z_coeff.get(Z, Fraction(0)) + contrib

        expected_z_coeff = {Z: c for Z, c in expected_z_coeff.items() if c != 0}

        got_z_coeff = eval_lookup.get((X, Y), {})

        # Check all expected terms are present and correct
        for Z, exp_c in expected_z_coeff.items():
            if Z not in basis_set:
                errors.append(f'  Unknown basis element {Z} in evaluated gamma({X},{Y})')
                continue
            got_c = got_z_coeff.get(Z, Fraction(0))
            if got_c != exp_c:
                errors.append(
                    f'  Coeff mismatch gamma({X},{Y})[{Z}]: '
                    f'expected {exp_c}, got {got_c}'
                )
            pz = parity.get(Z, -1)
            if pz != expected_parity_gamma:
                errors.append(
                    f'  Parity error in gamma({X},{Y})[{Z}]: '
                    f'Z parity={pz}, expected {expected_parity_gamma}'
                )

        # Check no extra terms in evaluated
        for Z in got_z_coeff:
            if Z not in expected_z_coeff:
                errors.append(
                    f'  Unexpected term {Z} in evaluated gamma({X},{Y})'
                )

    return errors


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate C(n+1) Schema 3 (evaluated structure) JSON'
    )
    parser.add_argument('--n', type=int, nargs='+', default=[1, 2, 3])
    parser.add_argument('--profile', default='allplus', choices=list(PROFILES))
    parser.add_argument('--input-dir', default='data')
    parser.add_argument('--output-dir', default='data')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    for n in args.n:
        alg = f'C({n + 1}) = osp(2|{2 * n})'
        print(f'Evaluating gamma structure for {alg} with profile "{args.profile}"...')

        gamma_fname = os.path.join(args.input_dir, f'C_{n}_gamma.json')
        struct_fname = os.path.join(args.input_dir, f'C_{n}_structure.json')

        if not os.path.exists(gamma_fname):
            print(f'  ERROR: Schema 2 file not found: {gamma_fname}')
            sys.exit(1)
        if not os.path.exists(struct_fname):
            print(f'  ERROR: Schema 1 file not found: {struct_fname}')
            sys.exit(1)

        with open(gamma_fname) as f:
            gamma_schema = json.load(f)
        with open(struct_fname) as f:
            structure_schema = json.load(f)

        eval_schema = generate_evaluated_schema(gamma_schema, structure_schema, args.profile)

        # Consistency check
        gb_entries = gamma_schema['gb_matrix']['entries']
        gb_values = build_gb_values(gb_entries, args.profile)
        errors = check_consistency(eval_schema, gamma_schema, structure_schema, gb_values)
        if errors:
            print(f'  CONSISTENCY ERRORS:')
            for e in errors:
                print(e)
            sys.exit(1)
        else:
            print(f'  Consistency check PASSED.')

        out_fname = os.path.join(args.output_dir, f'C_{n}_evaluated_{args.profile}.json')
        with open(out_fname, 'w') as f:
            json.dump(eval_schema, f, indent=2)

        n_pairs = len(eval_schema['evaluated_gamma'])
        n_terms = sum(len(e['gamma_terms']) for e in eval_schema['evaluated_gamma'])
        print(f'  Written: {out_fname}')
        print(f'  Non-zero evaluated gamma pairs: {n_pairs}')
        print(f'  Total evaluated gamma terms: {n_terms}')


if __name__ == '__main__':
    main()
