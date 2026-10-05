import os
import pytest
from src.verify_C_structure import verify_algebra


@pytest.mark.parametrize("n", [1, 2, 3])
def test_verify_structure_json(n):
    filepath = os.path.join("data", f"C_{n}_structure.json")
    assert os.path.exists(filepath)
    res = verify_algebra(filepath)
    assert res["pass"] is True
    assert res["antisymmetry_failures"] == 0
    assert res["jacobi_failures"] == 0
