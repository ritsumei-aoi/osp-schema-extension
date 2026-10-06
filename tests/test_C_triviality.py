import pytest

from C_triviality import analyse


@pytest.mark.parametrize("n", [1, 2])
def test_triviality_conclusions(n):
    r = analyse(n)
    # Layer 3 == Layer 4 (delta f_gb) exactly, for every profile, incl. K components
    for row in r["comparison"]:
        assert row["mismatch_g"] == 0 and row["mismatch_K"] == 0
    # odd derivations are inner: ker(delta) = ad(g_odd)
    assert r["system"]["kernel_dim_g"] == r["system"]["odd_dim"] == 4 * n
    for name, res in r["profiles"].items():
        assert res["mod-K"]["solvable"] and res["strict-gK"]["solvable"]
        assert res["strict-g"]["solvable"] == (name == "zero")
    assert all(not v for v in r["negative_control"].values())
    assert r["central_formula_failures"] == 0
    assert len(r["gb_with_K_component"]) == 4 * n
