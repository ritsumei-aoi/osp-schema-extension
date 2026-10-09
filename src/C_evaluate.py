#!/usr/bin/env python3
"""
Schema 3: Evaluated structure for C(n+1) = osp(2|2n).

Substitutes concrete values into the gb parameters from Schema 2 (gamma structure).
Uses the representative assignment: all gb parameters = +1.

Output: C_{n}_evaluated.json for n=1, 2, 3.
"""

from fractions import Fraction
from collections import defaultdict
import json
import os
import re
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def evaluate_coeff_expr(coeff_expr_str, gb_values):
    """Evaluate a coeff_expr string given gb_values dict.

    coeff_expr_str is like "gb_a1p_b1p", "-gb_a1m_b2m",
    "gb_a1p_b1p + gb_a1m_b1m", "2*gb_a1p_b1p - gb_a1m_b1m", etc.

    Returns: Fraction
    """
    if not coeff_expr_str or coeff_expr_str.strip() == '0':
        return Fraction(0)

    # Tokenize: split by + and -, preserving signs
    # Replace "- " with "+ -" for easier parsing
    expr = coeff_expr_str.strip()
    # Normalize: "- gb..." -> "+ -1*gb..."
    expr = re.sub(r'\s*-\s*(\w)', r' + -\1', expr)
    expr = re.sub(r'^\s*\+\s*', '', expr)

    total = Fraction(0)
    # Split by " + "
    parts = re.split(r'\s*\+\s*', expr)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Part is like "gb_a1p_b1p" or "-gb_a1m_b1p" or "2*gb_a1p_b1p" or "-2*gb_a1m_b1m"
        coeff = Fraction(1)
        gb_part = part
        if '*' in part:
            coeff_str, gb_part = part.split('*', 1)
            coeff_str = coeff_str.strip()
            gb_part = gb_part.strip()
            if coeff_str.startswith('-'):
                coeff = Fraction(-int(coeff_str[1:]) if coeff_str[1:] else 1)
                coeff = Fraction(coeff_str)
            else:
                coeff = Fraction(coeff_str)
        elif gb_part.startswith('-'):
            coeff = Fraction(-1)
            gb_part = gb_part[1:].strip()

        val = gb_values.get(gb_part, Fraction(0))
        total += coeff * val

    return total


def evaluate_gamma(gamma_terms, gb_values):
    """Evaluate gamma coefficients at given gb_values.

    Returns: list of {X, Y, Z, coeff} with concrete Fraction coefficients.
    """
    result = {}
    for term in gamma_terms:
        X, Y, Z = term['X'], term['Y'], term['Z']
        val = evaluate_coeff_expr(term['coeff_expr'], gb_values)
        if val != 0:
            key = (X, Y, Z)
            result[key] = result.get(key, Fraction(0)) + val

    return [{'X': X, 'Y': Y, 'Z': Z, 'coeff': str(val)}
            for (X, Y, Z), val in result.items() if val != 0]


def build_schema3_json(n, gb_values):
    """Build Schema 3 JSON for C(n+1) with bosonic rank n."""
    path2 = os.path.join(DATA_DIR, f'C_{n}_gamma.json')
    with open(path2) as f:
        schema2 = json.load(f)

    gamma_terms = schema2['inhomogeneous_deformation']['gamma_coefficients']
    gb_params = schema2['inhomogeneous_deformation']['gb_matrix']['parameters']

    # Evaluate gamma at gb_values
    evaluated_gamma = evaluate_gamma(gamma_terms, gb_values)

    # Build gb assignment record
    gb_assignment = {p: str(gb_values.get(p, Fraction(0))) for p in gb_params}

    schema3 = dict(schema2)
    schema3['evaluation'] = {
        'description': 'Schema 3: gamma structure evaluated at specific gb values',
        'gb_assignment': gb_assignment,
        'evaluated_gamma': evaluated_gamma,
        'note': 'evaluated_gamma gives [X,Y]_gamma - [X,Y]_0 = kappa * sum_Z coeff*Z',
    }
    schema3['metadata'] = {
        'generated_by': 'src/C_evaluate.py',
        'generation_date': str(date.today()),
        'references': [
            'docs/math/C_inhomogeneous_definition.md',
            f'data/C_{n}_gamma.json',
        ],
    }
    return schema3


def main():
    for n in [1, 2, 3]:
        print(f'Evaluating C({n+1}) structure (n={n}) with all gb=1...')

        # Build gb_values: all gb parameters = 1
        gb_params = []
        for j in range(1, n+1):
            for sigma in ['a1p', 'a1m']:
                for s in ['p', 'm']:
                    gb_params.append(f'gb_{sigma}_b{j}{s}')

        gb_values = {p: Fraction(1) for p in gb_params}
        schema3 = build_schema3_json(n, gb_values)
        ev = schema3['evaluation']
        print(f'  Evaluated gamma terms: {len(ev["evaluated_gamma"])}')

        fname = os.path.join(DATA_DIR, f'C_{n}_evaluated.json')
        with open(fname, 'w') as f:
            json.dump(schema3, f, indent=2)
        print(f'  Written: {fname}')


if __name__ == '__main__':
    main()
