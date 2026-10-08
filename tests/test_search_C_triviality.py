import pytest

from src.search_C_triviality import compare_rank


@pytest.mark.parametrize(("n", "obstruction_rank"), [(1, 4), (2, 8), (3, 12)])
def test_scalar_kappa_obstruction_has_full_parameter_rank(n, obstruction_rank):
    result = compare_rank("data", n)
    assert result["scalar_obstruction_matrix_rank"] == obstruction_rank
    assert result["kernel_dimension"] == 0
    assert result["all_plus_scalar_obstructed"]
    assert result["all_plus_scalar_obstructions"]
    assert result["zero_assignment_trivial"]
    assert not result["coboundary_has_scalar_K"]
