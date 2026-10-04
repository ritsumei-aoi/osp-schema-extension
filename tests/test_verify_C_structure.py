"""
test_verify_C_structure.py: Pytest wrapper for verification of anti-symmetry and Super Jacobi identity.
"""

from src.verify_C_structure import run_verification


def test_structure_verification_all_pass():
    summary = run_verification()
    for algebra, res in summary.items():
        assert res["anti_symmetry_passed"], f"{algebra} failed anti-symmetry checks: {res['failures']}"
        assert res["super_jacobi_passed"], f"{algebra} failed Super Jacobi checks: {res['failures']}"
        assert res["status"] == "PASS"
