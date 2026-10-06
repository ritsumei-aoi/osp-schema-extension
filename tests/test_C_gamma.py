"""
Tests for C_gamma.py — Schema 2 (gamma structure) for C(n+1) = osp(2|2n).

T1: gb_label construction
T2: pairs with no a_1 in either generator → gamma = 0
T3: (odd, odd) pairs for n=1 — hand-verified entries
T4: graded antisymmetry of gamma
T5: JSON schema structure validation
"""

import sys
import os
import json
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_gamma import (
    _gb_label, gb_labels, _kappa_coeff_bracket, identify_extended,
    compute_gamma_entries, generate_schema2,
)
from C_generators import make_generators, basis_list, _pbw_index


# ──────────────────────────────────────────────────────────────────
# T1: gb_label construction
# ──────────────────────────────────────────────────────────────────

def test_T1_gb_label():
    assert _gb_label('b_1_p', 'a_1_p') == 'gb_p_1_p'
    assert _gb_label('b_1_m', 'a_1_p') == 'gb_p_1_m'
    assert _gb_label('b_2_p', 'a_1_m') == 'gb_m_2_p'
    assert _gb_label('b_3_m', 'a_1_m') == 'gb_m_3_m'

    labels_n1 = gb_labels(1)
    assert len(labels_n1) == 4
    assert labels_n1 == ['gb_p_1_p', 'gb_p_1_m', 'gb_m_1_p', 'gb_m_1_m']

    labels_n2 = gb_labels(2)
    assert len(labels_n2) == 8

    print('T1 PASS: gb_label construction')


# ──────────────────────────────────────────────────────────────────
# T2: pairs with no a_1 in either generator → gamma = 0
# ──────────────────────────────────────────────────────────────────

def _has_a1(gen_label: str, gens: dict) -> bool:
    """True iff the generator's realization contains any a_1 oscillator."""
    elem, _ = gens[gen_label]
    for word in elem:
        if any(o.startswith('a_') for o in word):
            return True
    return False


def test_T2_no_a1_pairs_zero(n: int = 1):
    gens = make_generators(n)
    pbw = _pbw_index(n)
    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis

    no_a1 = [la for la in all_basis if not _has_a1(la, gens)]

    failures = []
    for la in no_a1:
        ea, pa = gens[la]
        for lb in no_a1:
            eb, pb_val = gens[lb]
            kc = _kappa_coeff_bracket(ea, pa, eb, pb_val, pbw)
            if kc:
                failures.append((la, lb, kc))

    if failures:
        for la, lb, kc in failures[:3]:
            print(f'  FAIL: gamma({la}, {lb}) = {kc}')
        raise AssertionError(f'T2 FAIL: {len(failures)} non-zero gamma pairs with no a_1')

    print(f'T2 PASS: n={n}, {len(no_a1)} no-a_1 generators, all {len(no_a1)**2} pairs give gamma=0')


# ──────────────────────────────────────────────────────────────────
# T3: (odd, odd) pairs for n=1 — hand-verified entries
# ──────────────────────────────────────────────────────────────────

def test_T3_odd_odd_n1():
    """
    For n=1, odd basis = {E_eps1_del1_pp, E_eps1_del1_pm, E_eps1_del1_mp, E_eps1_del1_mm}.
    Notation: E_σs = E_eps1_del1_{σ}{s} where σ,s ∈ {p,m}.

    From the derivation (§3' Rev.2):
      gamma(E_σs, E_σ's') = -gb_{σ',1,s}·E_eps1_del1_{σ,s'} - gb_{σ,1,s'}·E_eps1_del1_{σ',s}

    Hand-computed spot checks for n=1:
      gamma(E_pp, E_pm): σ=p,s=p, σ'=p,s'=m
        = -gb_{p,1,p}·E_eps1_del1_{p,m} - gb_{p,1,m}·E_eps1_del1_{p,p}
        = -gb_p_1_p · E_pm - gb_p_1_m · E_pp
      gamma(E_pp, E_mp): σ=p,s=p, σ'=m,s'=p
        = -gb_{m,1,p}·E_eps1_del1_{p,p} - gb_{p,1,p}·E_eps1_del1_{m,p}
        = -gb_m_1_p · E_pp - gb_p_1_p · E_mp
      gamma(E_pm, E_mp): σ=p,s=m, σ'=m,s'=p
        = -gb_{m,1,m}·E_eps1_del1_{p,p} - gb_{p,1,p}·E_eps1_del1_{m,m}
        = -gb_m_1_m · E_pp - gb_p_1_p · E_mm

    Also, graded antisymmetry (both odd):
      gamma(E_b, E_a) = +gamma(E_a, E_b) (since p(odd)*p(odd)=1, sign = -(-1)^1 = +1)
    """
    n = 1
    gens = make_generators(n)
    pbw = _pbw_index(n)
    entries = compute_gamma_entries(n)

    # Build lookup: (a, b, c) -> coeff_gb
    gamma_table = {}
    for e in entries:
        gamma_table[(e['a'], e['b'], e['c'])] = e['coeff_gb']

    def coeff(a, b, c, gb):
        return gamma_table.get((a, b, c), {}).get(gb, '0')

    # Check gamma(E_pp, E_pm)
    a, b = 'E_eps1_del1_pp', 'E_eps1_del1_pm'
    assert coeff(a, b, 'E_eps1_del1_pm', 'gb_p_1_p') == '-1', \
        f'Expected gamma({a},{b})^E_pm coeff gb_p_1_p = -1, got {coeff(a,b,"E_eps1_del1_pm","gb_p_1_p")}'
    assert coeff(a, b, 'E_eps1_del1_pp', 'gb_p_1_m') == '-1', \
        f'Expected gamma({a},{b})^E_pp coeff gb_p_1_m = -1, got {coeff(a,b,"E_eps1_del1_pp","gb_p_1_m")}'

    # Check gamma(E_pp, E_mp)
    a, b = 'E_eps1_del1_pp', 'E_eps1_del1_mp'
    assert coeff(a, b, 'E_eps1_del1_pp', 'gb_m_1_p') == '-1', \
        f'Expected gamma({a},{b})^E_pp coeff gb_m_1_p = -1'
    assert coeff(a, b, 'E_eps1_del1_mp', 'gb_p_1_p') == '-1', \
        f'Expected gamma({a},{b})^E_mp coeff gb_p_1_p = -1'

    # Check gamma(E_pm, E_mp)
    a, b = 'E_eps1_del1_pm', 'E_eps1_del1_mp'
    assert coeff(a, b, 'E_eps1_del1_pp', 'gb_m_1_m') == '-1', \
        f'Expected gamma({a},{b})^E_pp coeff gb_m_1_m = -1'
    assert coeff(a, b, 'E_eps1_del1_mm', 'gb_p_1_p') == '-1', \
        f'Expected gamma({a},{b})^E_mm coeff gb_p_1_p = -1'

    # Self-pairing: gamma(E_pp, E_pp): σ=σ'=p, s=s'=p
    # = -gb_{p,1,p}·E_pp - gb_{p,1,p}·E_pp = -2·gb_p_1_p · E_pp
    a = b = 'E_eps1_del1_pp'
    val = coeff(a, b, 'E_eps1_del1_pp', 'gb_p_1_p')
    assert val == '-2', f'Expected gamma(E_pp,E_pp)^E_pp coeff gb_p_1_p = -2, got {val}'

    print('T3 PASS: n=1 odd-odd gamma entries match hand computation')


# ──────────────────────────────────────────────────────────────────
# T4: graded antisymmetry of gamma
# ──────────────────────────────────────────────────────────────────

def test_T4_graded_antisymmetry(n: int = 1):
    """
    gamma(G_a, G_b) = -(-1)^{pa*pb} * gamma(G_b, G_a)
    i.e., for all a,b,c:
      gamma^c_{ab} + (-1)^{pa*pb} * gamma^c_{ba} = 0
    """
    gens = make_generators(n)
    odd_basis, even_basis = basis_list(n)
    all_basis = even_basis + odd_basis
    parity = {la: gens[la][1] for la in all_basis}

    entries = compute_gamma_entries(n)

    # Build table: (a, b, c, gb_label) -> Fraction
    table: dict = {}
    for e in entries:
        for gb, cstr in e['coeff_gb'].items():
            key = (e['a'], e['b'], e['c'], gb)
            if '/' in cstr:
                num, den = cstr.split('/')
                table[key] = Fraction(int(num), int(den))
            else:
                table[key] = Fraction(int(cstr))

    failures = []
    for la in all_basis:
        for lb in all_basis:
            sign = (-1) ** (parity[la] * parity[lb])
            # Collect all (c, gb) that appear
            pairs_ab = {(c, gb) for (a, b, c, gb) in table if a == la and b == lb}
            pairs_ba = {(c, gb) for (a, b, c, gb) in table if a == lb and b == la}
            all_pairs = pairs_ab | pairs_ba

            for (c, gb) in all_pairs:
                c_ab = table.get((la, lb, c, gb), Fraction(0))
                c_ba = table.get((lb, la, c, gb), Fraction(0))
                residual = c_ab + sign * c_ba
                if residual != 0:
                    failures.append((la, lb, c, gb, residual))

    if failures:
        for la, lb, c, gb, r in failures[:5]:
            print(f'  FAIL: gamma({la},{lb})^{c}[{gb}] antisymm residual = {r}')
        raise AssertionError(f'T4 FAIL: {len(failures)} antisymmetry violations for n={n}')

    print(f'T4 PASS: n={n} graded antisymmetry holds for all gamma entries')


# ──────────────────────────────────────────────────────────────────
# T5: JSON schema structure validation
# ──────────────────────────────────────────────────────────────────

def test_T5_schema_structure(n: int = 1):
    schema = generate_schema2(n)

    assert schema['schema_version'] == '5.0'
    assert schema['schema_layer'] == 2
    assert schema['index_convention'] == 'upper_c'
    assert schema['algebra']['family'] == 'C'
    assert schema['algebra']['n'] == n
    assert schema['gram_matrix'] is None

    gb = schema['deformation_parameters']['gb_matrix']
    assert gb['rows'] == ['a_1_p', 'a_1_m']
    assert len(gb['cols']) == 2 * n
    assert schema['deformation_parameters']['count'] == 4 * n

    gamma = schema['gamma_cocycle']
    assert isinstance(gamma, list)
    assert len(gamma) > 0

    # Each entry has correct keys and coeff_gb is non-empty
    for e in gamma:
        assert 'a' in e and 'b' in e and 'c' in e and 'coeff_gb' in e
        assert isinstance(e['coeff_gb'], dict)
        assert len(e['coeff_gb']) > 0
        for gb_key, cstr in e['coeff_gb'].items():
            assert gb_key.startswith('gb_')
            # Coefficient is a valid fraction string
            if '/' in cstr:
                num, den = cstr.split('/')
                _ = Fraction(int(num), int(den))
            else:
                _ = Fraction(int(cstr))

    print(f'T5 PASS: n={n} Schema 2 JSON structure valid, {len(gamma)} gamma entries')


# ──────────────────────────────────────────────────────────────────
# Additional: run T2 and T4 for n=2,3
# ──────────────────────────────────────────────────────────────────

def test_T2_n2():
    test_T2_no_a1_pairs_zero(n=2)


def test_T2_n3():
    test_T2_no_a1_pairs_zero(n=3)


def test_T4_n2():
    test_T4_graded_antisymmetry(n=2)


def test_T4_n3():
    test_T4_graded_antisymmetry(n=3)


def test_T5_n2():
    test_T5_schema_structure(n=2)


def test_T5_n3():
    test_T5_schema_structure(n=3)


# ──────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    all_pass = True
    tests = [
        ('T1', test_T1_gb_label),
        ('T2 n=1', lambda: test_T2_no_a1_pairs_zero(1)),
        ('T2 n=2', test_T2_n2),
        ('T2 n=3', test_T2_n3),
        ('T3', test_T3_odd_odd_n1),
        ('T4 n=1', lambda: test_T4_graded_antisymmetry(1)),
        ('T4 n=2', test_T4_n2),
        ('T4 n=3', test_T4_n3),
        ('T5 n=1', lambda: test_T5_schema_structure(1)),
        ('T5 n=2', test_T5_n2),
        ('T5 n=3', test_T5_n3),
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
