"""
Unit tests for C_generators.py: parity, generator counts, and structure constant consistency.
"""

import json
import os
import sys
import pytest
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import (
    build_basis, build_parity, build_schema1, bracket,
    number_op_to_cartans, osc_product_to_gens
)


@pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_basis_dimensions(n, expected_even, expected_odd, expected_total):
    even, odd = build_basis(n)
    assert len(even) == expected_even, f"n={n}: even dim {len(even)} != {expected_even}"
    assert len(odd) == expected_odd, f"n={n}: odd dim {len(odd)} != {expected_odd}"
    assert len(even) + len(odd) == expected_total


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_assignment(n):
    even, odd = build_basis(n)
    parity = build_parity(even, odd)
    for g in even:
        assert parity[g] == 0, f"Even generator {g} has wrong parity"
    for g in odd:
        assert parity[g] == 1, f"Odd generator {g} has wrong parity"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_labels_unique(n):
    even, odd = build_basis(n)
    all_labels = even + odd
    assert len(all_labels) == len(set(all_labels)), "Duplicate generator labels"


def test_number_op_cartans_n1():
    """n_1 = -H_2 - 1/2 for n=1."""
    gens, sc = number_op_to_cartans(1, 1, False)
    assert gens == {"H_2": Fraction(-1)}
    assert sc == Fraction(-1, 2)


def test_number_op_cartans_fermionic_n1():
    """n_a = H_1 + H_2 + 1/2 for n=1."""
    gens, sc = number_op_to_cartans(None, 1, True)
    assert gens == {"H_1": Fraction(1), "H_2": Fraction(1)}
    assert sc == Fraction(1, 2)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_cartan_diagonal_action(n):
    """[H_k, X] = eigenvalue * X for all root generators X."""
    even, odd = build_basis(n)
    parity = build_parity(even, odd)
    cartans = [g for g in even if g.startswith("H_")]
    roots = [g for g in even + odd if not g.startswith("H_")]

    for H in cartans:
        for X in roots:
            result = bracket(H, X, n, parity)
            # Result should be proportional to X (diagonal action)
            for Z, c in result.items():
                assert Z == X, f"[{H}, {X}] gave non-diagonal term {Z}"


def test_cartan_commute_n1():
    """[H_k, H_l] = 0 for all k, l."""
    n = 1
    even, odd = build_basis(n)
    parity = build_parity(even, odd)
    cartans = [g for g in even if g.startswith("H_")]
    for i, H1 in enumerate(cartans):
        for j, H2 in enumerate(cartans):
            if j <= i:
                continue
            result = bracket(H1, H2, n, parity)
            assert result == {}, f"[{H1}, {H2}] != 0: {result}"


def test_known_bracket_eps_del_pp_mm_n1():
    """[E_eps1_del1_pp, E_eps1_del1_mm] = -H_1 - 2*H_2 for n=1."""
    n = 1
    even, odd = build_basis(n)
    parity = build_parity(even, odd)
    result = bracket("E_eps1_del1_pp", "E_eps1_del1_mm", n, parity)
    assert result.get("H_1") == Fraction(-1), f"H_1 coeff wrong: {result}"
    assert result.get("H_2") == Fraction(-2), f"H_2 coeff wrong: {result}"
    assert len(result) == 2, f"Extra terms: {result}"


def test_known_bracket_E2del_n1():
    """[E_2del1_p, E_2del1_m] = 4*H_2 for n=1 (direct computation verified)."""
    n = 1
    even, odd = build_basis(n)
    parity = build_parity(even, odd)
    result = bracket("E_2del1_p", "E_2del1_m", n, parity)
    assert result.get("H_2") == Fraction(4), f"H_2 coeff wrong: {result}"


def test_known_cartan_eigenvalues_n1():
    """[H_1, E_eps1_del1_pp] = 2 (eps+delta_1 eigenvalue wrt H_1)."""
    n = 1
    even, odd = build_basis(n)
    parity = build_parity(even, odd)
    result = bracket("H_1", "E_eps1_del1_pp", n, parity)
    assert result == {"E_eps1_del1_pp": Fraction(2)}, f"Wrong: {result}"

    result2 = bracket("H_2", "E_eps1_del1_pp", n, parity)
    assert result2 == {"E_eps1_del1_pp": Fraction(-1)}, f"Wrong: {result2}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constant_count(n):
    """Structure constants are non-empty for all n."""
    even, odd = build_basis(n)
    parity = build_parity(even, odd)
    from C_generators import compute_structure_constants
    sc = compute_structure_constants(n, even, odd, parity)
    assert len(sc) > 0, f"No structure constants for n={n}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_schema_structure(n):
    """Schema 1 JSON has all required top-level keys."""
    fname = f"data/C_{n}_structure.json"
    if not os.path.exists(fname):
        pytest.skip(f"{fname} not found")
    with open(fname) as f:
        d = json.load(f)
    required = ["schema_version", "algebra", "central_elements", "oscillator_generators",
                "oscillator_relations", "basis", "parity", "generator_realization",
                "structure_constants", "metadata"]
    for key in required:
        assert key in d, f"Missing key {key} in {fname}"
    assert d["algebra"]["family"] == "C"
    assert d["algebra"]["m"] == 1
    assert d["algebra"]["n"] == n
