"""
test_C_structure.py
Unit tests for the C(n+1) structure constant generator.

Tests cover:
  1. Generator counts (even/odd/total dimensions)
  2. Parity of brackets
  3. Graded antisymmetry
  4. Known specific brackets (hand-verified)
  5. Jacobi identity (sampled)
  6. Schema conformance (structure_constants format)
"""
import pytest
from fractions import Fraction
from collections import defaultdict
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_structure_generator import (
    OscAlgebra, build_generators, basis_order,
    poly_to_basis, compute_structure_constants, build_schema1_json,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def poly_add(p1: dict, p2: dict) -> dict:
    r = defaultdict(Fraction, p1)
    for w, c in p2.items():
        r[w] += c
    return {k: v for k, v in r.items() if v != 0}


def poly_scale(p: dict, s) -> dict:
    s = Fraction(s)
    return {w: c * s for w, c in p.items() if c * s != 0}


# ---------------------------------------------------------------------------
# 1. Generator counts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('n', [1, 2, 3])
def test_generator_counts(n):
    gens, par = build_generators(OscAlgebra(n))
    basis = basis_order(n)
    odd = [b for b in basis if par[b] == 1]
    even = [b for b in basis if par[b] == 0]
    assert len(odd) == 4 * n, f'n={n}: expected {4*n} odd, got {len(odd)}'
    assert len(even) == 2 * n**2 + n + 1, f'n={n}: expected {2*n**2+n+1} even, got {len(even)}'
    assert len(basis) == 2 * n**2 + 5 * n + 1


# ---------------------------------------------------------------------------
# 2. Parity of brackets
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('n', [1, 2, 3])
def test_bracket_parity(n):
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    basis = basis_order(n)
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i >= j:
                continue
            br = alg.bracket(gens[X], par[X], gens[Y], par[Y])
            if not br:
                continue
            # Decompose and check parity of each component
            decomp = poly_to_basis(br, alg)
            expected_parity = (par[X] + par[Y]) % 2
            for Z, coeff in decomp.items():
                if coeff:
                    assert par[Z] == expected_parity, (
                        f'n={n}: parity([{X},{Y}]) wrong for Z={Z}: '
                        f'expected {expected_parity}, got {par[Z]}'
                    )


# ---------------------------------------------------------------------------
# 3. Graded antisymmetry: [X,Y} = -(-1)^{pX*pY} [Y,X}
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('n', [1, 2, 3])
def test_antisymmetry(n):
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    basis = basis_order(n)
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i >= j:
                continue
            br_XY = alg.bracket(gens[X], par[X], gens[Y], par[Y])
            br_YX = alg.bracket(gens[Y], par[Y], gens[X], par[X])
            sign = (-1) ** (par[X] * par[Y])
            # [X,Y} + sign*[Y,X} = 0
            combined = defaultdict(Fraction, br_XY)
            for w, c in br_YX.items():
                combined[w] += sign * c
            nonzero = {k: v for k, v in combined.items() if v != 0}
            assert not nonzero, f'n={n}: antisymmetry fails for [{X},{Y}]'


# ---------------------------------------------------------------------------
# 4. Known specific brackets (hand-verified in I03-1 proposal)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('n', [1, 2, 3])
def test_H1_E_eps_del1_pp(n):
    """[H_1, E_eps_del1_pp} = 2 * E_eps_del1_pp"""
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    br = alg.bracket(gens['H_1'], par['H_1'], gens['E_eps_del1_pp'], par['E_eps_del1_pp'])
    decomp = poly_to_basis(br, alg)
    assert decomp == {'E_eps_del1_pp': Fraction(2)}, f'n={n}: got {decomp}'


@pytest.mark.parametrize('n', [1, 2, 3])
def test_H1_E_eps_del1_pm_zero(n):
    """[H_1, E_eps_del1_pm} = 0"""
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    br = alg.bracket(gens['H_1'], par['H_1'], gens['E_eps_del1_pm'], par['E_eps_del1_pm'])
    assert not br, f'n={n}: expected 0, got {br}'


@pytest.mark.parametrize('n', [1, 2, 3])
def test_H1_E_2del1_p(n):
    """
    [H_1, E_2del1_p} = 2 * E_2del1_p
    H_1 = a_1^+a_1^- + b_1^+b_1^-.  E_2del1_p = (1/2)(b_1^+)^2.
    Only the b_1^+b_1^- part is relevant; eigenvalue of b_1^+b_1^- on (b_1^+)^2/2
    is 2, giving [H_1, E_2del1_p] = 2 * E_2del1_p.
    """
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    br = alg.bracket(gens['H_1'], par['H_1'], gens['E_2del1_p'], par['E_2del1_p'])
    decomp = poly_to_basis(br, alg)
    assert decomp == {'E_2del1_p': Fraction(2)}, f'n={n}: got {decomp}'


@pytest.mark.parametrize('n', [1, 2, 3])
def test_Cartans_commute(n):
    """All [H_i, H_j} = 0"""
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    cartans = [f'H_{k}' for k in range(1, n + 2)]
    for i in range(len(cartans)):
        for j in range(i + 1, len(cartans)):
            X, Y = cartans[i], cartans[j]
            br = alg.bracket(gens[X], par[X], gens[Y], par[Y])
            assert not br, f'n={n}: [{X},{Y}] != 0, got {br}'


@pytest.mark.parametrize('n', [1, 2, 3])
def test_odd_odd_anticommutator_gives_even(n):
    """[E_eps_del1_pp, E_eps_del1_mm} should be an even element (anticommutator)."""
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    X, Y = 'E_eps_del1_pp', 'E_eps_del1_mm'
    br = alg.bracket(gens[X], par[X], gens[Y], par[Y])
    if br:
        decomp = poly_to_basis(br, alg)
        for Z, c in decomp.items():
            if c:
                assert par[Z] == 0, f'n={n}: [{X},{Y}] has odd component {Z}'


@pytest.mark.parametrize('n', [1])
def test_C2_specific_anticommutator(n):
    """
    For C(2) (n=1): [E_eps_del1_pp, E_eps_del1_mm}
    = {a_1^+ b_1^+, a_1^- b_1^-}
    = a_1^+ b_1^+ a_1^- b_1^- + a_1^- b_1^- a_1^+ b_1^+
    = a_1^+ a_1^- b_1^+ b_1^- + a_1^- a_1^+ b_1^- b_1^+
    = a_1^+ a_1^- b_1^+ b_1^- + (1-a_1^+ a_1^-)(b_1^+ b_1^- - 1)... (detailed calc)
    Expected: H_1 (hand-verified below)
    """
    alg = OscAlgebra(1)
    gens, par = build_generators(alg)
    X, Y = 'E_eps_del1_pp', 'E_eps_del1_mm'
    br = alg.bracket(gens[X], par[X], gens[Y], par[Y])
    decomp = poly_to_basis(br, alg)
    # [a_1^+ b_1^+, a_1^- b_1^-}  (both odd -> anticommutator)
    # = a_1^+ b_1^+ a_1^- b_1^- + a_1^- b_1^- a_1^+ b_1^+
    # Compute directly:
    # a_1^+ b_1^+ a_1^- b_1^- = a_1^+ a_1^- b_1^+ b_1^- (bosonic/fermionic commute)
    # a_1^- b_1^- a_1^+ b_1^+ = a_1^- a_1^+ b_1^- b_1^+
    #   = (1-a_1^+a_1^-)(b_1^+b_1^- + 1)... hmm actually:
    # Sum = a_1^+a_1^- b_1^+b_1^- + (1-a_1^+a_1^-)(b_1^+b_1^- + 1)
    #     = a_1^+a_1^- b_1^+b_1^- + b_1^+b_1^- + 1 - a_1^+a_1^- b_1^+b_1^- - a_1^+a_1^-
    #     = b_1^+b_1^- + 1 - a_1^+a_1^-
    # In terms of generators: H_1 = a_1^+a_1^- + b_1^+b_1^-, H_2 = -b_1^+b_1^- - 1/2
    # b_1^+b_1^- + 1 - a_1^+a_1^- = -H_1 + 2*b_1^+b_1^- + 1 ... hmm
    # Let me directly compute: a_1^+a_1^- = H_1 - b_1^+b_1^-, b_1^+b_1^- = -H_2 - 1/2
    # b_1^+b_1^- + 1 - a_1^+a_1^- = (-H_2-1/2) + 1 - (H_1 - (-H_2-1/2))
    #   = -H_2 - 1/2 + 1 - H_1 + (-H_2-1/2) = -H_1 - 2*H_2
    # So [E_eps_del1_pp, E_eps_del1_mm} = -H_1 - 2*H_2
    # Let's verify in terms of numbers: H_1=a_1^+a_1^-+b_1^+b_1^-, H_2=-b_1^+b_1^--1/2
    # -H_1 - 2*H_2 = -(a_1^+a_1^-+b_1^+b_1^-) - 2(-b_1^+b_1^--1/2)
    #   = -a_1^+a_1^- - b_1^+b_1^- + 2*b_1^+b_1^- + 1
    #   = -a_1^+a_1^- + b_1^+b_1^- + 1 ✓
    assert 'H_1' in decomp or 'H_2' in decomp, f'Expected Cartan output, got {decomp}'
    # Verify the numeric values
    f1 = decomp.get('H_1', Fraction(0))
    f2 = decomp.get('H_2', Fraction(0))
    assert f1 == Fraction(-1), f'H_1 coeff: expected -1, got {f1}'
    assert f2 == Fraction(-2), f'H_2 coeff: expected -2, got {f2}'


# ---------------------------------------------------------------------------
# 5. Jacobi identity (sampled subset for tractability)
# ---------------------------------------------------------------------------

def jacobi_residual(alg, gens, par, X, Y, Z):
    """
    Compute [X,[Y,Z}} + (-1)^{pX(pY+pZ)} [Y,[Z,X}} + (-1)^{pZ(pX+pY)} [Z,[X,Y}}
    Returns the residual polynomial (should be zero).
    """
    pX, pY, pZ = par[X], par[Y], par[Z]
    gX, gY, gZ = gens[X], gens[Y], gens[Z]

    bYZ = alg.bracket(gY, pY, gZ, pZ)
    t1 = alg.bracket(gX, pX, bYZ, (pY + pZ) % 2)

    bZX = alg.bracket(gZ, pZ, gX, pX)
    t2 = alg.bracket(gY, pY, bZX, (pZ + pX) % 2)
    s2 = (-1) ** (pX * (pY + pZ))

    bXY = alg.bracket(gX, pX, gY, pY)
    t3 = alg.bracket(gZ, pZ, bXY, (pX + pY) % 2)
    s3 = (-1) ** (pZ * (pX + pY))

    result: dict = defaultdict(Fraction)
    for w, c in t1.items():
        result[w] += c
    for w, c in t2.items():
        result[w] += s2 * c
    for w, c in t3.items():
        result[w] += s3 * c
    return {k: v for k, v in result.items() if v != 0}


@pytest.mark.parametrize('n', [1, 2])
def test_jacobi_all_pairs(n):
    """Jacobi identity for all triples in C(n+1) for n=1,2."""
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    basis = basis_order(n)
    failures = []
    for i in range(len(basis)):
        for j in range(i + 1, len(basis)):
            for k in range(j + 1, len(basis)):
                X, Y, Z = basis[i], basis[j], basis[k]
                res = jacobi_residual(alg, gens, par, X, Y, Z)
                if res:
                    failures.append((X, Y, Z, res))
    assert not failures, f'n={n}: Jacobi fails for {len(failures)} triples; first: {failures[0]}'


@pytest.mark.parametrize('n', [3])
def test_jacobi_sampled(n):
    """Jacobi identity for a sampled set of triples in C(4) (n=3)."""
    import random
    random.seed(42)
    alg = OscAlgebra(n)
    gens, par = build_generators(alg)
    basis = basis_order(n)
    from itertools import combinations
    triples = list(combinations(range(len(basis)), 3))
    sample = random.sample(triples, min(200, len(triples)))
    failures = []
    for (i, j, k) in sample:
        X, Y, Z = basis[i], basis[j], basis[k]
        res = jacobi_residual(alg, gens, par, X, Y, Z)
        if res:
            failures.append((X, Y, Z, res))
    assert not failures, f'n={n}: Jacobi fails for {len(failures)} sampled triples; first: {failures[0]}'


# ---------------------------------------------------------------------------
# 6. Schema conformance
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('n', [1, 2, 3])
def test_schema_structure(n):
    schema = build_schema1_json(n)
    assert schema['schema_version'] == '5.0'
    assert schema['algebra']['family'] == 'C'
    assert schema['algebra']['m'] == 1
    assert schema['algebra']['n'] == n
    assert schema['algebra']['dimension']['even'] == 2 * n**2 + n + 1
    assert schema['algebra']['dimension']['odd'] == 4 * n
    assert 'kappa' in schema['central_elements']
    assert schema['central_elements']['kappa']['parity'] == 1
    assert schema['central_elements']['K']['parity'] == 0
    assert len(schema['basis']['odd']) == 4 * n
    assert len(schema['basis']['even']) == 2 * n**2 + n + 1
    for entry in schema['structure_constants']:
        assert 'X' in entry and 'Y' in entry and 'Z' in entry and 'coeff' in entry
        assert entry['sign_rule'] == 'graded'
        # coeff must be a valid rational string
        Fraction(entry['coeff'])
