"""Schema 4: coboundary data for C(n+1) from elementary odd linear maps.

An odd linear map f: g -> g reverses parity.  The elementary maps are
    f_ij(X_j) = X_i ,   f_ij(X_k) = 0 for k != j ,   with p(X_i) != p(X_j).
A general odd map is f = sum phi_ij f_ij, so its coboundary is sum phi_ij (delta f_ij).
Coboundary (C_coboundary_definition.md):
    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y])

Reads the kappa-free structure constants from data/C_{n}_structure.json (Schema 1).
Checks for every elementary map (n = 1, 2 fully; n = 3 on a fixed random sample, see below):
  * graded anti-symmetry of delta f
  * parity: the value (delta f)(X,Y) has parity p(X)+p(Y)+1
  * cocycle condition in the kappa-left convention (the convention of gamma), so delta f
    lies in the same space as gamma
Usage:  python3 src/C_coboundary.py
"""

import datetime
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from verify_C_structure import load_structure  # noqa: E402

ROOT = os.path.dirname(HERE)
DATA_DIR = os.path.join(ROOT, 'data')
RANKS = (1, 2, 3)
N3_SAMPLE = 40  # maps checked for the cocycle condition at n = 3 (all maps at n = 1, 2)


def _frac(value):
    return str(Fraction(value))


def _bracket(table, u, v):
    out = {}
    for x, a in u.items():
        for y, b in v.items():
            for z, c in table.get((x, y), {}).items():
                out[z] = out.get(z, 0) + a * b * c
    return {z: c for z, c in out.items() if c != 0}


def _add(u, v, sign=1):
    out = dict(u)
    for k, c in v.items():
        out[k] = out.get(k, 0) + sign * c
    return {k: c for k, c in out.items() if c != 0}


def delta_of_elementary(basis, parity, table, i, j):
    """(delta f_ij)(X,Y) for all basis pairs; returns {(X,Y): {Z: coeff}} with non-zero values."""
    f = {j: {i: Fraction(1)}}  # f(X_j) = X_i, f(X_k) = 0 otherwise
    out = {}
    for x in basis:
        for y in basis:
            px, py = parity[x], parity[y]
            fy = f.get(y, {})
            fx = f.get(x, {})
            term1 = _bracket(table, {x: Fraction(1)}, fy) if fy else {}
            term1 = {z: c * (-1) ** px for z, c in term1.items()}
            term2 = _bracket(table, {y: Fraction(1)}, fx) if fx else {}
            term2 = {z: c * (-(-1) ** ((px + 1) * py)) for z, c in term2.items()}
            bxy = _bracket(table, {x: Fraction(1)}, {y: Fraction(1)})
            term3 = {}
            for z, c in bxy.items():
                if z in f:
                    for w, d in f[z].items():
                        term3[w] = term3.get(w, 0) - c * d
            value = _add(_add(term1, term2), term3)
            if value:
                out[(x, y)] = value
    return out


def check_map(basis, parity, table, delta):
    """Return failure counts for one delta f (super-antisymmetry, parity, cocycle)."""
    fails = {'antisymmetry': 0, 'parity': 0, 'cocycle': 0}
    for (x, y), img in delta.items():
        for z in img:
            if (parity[z] - parity[x] - parity[y] - 1) % 2 != 0:
                fails['parity'] += 1
        sign = (-1) ** (parity[x] * parity[y])
        rev = delta.get((y, x), {})
        if _add(img, rev, sign):
            fails['antisymmetry'] += 1
    # cocycle in the kappa-left convention (same formula as C_gamma.gamma_checks)
    for x in basis:
        for y in basis:
            for z in basis:
                s = (-1) ** (parity[x] * parity[y])
                ex, ey, ez = {x: Fraction(1)}, {y: Fraction(1)}, {z: Fraction(1)}
                g = lambda a, b: dict(delta.get((a, b), {}))  # noqa: E731
                gbil = lambda u, v: _gbil(delta, u, v)  # noqa: E731
                t = _bracket(table, ex, g(y, z))
                t = {c: v * (-1) ** parity[x] for c, v in t.items()}
                t = _add(t, gbil(ex, _bracket(table, ey, ez)))
                t = _add(t, _bracket(table, g(x, y), ez), -1)
                t = _add(t, gbil(_bracket(table, ex, ey), ez), -1)
                t = _add(t, _bracket(table, ey, g(x, z)), -s * (-1) ** parity[y])
                t = _add(t, gbil(ey, _bracket(table, ex, ez)), -s)
                if t:
                    fails['cocycle'] += 1
    return fails


def _gbil(delta, u, v):
    out = {}
    for a, x in u.items():
        for b, y in v.items():
            for c, z in delta.get((a, b), {}).items():
                out[c] = out.get(c, 0) + x * y * z
    return {c: w for c, w in out.items() if w != 0}


def elementary_maps(basis, parity):
    """All parity-reversing pairs (i, j): f_ij(X_j) = X_i."""
    return [(i, j) for i in basis for j in basis if parity[i] != parity[j]]


def build_schema4(n, generation_date):
    doc, labels, parity_map, table = load_structure(n, DATA_DIR)
    basis = labels
    parity = {x: parity_map[x] for x in basis}
    maps = elementary_maps(basis, parity)
    rng = random.Random(20261008)
    sampled = maps if n < 3 else rng.sample(maps, min(N3_SAMPLE, len(maps)))
    sampled_set = set(sampled)

    records = []
    checked = {'antisymmetry': 0, 'parity': 0, 'cocycle': 0}
    maps_checked = 0
    for (i, j) in maps:
        delta = delta_of_elementary(basis, parity, table, i, j)
        entries = []
        for (x, y) in sorted(delta):
            for z, c in sorted(delta[(x, y)].items()):
                entries.append({'X': x, 'Y': y, 'Z': z, 'coeff': _frac(c)})
        records.append({'i': i, 'j': j, 'coboundary': entries})
        if (i, j) in sampled_set:
            maps_checked += 1
            fails = check_map(basis, parity, table, delta)
            for key in checked:
                checked[key] += fails[key]
    return {
        'schema_version': '5.0',
        'algebra_ref': 'C_%d_structure.json' % n,
        'map_convention': 'f(X_j) = X_i, other basis elements to 0; p(X_i) != p(X_j)',
        'delta_convention': '(delta f)(X,Y) = (-1)^{p(X)} [X,f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y,f(X)] - f([X,Y])',
        'number_of_maps': len(maps),
        'maps': records,
        'checks': {
            'maps_checked_for_cocycle': maps_checked,
            'failures': checked,
            'sampling': 'all maps' if n < 3 else 'random sample of %d maps (seed 20261008)' % len(sampled),
        },
        'metadata': {
            'generated_by': 'src/C_coboundary.py',
            'generation_date': generation_date,
        },
    }


def main():
    generation_date = datetime.date.today().isoformat()
    for n in RANKS:
        doc = build_schema4(n, generation_date)
        path = os.path.join(DATA_DIR, 'C_%d_coboundary.json' % n)
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
            fh.write('\n')
        print('n=%d maps=%d entries=%d checks=%s' % (
            n, doc['number_of_maps'], sum(len(m['coboundary']) for m in doc['maps']), doc['checks']))


if __name__ == '__main__':
    main()
