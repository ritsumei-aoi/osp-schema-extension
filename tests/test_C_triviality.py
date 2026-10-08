"""Tests for I08: Layer 3 / Layer 4 comparison and the independent triviality search."""
import pytest

from C_triviality import compare_layers, build_cache, triviality_search, symbolic_facts
from C_evaluate import profiles

NS = [1, 2, 3]


@pytest.fixture(scope="module")
def caches():
    return {n: build_cache(n) for n in NS}


@pytest.mark.parametrize("n", NS)
def test_layers_coincide_for_all_profiles(n):
    for prof in profiles(n):
        r = compare_layers(n, prof)
        assert r["mismatches"] == {}
        assert r["layer3_entries"] == r["layer4_entries"] == r["common"]


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("profile", ["all_plus", "single_a1p_b1p", "generic", "zero"])
def test_search_full_and_adjoint_consistent_with_nullity_4n(caches, n, profile):
    for variant in ("full", "adjoint"):
        r = triviality_search(n, profile, variant, caches[n])
        assert r["consistent"], r["failing_equations"][:3]
        assert r["nullity"] == 4 * n          # kernel = inner odd derivations ad(W), W in g_1


@pytest.mark.parametrize("n", NS)
def test_strict_reading_fails_exactly_on_K_components(caches, n):
    for prof in profiles(n):
        r = triviality_search(n, prof, "strict", caches[n])
        K = compare_layers(n, prof)["K_entries"]
        if prof == "zero":
            assert r["consistent"]
        else:
            assert not r["consistent"]
            assert len(r["failing_equations"]) == K
            assert all(eq[2] == "K" for eq, _ in r["failing_equations"])


@pytest.mark.parametrize("n", NS)
def test_every_gb_parameter_obstructs_strict_triviality(n):
    assert symbolic_facts(n)["all_gb_appear_in_K"]
