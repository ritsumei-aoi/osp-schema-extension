"""Issue I04: the stored structure constants satisfy antisymmetry and super-Jacobi."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_common import LieSuperalgebra  # noqa: E402
from verify_C_structure import check_antisymmetry, check_jacobi, check_parity_closure  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_verify_structure(n):
    g = LieSuperalgebra.load(n)
    assert check_parity_closure(g) == []
    assert check_antisymmetry(g) == []
    count, failures = check_jacobi(g)
    assert count == len(g.labels) ** 3
    assert failures == []
