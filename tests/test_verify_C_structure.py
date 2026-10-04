import pytest
from src.verify_C_structure import verify_all


def test_structure_verification_all():
    results = verify_all("data")
    assert len(results) == 3
    for res in results:
        assert res["status"] == "PASS"
        assert res["antisymmetry_failures"] == 0
        assert res["jacobi_failures"] == 0
