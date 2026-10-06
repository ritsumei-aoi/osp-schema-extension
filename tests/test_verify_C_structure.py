import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from verify_C_structure import verify  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_antisymmetry_and_jacobi(n):
    r = verify(n)
    assert r["antisym_failures"] == [] and r["jacobi_failures"] == []
