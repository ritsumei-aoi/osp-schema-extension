"""
Tests for C_evaluated.py — Schema 3 (Evaluated Structure) for C(n+1) = osp(2|2n).

T1: pairs with gamma=0 (no a_1 in either generator) have empty kappa_part
T2: for all_plus profile, all non-zero Schema 2 gamma entries appear in kappa_part
T3: graded antisymmetry of the evaluated deformed bracket
"""

import sys
import os
import json
from fractions import Fraction
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_evaluated import (
    generate_schema3, _load_schema1, _load_schema2,
    _eval_gamma, _gb_all_plus, _gb_diagonal, _gb_anti_diagonal,
)
from C_generators import basis_list, make_generators


# ──────────────────────────────────────────────────────────────────
# T1: pairs with no a_1 → kappa_part absent
# ──────────────────────────────────────────────────────────────────

def _has_a1(gen_label: str, gens: dict) -> bool:
    elem, _ = gens[gen_label]
    return any(any(o.startswith('a_') for o in word) for word in elem)


def test_T1_no_a1_pairs_no_kappa(n: int = 1, profile: str = 'all_plus'):
    gens = make_generators(n)
    schema = generate_schema3(n, profile)
    failures = []
    for entry in schema['deformed_brackets']:
        X, Y = entry['X'], entry['Y']
        if not _has_a1(X, gens) and not _has_a1(Y, gens):
            if 'kappa_part' in entry and entry['kappa_part']:
                failures.append((X, Y, entry['kappa_part']))
    if failures:
        for X, Y, kp in failures[:3]:
            print(f'  FAIL: ({X}, {Y}) has kappa_part={kp}')
        raise AssertionError(f'T1 FAIL n={n}: {len(failures)} no-a_1 pairs have non-empty kappa_part')
    print(f'T1 PASS: n={n} [{profile}] — all no-a_1 pairs have no kappa_part')


# ──────────────────────────────────────────────────────────────────
# T2: all_plus activates all Schema 2 gamma entries
# ──────────────────────────────────────────────────────────────────

def test_T2_all_plus_covers_gamma(n: int = 1):
    """All (a,b,c) gamma entries from Schema 2 should appear in Schema 3 kappa_part."""
    gamma_table = _load_schema2(n)
    gb_values = _gb_all_plus(n)

    schema = generate_schema3(n, 'all_plus')
    kappa_lookup: dict = {}
    for entry in schema['deformed_brackets']:
        X, Y = entry['X'], entry['Y']
        for item in entry.get('kappa_part', []):
            key = (X, Y, item['Z'])
            if '/' in item['coeff']:
                a, b = item['coeff'].split('/')
                kappa_lookup[key] = Fraction(int(a), int(b))
            else:
                kappa_lookup[key] = Fraction(int(item['coeff']))

    # Check every canonical (a,b) gamma entry is represented
    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis
    idx = {g: i for i, g in enumerate(all_basis)}

    missing = []
    for (a, b), cv in gamma_table.items():
        if a not in idx or b not in idx:
            continue
        if idx[a] > idx[b]:
            continue  # non-canonical direction, skip
        evaluated = _eval_gamma(cv, gb_values)
        for c, expected in evaluated.items():
            got = kappa_lookup.get((a, b, c), Fraction(0))
            if got != expected:
                missing.append((a, b, c, expected, got))

    if missing:
        for a, b, c, exp, got in missing[:5]:
            print(f'  FAIL: gamma({a},{b})^{c}: expected {exp}, got {got}')
        raise AssertionError(f'T2 FAIL n={n}: {len(missing)} mismatched kappa entries')

    print(f'T2 PASS: n={n} all_plus — all canonical gamma entries correctly appear in kappa_part')


# ──────────────────────────────────────────────────────────────────
# T3: graded antisymmetry of the evaluated deformed bracket
# ──────────────────────────────────────────────────────────────────

def _build_full_evaluated(schema: dict, parity: dict):
    """
    Build full (both directions) evaluated bracket table from Schema 3.
    Returns: {(X,Y): {'g': {Z:Fraction}, 'k': {Z:Fraction}}}
    """
    def _parse(s):
        if '/' in s:
            a, b = s.split('/')
            return Fraction(int(a), int(b))
        return Fraction(int(s))

    fwd: dict = {}
    for entry in schema['deformed_brackets']:
        X, Y = entry['X'], entry['Y']
        g = {it['Z']: _parse(it['coeff']) for it in entry.get('g_part', [])}
        k = {it['Z']: _parse(it['coeff']) for it in entry.get('kappa_part', [])}
        fwd[(X, Y)] = {'g': g, 'k': k}

    # Build reverse via antisymmetry
    full: dict = dict(fwd)
    for (X, Y), parts in fwd.items():
        if X == Y:
            continue
        sign = (-1) ** (parity[X] * parity[Y])
        rev_g = {Z: -Fraction(sign) * c for Z, c in parts['g'].items()}
        rev_k = {Z: -Fraction(sign) * c for Z, c in parts['k'].items()}
        if (Y, X) not in full:
            full[(Y, X)] = {'g': rev_g, 'k': rev_k}

    return full


def test_T3_graded_antisymmetry(n: int = 1, profile: str = 'all_plus'):
    """
    [X,Y]_gamma + (-1)^{pa*pb} [Y,X]_gamma = 0
    Both g_part and kappa_part must be antisymmetric.
    """
    parity, _ = _load_schema1(n)
    schema = generate_schema3(n, profile)
    full = _build_full_evaluated(schema, parity)

    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis

    failures = []
    for X in all_basis:
        for Y in all_basis:
            sign = (-1) ** (parity[X] * parity[Y])
            XY = full.get((X, Y), {'g': {}, 'k': {}})
            YX = full.get((Y, X), {'g': {}, 'k': {}})

            for part in ('g', 'k'):
                all_Z = set(XY[part].keys()) | set(YX[part].keys())
                for Z in all_Z:
                    res = XY[part].get(Z, Fraction(0)) + sign * YX[part].get(Z, Fraction(0))
                    if res != 0:
                        failures.append((X, Y, Z, part, res))

    if failures:
        for X, Y, Z, part, r in failures[:5]:
            print(f'  FAIL: [{X},{Y}]^{Z} {part}-part antisymm residual = {r}')
        raise AssertionError(f'T3 FAIL n={n} [{profile}]: {len(failures)} antisymmetry violations')

    print(f'T3 PASS: n={n} [{profile}] — graded antisymmetry holds for g_part and kappa_part')


# ──────────────────────────────────────────────────────────────────
# JSON schema structure check
# ──────────────────────────────────────────────────────────────────

def test_T_schema(n: int = 1, profile: str = 'all_plus'):
    schema = generate_schema3(n, profile)
    assert schema['schema_version'] == '5.0'
    assert schema['schema_layer'] == 3
    assert schema['algebra']['family'] == 'C'
    assert schema['algebra']['n'] == n
    assert 'gb_profile' in schema
    assert schema['gb_profile']['label'] == profile
    assert isinstance(schema['deformed_brackets'], list)
    assert len(schema['deformed_brackets']) > 0
    for e in schema['deformed_brackets']:
        assert 'X' in e and 'Y' in e and 'g_part' in e
        assert isinstance(e['g_part'], list)
        if 'kappa_part' in e:
            assert isinstance(e['kappa_part'], list)
            assert len(e['kappa_part']) > 0
    print(f'T_schema PASS: n={n} [{profile}] valid Schema 3 JSON ({len(schema["deformed_brackets"])} entries)')


# ──────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    all_pass = True
    tests = []
    for n in [1, 2, 3]:
        for profile in ['all_plus', 'diagonal', 'anti_diagonal']:
            tests.append((f'T1 n={n} {profile}', lambda n=n, p=profile: test_T1_no_a1_pairs_no_kappa(n, p)))
            tests.append((f'T3 n={n} {profile}', lambda n=n, p=profile: test_T3_graded_antisymmetry(n, p)))
            tests.append((f'T_schema n={n} {profile}', lambda n=n, p=profile: test_T_schema(n, p)))
    for n in [1, 2, 3]:
        tests.append((f'T2 n={n}', lambda n=n: test_T2_all_plus_covers_gamma(n)))

    for name, fn in tests:
        try:
            fn()
        except Exception as e:
            print(f'[FAIL] {name}: {e}')
            all_pass = False

    print()
    print('ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED')
    sys.exit(0 if all_pass else 1)
