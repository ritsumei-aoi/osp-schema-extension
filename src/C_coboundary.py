#!/usr/bin/env python3
"""
Schema 4: Coboundary structure for C(n+1) = osp(2|2n).

Computes the coboundary delta_f of an odd linear map f: g -> g.

The coboundary formula:
  (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])

where [.,.] is the standard Lie superalgebra bracket (from Schema 1).

The map f is parameterized by:
  f(Z_j) = sum_i phi_{ij} * Z_i
where {Z_i} is the basis of g and phi_{ij} are the phi parameters.

Parity constraint on f: f is odd, so f maps Z_j to generators of opposite parity.
That is, phi_{ij} != 0 only if p(Z_i) != p(Z_j).

We use a canonical choice of f: f(E_odd_k) = phi_k * H_1 (f maps each odd
generator to H_1 with a phi parameter), and f(H_j) = 0, f(E_even) = 0.
This is a simple but general representative for studying the coboundary structure.

For comparison with the gamma structure (deformation), we compute (delta f)(X,Y)
for the same pairs and see when it matches gamma(X,Y).
"""

from fractions import Fraction
from collections import defaultdict
import json
import os
import sys
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC_DIR)


def load_structure_constants(n):
    """Load structure constants as a map {(X,Y): {Z: coeff}} from Schema 1."""
    path = os.path.join(DATA_DIR, f'C_{n}_structure.json')
    with open(path) as f:
        data = json.load(f)

    parity = data['parity']
    basis = data['basis']['even'] + data['basis']['odd']
    bracket = {}
    for X in basis:
        for Y in basis:
            bracket[(X, Y)] = {}

    for sc in data['structure_constants']:
        X, Y, Z = sc['X'], sc['Y'], sc['Z']
        c = Fraction(sc['coeff'])
        if (X, Y) not in bracket:
            bracket[(X, Y)] = {}
        bracket[(X, Y)][Z] = bracket[(X, Y)].get(Z, Fraction(0)) + c

    return bracket, parity, basis, data


def apply_bracket(bracket, X, Y):
    """Return {Z: coeff} for [X,Y}."""
    return {k: v for k, v in bracket.get((X, Y), {}).items() if v != 0}


def compute_coboundary(n, phi_map, bracket, parity, basis):
    """Compute (delta f)(X, Y) for all pairs.

    phi_map: dict {Z_j_label: {Z_i_label: phi_coeff}} defining f(Z_j) = sum_i phi_coeff * Z_i.

    Returns: list of {X, Y, Z, coeff} for non-zero (delta f)(X,Y) coefficients.
    """
    def apply_f(label):
        """Compute f(label) as dict {Z: coeff}."""
        return phi_map.get(label, {})

    def bracket_with_f(X, fY_dict):
        """Compute [X, sum coeff*Z] = sum coeff * [X,Z]."""
        result = defaultdict(Fraction)
        for z, cz in fY_dict.items():
            for w, cw in apply_bracket(bracket, X, z).items():
                result[w] += cz * cw
        return {k: v for k, v in result.items() if v != 0}

    coboundary_terms = []

    for X in basis:
        for Y in basis:
            pX = parity[X]
            pY = parity[Y]

            # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X,Y])
            s1 = (-1) ** pX
            s2 = (-1) ** ((pX + 1) * pY)

            fY = apply_f(Y)
            fX = apply_f(X)
            XY = apply_bracket(bracket, X, Y)

            # f([X,Y])
            fXY = defaultdict(Fraction)
            for z, cz in XY.items():
                for w, cw in apply_f(z).items():
                    fXY[w] += cz * cw

            # [X, f(Y)]
            XfY = bracket_with_f(X, fY)
            # [Y, f(X)]
            YfX = bracket_with_f(Y, fX)

            combined = defaultdict(Fraction)
            for z, c in XfY.items():
                combined[z] += Fraction(s1) * c
            for z, c in YfX.items():
                combined[z] -= Fraction(s2) * c
            for z, c in fXY.items():
                combined[z] -= c

            for Z, coeff in combined.items():
                if coeff != 0:
                    coboundary_terms.append({'X': X, 'Y': Y, 'Z': Z, 'coeff': str(coeff)})

    return coboundary_terms


def build_canonical_phi_map(basis, parity, n):
    """Build a canonical odd linear map f.

    Choice: f(E_odd) = phi_k * H_1 for each odd generator E_odd_k.
    f(E_even) = 0.

    Using phi_k = 1 for all k (representative choice).

    This map is odd: maps odd generators to even generators. ✓
    """
    phi_map = {}
    phi_record = {}

    for label in basis:
        if parity[label] == 1:
            # Odd generator: f(odd) -> H_1 with coeff 1
            phi_map[label] = {'H_1': Fraction(1)}
            phi_record[f'phi_{label}_H_1'] = '1'

    return phi_map, phi_record


def build_schema4_json(n, coboundary_terms, phi_record):
    """Build Schema 4 JSON for C(n+1) with bosonic rank n."""
    path1 = os.path.join(DATA_DIR, f'C_{n}_structure.json')
    with open(path1) as f:
        schema1 = json.load(f)

    schema4 = dict(schema1)
    schema4['coboundary'] = {
        'description': 'Schema 4: coboundary delta_f of the canonical odd linear map f',
        'f_map': {
            'description': 'Odd linear map f: g -> g, f(odd) = 1*H_1, f(even) = 0',
            'phi_parameters': phi_record,
        },
        'coboundary_formula': '(delta f)(X,Y) = (-1)^{pX}[X,f(Y)] - (-1)^{(pX+1)*pY}[Y,f(X)] - f([X,Y])',
        'delta_f_coefficients': coboundary_terms,
    }
    schema4['metadata'] = {
        'generated_by': 'src/C_coboundary.py',
        'generation_date': str(date.today()),
        'references': [
            'docs/math/C_coboundary_definition.md',
            f'data/C_{n}_structure.json',
        ],
    }
    return schema4


def main():
    for n in [1, 2, 3]:
        print(f'Computing coboundary structure for C({n+1}) (n={n})...')
        bracket, parity, basis, data = load_structure_constants(n)
        phi_map, phi_record = build_canonical_phi_map(basis, parity, n)
        coboundary_terms = compute_coboundary(n, phi_map, bracket, parity, basis)
        print(f'  Coboundary terms: {len(coboundary_terms)}')

        schema4 = build_schema4_json(n, coboundary_terms, phi_record)
        fname = os.path.join(DATA_DIR, f'C_{n}_coboundary.json')
        with open(fname, 'w') as f:
            json.dump(schema4, f, indent=2)
        print(f'  Written: {fname}')


if __name__ == '__main__':
    main()
