"""
Tests for C_generators.py: parity, dimension counts, known brackets, Jacobi identity.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from fractions import Fraction
from C_generators import (
    build_algebra, build_word_map, graded_bracket, decompose, generate_schema
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def get_bracket_dict(n):
    """Return {(X, Y): [(Z, coeff), ...]} for all non-zero brackets."""
    basis_odd, basis_even, parity, gen_poly, osc_idx = build_algebra(n)
    all_basis = basis_odd + basis_even
    word_map = build_word_map(gen_poly, basis_odd, basis_even)
    result = {}
    for i in range(len(all_basis)):
        for j in range(i + 1, len(all_basis)):
            X, Y = all_basis[i], all_basis[j]
            px, py = parity[X], parity[Y]
            br = graded_bracket(gen_poly[X], gen_poly[Y], px, py, osc_idx, n)
            if br:
                terms = decompose(br, gen_poly, basis_odd, basis_even, n, word_map)
                if terms:
                    result[(X, Y)] = dict(terms)
    return result, parity


def bracket_coeff(bdict, parity_map, X, Y, Z):
    """
    Return coefficient of Z in [X,Y}.
    bdict stores upper-triangle (PBW order i<j); applies graded antisymmetry for (Y,X).
    """
    if (X, Y) in bdict:
        return bdict[(X, Y)].get(Z, Fraction(0))
    if (Y, X) in bdict:
        # [X, Y} = -(-1)^{p(X)*p(Y)} [Y, X}
        sign = Fraction(-(-1) ** (parity_map[X] * parity_map[Y]))
        return sign * bdict[(Y, X)].get(Z, Fraction(0))
    return Fraction(0)


# ─── Dimension tests ─────────────────────────────────────────────────────────

@pytest.mark.parametrize('n,even_exp,odd_exp,total_exp', [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_dimension_counts(n, even_exp, odd_exp, total_exp):
    basis_odd, basis_even, parity, gen_poly, osc_idx = build_algebra(n)
    assert len(basis_odd) == odd_exp, f"n={n}: odd count"
    assert len(basis_even) == even_exp, f"n={n}: even count"
    assert len(basis_odd) + len(basis_even) == total_exp, f"n={n}: total count"


# ─── Parity tests ────────────────────────────────────────────────────────────

@pytest.mark.parametrize('n', [1, 2, 3])
def test_all_generators_have_parity(n):
    basis_odd, basis_even, parity, gen_poly, osc_idx = build_algebra(n)
    for lbl in basis_odd:
        assert parity[lbl] == 1, f"{lbl} should be odd"
    for lbl in basis_even:
        assert parity[lbl] == 0, f"{lbl} should be even"


@pytest.mark.parametrize('n', [1, 2, 3])
def test_bracket_parity_closure(n):
    """[X, Y} must have parity p(X) + p(Y) mod 2."""
    bdict, parity = get_bracket_dict(n)
    basis_odd, basis_even, _, gen_poly, osc_idx = build_algebra(n)
    all_basis = basis_odd + basis_even
    for (X, Y), terms in bdict.items():
        expected_parity = (parity[X] + parity[Y]) % 2
        for Z in terms:
            assert parity[Z] == expected_parity, (
                f"n={n}: [{X},{Y}] -> {Z} has parity {parity[Z]}, "
                f"expected {expected_parity}"
            )


# ─── Known bracket tests ──────────────────────────────────────────────────────

@pytest.mark.parametrize('n', [1, 2, 3])
def test_H1_acts_on_E_eps1_del1_pp(n):
    """[H_1, E_eps1_del1_pp] = 2 * E_eps1_del1_pp (root eigenvalue)."""
    bdict, parity = get_bracket_dict(n)
    c = bracket_coeff(bdict, parity, 'H_1', 'E_eps1_del1_pp', 'E_eps1_del1_pp')
    assert c == Fraction(2), f"n={n}: [H_1, E_eps1_del1_pp] coefficient = {c}, expected 2"


@pytest.mark.parametrize('n', [1, 2, 3])
def test_E_eps1_del1_pp_mp_anticommutator(n):
    """{E_eps1_del1_pp, E_eps1_del1_mp} = 2 * E_2del1_p."""
    bdict, parity = get_bracket_dict(n)
    c = bracket_coeff(bdict, parity, 'E_eps1_del1_pp', 'E_eps1_del1_mp', 'E_2del1_p')
    assert c == Fraction(2), (
        f"n={n}: {{E_eps1_del1_pp, E_eps1_del1_mp}} -> E_2del1_p = {c}, expected 2"
    )


@pytest.mark.parametrize('n', [1, 2, 3])
def test_E_eps1_del1_pm_mm_anticommutator(n):
    """{E_eps1_del1_pm, E_eps1_del1_mm} = 2 * E_2del1_m."""
    bdict, parity = get_bracket_dict(n)
    c = bracket_coeff(bdict, parity, 'E_eps1_del1_pm', 'E_eps1_del1_mm', 'E_2del1_m')
    assert c == Fraction(2), (
        f"n={n}: {{E_eps1_del1_pm, E_eps1_del1_mm}} -> E_2del1_m = {c}, expected 2"
    )


@pytest.mark.parametrize('n', [1, 2, 3])
def test_Cartan_self_bracket_zero(n):
    """[H_k, H_l] = 0 for all k, l (Cartan generators commute)."""
    bdict, _ = get_bracket_dict(n)
    for k in range(1, n + 2):
        for l in range(k + 1, n + 2):
            Hk, Hl = f'H_{k}', f'H_{l}'
            assert (Hk, Hl) not in bdict, f"n={n}: [{Hk},{Hl}] should be 0"


@pytest.mark.parametrize('n', [1, 2, 3])
def test_schema_dimension_matches(n):
    """Schema algebra.dimension matches basis lengths."""
    schema = generate_schema(n)
    dim = schema['algebra']['dimension']
    basis_odd = schema['basis']['odd']
    basis_even = schema['basis']['even']
    assert len(basis_odd) == dim['odd'], f"n={n}: odd mismatch"
    assert len(basis_even) == dim['even'], f"n={n}: even mismatch"
    assert len(basis_odd) + len(basis_even) == dim['total'], f"n={n}: total mismatch"


@pytest.mark.parametrize('n', [1, 2, 3])
def test_structure_constants_parity(n):
    """Every structure constant entry has consistent Z-parity."""
    schema = generate_schema(n)
    parity = schema['parity']
    for entry in schema['structure_constants']:
        X, Y, Z = entry['X'], entry['Y'], entry['Z']
        expected = (parity[X] + parity[Y]) % 2
        assert parity[Z] == expected, (
            f"n={n}: [{X},{Y}] -> {Z} parity mismatch"
        )


# ─── Jacobi identity test ─────────────────────────────────────────────────────

def _full_bracket(lbl_X, lbl_Y, gen_poly, parity, basis_odd, basis_even, osc_idx, n, word_map):
    """Compute [X, Y} returning {Z_lbl: Fraction} (uses both orderings)."""
    px, py = parity[lbl_X], parity[lbl_Y]
    br = graded_bracket(gen_poly[lbl_X], gen_poly[lbl_Y], px, py, osc_idx, n)
    if not br:
        return {}
    return dict(decompose(br, gen_poly, basis_odd, basis_even, n, word_map))


def jacobi_term(A, B, C, gen_poly, parity, basis_odd, basis_even, osc_idx, n, word_map):
    """
    Compute one Jacobi term: [A, [B, C}}.
    Returns {Z: Fraction}.
    """
    inner = _full_bracket(B, C, gen_poly, parity, basis_odd, basis_even, osc_idx, n, word_map)
    # Also need [C, B} = -(-1)^{pb*pc} [B,C}
    pb, pc = parity[B], parity[C]
    # [B, C} is stored in inner; [C, B} = -(-1)^{pb*pc} [B, C}
    # But we already have [B, C} for the specific ordering – we computed the bracket directly.
    # For Jacobi we need [A, [B, C}] = sum_Z c_Z [A, Z]
    result = {}
    pa = parity[A]
    for Z, cz in inner.items():
        pz = parity[Z]
        # [A, Z}: compute it
        # Need the bracket in canonical (smaller PBW index first) order
        basis_all = basis_odd + basis_even
        idx_A = basis_all.index(A)
        idx_Z = basis_all.index(Z)
        if idx_A < idx_Z:
            br_az = _full_bracket(A, Z, gen_poly, parity, basis_odd, basis_even, osc_idx, n, word_map)
            sign = Fraction(1)
        else:
            br_az = _full_bracket(Z, A, gen_poly, parity, basis_odd, basis_even, osc_idx, n, word_map)
            # [A, Z} = -(-1)^{pa*pz} [Z, A}
            sign = Fraction(-(-1) ** (pa * pz))
        for W, cw in br_az.items():
            result[W] = result.get(W, Fraction(0)) + cz * sign * cw
    return {w: v for w, v in result.items() if v != 0}


@pytest.mark.parametrize('n', [1, 2, 3])
def test_jacobi_identity_sample(n):
    """
    Check the graded Jacobi identity for a sample of triples.
    Jacobi: [A,[B,C}} + (-1)^{pa(pb+pc)} [B,[C,A}} + (-1)^{pc(pa+pb)} [C,[A,B}} = 0
    """
    basis_odd, basis_even, parity, gen_poly, osc_idx = build_algebra(n)
    all_basis = basis_odd + basis_even
    word_map = build_word_map(gen_poly, basis_odd, basis_even)

    # Select a fixed sample of triples
    sample_triples = [
        (all_basis[0], all_basis[1], all_basis[len(basis_odd)]),      # odd,odd,even
        (all_basis[0], all_basis[len(basis_odd)], all_basis[len(basis_odd) + 1]),  # odd,even,even
        (all_basis[len(basis_odd)], all_basis[len(basis_odd) + 1], all_basis[len(basis_odd) + 2]),  # even,even,even
    ]
    if n >= 2:
        sample_triples.append((all_basis[0], all_basis[2], all_basis[len(basis_odd) + 1]))

    def jacobi_sum(A, B, C):
        pa, pb, pc = parity[A], parity[B], parity[C]
        t1 = jacobi_term(A, B, C, gen_poly, parity, basis_odd, basis_even, osc_idx, n, word_map)
        t2 = jacobi_term(B, C, A, gen_poly, parity, basis_odd, basis_even, osc_idx, n, word_map)
        t3 = jacobi_term(C, A, B, gen_poly, parity, basis_odd, basis_even, osc_idx, n, word_map)
        s2 = Fraction((-1) ** (pa * (pb + pc)))
        s3 = Fraction((-1) ** (pc * (pa + pb)))
        total = {}
        for d, sign in [(t1, Fraction(1)), (t2, s2), (t3, s3)]:
            for w, v in d.items():
                total[w] = total.get(w, Fraction(0)) + sign * v
        return {w: v for w, v in total.items() if v != 0}

    for A, B, C in sample_triples:
        jac = jacobi_sum(A, B, C)
        assert not jac, (
            f"n={n}: Jacobi identity failed for ({A},{B},{C}): {jac}"
        )
