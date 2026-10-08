"""Tests for src/C_triviality.py (Issue I08)."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import C_evaluate as E  # noqa: E402
import C_triviality as T  # noqa: E402

NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("profile", E.PROFILES)
def test_layer_comparison(n, profile):
    r = T.compare_layers(n, profile)
    assert r["g_part_identical"] is True
    assert r["K_part_equals_K_extension"] is True
    assert r["trivial_extended"] is True
    # strictly trivial iff the deformation vanishes (zero profile)
    assert r["trivial_strict"] == (profile == "zero")
    assert r["gamma_g_terms"] == r["deltaf_terms"]


@pytest.mark.parametrize("n", [1, 2])
@pytest.mark.parametrize("profile", ["all_plus", "zero", "single", "random"])
def test_general_search(n, profile):
    strict = T.general_search(n, profile, extended=False)
    ext = T.general_search(n, profile, extended=True)
    # g-rows are always solvable; only K-rows can obstruct
    assert strict["residual_active_rows"] < 1e-9
    assert ext["solvable"] is True
    assert strict["solvable"] == (profile == "zero")
    # kernel of delta on odd maps = inner odd derivations ad(z), z in g_1: dimension 4n
    assert strict["nullity"] == 4 * n
    assert ext["nullity"] == 4 * n     # lambda is uniquely determined


@pytest.mark.parametrize("n", NS)
def test_every_gb_is_obstructed(n):
    r = T.K_obstruction(n)
    assert r["all_gb_obstructed"] is True
    assert len(r["witnesses"]) == 4 * n
