"""I08: which gb profiles make the deformation of C(n+1) trivial?

Let gamma(gb) = sum_m gb_m G_m be the g-valued deformation (Schema 2) and D = Im(delta) the space of
coboundaries of odd maps (Schema 4).  The deformation is trivial at gb iff gamma(gb) lies in D.  Since
gamma is linear in gb, the set T = {gb : gamma(gb) in D} is a linear subspace of the 4n-dimensional gb
space.  This module computes T exactly (rational arithmetic) and its defining linear equations.

K-part.  The K-components of gamma (K = identity, central) are a separate cochain.  An odd map
f'(Z) = l(Z) K (Z odd) contributes the K-valued coboundary (X,Y) -> -l(p_odd [X,Y]) and nothing to the
g-valued part.  So the K-part is trivial at gb iff gamma_K(gb) is of that form.  Both conditions are
computed here; the doc's triviality concerns the g-valued part (T_g), the K-part is reported separately.

Usage:  python3 src/triviality_search.py
"""

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from verify_C_structure import load_structure  # noqa: E402

ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, 'data')
RANKS = (1, 2, 3)


def _clean(vec):
    return {k: v for k, v in vec.items() if v != 0}


def relations(vectors):
    """Basis of the space of linear relations sum_i a_i v_i = 0 among the given sparse vectors.

    Returns a list of dicts {i: a_i}.  Exact elimination over Q with combination tracking.
    """
    rows = []  # (pivot, vec, combo) with vec = sum combo[i] * v_i
    found = []
    for idx, v in enumerate(vectors):
        vec = dict(v)
        combo = {idx: Fraction(1)}
        for pivot, rvec, rcombo in rows:
            f = vec.get(pivot)
            if f:
                for k, c in rvec.items():
                    vec[k] = vec.get(k, 0) - f * c
                for k, c in rcombo.items():
                    combo[k] = combo.get(k, 0) - f * c
                vec = _clean(vec)
                combo = _clean(combo)
        if not vec:
            found.append(_clean(combo))
            continue
        pivot = next(iter(vec))
        factor = vec[pivot]
        rows.append((pivot, {k: c / factor for k, c in vec.items()},
                     {k: c / factor for k, c in combo.items()}))
    return found


def nullspace(matrix, ncols):
    """Exact basis of {x : M x = 0} for a matrix given as a list of rows of length ncols."""
    rows = [list(r) for r in matrix]
    pivots = []
    r = 0
    for c in range(ncols):
        pr = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if pr is None:
            continue
        rows[r], rows[pr] = rows[pr], rows[r]
        pv = rows[r][c]
        rows[r] = [x / pv for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(ncols) if c not in pivots]
    basis = []
    for fc in free:
        x = [Fraction(0)] * ncols
        x[fc] = Fraction(1)
        for row_index, pc in enumerate(pivots):
            x[pc] = -rows[row_index][fc]
        basis.append(x)
    return basis


def trivial_subspace(gb_vectors, coboundary_vectors, ngb):
    """T = {gb : sum_m gb_m gb_vectors[m] in span(coboundary_vectors)}.

    Returns (basis_of_T, constraints) where basis_of_T are vectors in Q^ngb and constraints are
    rows c with gb in T  <=>  c . gb = 0 for all rows.
    """
    vectors = list(coboundary_vectors) + list(gb_vectors)
    rels = relations(vectors)
    nd = len(coboundary_vectors)
    projected = []
    for rel in rels:
        t = [-rel.get(nd + m, Fraction(0)) for m in range(ngb)]
        if any(t):
            projected.append(t)
    # basis of T = span of projected relations (row reduce to independent set)
    basis = []
    for t in projected:
        trial = basis + [t]
        if len(_row_basis(trial)) > len(_row_basis(basis)):
            basis.append(t)
    constraints = nullspace(basis, ngb) if basis else [[Fraction(int(i == j)) for j in range(ngb)]
                                                        for i in range(ngb)]
    return basis, constraints


def certificate(columns, target):
    """Exact coefficients phi with sum_k phi_k columns[k] = target, verified by reconstruction.

    Returns a list of Fractions (one per column), or None if target is not in the span.
    """
    vectors = list(columns) + [target]
    nt = len(columns)
    for rel in relations(vectors):
        a_t = rel.get(nt, Fraction(0))
        if a_t != 0:
            phi = [-rel.get(k, Fraction(0)) / a_t for k in range(nt)]
            if _reconstruct(columns, phi) == _clean(target):
                return phi
    return None


def _reconstruct(columns, phi):
    out = {}
    for c, col in zip(phi, columns):
        if c != 0:
            for k, v in col.items():
                out[k] = out.get(k, 0) + c * v
    return _clean(out)


def _row_basis(rows):
    """Row-echelon basis (as a list of independent rows) of a list of rational vectors."""
    out = []
    pivots = []
    for r in rows:
        v = list(r)
        for row, p in zip(out, pivots):
            if v[p] != 0:
                f = v[p] / row[p]
                v = [a - f * b for a, b in zip(v, row)]
        nz = next((i for i, x in enumerate(v) if x != 0), None)
        if nz is not None:
            out.append(v)
            pivots.append(nz)
    return out


def load_inputs(n, data_dir=DATA_DIR):
    """Read the JSON layers needed for the analysis (Schemas 1, 2, 4)."""
    s1, labels, parity_map, table = load_structure(n, data_dir)
    with open(os.path.join(data_dir, 'C_%d_gamma.json' % n), encoding='utf-8') as fh:
        s2 = json.load(fh)
    with open(os.path.join(data_dir, 'C_%d_coboundary.json' % n), encoding='utf-8') as fh:
        s4 = json.load(fh)
    gb_labels = list(s2['gb_matrix']['labels'])
    g_vectors = {label: {} for label in gb_labels}
    for e in s2['inhomogeneous_deformation']['entries']:
        key = (e['X'], e['Y'], e['Z'])
        g_vectors[e['gb']][key] = g_vectors[e['gb']].get(key, 0) + Fraction(e['coeff'])
    k_vectors = {label: {} for label in gb_labels}
    for e in s2['inhomogeneous_deformation']['K_components']:
        k_vectors[e['gb']][(e['X'], e['Y'])] = Fraction(e['coeff'])
    coboundary = []
    for record in s4['maps']:
        vec = {}
        for e in record['coboundary']:
            vec[(e['X'], e['Y'], e['Z'])] = Fraction(e['coeff'])
        coboundary.append(vec)
    # K-coboundaries: f'(Z) = K for odd Z, (X,Y) -> -coefficient of Z in [X,Y]
    k_coboundary = []
    for z in labels:
        if parity_map[z] != 1:
            continue
        vec = {}
        for (x, y), img in table.items():
            if z in img:
                vec[(x, y)] = -img[z]
        k_coboundary.append(vec)
    return {
        'labels': labels, 'parity': parity_map, 'table': table,
        'gb_labels': gb_labels, 'g_vectors': g_vectors, 'k_vectors': k_vectors,
        'coboundary': coboundary, 'k_coboundary': k_coboundary,
    }


def analyse(n, data_dir=DATA_DIR):
    inp = load_inputs(n, data_dir)
    gb_labels = inp['gb_labels']
    ngb = len(gb_labels)
    gvecs = [inp['g_vectors'][label] for label in gb_labels]
    kvecs = [inp['k_vectors'][label] for label in gb_labels]
    tg_basis, tg_constraints = trivial_subspace(gvecs, inp['coboundary'], ngb)
    tk_basis, tk_constraints = trivial_subspace(kvecs, inp['k_coboundary'], ngb)
    return {
        'n': n,
        'gb_labels': gb_labels,
        'dim_gb': ngb,
        'coboundary_maps': len(inp['coboundary']),
        'dim_T_g': len(tg_basis) if tg_basis else ngb - len(tg_constraints),
        'dim_T_K': len(tk_basis) if tk_basis else ngb - len(tk_constraints),
        'constraints_g': tg_constraints,
        'constraints_K': tk_constraints,
        'inputs': inp,
    }


def _fmt(row, labels):
    terms = []
    for c, label in zip(row, labels):
        if c != 0:
            terms.append('%s*%s' % (_frac(c), label))
    return ' + '.join(terms) + ' = 0' if terms else '0 = 0'


def _frac(c):
    return str(Fraction(c))


def in_T(constraints, profile):
    """Membership: all constraint rows vanish on the profile (list of Fractions)."""
    return all(sum(c * p for c, p in zip(row, profile)) == 0 for row in constraints)


def trivialisers(n, data_dir=DATA_DIR):
    """Certificates for every unit profile gb = e_m: an odd map f^(m) with delta f^(m) = gamma_m (g-part)
    and an odd K-map l^(m) with K-coboundary = gamma_K,m.  Each is verified by exact reconstruction.
    """
    inp = load_inputs(n, data_dir)
    labels = inp['gb_labels']
    map_keys = [(rec['i'], rec['j']) for rec in json.load(
        open(os.path.join(data_dir, 'C_%d_coboundary.json' % n), encoding='utf-8'))['maps']]
    g_cert, k_cert = {}, {}
    for label in labels:
        phi = certificate(inp['coboundary'], inp['g_vectors'][label])
        if phi is None:
            g_cert[label] = None
        else:
            g_cert[label] = {'%s|%s' % key: _frac(c) for key, c in zip(map_keys, phi) if c != 0}
        kvec = inp['k_vectors'][label]
        if not kvec:
            k_cert[label] = {}
            continue
        lam = certificate(inp['k_coboundary'], kvec)
        if lam is None:
            k_cert[label] = None
        else:
            z_odd = [z for z in inp['labels'] if inp['parity'][z] == 1]
            k_cert[label] = {z: _frac(c) for z, c in zip(z_odd, lam) if c != 0}
    return g_cert, k_cert


def layer3_vs_layer4(n, g_cert, k_cert, data_dir=DATA_DIR):
    """Compare Schema 3 (evaluated gamma at gb = 1) with Schema 4 (delta of the summed certificates).

    f_1 = sum over unit profiles of the trivialisers, so delta f_1 should equal gamma(gb = 1) exactly.
    """
    inp = load_inputs(n, data_dir)
    with open(os.path.join(data_dir, 'C_%d_evaluated.json' % n), encoding='utf-8') as fh:
        s3 = json.load(fh)
    with open(os.path.join(data_dir, 'C_%d_coboundary.json' % n), encoding='utf-8') as fh:
        s4 = json.load(fh)
    # f_1 as coefficients on elementary maps 'i|j'
    f_total = {}
    for cert in g_cert.values():
        for key, c in cert.items():
            f_total[key] = f_total.get(key, Fraction(0)) + Fraction(c)
    f_total = {k: v for k, v in f_total.items() if v != 0}
    # delta f_1 from Schema 4
    delta_f1 = {}
    for rec in s4['maps']:
        key = '%s|%s' % (rec['i'], rec['j'])
        if key in f_total:
            for e in rec['coboundary']:
                k3 = (e['X'], e['Y'], e['Z'])
                delta_f1[k3] = delta_f1.get(k3, 0) + f_total[key] * Fraction(e['coeff'])
    delta_f1 = {k: v for k, v in delta_f1.items() if v != 0}
    gamma1 = {}
    for e in s3['structure_constants']:
        value = Fraction(e['coeff_kappa1'])
        if value != 0:
            gamma1[(e['X'], e['Y'], e['Z'])] = value
    mismatches = sum(1 for k in set(delta_f1) | set(gamma1) if delta_f1.get(k, 0) != gamma1.get(k, 0))
    # K-part: gamma_K = sum_z lambda_z * (-C^z_{XY})
    k_total = {}
    for cert in k_cert.values():
        for z, c in cert.items():
            k_total[z] = k_total.get(z, Fraction(0)) + Fraction(c)
    k_delta = {}
    for (x, y), img in inp['table'].items():
        for z, c in img.items():
            if z in k_total and k_total[z] != 0:
                k_delta[(x, y)] = k_delta.get((x, y), Fraction(0)) - k_total[z] * c
    k_delta = {k: v for k, v in k_delta.items() if v != 0}
    k_gamma = {}
    for e in s3['K_components']:
        value = Fraction(e['coeff_kappa1'])
        if value != 0:
            k_gamma[(e['X'], e['Y'])] = value
    k_mismatches = sum(1 for k in set(k_delta) | set(k_gamma) if k_delta.get(k, 0) != k_gamma.get(k, 0))
    return {
        'f_1_map_entries': {k: _frac(v) for k, v in sorted(f_total.items())},
        'g_entries_compared': len(set(delta_f1) | set(gamma1)),
        'g_mismatches': mismatches,
        'K_entries_compared': len(set(k_delta) | set(k_gamma)),
        'K_mismatches': k_mismatches,
    }


def main():
    summary = {}
    for n in RANKS:
        r = analyse(n)
        labels = r['gb_labels']
        print('n=%d  dim gb=%d  coboundary maps=%d  dim T_g=%d  dim T_K=%d' % (
            n, r['dim_gb'], r['coboundary_maps'], r['dim_T_g'], r['dim_T_K']))
        print('  T_g constraints:')
        for row in r['constraints_g']:
            print('    ', _fmt(row, labels))
        print('  T_K constraints:')
        for row in r['constraints_K']:
            print('    ', _fmt(row, labels))
        g_cert, k_cert = trivialisers(n)
        missing_g = [label for label, cert in g_cert.items() if cert is None]
        missing_k = [label for label, cert in k_cert.items() if cert is None]
        print('  certificates: g-part found for %d/%d unit profiles, K-part for %d/%d' % (
            len(g_cert) - len(missing_g), len(g_cert), len(k_cert) - len(missing_k), len(k_cert)))
        comparison = layer3_vs_layer4(n, g_cert, k_cert)
        print('  Layer 3 vs Layer 4 at gb=1: g mismatches=%d of %d, K mismatches=%d of %d' % (
            comparison['g_mismatches'], comparison['g_entries_compared'],
            comparison['K_mismatches'], comparison['K_entries_compared']))
        summary[n] = {
            'gb_labels': labels,
            'dim_T_g': r['dim_T_g'],
            'dim_T_K': r['dim_T_K'],
            'constraints_g': [[_frac(c) for c in row] for row in r['constraints_g']],
            'constraints_K': [[_frac(c) for c in row] for row in r['constraints_K']],
            'unit_profile_certificates_g': g_cert,
            'unit_profile_certificates_K': k_cert,
            'layer3_vs_layer4_gb_one': comparison,
        }
    with open(os.path.join(DATA_DIR, 'C_triviality.json'), 'w', encoding='utf-8') as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
        fh.write('\n')


if __name__ == '__main__':
    main()
