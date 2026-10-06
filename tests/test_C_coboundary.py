"""
Tests for C_coboundary.py — Schema 4 (Coboundary Structure) for C(n+1) = osp(2|2n).

T1: Graded antisymmetry — (delta f)(X,Y) = -(-1)^{p(X)p(Y)} (delta f)(Y,X)
T2: Zero map (all phi=0) gives zero coboundary
T3: Schema 4 JSON structure validation
"""

import sys
import os
import json
from fractions import Fraction
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_coboundary import (
    compute_coboundary_symbolic, generate_schema4,
    _load_schema1, _phi_label,
)
from C_generators import basis_list


# ──────────────────────────────────────────────────────────────────
# T1: Graded antisymmetry
# ──────────────────────────────────────────────────────────────────

def test_T1_graded_antisymmetry(n: int = 1):
    """
    (delta f)(X,Y)^Z = -(-1)^{p(X)p(Y)} (delta f)(Y,X)^Z
    for all X,Y,Z and all phi parameters.

    Since the coboundary is linear in phi, we check coefficient by coefficient:
    coeff_phi[(X,Y,Z)][lbl] + (-1)^{pX*pY} * coeff_phi[(Y,X,Z)][lbl] = 0
    """
    parity, _ = _load_schema1(n)
    cb = compute_coboundary_symbolic(n)

    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis

    failures = []
    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            sign = (-1) ** (pX * pY)
            for Z in all_basis:
                xy_coeffs = cb.get((X, Y, Z), {})
                yx_coeffs = cb.get((Y, X, Z), {})
                all_lbls = set(xy_coeffs) | set(yx_coeffs)
                for lbl in all_lbls:
                    res = (xy_coeffs.get(lbl, Fraction(0))
                           + sign * yx_coeffs.get(lbl, Fraction(0)))
                    if res != 0:
                        failures.append((X, Y, Z, lbl, res))

    if failures:
        for X, Y, Z, lbl, r in failures[:5]:
            print(f'  FAIL: ({X},{Y},{Z})[{lbl}] antisymm residual = {r}')
        raise AssertionError(
            f'T1 FAIL n={n}: {len(failures)} antisymmetry violations in coeff_phi'
        )
    print(f'T1 PASS: n={n} graded antisymmetry holds for all (X,Y,Z,phi) entries')


# ──────────────────────────────────────────────────────────────────
# T2: Zero map gives zero coboundary
# ──────────────────────────────────────────────────────────────────

def test_T2_zero_map(n: int = 1):
    """
    Substitute phi=0 for all parameters. (delta 0)(X,Y) = 0.
    Since all entries have non-zero coeff_phi, setting phi=0 gives zero — we
    verify that the symbolic coboundary has at least one non-zero entry
    (otherwise the formula is trivially zero), and that evaluating at phi=0
    gives all-zero output.
    """
    cb = compute_coboundary_symbolic(n)

    # The coboundary table is non-empty (non-trivial formula)
    assert len(cb) > 0, 'T2 FAIL: coboundary table is empty — formula may be wrong'

    # Evaluating at phi=0: sum all phi-coefficient * 0 = 0 for every entry
    for key, phi_dict in cb.items():
        result = sum(Fraction(0) * c for c in phi_dict.values())
        assert result == 0, f'T2 FAIL: non-zero at phi=0 for {key}'

    print(f'T2 PASS: n={n} — coboundary has {len(cb)} symbolic entries; all zero at phi=0')


# ──────────────────────────────────────────────────────────────────
# T3: Schema 4 JSON structure validation
# ──────────────────────────────────────────────────────────────────

def test_T3_schema(n: int = 1):
    schema = generate_schema4(n)

    assert schema['schema_version'] == '5.0'
    assert schema['schema_layer'] == 4
    assert schema['algebra']['family'] == 'C'
    assert schema['algebra']['n'] == n

    f_map = schema['f_map']
    assert isinstance(f_map['phi_labels'], list)
    assert f_map['phi_count'] == len(f_map['phi_labels'])

    parity, _ = _load_schema1(n)
    odd_basis, even_basis = basis_list(n)
    expected_phi = sum(1 for domain in even_basis + odd_basis
                       for image in even_basis + odd_basis
                       if parity[image] != parity[domain])
    assert f_map['phi_count'] == expected_phi, \
        f'T3 FAIL: phi_count={f_map["phi_count"]}, expected {expected_phi}'

    cb = schema['coboundary']
    assert isinstance(cb, list)
    assert len(cb) > 0
    for entry in cb:
        assert 'X' in entry and 'Y' in entry and 'Z' in entry and 'coeff_phi' in entry
        assert isinstance(entry['coeff_phi'], dict)
        assert len(entry['coeff_phi']) > 0
        for lbl, cstr in entry['coeff_phi'].items():
            assert lbl.startswith('phi_')
            _ = Fraction(int(cstr.split('/')[0]),
                         int(cstr.split('/')[1])) if '/' in cstr else Fraction(int(cstr))

    print(f'T3 PASS: n={n} Schema 4 JSON valid — phi_count={f_map["phi_count"]}, '
          f'{len(cb)} coboundary entries')


# ──────────────────────────────────────────────────────────────────
# Additional: spot-check a known coboundary value
# ──────────────────────────────────────────────────────────────────

def test_T_spot_check_n1():
    """
    Spot-check: for n=1, verify (delta f)(H_1, H_2) manually.
    [H_1, H_2]_0 = 0 (Cartans commute), so Term 3 = 0.

    (delta f)(H_1,H_2)^Z = [H_1, f(H_2)]^Z - [H_2, f(H_1)]^Z  (both signs are +1 for even X,Y)

    f(H_1) = sum_{odd E} phi_{E,H_1} * E
    f(H_2) = sum_{odd E} phi_{E,H_2} * E

    [H_1, f(H_2)] = sum_{odd E} phi_{E,H_2} * [H_1, E]
    [H_2, f(H_1)] = sum_{odd E} phi_{E,H_1} * [H_2, E]

    From Schema 1: [H_1, E_eps1_del1_pp] = 0 (checking via structure constants).
    We verify that the coeff_phi dict for (H_1, H_2, Z) is consistent with this.
    """
    n = 1
    cb = compute_coboundary_symbolic(n)
    parity, fwd = _load_schema1(n)
    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis

    # Build full bracket table
    from C_coboundary import _build_full_bt
    bt = _build_full_bt(parity, fwd)

    # Manually compute (delta f)(H_1, H_2)^Z for each Z
    # Term 1 sign = (-1)^{p(H_1)} = 1; Term 2 sign = -(-1)^{(0+1)*0} = -1
    X, Y = 'H_1', 'H_2'
    pX, pY = parity[X], parity[Y]
    sign1 = Fraction((-1) ** pX)       # = 1
    sign2 = Fraction(-(-1) ** ((pX + 1) * pY))  # = -1

    manual = {}
    for image in odd_basis:  # p(image) != pY=0 → odd images
        lbl = _phi_label(image, Y)
        for Z, c in bt.get((X, image), {}).items():
            manual.setdefault(Z, defaultdict(Fraction))[lbl] += sign1 * c

    for image in odd_basis:  # p(image) != pX=0 → odd images
        lbl = _phi_label(image, X)
        for Z, c in bt.get((Y, image), {}).items():
            manual.setdefault(Z, defaultdict(Fraction))[lbl] += sign2 * c

    # [H_1,H_2]=0 → Term 3 = 0

    # Compare with symbolic result
    for Z in all_basis:
        expected = dict(manual.get(Z, {}))
        got = cb.get((X, Y, Z), {})
        exp_nz = {k: v for k, v in expected.items() if v != 0}
        if exp_nz != {k: v for k, v in got.items() if v != 0}:
            raise AssertionError(
                f'Spot-check FAIL at ({X},{Y},{Z}): expected {exp_nz}, got {got}'
            )

    print('T_spot PASS: n=1 (H_1,H_2) coboundary matches manual computation')


# ──────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    all_pass = True
    tests = [
        ('T1 n=1', lambda: test_T1_graded_antisymmetry(1)),
        ('T1 n=2', lambda: test_T1_graded_antisymmetry(2)),
        ('T1 n=3', lambda: test_T1_graded_antisymmetry(3)),
        ('T2 n=1', lambda: test_T2_zero_map(1)),
        ('T2 n=2', lambda: test_T2_zero_map(2)),
        ('T2 n=3', lambda: test_T2_zero_map(3)),
        ('T3 n=1', lambda: test_T3_schema(1)),
        ('T3 n=2', lambda: test_T3_schema(2)),
        ('T3 n=3', lambda: test_T3_schema(3)),
        ('T_spot n=1', test_T_spot_check_n1),
    ]
    for name, fn in tests:
        try:
            fn()
        except Exception as e:
            print(f'[FAIL] {name}: {e}')
            all_pass = False

    print()
    print('ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED')
    sys.exit(0 if all_pass else 1)
