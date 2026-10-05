"""
C(n+1) = osp(2|2n) coboundary structure (Schema 4).

Computes the coboundary (delta f)(X, Y) for an odd linear map f: g -> g.
The coboundary is:
  (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])

The map f is parameterized by phi_{source, target} where:
  f(target) = sum_{source} phi_{source, target} * source
with p(source) != p(target) (f is odd).
"""

import json
import sys
from fractions import Fraction
from datetime import date


def load_structure_constants(filepath):
    """Load structure constants into a dict: (X, Y) -> {Z: coeff}."""
    with open(filepath) as f:
        data = json.load(f)
    sc = {}
    for entry in data['structure_constants']:
        key = (entry['X'], entry['Y'])
        if key not in sc:
            sc[key] = {}
        sc[key][entry['Z']] = Fraction(entry['coeff'])
    return data, sc


def get_bracket(sc, parity, x, y):
    """Get [X, Y} using stored structure constants + antisymmetry."""
    if (x, y) in sc:
        return dict(sc[(x, y)])
    elif (y, x) in sc:
        sign = Fraction(-1) ** (1 + parity[x] * parity[y])
        return {z: sign * c for z, c in sc[(y, x)].items()}
    return {}


def compute_coboundary(data, sc):
    """
    Compute the coboundary matrix for the odd linear map f.

    Returns list of entries:
    {X, Y, Z, phi_source, phi_target, coeff}

    meaning (delta f)(X, Y)^Z has coefficient 'coeff' multiplying phi_{source, target}.
    """
    basis = data['basis']['odd'] + data['basis']['even']
    parity = {k: v for k, v in data['parity'].items()}
    entries = []

    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            if i >= j:
                continue
            px, py = parity[x], parity[y]

            result_terms = {}

            for k in basis:
                pk = parity[k]
                if pk == py:
                    continue
                bracket_xk = get_bracket(sc, parity, x, k)
                for z, c_xkz in bracket_xk.items():
                    sign1 = Fraction(-1) ** px
                    key = (z, k, y)
                    val = sign1 * c_xkz
                    result_terms[key] = result_terms.get(key, Fraction(0)) + val

            for k in basis:
                pk = parity[k]
                if pk == px:
                    continue
                bracket_yk = get_bracket(sc, parity, y, k)
                for z, c_ykz in bracket_yk.items():
                    sign2 = Fraction(-1) ** ((px + 1) * py)
                    key = (z, k, x)
                    val = -sign2 * c_ykz
                    result_terms[key] = result_terms.get(key, Fraction(0)) + val

            bracket_xy = get_bracket(sc, parity, x, y)
            for w, c_xyw in bracket_xy.items():
                pw = parity[w]
                for z in basis:
                    pz = parity[z]
                    if pz == pw:
                        continue
                    key = (z, z, w)
                    val = -c_xyw
                    result_terms[key] = result_terms.get(key, Fraction(0)) + val

            for (z, source, target), coeff in result_terms.items():
                if coeff != Fraction(0):
                    entries.append({
                        'X': x,
                        'Y': y,
                        'Z': z,
                        'phi_source': source,
                        'phi_target': target,
                        'coeff': str(coeff)
                    })

    return entries


def generate_schema4(n):
    print(f"Computing coboundary for C({n+1}) = osp(2|{2*n}) (n={n})...")
    filepath = f'data/C_{n}_structure.json'
    data, sc = load_structure_constants(filepath)

    cob_entries = compute_coboundary(data, sc)

    even_dim = 2 * n * n + n + 1
    odd_dim = 4 * n

    phi_params = []
    basis = data['basis']['odd'] + data['basis']['even']
    parity = data['parity']
    for target in basis:
        for source in basis:
            if parity[source] != parity[target]:
                phi_params.append({
                    'label': f'phi_{source}_{target}',
                    'source': source,
                    'target': target,
                    'source_parity': parity[source],
                    'target_parity': parity[target]
                })

    schema = {
        'schema_version': '5.0',
        'layer': 4,
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
        'phi_parameters': {
            'description': 'Parameters of the odd linear map f: g -> g',
            'total_count': len(phi_params),
            'even_to_odd': even_dim * odd_dim,
            'odd_to_even': odd_dim * even_dim,
        },
        'coboundary_coefficients': cob_entries,
        'basis': data['basis'],
        'parity': data['parity'],
        'metadata': {
            'generated_by': 'C_coboundary.py',
            'generation_date': str(date.today()),
            'description': f'Coboundary structure for C({n+1})',
            'references': [
                'Frappat et al. (2000)',
                'Bakalov and Sullivan (2017)'
            ]
        }
    }
    return schema


def main():
    for n in [1, 2, 3]:
        schema = generate_schema4(n)
        filename = f'data/C_{n}_coboundary.json'
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"  {filename}: {len(schema['coboundary_coefficients'])} coboundary entries, "
              f"{schema['phi_parameters']['total_count']} phi params")


if __name__ == '__main__':
    main()
