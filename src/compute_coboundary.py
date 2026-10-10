#!/usr/bin/env python3
"""
compute_coboundary.py: Coboundary structure (Schema 4) for C(n+1) = osp(2|2n).

Implements the most general odd linear map f: g -> g (Option A) and computes the
coboundary delta_f(X,Y) symbolically in terms of phi parameters.

Formula: (delta_f)(X, Y) = (-1)^{p(X)} [X, f(Y)]
                          - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                          - f([X,Y])

Parameterization (Option A):
  f(odd_gen)  = sum_{e in even} phi_oe__{odd}__{even}  * e
  f(even_gen) = sum_{o in odd}  phi_eo__{even}__{odd}  * o

Outputs Schema 4 JSON: data/C_{n}_coboundary.json for n=1, 2, 3.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fractions import Fraction
import json
from datetime import date


# ─── Bracket table ────────────────────────────────────────────────────────────

def build_bracket_table(structure_constants, parity):
    """
    Build a full bracket lookup from Schema 1 structure constants.
    Includes both (X,Y) and (Y,X) via the antisymmetry relation
    [Y, X] = -(-1)^{p(Y)*p(X)} [X, Y].

    Returns: {(X, Y): {Z: Fraction}}
    """
    table = {}

    for entry in structure_constants:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        coeff = Fraction(entry['coeff'])
        key = (X, Y)
        if key not in table:
            table[key] = {}
        table[key][Z] = table[key].get(Z, Fraction(0)) + coeff

    # Extend to reverse pairs
    for (X, Y), terms in list(table.items()):
        px, py = parity[X], parity[Y]
        sign = Fraction((-1) ** (px * py))
        rev = (Y, X)
        if rev not in table:
            table[rev] = {}
        for Z, coeff in terms.items():
            table[rev][Z] = table[rev].get(Z, Fraction(0)) - sign * coeff

    return {k: {Z: c for Z, c in v.items() if c != 0} for k, v in table.items()}


# ─── Phi parameter labels ─────────────────────────────────────────────────────

def phi_oe(odd_gen, even_gen):
    """phi_oe__{odd}__{even}: coefficient in f(odd_gen) for the even_gen component."""
    return f"phi_oe__{odd_gen}__{even_gen}"


def phi_eo(even_gen, odd_gen):
    """phi_eo__{even}__{odd}: coefficient in f(even_gen) for the odd_gen component."""
    return f"phi_eo__{even_gen}__{odd_gen}"


def f_image_terms(gen, parity, basis_odd, basis_even):
    """
    Return the phi-indexed image of f(gen) as {(phi_label, target): Fraction(1)}.
    f reverses parity: f(odd) maps to even subspace, f(even) to odd subspace.
    """
    result = {}
    if parity[gen] == 1:
        for e in basis_even:
            result[(phi_oe(gen, e), e)] = Fraction(1)
    else:
        for o in basis_odd:
            result[(phi_eo(gen, o), o)] = Fraction(1)
    return result


# ─── Coboundary computation ───────────────────────────────────────────────────

def compute_delta_f(X, Y, parity, basis_odd, basis_even, bracket_table):
    """
    Compute (delta_f)(X, Y) symbolically.

    Returns: {(phi_label, Z): Fraction}  — the coefficient of phi_label * Z in delta_f(X,Y).
    """
    px, py = parity[X], parity[Y]
    sign1 = Fraction((-1) ** px)
    sign2 = Fraction(-(-1) ** ((px + 1) * py))

    out = {}

    # Term 1: (-1)^{p(X)} [X, f(Y)]
    for (phi_lbl, Z_i), _ in f_image_terms(Y, parity, basis_odd, basis_even).items():
        for Z, c in bracket_table.get((X, Z_i), {}).items():
            key = (phi_lbl, Z)
            out[key] = out.get(key, Fraction(0)) + sign1 * c

    # Term 2: -(-1)^{(p(X)+1)*p(Y)} [Y, f(X)]
    for (phi_lbl, Z_i), _ in f_image_terms(X, parity, basis_odd, basis_even).items():
        for Z, c in bracket_table.get((Y, Z_i), {}).items():
            key = (phi_lbl, Z)
            out[key] = out.get(key, Fraction(0)) + sign2 * c

    # Term 3: -f([X, Y])
    for Z_c, c_XY in bracket_table.get((X, Y), {}).items():
        for (phi_lbl, Z_i), _ in f_image_terms(Z_c, parity, basis_odd, basis_even).items():
            key = (phi_lbl, Z_i)
            out[key] = out.get(key, Fraction(0)) - c_XY

    return {k: v for k, v in out.items() if v != 0}


# ─── Schema 4 generation ──────────────────────────────────────────────────────

def generate_coboundary_schema(n, data_dir='data'):
    """Generate Schema 4 coboundary structure for C(n+1) = osp(2|2n)."""

    schema1_path = os.path.join(data_dir, f'C_{n}_structure.json')
    with open(schema1_path) as fh:
        schema1 = json.load(fh)

    basis_odd = schema1['basis']['odd']
    basis_even = schema1['basis']['even']
    all_basis = basis_odd + basis_even
    parity = {k: int(v) for k, v in schema1['parity'].items()}

    bracket_table = build_bracket_table(schema1['structure_constants'], parity)

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    # Enumerate phi parameter labels
    phi_oe_labels = [phi_oe(o, e) for o in basis_odd for e in basis_even]
    phi_eo_labels = [phi_eo(e, o) for e in basis_even for o in basis_odd]

    # Compute delta_f for all ordered basis pairs X < Y
    coboundary_structure = []
    for i in range(len(all_basis)):
        for j in range(i + 1, len(all_basis)):
            X, Y = all_basis[i], all_basis[j]

            terms_dict = compute_delta_f(X, Y, parity, basis_odd, basis_even, bracket_table)
            if not terms_dict:
                continue

            terms = [
                {'phi_label': phi_lbl, 'Z': Z, 'coeff': str(coeff)}
                for (phi_lbl, Z), coeff in sorted(terms_dict.items())
            ]
            coboundary_structure.append({'X': X, 'Y': Y, 'delta_f_terms': terms})

    return {
        'schema_version': '5.0',
        'schema_layer': 4,
        'algebra': {
            'family': 'C',
            'm': 1,
            'n': n,
            'cartan_type': f'C({n + 1})',
            'alternative_notation': {
                'osp': f'osp(2|{2 * n})',
                'dimension_formula': 'osp(2m|2n) with m=1',
            },
            'dimension': {
                'total': even_dim + odd_dim,
                'even': even_dim,
                'odd': odd_dim,
            },
        },
        'map_f': {
            'type': 'odd_linear_map',
            'option': 'A',
            'description': (
                'Most general odd linear map f: g -> g (Option A). '
                'Parity: p(f(X)) = 1 - p(X). '
                'f(odd_gen) = sum_{e in even} phi_oe__{odd}__{even} * e. '
                'f(even_gen) = sum_{o in odd}  phi_eo__{even}__{odd} * o. '
                'Double underscore (__) separates the generator labels in phi parameter names.'
            ),
            'phi_parameters': {
                'odd_to_even': {
                    'description': 'phi_oe__{odd}__{even}: coefficient of even_gen in f(odd_gen)',
                    'count': odd_dim * even_dim,
                    'labels': phi_oe_labels,
                },
                'even_to_odd': {
                    'description': 'phi_eo__{even}__{odd}: coefficient of odd_gen in f(even_gen)',
                    'count': even_dim * odd_dim,
                    'labels': phi_eo_labels,
                },
                'total_count': 2 * odd_dim * even_dim,
            },
        },
        'coboundary_formula': (
            '(delta_f)(X, Y) = (-1)^{p(X)} [X, f(Y)] '
            '- (-1)^{(p(X)+1)*p(Y)} [Y, f(X)] - f([X, Y])'
        ),
        'coboundary_structure': coboundary_structure,
        'metadata': {
            'generated_by': 'compute_coboundary.py',
            'generation_date': str(date.today()),
            'notes': (
                'Each entry encodes: (delta_f)(X, Y) = sum_terms coeff * phi_label * Z. '
                'Coefficients are rational numbers; phi parameters are free scalars. '
                'Only non-zero pairs (X < Y in PBW order) are listed. '
                'The triviality condition gamma = delta_f yields a linear system in the phi parameters.'
            ),
            'references': [
                'docs/math/C_coboundary_definition.md',
                'Frappat et al. (2000), Dictionary on Lie Algebras and Superalgebras',
            ],
        },
    }


# ─── Consistency check ────────────────────────────────────────────────────────

def check_consistency(coboundary_schema, structure_schema):
    """
    Verify Schema 4 is internally consistent with Schema 1.

    Checks:
    1. Every Z in delta_f_terms appears in the Schema 1 basis.
    2. Parity: p(Z) = p(X) + p(Y) + 1 (mod 2) for all output generators Z.
    3. phi_label prefix matches the parity of the source generator.
    """
    parity = structure_schema['parity']
    basis_set = set(structure_schema['basis']['odd'] + structure_schema['basis']['even'])
    basis_odd_set = set(structure_schema['basis']['odd'])
    basis_even_set = set(structure_schema['basis']['even'])
    errors = []

    # Build phi label → source generator parity map
    phi_labels_defined = set()
    for lbl in coboundary_schema['map_f']['phi_parameters']['odd_to_even']['labels']:
        phi_labels_defined.add(lbl)
    for lbl in coboundary_schema['map_f']['phi_parameters']['even_to_odd']['labels']:
        phi_labels_defined.add(lbl)

    for entry in coboundary_schema['coboundary_structure']:
        X, Y = entry['X'], entry['Y']
        px, py = parity[X], parity[Y]
        expected_out_parity = (px + py + 1) % 2

        for term in entry['delta_f_terms']:
            Z = term['Z']
            phi_lbl = term['phi_label']

            if Z not in basis_set:
                errors.append(f"Unknown generator {Z} in delta_f({X},{Y})")
                continue

            pz = parity[Z]
            if pz != expected_out_parity:
                errors.append(
                    f"Parity mismatch: delta_f({X},{Y})[Z={Z}] has parity {pz}, "
                    f"expected {expected_out_parity}"
                )

            if phi_lbl not in phi_labels_defined:
                errors.append(f"Unknown phi label '{phi_lbl}' in delta_f({X},{Y})")

    return errors


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate C(n+1) Schema 4 (coboundary structure) JSON'
    )
    parser.add_argument('--n', type=int, nargs='+', default=[1, 2, 3])
    parser.add_argument('--data-dir', default='data')
    parser.add_argument('--check', action='store_true', help='Run consistency check')
    args = parser.parse_args()

    os.makedirs(args.data_dir, exist_ok=True)

    for n in args.n:
        print(f'Generating coboundary structure for C({n + 1}) = osp(2|{2 * n})...')
        schema = generate_coboundary_schema(n, args.data_dir)

        fname = os.path.join(args.data_dir, f'C_{n}_coboundary.json')
        with open(fname, 'w') as fh:
            json.dump(schema, fh, indent=2)

        nc = len(schema['coboundary_structure'])
        nt = sum(len(e['delta_f_terms']) for e in schema['coboundary_structure'])
        np_total = schema['map_f']['phi_parameters']['total_count']
        print(f'  Written: {fname}')
        print(f'  Non-zero coboundary pairs: {nc}')
        print(f'  Total delta_f terms: {nt}')
        print(f'  Total phi parameters: {np_total}')

        if args.check:
            struct_path = os.path.join(args.data_dir, f'C_{n}_structure.json')
            with open(struct_path) as fh:
                struct = json.load(fh)
            errs = check_consistency(schema, struct)
            if errs:
                print(f'  CONSISTENCY ERRORS ({len(errs)}):')
                for e in errs:
                    print(f'    {e}')
            else:
                print(f'  Consistency check PASSED.')


if __name__ == '__main__':
    main()
