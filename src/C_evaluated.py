"""Schema 3: the evaluated structure of C(n+1) for a representative assignment of the gb parameters.

Reads only data/C_{n}_structure.json (Schema 1) and data/C_{n}_gamma.json (Schema 2) and substitutes
numbers for the gb parameters.  The deformed bracket is
    [X, Y]_gb = [X, Y]_0 + kappa * (sum_gb gb * gamma(X, Y))  (+ K-components),
so the evaluated file records both the kappa-free coefficient (Schema 1) and the kappa coefficient.

Representative assignment (I06): all 4n parameters set to +1.  The same function evaluates any
profile, which I08 uses.

Usage:  python3 src/C_evaluated.py
"""

import datetime
import json
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, 'data')
RANKS = (1, 2, 3)


def _frac(value):
    return str(Fraction(value))


def load_schema1(n, data_dir=DATA_DIR):
    with open(os.path.join(data_dir, 'C_%d_structure.json' % n), encoding='utf-8') as fh:
        doc = json.load(fh)
    table = {}
    for entry in doc['structure_constants']:
        key = (entry['X'], entry['Y'], entry['Z'])
        table[key] = Fraction(entry['coeff'])
    return doc, table


def load_schema2(n, data_dir=DATA_DIR):
    with open(os.path.join(data_dir, 'C_%d_gamma.json' % n), encoding='utf-8') as fh:
        doc = json.load(fh)
    entries = {}
    for e in doc['inhomogeneous_deformation']['entries']:
        entries.setdefault((e['X'], e['Y'], e['Z']), {})[e['gb']] = Fraction(e['coeff'])
    k_entries = {}
    for e in doc['inhomogeneous_deformation']['K_components']:
        k_entries.setdefault((e['X'], e['Y']), {})[e['gb']] = Fraction(e['coeff'])
    return doc, entries, k_entries


def gb_labels(n):
    """All 4n gb labels, in the order used by the Schema 2 gb_matrix."""
    return list(load_schema2(n)[0]['gb_matrix']['labels'])


def evaluate(n, gb_values, data_dir=DATA_DIR):
    """Evaluate the structure for gb_values = {label: Fraction}.  Labels not given default to 0."""
    _s1_doc, kappa0 = load_schema1(n, data_dir)
    _s2_doc, gamma, k_gamma = load_schema2(n, data_dir)
    kappa1 = {}
    for key, per_gb in gamma.items():
        value = sum(gb_values.get(label, 0) * coeff for label, coeff in per_gb.items())
        if value != 0:
            kappa1[key] = value
    k_part = {}
    for key, per_gb in k_gamma.items():
        value = sum(gb_values.get(label, 0) * coeff for label, coeff in per_gb.items())
        if value != 0:
            k_part[key] = value
    return kappa0, kappa1, k_part


def build_schema3(n, gb_values, rule, generation_date, data_dir=DATA_DIR):
    kappa0, kappa1, k_part = evaluate(n, gb_values, data_dir)
    keys = sorted(set(kappa0) | set(kappa1))
    structure_constants = []
    for key in keys:
        c0 = kappa0.get(key, Fraction(0))
        c1 = kappa1.get(key, Fraction(0))
        if c0 == 0 and c1 == 0:
            continue
        structure_constants.append({
            'X': key[0], 'Y': key[1], 'Z': key[2],
            'coeff_kappa0': _frac(c0),
            'coeff_kappa1': _frac(c1),
        })
    k_list = [{'X': key[0], 'Y': key[1], 'coeff_kappa1': _frac(value)}
              for key, value in sorted(k_part.items())]
    labels = gb_labels(n)
    return {
        'schema_version': '5.0',
        'algebra_ref': 'C_%d_structure.json' % n,
        'gb_values': {label: _frac(gb_values.get(label, 0)) for label in labels},
        'representative_rule': rule,
        'structure_constants': structure_constants,
        'K_components': k_list,
        'metadata': {
            'generated_by': 'src/C_evaluated.py',
            'generation_date': generation_date,
            'bracket': '[X,Y]_gb = [X,Y]_0 + kappa * kappa1 (+ K_components * kappa * K)',
        },
    }


def consistency_with_schema2(n, gb_values, data_dir=DATA_DIR):
    """Recompute kappa1 directly from the Schema 2 entries (independent summation) and compare."""
    _s2_doc, gamma, k_gamma = load_schema2(n, data_dir)
    expected = {}
    for e in _s2_doc['inhomogeneous_deformation']['entries']:
        key = (e['X'], e['Y'], e['Z'])
        expected[key] = expected.get(key, Fraction(0)) + gb_values.get(e['gb'], 0) * Fraction(e['coeff'])
    expected = {k: v for k, v in expected.items() if v != 0}
    _kappa0, kappa1, _kp = evaluate(n, gb_values, data_dir)
    mismatches = sum(1 for k in set(expected) | set(kappa1) if expected.get(k, 0) != kappa1.get(k, 0))
    return {'entries_compared': len(set(expected) | set(kappa1)), 'mismatches': mismatches}


def main():
    generation_date = datetime.date.today().isoformat()
    for n in RANKS:
        labels = gb_labels(n)
        gb_values = {label: Fraction(1) for label in labels}
        doc = build_schema3(n, gb_values, 'all gb = 1 (representative assignment)', generation_date)
        path = os.path.join(DATA_DIR, 'C_%d_evaluated.json' % n)
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write('\n')
        check = consistency_with_schema2(n, gb_values)
        print('n=%d structure_constants=%d K=%d schema2_consistency=%s' % (
            n, len(doc['structure_constants']), len(doc['K_components']), check))


if __name__ == '__main__':
    main()
