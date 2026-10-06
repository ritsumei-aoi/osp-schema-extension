import os
import random
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import C_coboundary as B  # noqa: E402
import C_evaluate as E  # noqa: E402
import C_gamma as CG  # noqa: E402
import C_triviality as T  # noqa: E402

NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("profile", E.PROFILES)
def test_extended_f_layers_coincide(n, profile):
    assert T.compare(n, profile)["coincide"]


@pytest.mark.parametrize("n", NS)
def test_strict_f_discrepancy_is_exactly_the_K_component(n):
    r = T.compare(n, "all_plus", strict=True)
    assert not r["coincide"]
    assert r["only_L4"] == [] and r["differ"] == []
    assert r["only_L3"] and all(k[2] == "K" for k in r["only_L3"])


@pytest.mark.parametrize("n", NS)
def test_K_obstruction_has_full_rank(n):
    rank, npar, _, wit = T.K_obstruction(n)
    assert rank == npar == 4 * n and len(wit) == 4 * n


@pytest.mark.parametrize("n", [1, 2])
def test_trivial_subspace_dimensions(n):
    strict, *_ = B.trivial_subspace(n, False)
    ext, *_ = B.trivial_subspace(n, True)
    gpart, *_ = B.trivial_subspace(n, False, gamma_K=False)
    assert strict["trivial_gb_dim"] == 0
    assert ext["trivial_gb_dim"] == gpart["trivial_gb_dim"] == 4 * n
    assert ext["num_phi"] - ext["rank_delta"] == 4 * n  # odd derivations = ad(odd)


@pytest.mark.parametrize("n", NS)
def test_closed_form_f(n):
    for seed in range(3):
        rnd = random.Random(seed)
        gb = dict((k, rnd.randint(-3, 3)) for k in CG.gb_keys(n))
        _, gam = CG.gamma_table(n, gb)
        assert B.delta_f(n, T.closed_form_f(n, gb)) == gam
