#!/usr/bin/env python3
"""
verify_C_structure.py
Verify anti-symmetry and Super Jacobi identity for C(n+1) structure constants.

Loads data/C_{n}_structure.json for n=1,2,3 and performs exact rational checks.

Anti-symmetry:  [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}  for all pairs (X,Y).
Super Jacobi:   (-1)^{pX pZ}[X,[Y,Z}} + (-1)^{pY pX}[Y,[Z,X}}
                + (-1)^{pZ pY}[Z,[X,Y}} = 0   for all triples (X,Y,Z).
"""

from fractions import Fraction
from collections import defaultdict
import json
import os
import sys


# ── Data loading ──────────────────────────────────────────────────────────────

def load_schema(n: int) -> dict:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fname = os.path.join(root, 'data', f'C_{n}_structure.json')
    with open(fname) as f:
        return json.load(f)


def parse_coeff(s: str) -> Fraction:
    if '/' in s:
        num, den = s.split('/')
        return Fraction(int(num), int(den))
    return Fraction(int(s))


# ── Bracket from structure constants ─────────────────────────────────────────

def build_bracket(schema: dict):
    """
    Parse structure constants into a callable bracket.
    Returns (bracket_fn, parity_dict, basis_list).
    bracket_fn(X, Y) -> {Z: Fraction}
    """
    parity = {k: int(v) for k, v in schema['parity'].items()}
    basis = schema['basis']['even'] + schema['basis']['odd']

    # Accumulate into sc[X][Y][Z]
    raw = defaultdict(lambda: defaultdict(lambda: defaultdict(Fraction)))
    for entry in schema['structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        raw[X][Y][Z] += parse_coeff(entry['coeff'])

    # Freeze and drop zeros
    sc = {X: {Y: {Z: c for Z, c in Zmap.items() if c}
              for Y, Zmap in Ymap.items()}
          for X, Ymap in raw.items()}

    def bracket_fn(X: str, Y: str) -> dict:
        return dict(sc.get(X, {}).get(Y, {}))

    return bracket_fn, parity, basis


# ── Utility ───────────────────────────────────────────────────────────────────

def add_scaled(acc: dict, other: dict, scale: Fraction):
    """acc += scale * other  (in-place, prunes zeros)."""
    for Z, c in other.items():
        v = acc.get(Z, Fraction(0)) + scale * c
        if v:
            acc[Z] = v
        else:
            acc.pop(Z, None)


def apply_bracket(bracket_fn, X: str, poly: dict) -> dict:
    """[X, poly} = Σ_k poly[k] · [X, k}"""
    result = {}
    for k, ck in poly.items():
        add_scaled(result, bracket_fn(X, k), ck)
    return result


# ── Anti-symmetry check ───────────────────────────────────────────────────────

def check_antisymmetry(bracket_fn, parity: dict, basis: list) -> list:
    """
    Verify [X,Y} = -(-1)^{pX pY} [Y,X} for all (X,Y).
    Returns list of failure descriptions.
    """
    failures = []
    for X in basis:
        pX = parity[X]
        for Y in basis:
            pY = parity[Y]
            XY = bracket_fn(X, Y)
            YX = bracket_fn(Y, X)
            sign = Fraction((-1) ** (pX * pY))
            # [X,Y} + sign*[Y,X} should vanish
            residual = dict(XY)
            add_scaled(residual, YX, sign)
            if residual:
                failures.append(
                    f'[{X}, {Y}]  residual={residual}')
    return failures


# ── Super Jacobi check ────────────────────────────────────────────────────────

def check_jacobi(bracket_fn, parity: dict, basis: list) -> list:
    """
    Verify the super Jacobi identity for all triples with xi <= yi <= zi
    (sufficient by linearity and antisymmetry).
    Returns list of failure descriptions.
    """
    failures = []
    n = len(basis)
    for xi in range(n):
        X = basis[xi]
        pX = parity[X]
        for yi in range(xi, n):
            Y = basis[yi]
            pY = parity[Y]
            for zi in range(yi, n):
                Z = basis[zi]
                pZ = parity[Z]

                YZ = bracket_fn(Y, Z)
                ZX = bracket_fn(Z, X)
                XY = bracket_fn(X, Y)

                pYZ = (pY + pZ) % 2
                pZX = (pZ + pX) % 2
                pXY = (pX + pY) % 2

                t1 = apply_bracket(bracket_fn, X, YZ)
                t2 = apply_bracket(bracket_fn, Y, ZX)
                t3 = apply_bracket(bracket_fn, Z, XY)

                residual = {}
                add_scaled(residual, t1, Fraction((-1) ** (pX * pZ)))
                add_scaled(residual, t2, Fraction((-1) ** (pY * pX)))
                add_scaled(residual, t3, Fraction((-1) ** (pZ * pY)))

                if residual:
                    failures.append(
                        f'({X}, {Y}, {Z})  residual={residual}')
    return failures


# ── Per-algebra verification ──────────────────────────────────────────────────

def verify_n(n: int) -> dict:
    schema = load_schema(n)
    bracket_fn, parity, basis = build_bracket(schema)
    dim = len(basis)

    n_pairs   = dim * dim
    n_triples = sum(1 for xi in range(dim)
                      for yi in range(xi, dim)
                      for zi in range(yi, dim))

    anti_fail = check_antisymmetry(bracket_fn, parity, basis)
    jac_fail  = check_jacobi(bracket_fn, parity, basis)

    d = schema['algebra']['dimension']
    return {
        'n':              n,
        'algebra':        schema['algebra']['cartan_type'],
        'dim_even':       d['even'],
        'dim_odd':        d['odd'],
        'sc_entries':     len(schema['structure_constants']),
        'pairs_checked':  n_pairs,
        'triples_checked': n_triples,
        'anti_failures':  anti_fail,
        'jac_failures':   jac_fail,
    }


# ── Report ────────────────────────────────────────────────────────────────────

def main():
    print('C(n+1) Structure Constants Verification')
    print('=' * 62)

    overall_pass = True
    for n in [1, 2, 3]:
        print(f'\nn={n}  C({n+1}) = osp(2|{2*n})')
        r = verify_n(n)
        print(f'  dim {r["dim_even"]}|{r["dim_odd"]}   '
              f'SC entries: {r["sc_entries"]}')
        print(f'  Anti-symmetry pairs checked : {r["pairs_checked"]}')
        print(f'  Jacobi triples checked      : {r["triples_checked"]}')

        anti_ok = not r['anti_failures']
        jac_ok  = not r['jac_failures']

        print(f'  Anti-symmetry : {"PASS" if anti_ok else "FAIL  (" + str(len(r["anti_failures"])) + " failures)"}')
        print(f'  Super Jacobi  : {"PASS" if jac_ok  else "FAIL  (" + str(len(r["jac_failures"]))  + " failures)"}')

        if not anti_ok:
            overall_pass = False
            for msg in r['anti_failures'][:3]:
                print(f'    Anti-sym FAIL: {msg}')
            if len(r['anti_failures']) > 3:
                print(f'    ... {len(r["anti_failures"])} total')

        if not jac_ok:
            overall_pass = False
            for msg in r['jac_failures'][:3]:
                print(f'    Jacobi FAIL: {msg}')
            if len(r['jac_failures']) > 3:
                print(f'    ... {len(r["jac_failures"])} total')

    print('\n' + '=' * 62)
    if overall_pass:
        print('OVERALL RESULT: ALL CHECKS PASSED')
    else:
        print('OVERALL RESULT: FAILURES DETECTED — see above')
        sys.exit(1)


if __name__ == '__main__':
    main()
