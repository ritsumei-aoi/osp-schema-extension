"""
Unit tests for triviality condition analysis on C(n+1) across n=1, 2, 3.
"""

import pytest
from src.analyze_triviality import analyze_triviality_for_n


@pytest.mark.parametrize("n, expected_gb_count", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_triviality_obstruction_analysis(n, expected_gb_count):
    res = analyze_triviality_for_n(n)
    assert res["n_gb"] == expected_gb_count
    assert res["obstruction_count"] == expected_gb_count
    assert res["is_all_ones_trivial"] is False
    for param, status in res["single_param_results"].items():
        assert status == "NON-TRIVIAL"
