"""Generate Schema 1 (algebra structure) JSON for C(n+1) = osp(2|2n).

Usage:
    python src/C_generators.py            # writes data/C_1_structure.json,
                                          #        data/C_2_structure.json,
                                          #        data/C_3_structure.json

Structure constants are computed exactly in ``src/C_algebra.py``.
"""

import json
from fractions import Fraction
from pathlib import Path

from C_algebra import (build_basis, letter_label, parity, structure_constants)

GENERATION_DATE = '2026-10-08'
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'


def _frappat_letter(letter):
    if letter[0] == 'a':
        return 'a_1^' + ('+' if letter[1] > 0 else '-')
    return f"b_{letter[1]}^" + ('+' if letter[2] > 0 else '-')


def _frappat(elem):
    parts = []
    for (_, word), c in sorted(elem.items(), key=lambda t: (len(t[0][1]), t[0][1])):
        if not word:
            parts.append(str(c))
            continue
        name = ' '.join(_frappat_letter(l) for l in word)
        if c == 1:
            parts.append(name)
        elif c == -1:
            parts.append('-' + name)
        else:
            parts.append(f"{c}*{name}")
    return ' + '.join(parts).replace('+ -', '- ')


def _standard_form(elem):
    rows = []
    for (_, word), c in sorted(elem.items(), key=lambda t: (len(t[0][1]), t[0][1])):
        rows.append({'words': [letter_label(l) for l in word],
                     'coeff': str(c)})
    return rows


def build_schema1(n):
    basis, table, residuals = structure_constants(n)
    labels = [item['label'] for item in basis]
    even = [item['label'] for item in basis if item['parity'] == 0]
    odd = [item['label'] for item in basis if item['parity'] == 1]
    n_even, n_odd = len(even), len(odd)
    assert n_even == 2 * n * n + n + 1 and n_odd == 4 * n

    bosons = []
    for k in range(1, n + 1):
        bosons += [f'b_{k}_p', f'b_{k}_m']

    structure = []
    for (i, j) in sorted(table):
        X, Y = labels[i], labels[j]
        for k, c in sorted(table[(i, j)].items()):
            structure.append({'X': X, 'Y': Y, 'Z': labels[k], 'coeff': str(c),
                              'sign_rule': 'super-skew: [Y,X] = -(-1)^{p(X)p(Y)} [X,Y]'})
    for (i, j), res in sorted(residuals.items()):
        for w, c in res.items():
            structure.append({'X': labels[i], 'Y': labels[j], 'Z': 'K',
                              'coeff': str(c), 'word': [letter_label(l) for l in w],
                              'note': 'closure residual (must not occur)'})

    schema = {
        'schema_version': '5.0',
        'algebra': {
            'family': 'C', 'm': 1, 'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {
                'osp': f'osp(2|{2 * n})',
                'dimension_formula': 'osp(2m|2n) with m=1',
            },
            'dimension': {'total': 2 * n * n + 5 * n + 1,
                          'even': n_even, 'odd': n_odd},
        },
        'oscillator_generators': {
            'fermions': {'count': 2, 'm': 1, 'labels': ['a_1_p', 'a_1_m'],
                         'parity': 1,
                         'description': 'Standard fermionic pair a_1^+ (a_1_p), a_1^- (a_1_m)'},
            'bosons': {'count': 2 * n, 'n': n, 'labels': bosons,
                       'description': f'Bosonic oscillators b_k^± with k=1,...,{n}'},
        },
        'oscillator_relations': {
            'standard_fermion_anticommutators': {
                'relation': '{a_1^-, a_1^+} = 1',
                'self_relations': '(a_1^±)^2 = 0'},
            'bosonic_commutators': {
                'same_type': '[b_i^±, b_j^±] = 0',
                'conjugate_pair': '[b_i^-, b_j^+] = δ_ij'},
            'mixed_commutators': {
                'boson_fermion': '[b_k^±, a_1^±] = 0 (undeformed)'},
        },
        'central_elements': {
            'kappa': {'parity': 1, 'description': 'Odd central element; κ^2 = 0'},
            'K': {'parity': 0, 'value': 1,
                  'description': 'Even central element identified with the scalar 1; not a basis element'},
        },
        'basis': {
            'even': even,
            'odd': odd,
            'ordering_convention': 'PBW: κ < [odd] < [even]; K = 1 excluded from basis',
        },
        'parity': {item['label']: item['parity'] for item in basis},
        'generator_realization': {
            'description': 'Standard form with canonical word order: a_1_p, a_1_m, b_1_p, ..., b_n_p, b_1_m, ..., b_n_m',
            'realizations': {
                item['label']: {
                    'standard_form': _standard_form(item['elem']),
                    'frappat_form': _frappat(item['elem']),
                    'parity': item['parity'],
                } for item in basis
            },
        },
        'structure_constants': structure,
        'metadata': {
            'generated_by': 'src/C_generators.py',
            'generation_date': GENERATION_DATE,
            'references': [
                'Frappat, Sciarrino, Sorba, Dictionary on Lie Algebras and Superalgebras (2000); arXiv:hep-th/9607161',
                'Bakalov and Sullivan (2017)',
            ],
        },
    }
    return schema


def main():
    DATA_DIR.mkdir(exist_ok=True)
    for n in (1, 2, 3):
        schema = build_schema1(n)
        path = DATA_DIR / f'C_{n}_structure.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
            f.write('\n')
        print(f'wrote {path} ({len(schema["structure_constants"])} structure constant entries)')


if __name__ == '__main__':
    main()
