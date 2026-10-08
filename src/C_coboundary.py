"""Coboundary structure for C(n+1) (Schema 4, Layer 4) (I07).

An odd linear map f: g -> g (parity-reversing) is given on the basis by the
elementary maps f_{j->i}: Z_j -> Z_i with p(Z_i) = p(Z_j) + 1, Z_m -> 0 for m != j.
For each elementary map the coboundary is

    (δf)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y])

with the undeformed bracket taken from Schema 1 (data/C_{n}_structure.json).

Checks performed here:
  * parity: every entry of δf has parity p(X)+p(Y)+1, Z in the basis;
  * cocycle: the linearized Jacobi identity holds for δf, i.e. with the odd
    parameter κ (signs as derived in I07):
      (-1)^{pX}[X,γ(Y,Z)] + γ(X,[Y,Z]) - [γ(X,Y),Z] - γ([X,Y],Z)
      - (-1)^{pXpY+pY}[Y,γ(X,Z)] - (-1)^{pXpY} γ(Y,[X,Z]) = 0.

Usage:
    python src/C_coboundary.py   # writes data/C_{1,2,3}_coboundary.json
"""

import json
import random
from fractions import Fraction
from pathlib import Path

from verify_C_structure import bracket, build_table, load

GENERATION_DATE = '2026-10-08'
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'


def elementary_maps(labels, parity):
    """All elementary odd maps as (j, i) with p(i) = p(j) + 1 mod 2."""
    out = []
    for j in range(len(labels)):
        for i in range(len(labels)):
            if parity[i] == (parity[j] + 1) % 2:
                out.append((j, i))
    return out


def apply_f(f, vec):
    """f given as (j, i) meaning Z_j -> Z_i. Applied to a sparse vector."""
    j, i = f
    return {i: vec[j]} if j in vec and vec[j] != 0 else {}


def coboundary_full(f, labels, parity, table):
    """Return dict {(a, b): vec} with (δf)(Z_a, Z_b) for all ordered pairs."""
    n_basis = len(labels)
    out = {}
    for a in range(n_basis):
        for b in range(n_basis):
            X, Y = {a: Fraction(1)}, {b: Fraction(1)}
            pX, pY = parity[a], parity[b]
            fY = apply_f(f, Y)
            fX = apply_f(f, X)
            XY = bracket(X, Y, table)
            t1 = bracket(X, fY, table)
            t2 = bracket(Y, fX, table)
            fXY = {}
            for m, c in XY.items():
                for k, v in apply_f(f, {m: c}).items():
                    fXY[k] = fXY.get(k, 0) + v
            s1 = -1 if pX % 2 else 1
            s2 = -1 if ((pX + 1) * pY) % 2 else 1
            vec = {}
            for k, v in t1.items():
                vec[k] = vec.get(k, 0) + s1 * v
            for k, v in t2.items():
                vec[k] = vec.get(k, 0) - s2 * v
            for k, v in fXY.items():
                vec[k] = vec.get(k, 0) - v
            out[(a, b)] = {k: v for k, v in vec.items() if v != 0}
    return out


def _add(*terms):
    out = {}
    for sign, vec in terms:
        for k, v in vec.items():
            out[k] = out.get(k, 0) + sign * v
    return {k: v for k, v in out.items() if v != 0}


def _gamma_of(gamma, u, v):
    """Bilinear extension of gamma (full ordered table) to sparse vectors."""
    out = {}
    for a, ca in u.items():
        for b, cb in v.items():
            for k, c in gamma[(a, b)].items():
                out[k] = out.get(k, 0) + ca * cb * c
    return out


def cocycle_failures(gamma, labels, parity, table):
    """Count triples (x, y, z) where the linearized Jacobi identity fails.

    gamma is the full ordered table {(a, b): vec}. The identity is

      (-1)^{pX}[X,γ(Y,Z)] + γ(X,[Y,Z]) - [γ(X,Y),Z] - γ([X,Y],Z)
      - (-1)^{pXpY+pY}[Y,γ(X,Z)] - (-1)^{pXpY} γ(Y,[X,Z]) = 0.
    """
    N = len(labels)
    failures = 0
    for x in range(N):
        for y in range(N):
            for z in range(N):
                X, Y, Z = {x: Fraction(1)}, {y: Fraction(1)}, {z: Fraction(1)}
                pX, pY = parity[x], parity[y]
                sgn_a = -1 if pX % 2 else 1
                sgn_b = -1 if (pX * pY + pY) % 2 else 1
                sgn_c = -1 if (pX * pY) % 2 else 1
                total = _add(
                    (sgn_a, bracket(X, _gamma_of(gamma, Y, Z), table)),
                    (1, _gamma_of(gamma, X, bracket(Y, Z, table))),
                    (-1, bracket(_gamma_of(gamma, X, Y), Z, table)),
                    (-1, _gamma_of(gamma, bracket(X, Y, table), Z)),
                    (-sgn_b, bracket(Y, _gamma_of(gamma, X, Z), table)),
                    (-sgn_c, _gamma_of(gamma, Y, bracket(X, Z, table))),
                )
                if total:
                    failures += 1
    return failures


def cochain_entries(full, labels):
    """Entries of δf for a ≤ b with nonzero coefficient, in Schema 4 form."""
    entries = []
    for (a, b) in sorted(full):
        if a > b:
            continue
        for k, v in sorted(full[(a, b)].items()):
            entries.append({'X': labels[a], 'Y': labels[b],
                            'Z': labels[k], 'coeff': str(v)})
    return entries


def build_schema4(n, maps_out):
    return {
        'schema_version': '5.0',
        'layer': 'Schema 4: coboundary structure (delta f for elementary odd maps)',
        'algebra': {'family': 'C', 'm': 1, 'n': n,
                    'cartan_type': f'C({n + 1})'},
        'map_definition': {
            'odd': 'f: g -> g, parity-reversing',
            'elementary': 'f_{j->i}: Z_j -> Z_i, Z_m -> 0 for m != j',
            'coboundary': '(δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])',
            'bracket': 'undeformed (Schema 1)',
        },
        'maps': maps_out,
        'metadata': {
            'generated_by': 'src/C_coboundary.py',
            'generation_date': GENERATION_DATE,
            'source': f'data/C_{n}_structure.json',
        },
    }


def process(n, cocycle_sample=None, rng=None):
    """Compute Schema 4 for n. cocycle_sample: number of maps for the cocycle test."""
    s1 = load(n)
    labels, parity, table, _ = build_table(s1)
    maps = elementary_maps(labels, parity)
    maps_out = []
    parity_violations = 0
    cocycle_checked, cocycle_bad = 0, 0
    if cocycle_sample is None or cocycle_sample >= len(maps):
        check_set = set(range(len(maps)))
    else:
        check_set = set(rng.sample(range(len(maps)), cocycle_sample))
    for idx, (j, i) in enumerate(maps):
        full = coboundary_full((j, i), labels, parity, table)
        for (a, b), vec in full.items():
            for k in vec:
                if parity[k] != (parity[a] + parity[b] + 1) % 2:
                    parity_violations += 1
        if idx in check_set:
            cocycle_checked += 1
            if cocycle_failures(full, labels, parity, table):
                cocycle_bad += 1
        maps_out.append({'name': f'{labels[j]}->{labels[i]}',
                         'source': labels[j], 'target': labels[i],
                         'entries': cochain_entries(full, labels)})
    return {'labels': labels, 'maps': maps, 'maps_out': maps_out,
            'parity_violations': parity_violations,
            'cocycle_checked': cocycle_checked, 'cocycle_bad': cocycle_bad}


def main():
    DATA_DIR.mkdir(exist_ok=True)
    rng = random.Random(20261008)
    for n in (1, 2, 3):
        sample = None if n == 1 else 30
        res = process(n, cocycle_sample=sample, rng=rng)
        schema = build_schema4(n, res['maps_out'])
        path = DATA_DIR / f'C_{n}_coboundary.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
            f.write('\n')
        total_entries = sum(len(m['entries']) for m in res['maps_out'])
        print(f'n={n}: wrote {path.name}: {len(res["maps"])} elementary maps, '
              f'{total_entries} entries, parity violations {res["parity_violations"]}, '
              f'cocycle checked on {res["cocycle_checked"]} maps, '
              f'failing {res["cocycle_bad"]}')


if __name__ == '__main__':
    main()
