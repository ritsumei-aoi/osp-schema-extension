"""Evaluated structure for C(n+1) (Schema 3, Layer 3) at fixed gb values (I06).

Substitutes numerical gb values into the symbolic γ of Schema 2 and writes
``data/C_{n}_evaluated.json``. The representative profile is ``all_plus_one``
(every gb parameter = +1). Other profiles are used in the I08 analysis.

Usage:
    python src/C_evaluate.py      # writes data/C_{1,2,3}_evaluated.json
"""

import json
from fractions import Fraction
from pathlib import Path

from C_gamma import gamma_table, gb_parameters
from C_algebra import gb_label

GENERATION_DATE = '2026-10-08'
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'

PROFILES = {
    # representative profile used for the Layer 3 file
    'all_plus_one': lambda g: Fraction(1),
}


def gb_values(n, profile):
    """Return {gb_label: Fraction} for all 4n parameters."""
    fn = PROFILES[profile]
    return {gb_label(g): fn(g) for g in gb_parameters(n)}


def evaluate_from_schema2(n, values):
    """Evaluate Schema 2 JSON at ``values``. Returns {(X, Y, Z): Fraction}."""
    with open(DATA_DIR / f'C_{n}_gamma.json', encoding='utf-8') as f:
        s2 = json.load(f)
    out = {}
    for e in s2['gamma']:
        total = sum(Fraction(t['coeff']) * values[t['gb']] for t in e['terms'])
        if total != 0:
            key = (e['X'], e['Y'], e['Z'])
            out[key] = out.get(key, 0) + total
    return {k: v for k, v in out.items() if v != 0}


def evaluate_from_engine(n, values):
    """Independent path: recompute γ from the oscillator engine, then substitute."""
    basis, gamma, residuals = gamma_table(n)
    labels = [b['label'] for b in basis] + ['K']
    out = {}
    for (i, j), per_k in gamma.items():
        for k, per_g in per_k.items():
            total = sum(v * values[gb_label(g)] for g, v in per_g.items())
            if total != 0:
                key = (basis[i]['label'], basis[j]['label'], labels[k])
                out[key] = out.get(key, 0) + total
    return {k: v for k, v in out.items() if v != 0}


def build_schema3(n, profile, evaluated):
    values = gb_values(n, profile)
    entries = [{'X': X, 'Y': Y, 'Z': Z, 'coeff': str(v)}
               for (X, Y, Z), v in sorted(evaluated.items())]
    return {
        'schema_version': '5.0',
        'layer': 'Schema 3: evaluated structure (gamma at fixed gb)',
        'algebra': {'family': 'C', 'm': 1, 'n': n,
                    'cartan_type': f'C({n + 1})'},
        'profile': {
            'name': profile,
            'gb': {lab: str(v) for lab, v in sorted(values.items())},
        },
        'evaluated_gamma': entries,
        'metadata': {
            'generated_by': 'src/C_evaluate.py',
            'generation_date': GENERATION_DATE,
            'source': f'data/C_{n}_gamma.json',
        },
    }


def main():
    DATA_DIR.mkdir(exist_ok=True)
    profile = 'all_plus_one'
    for n in (1, 2, 3):
        values = gb_values(n, profile)
        ev2 = evaluate_from_schema2(n, values)
        ev_engine = evaluate_from_engine(n, values)
        agree = ev2 == ev_engine
        schema = build_schema3(n, profile, ev2)
        path = DATA_DIR / f'C_{n}_evaluated.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
            f.write('\n')
        k_nonzero = sum(1 for (_, _, Z) in ev2 if Z == 'K')
        print(f'n={n}: wrote {path.name}: {len(ev2)} nonzero entries '
              f'({k_nonzero} with Z=K); Schema 2 vs engine agree: {agree}')


if __name__ == '__main__':
    main()
