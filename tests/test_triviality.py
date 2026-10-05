import pytest
from src.triviality_analysis import analyze_triviality_for_rank


@pytest.mark.parametrize("n, expected_f_dim, expected_gb_dim, expected_obstruction", [
    (1, 32, 4, 4),
    (2, 176, 8, 8),
])
def test_triviality_obstruction(n, expected_f_dim, expected_gb_dim, expected_obstruction):
    res = analyze_triviality_for_rank(n)
    assert res["f_dim"] == expected_f_dim
    assert res["gb_dim"] == expected_gb_dim
    assert res["obstruction_dim"] == expected_obstruction
    assert res["rank_constraint_matrix"] == expected_gb_dim
    assert res["trivial_gb_space_dim"] == 0
    assert res["all_plus_one_trivial"] is False
    assert res["zero_trivial"] is True
    assert res["is_unconditionally_nontrivial"] is True
