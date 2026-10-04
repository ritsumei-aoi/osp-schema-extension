import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.analyze_triviality import analyze_triviality_for_n

@pytest.mark.parametrize("n", [1, 2, 3])
def test_triviality_analysis(n):
    res = analyze_triviality_for_n(n)
    # Uniform assignment (all gb=1) must be non-trivial
    assert res["is_trivial_ones"] is False
    assert res["fit_err_ones"] > 1e-3
    # Full rank of obstruction matrix means arbitrary non-zero gb is non-trivial
    assert res["is_always_trivial"] is False
