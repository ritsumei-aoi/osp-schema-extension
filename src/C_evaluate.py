"""
C_evaluate.py
Evaluates the symbolic gamma coefficients (Schema 2) by substituting
concrete values for the gb deformation parameters, producing Schema 3 JSON.

Default assignment: all gb parameters = +1.
Additional sign profile: alternating signs gb_{sigma}_{j}_{s} = sigma_sign * s_sign.
"""

import json
import os
from fractions import Fraction
from datetime import datetime


def load_gamma(n, data_dir='data'):
    path = os.path.join(data_dir, f'C_{n}_gamma.json')
    with open(path) as f:
        return json.load(f)


def collect_gb_params(gamma_data):
    """Collect all gb parameter names from gamma coefficients."""
    params = set()
    for entry in gamma_data['gamma_coefficients']:
        params.update(entry['gb_coeffs'].keys())
    return sorted(params)


def evaluate_entry(entry, assignment):
    """
    Evaluate a gamma entry under the given gb assignment.
    assignment: dict {gb_label: int/Fraction}
    Returns Fraction value or None if zero.
    """
    total = Fraction(0)
    for gb_label, coeff_str in entry['gb_coeffs'].items():
        c = Fraction(coeff_str)
        v = Fraction(assignment.get(gb_label, 0))
        total += c * v
    return total


def evaluate_gamma(gamma_data, assignment):
    """Apply gb assignment to all gamma entries. Returns list of non-zero entries."""
    results = []
    for entry in gamma_data['gamma_coefficients']:
        val = evaluate_entry(entry, assignment)
        if val != 0:
            results.append({
                'X': entry['X'],
                'Y': entry['Y'],
                'Z': entry['Z'],
                'coeff': str(val)
            })
    return results


def make_all_ones_assignment(gb_params):
    return {p: 1 for p in gb_params}


def make_sign_profile_assignment(gb_params):
    """
    Alternating sign profile: gb_{sigma}_{j}_{s} = (+1 if sigma=p else -1) * (+1 if s=p else -1).
    """
    assignment = {}
    for p in gb_params:
        # label format: gb_{sigma}_{j}_{s}
        parts = p.split('_')  # ['gb', sigma, j, s]
        sigma = parts[1]
        s = parts[3]
        sigma_sign = 1 if sigma == 'p' else -1
        s_sign = 1 if s == 'p' else -1
        assignment[p] = sigma_sign * s_sign
    return assignment


def generate_evaluated(n, output_dir='data'):
    gamma_data = load_gamma(n, output_dir)
    gb_params = collect_gb_params(gamma_data)

    algebra_info = gamma_data['algebra'].copy()
    algebra_info['layer'] = 3

    # Assignment: all gb = +1
    assignment = make_all_ones_assignment(gb_params)
    evaluated = evaluate_gamma(gamma_data, assignment)

    out = {
        'schema_version': '5.0',
        'algebra': algebra_info,
        'gb_assignment': {p: str(assignment[p]) for p in gb_params},
        'gb_assignment_label': 'all_ones',
        'evaluated_gamma': evaluated,
        'metadata': {
            'source_file': f'C_{n}_gamma.json',
            'n_gamma_entries_symbolic': len(gamma_data['gamma_coefficients']),
            'n_gamma_entries_nonzero': len(evaluated),
            'generated_at': datetime.now().isoformat()
        }
    }

    path = os.path.join(output_dir, f'C_{n}_evaluated.json')
    with open(path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"n={n}: {len(evaluated)} non-zero evaluated entries → {path}")
    return out


def generate_all(output_dir='data'):
    for n in range(1, 4):
        generate_evaluated(n, output_dir)


if __name__ == '__main__':
    generate_all()
