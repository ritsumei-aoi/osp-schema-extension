"""
Unit Tests for C(n+1) Triviality Condition Analysis (Issue I08-1)
Validates the comparison and cohomological analysis routines between Layer 3 and Layer 4.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.compare_C_triviality import compare_layers_3_and_4, solve_parametric_triviality

@pytest.mark.parametrize("n", [1, 2, 3])
def test_layer3_vs_layer4_comparison(n):
    res = compare_layers_3_and_4(n)
    assert res["total_gamma_brackets"] > 0
    assert res["total_delta_f_brackets"] > 0
    assert res["common_triples_count"] == res["total_gamma_brackets"]
    assert res["common_triples_count"] == res["total_delta_f_brackets"]
    assert res["only_gamma_count"] == 0
    assert res["only_delta_f_count"] == 0

@pytest.mark.parametrize("n", [1, 2])
def test_triviality_condition_exact_system(n):
    res = solve_parametric_triviality(n)
    assert res["is_unconditionally_trivial"] is True
    assert res["independent_gb_constraints"] == 0
    assert res["rank_M_phi"] + res["dim_ker_delta"] == res["n_phi"]
