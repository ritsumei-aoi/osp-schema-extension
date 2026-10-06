import pytest

from C_triviality import analyse


@pytest.mark.parametrize("n", [1, 2])
def test_triviality_modes(n):
    r = analyse(n)
    m = r["modes"]
    # modulo the central part (and with central-valued f) every gb is trivial
    assert m["mod_K"]["gb_condition_rank"] == 0
    assert m["strict_cent"]["gb_condition_rank"] == 0
    # strict f: g -> g cannot reproduce the K-part: only gb = 0 survives
    assert m["strict"]["gb_condition_rank"] == 4 * n
    # kernel of delta on odd 1-cochains = inner odd derivations ad(g_odd), dim 4n
    assert m["mod_K"]["unknowns"] - m["mod_K"]["rank_delta"] == 4 * n
    assert all(p["trivial"] for p in m["mod_K"]["profiles"].values())
    cf = r["closed_form"]
    assert cf["oscillator_substitution_ok"]
    assert cf["mismatches_including_K"] == 0 and cf["mismatches_mod_K"] == 0
