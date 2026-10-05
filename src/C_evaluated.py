"""
C(n+1) = osp(2|2n) evaluated structure (Schema 3).

Substitutes concrete sign assignments into the gb parameters
and produces evaluated structure constants.
"""

import json
import sys
from fractions import Fraction
from datetime import date


def evaluate_gamma(gamma_data, gb_values):
    """
    Substitute gb_values into the symbolic gamma coefficients.
    gb_values: dict gb_label -> numeric value (Fraction)
    Returns: list of {X, Y, Z, coeff} with numeric coefficients.
    """
    result_dict = {}

    for entry in gamma_data['gamma_coefficients']:
        x, y, z = entry['X'], entry['Y'], entry['Z']
        gb_param = entry['gb_param']
        coeff = Fraction(entry['coeff'])
        gb_val = gb_values.get(gb_param, Fraction(0))

        key = (x, y, z)
        result_dict[key] = result_dict.get(key, Fraction(0)) + coeff * gb_val

    entries = []
    for (x, y, z), coeff in sorted(result_dict.items()):
        if coeff != Fraction(0):
            entries.append({
                'X': x,
                'Y': y,
                'Z': z,
                'coeff': str(coeff)
            })

    return entries


def build_evaluated_structure(structure_data, gamma_data, gb_values, gb_profile_name):
    """
    Build Schema 3: evaluated structure constants.
    The deformed bracket is [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)
    with gamma evaluated at specific gb values.
    """
    n = structure_data['algebra']['n']
    evaluated_gamma = evaluate_gamma(gamma_data, gb_values)

    gb_assignment = []
    for param in gamma_data['gb_matrix']['parameters']:
        label = param['label']
        gb_assignment.append({
            'label': label,
            'value': str(gb_values.get(label, Fraction(0)))
        })

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    schema = {
        'schema_version': '5.0',
        'layer': 3,
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {
                'osp': f'osp(2|{2 * n})'
            },
            'dimension': {
                'total': even_dim + odd_dim,
                'even': even_dim,
                'odd': odd_dim
            }
        },
        'gb_profile': {
            'name': gb_profile_name,
            'assignment': gb_assignment
        },
        'undeformed_structure_constants': structure_data['structure_constants'],
        'evaluated_gamma_coefficients': evaluated_gamma,
        'basis': structure_data['basis'],
        'parity': structure_data['parity'],
        'metadata': {
            'generated_by': 'C_evaluated.py',
            'generation_date': str(date.today()),
            'description': f'Evaluated structure for C({n+1}) with gb profile: {gb_profile_name}',
        }
    }
    return schema


def make_all_plus_profile(n):
    """All gb parameters set to +1."""
    from C_gamma import all_gb_labels
    return {label: Fraction(1) for label in all_gb_labels(n)}


def make_alternating_profile(n):
    """Alternating signs: gb_p_*_* = +1, gb_m_*_* = -1."""
    from C_gamma import all_gb_labels
    values = {}
    for label in all_gb_labels(n):
        sigma = label.split('_')[1]
        values[label] = Fraction(1) if sigma == 'p' else Fraction(-1)
    return values


def main():
    sys.path.insert(0, 'src')

    for n in [1, 2, 3]:
        with open(f'data/C_{n}_structure.json') as f:
            structure = json.load(f)
        with open(f'data/C_{n}_gamma.json') as f:
            gamma = json.load(f)

        gb_values = make_all_plus_profile(n)
        schema = build_evaluated_structure(structure, gamma, gb_values, 'all_plus')

        filename = f'data/C_{n}_evaluated_all_plus.json'
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2)

        print(f'C({n+1}): {filename} — '
              f'{len(schema["evaluated_gamma_coefficients"])} evaluated gamma entries')


if __name__ == '__main__':
    main()
