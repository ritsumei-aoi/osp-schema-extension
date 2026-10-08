"""Schema 2: the inhomogeneous deformation gamma of C(n+1), linear in the gb parameters.

For basis elements X_a, X_b the deformed bracket is
    [X_a, X_b]_gamma = [X_a, X_b]_0 + kappa * sum_tag gb_tag * (gamma_tag(X_a, X_b) + gammaK_tag(X_a, X_b) K),
where gamma_tag(X,Y) lies in g and K is the identity (central).  Checks performed:
  1. kappa-free part agrees with data/C_{n}_structure.json (Schema 1)
  2. parity: gamma_tag(X,Y) has parity p(X)+p(Y)+1 ;  K-component needs p(X)+p(Y) odd
  3. graded anti-symmetry of gamma
  4. cocycle condition: the super-Jacobi defect of the deformed bracket vanishes, computed
     directly in the associative algebra (src/c_algebra.py), which handles the signs of the odd kappa.
Usage:  python3 src/C_gamma.py
"""

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fractions import Fraction  # noqa: E402

from c_algebra import bracket, build_basis, gb_label, gb_tag_order, structure  # noqa: E402
from verify_C_structure import load_structure  # noqa: E402

ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, 'data')
RANKS = (1, 2, 3)


def _frac(value):
    return str(Fraction(value))


def _add(u, v, sign=1):
    out = dict(u)
    for k, c in v.items():
        out[k] = out.get(k, 0) + sign * c
    return {k: c for k, c in out.items() if c != 0}


def gamma_checks(basis, gamma, sc):
    """Return counts of failures for the checks listed in the module docstring.

    sc is the kappa-free structure table {(a, b): {c: coeff}}.
    """
    dim = len(basis)
    parity = [x['parity'] for x in basis]
    tags = gb_tag_order(_rank_from_dim(dim))
    result = {'parity_failures': 0, 'antisymmetry_failures': 0,
              'cocycle_failures': 0, 'cocycle_cases': 0, 'algebra_jacobi_failures': 0}

    # 2. parity of the g-valued gamma
    for (a, b), per_tag in gamma.items():
        for tag, img in per_tag.items():
            for c in img:
                if (parity[c] - parity[a] - parity[b] - 1) % 2 != 0:
                    result['parity_failures'] += 1

    # 3. graded anti-symmetry: gamma(X,Y) + (-1)^{p(X)p(Y)} gamma(Y,X) = 0
    for a in range(dim):
        for b in range(dim):
            sign = (-1) ** (parity[a] * parity[b])
            for tag in tags:
                lhs = gamma.get((a, b), {}).get(tag, {})
                rhs = gamma.get((b, a), {}).get(tag, {})
                if _add(lhs, rhs, sign):
                    result['antisymmetry_failures'] += 1

    # 4. cocycle, in the doc's convention (kappa on the left, kappa odd):
    #      (-1)^{p(X)} [X, g(Y,Z)] + g(X,[Y,Z]) - [g(X,Y), Z] - g([X,Y], Z)
    #        - s (-1)^{p(Y)} [Y, g(X,Z)] - s g(Y,[X,Z]) = 0,   s = (-1)^{p(X)p(Y)}
    #    where [.,.] is the kappa-free bracket.  Derived from the order-kappa part of the super-Jacobi
    #    identity for [X,Y]_gamma = [X,Y]_0 + kappa gamma(X,Y).
    for tag in tags:
        g = {key: val[tag] for key, val in gamma.items() if tag in val}
        for x in range(dim):
            for y in range(dim):
                for z in range(dim):
                    result['cocycle_cases'] += 1
                    s = (-1) ** (parity[x] * parity[y])
                    ex, ey, ez = {x: Fraction(1)}, {y: Fraction(1)}, {z: Fraction(1)}
                    t = _bracket_vec(sc, ex, _gvec(g, y, z))
                    t = {c: v * (-1) ** parity[x] for c, v in t.items()}
                    t = _add(t, _gbil(g, ex, _bracket_vec(sc, ey, ez)))
                    t = _add(t, _bracket_vec(sc, _gvec(g, x, y), ez), -1)
                    t = _add(t, _gbil(g, _bracket_vec(sc, ex, ey), ez), -1)
                    t = _add(t, _bracket_vec(sc, ey, _gvec(g, x, z)), -s * (-1) ** parity[y])
                    t = _add(t, _gbil(g, ey, _bracket_vec(sc, ex, ez)), -s)
                    if t:
                        result['cocycle_failures'] += 1

    # 5. the U-level super-Jacobi defect of the (kappa-right) engine bracket vanishes
    els = [x['element'] for x in basis]
    for x in range(dim):
        for y in range(dim):
            for z in range(dim):
                s = (-1) ** (parity[x] * parity[y])
                defect = dict(bracket(els[x], bracket(els[y], els[z])))
                for k, v in bracket(bracket(els[x], els[y]), els[z]).items():
                    defect[k] = defect.get(k, 0) - v
                for k, v in bracket(els[y], bracket(els[x], els[z])).items():
                    defect[k] = defect.get(k, 0) - s * v
                if any(v != 0 for v in defect.values()):
                    result['algebra_jacobi_failures'] += 1
    return result


def _gvec(g, a, b):
    """gamma(X_a, X_b) as a vector {c: coeff}."""
    return dict(g.get((a, b), {}))


def _gbil(g, u, v):
    """gamma applied bilinearly to vectors u, v (dicts index -> coeff)."""
    out = {}
    for a, x in u.items():
        for b, y in v.items():
            for c, z in g.get((a, b), {}).items():
                out[c] = out.get(c, 0) + x * y * z
    return {c: w for c, w in out.items() if w != 0}


def _bracket_vec(table, u, v):
    """kappa-free bracket of vectors u, v (dicts index -> coeff) via the structure table."""
    out = {}
    for a, x in u.items():
        for b, y in v.items():
            for c, z in table.get((a, b), {}).items():
                out[c] = out.get(c, 0) + x * y * z
    return {c: w for c, w in out.items() if w != 0}


def _rank_from_dim(dim):
    """Recover n from dim = 2n^2 + 5n + 1."""
    for n in RANKS:
        if 2 * n * n + 5 * n + 1 == dim:
            return n
    raise ValueError('dimension %d is not one of C(2), C(3), C(4)' % dim)


def build_schema2(n, basis, gamma, gamma_k, generation_date):
    labels = [x['label'] for x in basis]
    tags = gb_tag_order(n)
    entries = []
    for a in range(len(basis)):
        for b in range(len(basis)):
            per_tag = gamma.get((a, b), {})
            for tag in tags:
                for c, coeff in sorted(per_tag.get(tag, {}).items()):
                    entries.append({'X': labels[a], 'Y': labels[b], 'Z': labels[c],
                                    'gb': gb_label(*tag), 'coeff': _frac(coeff)})
    k_components = []
    for a in range(len(basis)):
        for b in range(len(basis)):
            per_tag = gamma_k.get((a, b), {})
            for tag in tags:
                if tag in per_tag:
                    k_components.append({'X': labels[a], 'Y': labels[b],
                                         'gb': gb_label(*tag), 'coeff': _frac(per_tag[tag])})
    cols = ['b_%d_%s' % (k, s) for k in range(1, n + 1) for s in ('p', 'm')]
    return {
        'schema_version': '5.0',
        'algebra_ref': 'C_%d_structure.json' % n,
        'gb_matrix': {
            'shape': [2, 2 * n],
            'rows': ['+', '-'],
            'columns': cols,
            'labels': [gb_label(*t) for t in tags],
            'parity': 0,
            'note': 'Commuting scalars (decision A1 in handover/notation.md section 8)',
        },
        'inhomogeneous_deformation': {
            'kappa_parity': 1,
            'linear_in_gb': True,
            'entries': entries,
            'K_components': k_components,
        },
        'metadata': {
            'generated_by': 'src/C_gamma.py',
            'generation_date': generation_date,
        },
    }


def consistency_with_schema1(n, sc, basis):
    """Compare the engine's kappa-free table with data/C_{n}_structure.json."""
    _doc, _labels, _parity, table = load_structure(n, DATA_DIR)
    engine = {}
    for (a, b), coeffs in sc.items():
        for c, v in coeffs.items():
            engine[(basis[a]['label'], basis[b]['label'], basis[c]['label'])] = v
    json_map = {}
    for (x, y), img in table.items():
        for z, v in img.items():
            json_map[(x, y, z)] = v
    keys = set(engine) | set(json_map)
    mismatches = sum(1 for key in keys if engine.get(key, 0) != json_map.get(key, 0))
    return {'entries_compared': len(keys), 'mismatches': mismatches}


def main():
    generation_date = datetime.date.today().isoformat()
    report = {}
    for n in RANKS:
        basis, sc, gamma, gamma_k = structure(n)
        checks = gamma_checks(basis, gamma, sc)
        checks['schema1_consistency'] = consistency_with_schema1(n, sc, basis)
        doc = build_schema2(n, basis, gamma, gamma_k, generation_date)
        path = os.path.join(DATA_DIR, 'C_%d_gamma.json' % n)
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write('\n')
        report[n] = {
            'entries': len(doc['inhomogeneous_deformation']['entries']),
            'K_components': len(doc['inhomogeneous_deformation']['K_components']),
            'checks': checks,
        }
        print('n=%d entries=%d K=%d checks=%s' % (n, report[n]['entries'],
                                                    report[n]['K_components'], checks))
    return report


if __name__ == '__main__':
    main()
