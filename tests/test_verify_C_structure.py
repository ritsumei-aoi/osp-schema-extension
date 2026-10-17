"""
Test running verify_C_structure on generated JSON files.
"""

import pytest
from src.verify_C_structure import verify_c_structure


@pytest.mark.parametrize("n", [1, 2, 3])
def test_verify_c_structure_full(n):
    res = verify_c_structure(n)
    assert res["antisymm_pass"] is True, f"Anti-symmetry check failed for n={n}"
    assert len(res["antisymm_failures"]) == 0
    assert res["jacobi_pass"] is True, f"Super Jacobi check failed for n={n}"
    assert len(res["jacobi_failures"]) == 0
