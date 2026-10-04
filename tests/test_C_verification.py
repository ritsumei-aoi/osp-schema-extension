"""
Tests for Super Jacobi identity and antisymmetry verification script.
"""

from src.verify_C_structure import run_verification


def test_structure_verification():
    summary = run_verification("data")
    for alg in ["C(2)", "C(3)", "C(4)"]:
        assert alg in summary
        assert summary[alg]["status"] == "PASS"
        assert summary[alg]["antisymmetry_errors"] == 0
        assert summary[alg]["jacobi_errors"] == 0
