"""Issue I04: antisymmetry and super Jacobi identity of the Schema 1 structure constants."""
from fractions import Fraction

import pytest

import verify_C_structure as V

NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
def test_closure_and_parity(n):
    basis, parity, table, _ = V.load_structure(n)
    assert V.check_closure(basis, parity, table) == []


@pytest.mark.parametrize("n", NS)
def test_antisymmetry(n):
    basis, parity, table, _ = V.load_structure(n)
    assert V.check_antisymmetry(basis, parity, table) == []


@pytest.mark.parametrize("n", NS)
def test_super_jacobi_all_ordered_triples(n):
    basis, parity, table, _ = V.load_structure(n)
    count, failures = V.check_jacobi(basis, parity, table, all_ordered=True)
    assert count == len(basis) ** 3
    assert failures == []


def test_jacobi_detects_a_corrupted_table():
    """Sanity check that the verifier is not vacuous."""
    basis, parity, table, _ = V.load_structure(1)
    bad = {k: dict(v) for k, v in table.items()}
    bad[("E_2del1_p", "E_2del1_m")] = {"H_2": Fraction(3)}
    bad[("E_2del1_m", "E_2del1_p")] = {"H_2": Fraction(-3)}
    assert V.check_antisymmetry(basis, parity, bad) == []
    _, failures = V.check_jacobi(basis, parity, bad)
    assert failures, "corrupted bracket should violate Jacobi"
