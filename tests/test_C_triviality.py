import pytest

from C_triviality import analyse


@pytest.mark.parametrize("n", [1, 2])
def test_triviality_dichotomy(n):
    rep = analyse(n, verbose=False)
    assert rep["dim_ker_delta_odd"] == 4 * n  # only inner odd derivations
    assert rep["T1_g_valued"]["trivial_for_all_gb"]
    assert rep["T1_g_valued"]["particular_solution_residual_mismatches"] == 0
    assert rep["T2_with_central_h"]["trivial_for_all_gb"]
    # strict notion: every single gb must vanish
    conds = rep["T3_strict_no_h"]["independent_conditions_on_gb"]
    assert len(conds) == 4 * n and all(len(c) == 1 for c in conds)
    assert rep["closed_form_check_mismatches"] == 0
    for pr in rep["profiles"]:
        assert pr["T1"]["trivial"] and pr["T2"]["trivial"]
        assert pr["T3"]["trivial"] == (pr["gb_nonzero"] == 0)
