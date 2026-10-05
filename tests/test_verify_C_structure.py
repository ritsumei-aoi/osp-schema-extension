"""
Unit test for Super Jacobi identity and anti-symmetry verification script.
"""

from src.verify_C_structure import verify_structure, verify_all

def test_verify_all_structures_pass():
    all_passed, results = verify_all()
    assert all_passed
    assert len(results) == 3
    for res in results:
        assert res["antisymmetry_pass"]
        assert res["jacobi_pass"]
        assert res["antisymmetry_failure_count"] == 0
        assert res["jacobi_failure_count"] == 0
