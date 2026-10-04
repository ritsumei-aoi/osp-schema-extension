from pathlib import Path

import pytest

from src.analyze_C_triviality import analyze_rank


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_kappa_obstruction_is_injective_and_coboundary_has_no_k(n):
    result = analyze_rank(ROOT / "data", n)
    assert result["kappa_obstruction_rank"] == result["parameter_count"] == 4 * n
    assert result["isolated_parameter_count"] == 4 * n
    assert len({equation["parameter"] for equation in result["isolated_equations"]}) == 4 * n
    assert result["all_plus_kappa_support_size"] > 0
    assert result["sample_kappa_coefficient"] == "-1"
    assert not result["sample_has_coboundary_k_component"]
    assert not result["coboundary_has_any_k_component"]
    assert result["zero_assignment_trivial"]
