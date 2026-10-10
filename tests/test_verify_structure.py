"""I04: Jacobi/anti-symmetry verification must pass for all generated data."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from verify_C_structure import verify


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_verified(n):
    ok, anti_fail, jacobi_fail, _, _ = verify(n, verbose=False)
    assert ok, f"n={n}: {anti_fail} anti-symmetry / {jacobi_fail} Jacobi failures"
