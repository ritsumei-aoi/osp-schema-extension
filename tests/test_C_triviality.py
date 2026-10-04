"""
Unit tests for triviality analysis of C(n+1).
"""

import pytest
from src.C_triviality_analysis import analyze_triviality


@pytest.mark.parametrize("n,expected_constraint_count", [
    (1, 4),
    (2, 8),
])
def test_triviality_constraints(n, expected_constraint_count):
    res = analyze_triviality(n)
    assert len(res["independent_constraints"]) == expected_constraint_count
    assert res["all_plus_one_solvable"] is False
    assert res["all_plus_one_obstructions"] > 0
