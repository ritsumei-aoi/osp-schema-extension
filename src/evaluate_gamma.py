#!/usr/bin/env python3
"""
evaluate_gamma.py

Evaluate the gamma structure (Schema 2) for a concrete gb profile -> Schema 3.
Profile A (all-ones): all 4n gb parameters = 1.

Outputs data/C_{n}_evaluated_all1.json for n=1,2,3.
"""

import sys
import json
import datetime
from fractions import Fraction
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Profile definitions
# ---------------------------------------------------------------------------

PROFILE_A = {
    'name': 'all_ones',
    'file_suffix': 'all1',
    'description': 'All gb parameters = 1 (standard reference profile)',
    'rule': lambda gb_label: Fraction(1),
}


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path) as f:
        return json.load(f)


def evaluate_profile(schema1, schema2, profile):
    """
    Build Schema 3 evaluated_brackets from Schema 1 (g-part) and Schema 2 (kappa-part).

    Returns list of {X, Y, g_part, kappa_part} sorted by basis index order.
    """
    gb_rule = profile['rule']

    # g-part: group Schema 1 structure_constants by (X, Y)
    g_table = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema1['structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        g_table[(X, Y)][Z] += Fraction(entry['coeff'])

    # kappa-part: group Schema 2 gamma by (X, Y), sum gb_val * coeff over gb_labels
    kappa_table = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema2['gamma']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        gb_val = gb_rule(entry['gb_label'])
        kappa_table[(X, Y)][Z] += gb_val * Fraction(entry['coeff'])

    # Build sorted pair list using basis order from Schema 1
    basis = schema1['basis']
    all_labels = basis['even'] + basis['odd']
    label_idx = {lbl: i for i, lbl in enumerate(all_labels)}

    all_pairs = sorted(
        set(g_table.keys()) | set(kappa_table.keys()),
        key=lambda xy: (label_idx.get(xy[0], 9999), label_idx.get(xy[1], 9999)),
    )

    def to_list(raw_dict):
        return [
            {'Z': z, 'coeff': str(c)}
            for z, c in sorted(raw_dict.items(),
                                key=lambda zc: label_idx.get(zc[0], 9999))
            if c != 0
        ]

    evaluated_brackets = []
    for (X, Y) in all_pairs:
        g_part = to_list(g_table.get((X, Y), {}))
        kappa_part = to_list(kappa_table.get((X, Y), {}))
        if g_part or kappa_part:
            evaluated_brackets.append({
                'X': X,
                'Y': Y,
                'g_part': g_part,
                'kappa_part': kappa_part,
            })

    return evaluated_brackets


def build_schema3(n, schema1, schema2, profile):
    """Build the full Schema 3 dict for C(n+1)."""
    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    gb_params = schema2['gb_matrix']['parameters']
    assignments = {p['label']: str(profile['rule'](p['label']))
                   for p in gb_params}

    evaluated_brackets = evaluate_profile(schema1, schema2, profile)

    n_with_g = sum(1 for b in evaluated_brackets if b['g_part'])
    n_with_k = sum(1 for b in evaluated_brackets if b['kappa_part'])

    return {
        'schema_version': '5.0',
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {'osp': f'osp(2|{2 * n})'},
            'dimension': {
                'even': even_dim,
                'odd': odd_dim,
                'total': even_dim + odd_dim,
            },
        },
        'gb_profile': {
            'name': profile['name'],
            'file_suffix': profile['file_suffix'],
            'description': profile['description'],
            'assignments': assignments,
        },
        'evaluated_brackets': evaluated_brackets,
        'metadata': {
            'generated_by': 'src/evaluate_gamma.py',
            'generation_date': datetime.date.today().isoformat(),
            'n': n,
            'gb_profile': profile['name'],
            'source_schema1': f'C_{n}_structure.json',
            'source_schema2': f'C_{n}_gamma.json',
            'stats': {
                'total_pairs': len(evaluated_brackets),
                'pairs_with_g_part': n_with_g,
                'pairs_with_kappa_part': n_with_k,
            },
            'references': [
                'C_inhomogeneous_definition.md',
                'docs/json_schema_specification.md',
            ],
        },
    }


# ---------------------------------------------------------------------------
# Consistency verification
# ---------------------------------------------------------------------------

def verify_schema3(schema3, schema1, schema2, profile):
    """
    Verify Schema 3 consistency against Schema 1 and Schema 2.

    Checks:
      1. g_part entries match Schema 1 structure_constants (exact Fraction equality)
      2. kappa_part entries match Schema 2 gamma (with gb substitution)
      3. No pair (X,Y) with non-zero g-part or kappa-part is missing
      4. Algebra dimension metadata matches
    """
    failures = []
    gb_rule = profile['rule']

    g_table = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema1['structure_constants']:
        g_table[(entry['X'], entry['Y'])][entry['Z']] += Fraction(entry['coeff'])

    kappa_table = defaultdict(lambda: defaultdict(Fraction))
    for entry in schema2['gamma']:
        gb_val = gb_rule(entry['gb_label'])
        kappa_table[(entry['X'], entry['Y'])][entry['Z']] += gb_val * Fraction(entry['coeff'])

    covered_pairs = set()
    for bracket in schema3['evaluated_brackets']:
        X, Y = bracket['X'], bracket['Y']
        covered_pairs.add((X, Y))

        g_expected = {z: c for z, c in g_table.get((X, Y), {}).items() if c != 0}
        g_actual = {e['Z']: Fraction(e['coeff']) for e in bracket['g_part']}
        if g_expected != g_actual:
            failures.append(
                f"g_part mismatch ({X},{Y}): expected={g_expected} actual={g_actual}"
            )

        k_expected = {z: c for z, c in kappa_table.get((X, Y), {}).items() if c != 0}
        k_actual = {e['Z']: Fraction(e['coeff']) for e in bracket['kappa_part']}
        if k_expected != k_actual:
            failures.append(
                f"kappa_part mismatch ({X},{Y}): expected={k_expected} actual={k_actual}"
            )

    missing = (set(g_table.keys()) | set(kappa_table.keys())) - covered_pairs
    if missing:
        failures.append(
            f"Missing {len(missing)} pair(s) from evaluated_brackets: {list(missing)[:5]}"
        )

    n = schema3['algebra']['n']
    if schema3['algebra']['dimension']['even'] != 2 * n * n + n + 1:
        failures.append(f"Even dim mismatch for n={n}")
    if schema3['algebra']['dimension']['odd'] != 4 * n:
        failures.append(f"Odd dim mismatch for n={n}")

    return failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    dry_run = '--dry-run' in sys.argv
    verify_only = '--verify' in sys.argv

    if '--data-dir' in sys.argv:
        idx = sys.argv.index('--data-dir')
        data_dir = Path(sys.argv[idx + 1])
    else:
        data_dir = Path(__file__).parent.parent / 'data'
    if not dry_run and not verify_only:
        data_dir.mkdir(exist_ok=True)

    profile = PROFILE_A
    overall_pass = True

    for n in [1, 2, 3]:
        print(f'\n--- C({n + 1}) = osp(2|{2 * n}), n={n} ---', flush=True)

        schema1 = load_json(data_dir / f'C_{n}_structure.json')
        schema2 = load_json(data_dir / f'C_{n}_gamma.json')

        schema3 = build_schema3(n, schema1, schema2, profile)
        stats = schema3['metadata']['stats']
        print(f'  Profile: {profile["name"]}')
        print(f'  Total pairs: {stats["total_pairs"]} '
              f'(g: {stats["pairs_with_g_part"]}, κ: {stats["pairs_with_kappa_part"]})')

        failures = verify_schema3(schema3, schema1, schema2, profile)
        if failures:
            print(f'  Consistency: FAIL ({len(failures)} issue(s))')
            for msg in failures[:5]:
                print(f'    {msg}')
            overall_pass = False
        else:
            print(f'  Consistency: PASS')

        suffix = profile['file_suffix']
        out_name = f'C_{n}_evaluated_{suffix}.json'
        if dry_run or verify_only:
            print(f'  [{"dry-run" if dry_run else "verify-only"}] would write data/{out_name}')
        else:
            out = data_dir / out_name
            with open(out, 'w') as f:
                json.dump(schema3, f, indent=2)
            print(f'  written: {out}')

    print(f'\n{"OVERALL: ALL CHECKS PASSED" if overall_pass else "OVERALL: SOME CHECKS FAILED"}')
    return 0 if overall_pass else 1


if __name__ == '__main__':
    sys.exit(main())
