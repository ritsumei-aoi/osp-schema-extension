"""Tests for the I08 triviality analysis."""
import copy

import pytest

from C_triviality import analyse, solve, load_profiles, residual, analytic_f, f_to_values
from C_cohomology import cocycle_dimensions


@pytest.mark.parametrize("n", (1, 2))
def test_readings(n):
    r = analyse(n)
    for reading in ("mod_K", "exact"):
        rr = r["readings"][reading]
        assert all(t["trivial"] and t["residual_entries"] == 0 for t in rr["targets"].values())
        assert rr["kernel_dim"] == 4 * n
    strict = r["readings"]["strict"]["targets"]
    assert strict["zero"]["trivial"]
    assert all(not t["trivial"] and t["inconsistent_components"] == ["K"]
               for k, t in strict.items() if k != "zero")
    assert set(r["analytic_candidate_residual_entries"].values()) == {0}


def test_analytic_f_generic_gb():
    gb = {"gb_p_1_p": 3, "gb_p_1_m": -2, "gb_m_1_p": 5, "gb_m_1_m": 7,
          "gb_p_2_p": -1, "gb_p_2_m": 4, "gb_m_2_p": 2, "gb_m_2_m": -6}
    from C_gamma import deformed_bracket_parts
    target = {p: g for p, (_, g) in deformed_bracket_parts(2, gb).items() if g}
    assert residual(2, f_to_values(analytic_f(2, gb)), target, "exact") == {}


def test_solver_detects_non_coboundary():
    _, ev = load_profiles(1)["all_plus"]
    bad = copy.deepcopy(ev)
    bad[("H_1", "H_2")]["E_eps1_del1_pp"] += 1
    bad[("H_2", "H_1")]["E_eps1_del1_pp"] -= 1
    solver, _, names = solve(1, {"ok": ev, "bad": bad}, "mod_K")
    assert solver.inconsistent[names.index("ok")] == []
    assert solver.inconsistent[names.index("bad")]


@pytest.mark.parametrize("n,expected", [(1, 28), (2, 168)])
def test_odd_H2_vanishes(n, expected):
    nvar, rk = cocycle_dimensions(n)
    assert nvar - rk == expected      # dim Z^2_odd == dim B^2_odd (rank of delta)
