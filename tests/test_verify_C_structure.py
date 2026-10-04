"""
Unit test wrapping Super Jacobi identity and Anti-symmetry verification
"""

import pytest
from src.verify_C_structure import run_verification

def test_c_structure_verification():
    results = run_verification()
    for key, res in results.items():
        assert res["anti_symmetry"]["passed"], f"Anti-symmetry failed for {key}"
        assert res["super_jacobi"]["passed"], f"Super Jacobi failed for {key}"
