import pytest

from src.analyze_C_triviality import analyze_rank


@pytest.mark.parametrize(("n", "expected_pairs"), [(1, 10), (2, 42), (3, 90)])
def test_k_obstruction_proves_only_zero_parameters_trivial(n, expected_pairs):
    report = analyze_rank(n)
    assert report["gb_parameter_count"] == 4 * n
    assert report["K_obstructed_pair_count"] == expected_pairs
    assert report["K_obstruction_rank"] == 4 * n
    assert report["K_obstruction_nullity"] == 0
    assert not report["coboundary_has_K_output"]
    assert report["all_positive_is_nontrivial"]
    assert report["zero_assignment_gamma_is_zero"]
    assert report["zero_assignment_is_trivial"]
    assert len(report["witnesses"]) == 4 * n
