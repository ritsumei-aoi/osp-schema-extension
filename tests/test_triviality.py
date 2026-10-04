"""
test_triviality.py: Pytest verification of triviality analysis and cohomological rank properties for C(n+1).
"""

import pytest
from src.triviality_analysis import analyze_triviality_rank


@pytest.mark.parametrize("n, expected_gb_count", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_cohomological_rank_increase(n, expected_gb_count):
    res = analyze_triviality_rank(n)
    assert res["num_gb_params"] == expected_gb_count
    # The rank increase must equal the number of gb parameters,
    # proving linear independence from the coboundary space B^2.
    assert res["param_rank_increase"] == expected_gb_count
    assert not res["eval_is_coboundary"]
