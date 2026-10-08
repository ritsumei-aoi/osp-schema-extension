"""Triviality analysis for the inhomogeneous deformation of C(n+1) (I08).

Question: for which gb is γ(gb) = δf for some odd linear map f?

Setup (exact rational arithmetic, data read from the JSON layers only):
    Layer 2  data/C_{n}_gamma.json       γ(gb) = Σ_p gb_p Γ_p   (Z in g or Z = K)
    Layer 4  data/C_{n}_coboundary.json  δf_m for elementary odd maps m (Z in g)

Two readings are analysed:
  * strict: f : g -> g, the reading of docs/math/C_coboundary_definition.md.
  * extended: f may also send an odd element to the central element K
    (K is even, so this is parity-reversing). Reported as an extra investigation.

Triviality is the linear system  Δ φ - Γ(gb) = 0  in the unknowns (φ, gb).
Eliminating the φ columns first leaves only gb-only rows, which are exactly the
conditions on gb. The trivial locus is their common kernel.

Usage:
    python src/C_triviality.py    # prints the analysis and writes data/C_triviality_summary.json
"""

import json
from fractions import Fraction
from pathlib import Path

from verify_C_structure import build_table, load
from C_coboundary import coboundary_full, elementary_maps

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'


def _read(n, layer):
    with open(DATA_DIR / f'C_{n}_{layer}.json', encoding='utf-8') as f:
        return json.load(f)


def extended_maps(labels, parity, table):
    """Elementary odd maps Z_j -> K for odd Z_j, as extra coboundary entries.

    Returns (labels_ext, parity_ext, table_ext, map_entries) where map_entries is a
    list of {(X,Y,Z): Fraction} dicts, one per extra map.
    """
    N = len(labels)
    labels_ext = labels + ['K']
    parity_ext = parity + [0]
    table_ext = dict(table)
    for i in range(N + 1):
        table_ext[(i, N)] = {}
        table_ext[(N, i)] = {}
    maps = []
    for j in range(N):
        if parity[j] != 1:
            continue
        full = coboundary_full((j, N), labels_ext, parity_ext, table_ext)
        entries = {}
        for (a, b), vec in full.items():
            if a > b:
                continue
            for k, v in vec.items():
                key = (labels_ext[a], labels_ext[b], labels_ext[k])
                entries[key] = entries.get(key, 0) + v
        maps.append({key: v for key, v in entries.items() if v != 0})
    return maps


def build_system(n, extended=False):
    """Return (gb_labels, phi_names, D, G) where
    D[row] = {φ-index: Fraction} and G[row] = {gb-index: Fraction}."""
    s1 = load(n)
    labels, parity, table, _ = build_table(s1)
    s2 = _read(n, 'gamma')
    s4 = _read(n, 'coboundary')

    gb_labels = [p['label'] for p in s2['gb_matrix']['parameters']]
    gb_index = {lab: i for i, lab in enumerate(gb_labels)}

    phi_names, D = [], {}
    for m, mp in enumerate(s4['maps']):
        phi_names.append(mp['name'])
        for e in mp['entries']:
            key = (e['X'], e['Y'], e['Z'])
            D.setdefault(key, {})[m] = Fraction(e['coeff'])

    if extended:
        for k, entries in enumerate(extended_maps(labels, parity, table)):
            m = len(phi_names)
            phi_names.append(f'odd->K#{k}')
            for key, v in entries.items():
                D.setdefault(key, {})[m] = v

    G = {}
    for e in s2['gamma']:
        key = (e['X'], e['Y'], e['Z'])
        for t in e['terms']:
            G.setdefault(key, {})[gb_index[t['gb']]] = Fraction(t['coeff'])
    return gb_labels, phi_names, D, G


def eliminate(num_phi, num_gb, D, G):
    """Eliminate φ and return (constraints, pivots).

    constraints: list of {gb-index: Fraction} rows with no φ part.
    pivots: {φ-column: row dict over φ-columns and gb-columns (gb cols offset by num_phi)}.
    Each equation is  Σ_m D φ_m - Σ_p G gb_p = 0.
    """
    rows = []
    for key in set(D) | set(G):
        row = {}
        for m, v in D.get(key, {}).items():
            row[m] = row.get(m, 0) + v
        for p, v in G.get(key, {}).items():
            row[num_phi + p] = row.get(num_phi + p, 0) - v
        row = {c: v for c, v in row.items() if v != 0}
        if row:
            rows.append(row)

    pivots = {}
    constraints = []
    for row in rows:
        row = dict(row)
        while True:
            phi_cols = [c for c in row if c < num_phi]
            if not phi_cols:
                break
            c = min(phi_cols)
            if c in pivots:
                f = row[c]
                for cc, vv in pivots[c].items():
                    row[cc] = row.get(cc, 0) - f * vv
                row = {cc: vv for cc, vv in row.items() if vv != 0}
            else:
                f = row[c]
                pivots[c] = {cc: vv / f for cc, vv in row.items()}
                row = None
                break
        if row is not None and row:
            constraints.append({c - num_phi: v for c, v in row.items()})
    return constraints, pivots


def rref(rows):
    """Reduced row echelon form of sparse rows.

    Returns (basis, pivots) where pivots[i] is the pivot column of basis[i].
    """
    basis, pivots = [], []
    for r in rows:
        r = dict(r)
        # basis is fully reduced, so each pivot column appears in one row only
        for idx, c in enumerate(pivots):
            if c in r:
                f = r[c]
                for cc, vv in basis[idx].items():
                    r[cc] = r.get(cc, 0) - f * vv
        r = {c: v for c, v in r.items() if v != 0}
        if not r:
            continue
        c0 = min(r)
        f = r[c0]
        r = {c: v / f for c, v in r.items()}
        for idx in range(len(basis)):
            if c0 in basis[idx]:
                g = basis[idx][c0]
                for cc, vv in r.items():
                    basis[idx][cc] = basis[idx].get(cc, 0) - g * vv
                basis[idx] = {c: v for c, v in basis[idx].items() if v != 0}
        basis.append(r)
        pivots.append(c0)
    return basis, pivots


def kernel_basis(constraints, num_gb):
    """Basis of {x ∈ Q^num_gb : c·x = 0 for all constraint rows c}."""
    basis, pivots = rref(constraints)
    free = [c for c in range(num_gb) if c not in pivots]
    out = []
    for fcol in free:
        vec = [Fraction(0)] * num_gb
        vec[fcol] = Fraction(1)
        for idx, pc in enumerate(pivots):
            vec[pc] = -basis[idx].get(fcol, Fraction(0))
        out.append(vec)
    return out


def solve_phi(gb_vec, num_phi, pivots):
    """Back-substitute φ for a numeric gb (free φ set to 0). Returns list of Fractions."""
    phi = [Fraction(0)] * num_phi
    for c in sorted(pivots, reverse=True):
        row = pivots[c]
        s = Fraction(0)
        for cc, vv in row.items():
            if cc == c:
                continue
            if cc < num_phi:
                s += vv * phi[cc]
            else:
                s += vv * gb_vec[cc - num_phi]
        phi[c] = -s
    return phi


def residual_ok(gb_vec, num_phi, D, G, phi):
    """Exact check of Δφ = Γ(gb) on every row."""
    keys = set(D) | set(G)
    for key in keys:
        lhs = sum(v * phi[m] for m, v in D.get(key, {}).items())
        rhs = sum(v * gb_vec[p] for p, v in G.get(key, {}).items())
        if lhs != rhs:
            return False
    return True


def analyse(n, extended):
    gb_labels, phi_names, D, G = build_system(n, extended)
    num_phi, num_gb = len(phi_names), len(gb_labels)
    constraints, pivots = eliminate(num_phi, num_gb, D, G)
    basis_rows, _ = rref(constraints)
    kernel = kernel_basis(constraints, num_gb)
    k_rows = sum(1 for key in G if key[2] == 'K')
    report = {
        'n': n,
        'reading': 'extended (f may map odd -> K)' if extended else 'strict (f: g -> g)',
        'num_phi': num_phi,
        'num_gb': num_gb,
        'num_equations': len(set(D) | set(G)),
        'rank_constraints': len(basis_rows),
        'trivial_locus_dim': len(kernel),
        'constraints': [
            {gb_labels[c]: str(v) for c, v in sorted(row.items())}
            for row in basis_rows
        ],
        'kernel_basis': [
            {gb_labels[c]: str(v) for c, v in enumerate(vec) if v != 0}
            for vec in kernel
        ],
        'K_equations': k_rows,
    }
    # witnesses: every kernel vector must admit an exact φ
    witness_ok = []
    for vec in kernel:
        phi = solve_phi(vec, num_phi, pivots)
        witness_ok.append(residual_ok(vec, num_phi, D, G, phi))
    report['kernel_witness_ok'] = witness_ok
    # the representative profile gb ≡ +1
    ones = [Fraction(1)] * num_gb
    report['all_plus_one_trivial'] = all(
        sum(v * ones[c] for c, v in row.items()) == 0 for row in basis_rows)
    return report, (gb_labels, phi_names, D, G, pivots)


def profile_evidence(n):
    """Layer 3 vs Layer 4 for named gb profiles (strict reading).

    For each profile: solve Δφ = Γ_g(gb) on the g-rows only, then list the rows
    where Δφ ≠ Γ(gb) on the full system (the K-rows). Returns a list of dicts.
    """
    gb_labels, phi_names, D, G = build_system(n, extended=False)
    num_phi, num_gb = len(phi_names), len(gb_labels)
    G_g = {k: v for k, v in G.items() if k[2] != 'K'}
    _, piv_g = eliminate(num_phi, num_gb, D, G_g)
    profiles = {'zero': [Fraction(0)] * num_gb,
                'all_plus_one': [Fraction(1)] * num_gb,
                f'single_{gb_labels[0]}': [Fraction(1)] + [Fraction(0)] * (num_gb - 1)}
    out = []
    for name, gb_vec in profiles.items():
        phi = solve_phi(gb_vec, num_phi, piv_g)
        mism = []
        for key in sorted(set(D) | set(G)):
            lhs = sum(v * phi[m] for m, v in D.get(key, {}).items())
            rhs = sum(v * gb_vec[p] for p, v in G.get(key, {}).items())
            if lhs != rhs:
                mism.append({'X': key[0], 'Y': key[1], 'Z': key[2],
                             'delta_f': str(lhs), 'gamma': str(rhs)})
        out.append({'profile': name,
                    'gb': {gb_labels[p]: str(v) for p, v in enumerate(gb_vec) if v != 0},
                    'mismatched_rows': len(mism),
                    'mismatches': mism})
    return out


def main():
    summary = {}
    for n in (1, 2, 3):
        for extended in (False, True):
            report, _ = analyse(n, extended)
            key = f'n{n}_{"extended" if extended else "strict"}'
            summary[key] = report
            print(f'n={n} {report["reading"]}: equations={report["num_equations"]}, '
                  f'φ-unknowns={report["num_phi"]}, gb-unknowns={report["num_gb"]}')
            print(f'  rank of gb-constraints = {report["rank_constraints"]}, '
                  f'trivial locus dim = {report["trivial_locus_dim"]}, '
                  f'K-equations = {report["K_equations"]}')
            print(f'  gb ≡ +1 trivial: {report["all_plus_one_trivial"]}; '
                  f'kernel witnesses verified: {all(report["kernel_witness_ok"])}')
        evidence = profile_evidence(n)
        summary[f'n{n}_profiles_strict'] = evidence
        for item in evidence:
            print(f'  profile {item["profile"]}: mismatched rows = {item["mismatched_rows"]}, '
                  f'all mismatches are K-rows: {all(m["Z"] == "K" for m in item["mismatches"])}')
    path = DATA_DIR / 'C_triviality_summary.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'wrote {path.name}')


if __name__ == '__main__':
    main()
