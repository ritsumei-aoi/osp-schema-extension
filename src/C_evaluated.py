#!/usr/bin/env python3
"""
C_evaluated.py: Generate evaluated structure constants (Schema 3) for C(n+1).

Substitutes concrete values for gb parameters into the symbolic gamma structure
from Schema 2, producing numerical deformed structure constants.

Representative assignment: all gb = +1 (all deformation parameters set to 1).
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from C_gamma import CnPlusOneGamma


def evaluate_gamma(gamma_entries, gb_assignment):
    """
    Substitute gb_assignment into the symbolic gamma structure.
    Returns list of {X, Y, Z, coeff} with rational coefficients.
    """
    evaluated = []
    # Accumulate over (X, Y, Z)
    acc = defaultdict(Fraction)
    for entry in gamma_entries:
        gx = entry['X']
        gy = entry['Y']
        gz = entry['Z']
        c = Fraction(0)
        for gb_label, coeff_str in entry['coeff_expr'].items():
            gb_val = gb_assignment.get(gb_label, Fraction(0))
            c += Fraction(coeff_str) * gb_val
        if c:
            acc[(gx, gy, gz)] += c
    for (gx, gy, gz), c in acc.items():
        if c:
            evaluated.append({'X': gx, 'Y': gy, 'Z': gz, 'coeff': str(c)})
    return evaluated


def build_schema3(n, gb_assignment_val=Fraction(1), output_dir='data'):
    """
    Build Schema 3 JSON for C(n+1) with given gb_assignment_val for all parameters.
    gb_assignment_val: Fraction value assigned to every gb parameter.
    """
    alg = CnPlusOneGamma(n)

    # Load Schema 2 (gamma)
    gamma_path = os.path.join(output_dir, f'C_{n}_gamma.json')
    with open(gamma_path) as f:
        schema2 = json.load(f)
    gamma_entries = schema2['gamma_structure']
    gb_labels = schema2['deformation_parameters']['labels']

    # Build gb assignment
    gb_assignment = {lbl: gb_assignment_val for lbl in gb_labels}
    gb_assignment_str = {lbl: str(v) for lbl, v in gb_assignment.items()}

    # Load Schema 1 structure constants
    sc1_path = os.path.join(output_dir, f'C_{n}_structure.json')
    with open(sc1_path) as f:
        schema1 = json.load(f)
    undeformed_sc = schema1['structure_constants']

    # Evaluate gamma
    gamma_evaluated = evaluate_gamma(gamma_entries, gb_assignment)

    # Build deformed structure constants:
    # [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)
    # Store undeformed and deformed separately
    doc = {
        'schema_version': '5.0',
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n+1})',
            'osp': f'osp(2|{2*n})',
        },
        'gb_assignment': gb_assignment_str,
        'undeformed_structure_constants': undeformed_sc,
        'gamma_evaluated': gamma_evaluated,
        'metadata': {
            'generated_by': 'src/C_evaluated.py',
            'generation_date': str(date.today()),
            'description': (
                'Schema 3: numerically evaluated deformation. '
                'undeformed_structure_constants: [X,Y]_0. '
                'gamma_evaluated: gamma(X,Y) evaluated at gb_assignment (kappa-coefficient of deformed bracket).'
            ),
        },
    }
    return doc


def generate_and_save(n, output_dir='data'):
    os.makedirs(output_dir, exist_ok=True)
    doc = build_schema3(n, gb_assignment_val=Fraction(1), output_dir=output_dir)
    out_path = os.path.join(output_dir, f'C_{n}_evaluated.json')
    with open(out_path, 'w') as f:
        json.dump(doc, f, indent=2)
    n_gamma = len(doc['gamma_evaluated'])
    n_sc = len(doc['undeformed_structure_constants'])
    print(f"C({n+1}) = osp(2|{2*n}): {n_sc} undeformed, "
          f"{n_gamma} gamma (all gb=1) → {out_path}")
    return doc


if __name__ == '__main__':
    for n in [1, 2, 3]:
        generate_and_save(n)
