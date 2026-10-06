"""Issue I08: tests for the triviality analysis."""

from __future__ import annotations

import json
import os
import sys

import pytest
import sympy as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "src"))

import C_triviality as tv  # noqa: E402
from C_evaluate import PROFILES  # noqa: E402

NS = [1, 2, 3]


@pytest.fixture(scope="module")
def report():
    path = os.path.join(REPO, "data", "C_triviality_report.json")
    if not os.path.exists(path):
        tv.main(["", "1", "2", "3"])
    with open(path) as fh:
        return json.load(fh)


@pytest.mark.parametrize("n", NS)
def test_all_profiles_are_trivial(report, n):
    rows = report["ranks"][str(n)]["profile_comparison"]
    assert {r["profile"] for r in rows} == set(PROFILES)
    for r in rows:
        assert r["identical"] is True, r
        assert r["gamma_entries"] == r["delta_f_entries"]


@pytest.mark.parametrize("n", NS)
def test_linear_system_is_consistent_over_Q_gb(report, n):
    full = report["ranks"][str(n)]["linear_analysis"]["full"]
    assert full["consistent"] is True
    assert full["obstructions"] == 0
    assert full["solver_solution_verified"] is True
    assert full["solver_solution_equals_canonical_f"] is True
    assert full["solution_space_dimension"] == 4 * n


@pytest.mark.parametrize("n", NS)
def test_restricted_system_is_obstructed(report, n):
    """With f: g -> g the K-components are an unremovable obstruction."""
    r = report["ranks"][str(n)]["linear_analysis"]["restricted"]
    assert r["consistent"] is False
    assert r["obstructions"] > 0
    assert r["obstructions"] == len(
        report["ranks"][str(n)]["restricted_obstruction_entries"])


@pytest.mark.parametrize("n", NS)
def test_solution_space_is_ad_of_odd_part(report, n):
    ss = report["ranks"][str(n)]["linear_analysis"]["solution_space"]
    assert ss["delta_vanishes_on_all"] is True
    assert ss["rank_of_ad_g_odd"] == 4 * n == ss["expected_rank"]
    full = report["ranks"][str(n)]["linear_analysis"]["full"]
    assert ss["rank_of_ad_g_odd"] == full["solution_space_dimension"]


@pytest.mark.parametrize("n", NS)
def test_obstruction_entries_are_exactly_the_K_components(report, n):
    obs = report["ranks"][str(n)]["restricted_obstruction_entries"]
    with open(os.path.join(REPO, "data", f"C_{n}_gamma.json")) as fh:
        g = json.load(fh)
    k_entries = [e for e in g["inhomogeneous_deformation"]["entries"] if e["Z"] == "K"]
    assert len(obs) == len(k_entries)
    # every obstruction sits on an (odd, even) pair and is non-zero
    for e in obs:
        assert (e["parity_X"], e["parity_Y"]) == (1, 0)
        assert sp.sympify(e["gamma_coeff"]) != 0


@pytest.mark.parametrize("n", [1, 2])
def test_live_comparison_matches_report(n, report):
    """Recompute the Layer3/Layer4 comparison without reading the report."""
    live = tv.compare_layers(n)
    assert all(r["identical"] for r in live)
    assert [r["profile"] for r in live] == [
        r["profile"] for r in report["ranks"][str(n)]["profile_comparison"]]
