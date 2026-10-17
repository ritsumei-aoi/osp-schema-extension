"""
Unit tests for triviality analysis of C(n+1).
Verifies cohomology ranks and triviality: gamma(gb) is a coboundary
for all parameter values across C(2), C(3), C(4).
"""

import pytest
from src.C_triviality_analysis import run_triviality_analysis


@pytest.mark.parametrize("n, expected_params, expected_rank_cob", [
    (1, 4, 28),
    (2, 8, 168),
    (3, 12, 516)
])
def test_triviality_cohomology_ranks(n, expected_params, expected_rank_cob):
    res = run_triviality_analysis(n)
    assert res["num_params"] == expected_params
    assert res["rank_cob"] == expected_rank_cob
    assert res["dim_der"] == 4 * n
    assert res["rank_aug"] == expected_rank_cob  # Augmented rank equals coboundary rank
    assert res["diff"] == 0                     # No obstruction: diff = 0
    assert res["is_trivial_for_all"] is True    # Trivial for all parameter values
