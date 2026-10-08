"""Generate the Schema 1 files data/C_{n}_structure.json for C(n+1) = osp(2|2n), n = 1, 2, 3.

Structure constants are computed exactly from the oscillator realization in c_algebra.py
(kappa-free part only; the deformation is handled in C_gamma.py).

Usage:  python3 src/C_generators.py
"""

import datetime
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from c_algebra import structure  # noqa: E402

ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, 'data')
RANKS = (1, 2, 3)


def _frac(value):
    """Exact rational as a JSON string, e.g. '1/2', '-1', '0'."""
    value = Fraction(value)
    return str(value)


def build_schema1(n, basis, sc, generation_date):
    """Assemble the Schema 1 dict (see docs/json_schema_specification.md, section 1)."""
    even = [x['label'] for x in basis if x['parity'] == 0]
    odd = [x['label'] for x in basis if x['parity'] == 1]
    dim_even, dim_odd = len(even), len(odd)
    if dim_even != 2 * n * n + n + 1 or dim_odd != 4 * n:
        raise ValueError('dimension mismatch for n=%d' % n)

    realizations = {}
    for x in basis:
        standard_form = [{'words': words, 'coeff': _frac(coeff)} for coeff, words in x['words']]
        realizations[x['label']] = {'standard_form': standard_form, 'parity': x['parity']}
    realizations['H_%d' % (n + 1)]['note'] = (
        'Terminal Cartan; the constant -1/2 comes from bosonic normal ordering of -b_n^+ b_n^-')

    structure_constants = []
    for a, A in enumerate(basis):
        for b, Bb in enumerate(basis):
            for c, coeff in sorted(sc[(a, b)].items()):
                if coeff == 0:
                    continue
                structure_constants.append({
                    'X': A['label'],
                    'Y': Bb['label'],
                    'Z': basis[c]['label'],
                    'coeff': _frac(coeff),
                    'sign_rule': 'graded',
                })

    return {
        'schema_version': '5.0',
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': 'C(n+1)',
            'alternative_notation': {
                'osp': 'osp(2|%d)' % (2 * n),
                'dimension_formula': 'osp(2m|2n) with m=1',
            },
            'dimension': {
                'total': dim_even + dim_odd,
                'even': dim_even,
                'odd': dim_odd,
                'formulas': {'even': '2n^2 + n + 1', 'odd': '4n', 'total': '2n^2 + 5n + 1'},
            },
        },
        'oscillator_generators': {
            'fermions': {
                'm': 1,
                'labels': ['a_1_p', 'a_1_m'],
                'parity': 1,
                'relation': '{a_1_m, a_1_p} = 1, (a_1_p)^2 = (a_1_m)^2 = 0',
                'description': 'Standard fermionic pair (CAR); replaces B(m,n)\'s supplementary fermion a_0.',
            },
            'bosons': {
                'n': n,
                'count': 2 * n,
                'labels': ['b_%d_%s' % (k, s) for k in range(1, n + 1) for s in ('p', 'm')],
                'description': 'Bosonic oscillators b_i^± with i=1,...,n',
            },
        },
        'oscillator_relations': {
            'standard_fermion_anticommutators': {
                'relation': '{a_1_m, a_1_p} = 1',
                'nilpotency': '(a_1_p)^2 = (a_1_m)^2 = 0',
            },
            'bosonic_commutators': {
                'same_type': '[b_i^±, b_j^±] = 0',
                'conjugate_pair': '[b_i^-, b_j^+] = delta_ij',
            },
            'mixed_commutators': {
                'boson_fermion': '[b_j^s, a_1^sigma] = 0 undeformed; deformed: '
                                 '[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa',
            },
        },
        'central_elements': {
            'kappa': {'parity': 1,
                      'relation': 'super-central (commutes with bosons, anticommutes with a_1^±), kappa^2 = 0',
                      'role': 'formal nilpotent parameter of the deformation'},
            'K': {'parity': 0, 'relation': 'central, identified with the scalar 1',
                  'role': 'not a basis element; its components are recorded in Schema 2/3'},
        },
        'basis': {
            'even': even,
            'odd': odd,
            'ordering_convention': 'PBW: kappa < [odd] < [even], K excluded. '
                                   'Odd: k-major, then pp, pm, mp, mm. Even: B(0,n) order.',
        },
        'parity': {x['label']: x['parity'] for x in basis},
        'generator_realization': {
            'description': 'Oscillator words, normal ordered (fermions left, a_1_p before a_1_m, '
                           'b_k_p before b_k_m, bosons sorted by k)',
            'ordering': ', '.join(['a_1_p', 'a_1_m'] +
                                  ['b_%d_%s' % (k, s) for k in range(1, n + 1) for s in ('p', 'm')]),
            'realizations': realizations,
        },
        'structure_constants': structure_constants,
        'metadata': {
            'generated_by': 'src/C_generators.py',
            'generation_date': generation_date,
            'references': [
                'Frappat, Sciarrino, Sorba (2000), Dictionary on Lie Algebras and Superalgebras, arXiv:hep-th/9607161',
                'Bakalov and Sullivan (2017), arXiv:1612.09400',
            ],
        },
    }


def write_schema1(n, out_dir=DATA_DIR, generation_date=None):
    """Compute and write data/C_{n}_structure.json.  Returns the path written."""
    if generation_date is None:
        generation_date = datetime.date.today().isoformat()
    basis, sc, _gamma, _gamma_k = structure(n)
    doc = build_schema1(n, basis, sc, generation_date)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'C_%d_structure.json' % n)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    return path


def main():
    for n in RANKS:
        path = write_schema1(n)
        print('wrote', os.path.relpath(path, ROOT))


if __name__ == '__main__':
    main()
