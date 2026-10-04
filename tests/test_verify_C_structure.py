"""Unit tests wrapping verify_C_structure."""

import pytest
from src.verify_C_structure import verify_c_structure


@pytest.mark.parametrize("n", [1, 2, 3])
def test_algebra_verification(n):
    result, asym_fails, jac_fails = verify_c_structure(n)
    assert result["status"] == "PASS"
    assert result["antisymmetry_failures"] == 0
    assert result["jacobi_failures"] == 0
