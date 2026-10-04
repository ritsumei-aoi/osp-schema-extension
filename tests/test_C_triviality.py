"""
Unit tests for triviality analysis of C(n+1) deformations.
"""

import pytest
from src.search_triviality import solve_triviality_system


@pytest.mark.parametrize("n,expected_gb_count", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_triviality_full_rank_constraints(n, expected_gb_count):
    res = solve_triviality_system(n)
    assert res["gb_params_count"] == expected_gb_count
    assert res["gb_constraints_rank"] == expected_gb_count
    assert res["all_plus_one_solvable"] is False
    assert res["all_plus_one_residual_equations"] > 0
