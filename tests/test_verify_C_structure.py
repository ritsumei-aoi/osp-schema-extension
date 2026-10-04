"""
Tests for Super Jacobi identity and skew-symmetry verification on C(n+1).
"""

import pytest
from src.verify_C_structure import load_structure, verify_skew_symmetry, verify_super_jacobi


@pytest.mark.parametrize("n", [1, 2, 3])
def test_skew_symmetry_and_super_jacobi(n):
    path = f"data/C_{n}_structure.json"
    basis, parity, brackets, data = load_structure(path)

    skew_ok, skew_errs = verify_skew_symmetry(basis, parity, brackets)
    assert skew_ok, f"Skew symmetry failed for C({n+1}): {skew_errs}"

    jacobi_ok, count, jacobi_errs = verify_super_jacobi(basis, parity, brackets)
    assert jacobi_ok, f"Super Jacobi failed for C({n+1}): {jacobi_errs}"
