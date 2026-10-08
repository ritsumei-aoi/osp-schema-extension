"""
C_evaluated_generator.py
Generate Schema 3 (Evaluated Structure) JSON for C(n+1) = osp(2|2n).

Substitutes concrete rational values for gb deformation parameters into
the symbolic gamma structure (Schema 2), producing numerically evaluated
deformed structure constants.

Output: C_{n}_evaluated_{profile_name}.json in the specified data directory.

Usage:
  python src/C_evaluated_generator.py [data_dir]   # writes JSON files
"""

import json
import sys
import datetime
from fractions import Fraction
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# gb sign profiles
# ---------------------------------------------------------------------------

def uniform_plus_profile(n: int) -> dict:
    """All 4n gb parameters set to +1."""
    values = {}
    for sigma in ['p', 'm']:
        for s in ['p', 'm']:
            for j in range(1, n + 1):
                values[f'gb_{sigma}{s}_{j}'] = Fraction(1)
    return values


PROFILES = {
    'uniform_plus': {
        'description': 'All gb parameters set to +1',
        'build': uniform_plus_profile,
    },
}


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_gamma(gamma_structure: list, gb_values: dict) -> list:
    """
    Substitute gb values into the symbolic gamma_structure.

    gamma_structure: list of {X, Y, Z, gb, coeff} from Schema 2.
    gb_values: {gb_label: Fraction}

    Returns list of {X, Y, Z, coeff} with rational coeff (no gb labels),
    aggregated per (X, Y, Z) triple, dropping exact zeros.
    """
    agg: dict = defaultdict(Fraction)
    for e in gamma_structure:
        gb_val = gb_values.get(e['gb'], Fraction(0))
        if gb_val == 0:
            continue
        agg[(e['X'], e['Y'], e['Z'])] += Fraction(e['coeff']) * gb_val

    return [
        {'X': X, 'Y': Y, 'Z': Z, 'coeff': str(c), 'sign_rule': 'graded'}
        for (X, Y, Z), c in sorted(agg.items())
        if c != 0
    ]


def build_schema3_json(n: int, profile_name: str, data_dir: Path) -> dict:
    """Build Schema 3 JSON for C(n+1) with bosonic rank n."""
    s1_path = data_dir / f'C_{n}_structure.json'
    s2_path = data_dir / f'C_{n}_gamma.json'

    with open(s1_path) as f:
        s1 = json.load(f)
    with open(s2_path) as f:
        s2 = json.load(f)

    profile = PROFILES[profile_name]
    gb_values = profile['build'](n)
    gb_rational = {k: str(v) for k, v in gb_values.items()}

    gamma_eval = evaluate_gamma(s2['gamma_structure'], gb_values)

    return {
        'schema_version': '5.0',
        'schema_layer': 3,
        'algebra': s1['algebra'],
        'central_elements': s1['central_elements'],
        'gb_profile': {
            'name': profile_name,
            'description': profile['description'],
            'values': gb_rational,
        },
        'structure_constants_0': s1['structure_constants'],
        'gamma_evaluated': gamma_eval,
        'metadata': {
            'generated_by': 'src/C_evaluated_generator.py',
            'generation_date': datetime.date.today().isoformat(),
            'n': n,
            'algebra': f'C({n + 1}) = osp(2|{2 * n})',
            'profile': profile_name,
            'source_schema1': str(s1_path),
            'source_schema2': str(s2_path),
            'n_undeformed_entries': len(s1['structure_constants']),
            'n_gamma_eval_entries': len(gamma_eval),
            'references': [
                'Frappat, Sciarrino, Sorba (2000)',
                'docs/math/C_inhomogeneous_definition.md',
            ],
        },
    }


# ---------------------------------------------------------------------------
# Consistency check: verify gamma_evaluated sums match Schema 2 for profile
# ---------------------------------------------------------------------------

def verify_consistency(schema3: dict, s2: dict, gb_values: dict) -> bool:
    """
    For each (X, Y) pair in Schema 2, recompute the evaluated gamma from
    Schema 2 directly and compare against gamma_evaluated in Schema 3.
    Returns True if consistent.
    """
    # Build reference from Schema 2
    ref: dict = defaultdict(Fraction)
    for e in s2['gamma_structure']:
        gb_val = gb_values.get(e['gb'], Fraction(0))
        ref[(e['X'], e['Y'], e['Z'])] += Fraction(e['coeff']) * gb_val

    # Build from Schema 3
    got: dict = {
        (e['X'], e['Y'], e['Z']): Fraction(e['coeff'])
        for e in schema3['gamma_evaluated']
    }

    # Compare
    all_keys = set(ref.keys()) | set(got.keys())
    ok = True
    for key in all_keys:
        r = ref.get(key, Fraction(0))
        g = got.get(key, Fraction(0))
        if r != g:
            print(f'  MISMATCH {key}: ref={r}, got={g}')
            ok = False
    return ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('data')

    for profile_name in PROFILES:
        print(f"\nProfile: {profile_name}")
        for n in [1, 2, 3]:
            # Load Schema 2 for consistency check
            s2_path = data_dir / f'C_{n}_gamma.json'
            with open(s2_path) as f:
                s2 = json.load(f)

            schema3 = build_schema3_json(n, profile_name, data_dir)
            gb_values = PROFILES[profile_name]['build'](n)

            print(f"  C({n+1}) n={n}: ", end='', flush=True)
            ok = verify_consistency(schema3, s2, gb_values)
            if not ok:
                print('CONSISTENCY FAIL — aborting.')
                sys.exit(1)

            out_path = data_dir / f'C_{n}_evaluated_{profile_name}.json'
            with open(out_path, 'w') as f:
                json.dump(schema3, f, indent=2)

            n0 = schema3['metadata']['n_undeformed_entries']
            ng = schema3['metadata']['n_gamma_eval_entries']
            print(f"OK  ({n0} undeformed + {ng} γ-eval entries) → {out_path}")


if __name__ == '__main__':
    main()
