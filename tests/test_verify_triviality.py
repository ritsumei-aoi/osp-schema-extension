"""
Unit tests for deformation triviality analysis and verification.
"""

import pytest
from src.verify_triviality import analyze_deformation_cohomology


@pytest.mark.parametrize("n, expected_dim, expected_map_dim, expected_cb_rank, expected_gb_count", [
    (1, 8, 32, 28, 4),
    (2, 19, 176, 168, 8),
    (3, 34, 528, 516, 12),
])
def test_cohomology_dimensions(n, expected_dim, expected_map_dim, expected_cb_rank, expected_gb_count):
    res = analyze_deformation_cohomology(n)
    assert res["total_dim"] == expected_dim
    assert res["odd_maps_dim"] == expected_map_dim
    assert res["coboundary_rank"] == expected_cb_rank
    assert res["num_gb_parameters"] == expected_gb_count
    assert res["derivation_kernel_dim"] == res["odd_maps_dim"] - res["coboundary_rank"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_triviality_iff_gb_zero(n):
    res = analyze_deformation_cohomology(n)
    # The evaluated all_plus_one deformation is non-trivial
    assert res["evaluated_is_trivial"] is False
    # The deformation space intersects the coboundary space only at 0
    assert res["added_rank_by_gb"] == res["num_gb_parameters"]
    assert res["trivial_only_at_zero"] is True
