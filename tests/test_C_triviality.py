"""Tests for the triviality analysis (Issue I08)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_evaluate import evaluate_gamma, gb_profile  # noqa: E402
from C_gamma import bracket_table_from_schema1  # noqa: E402
from C_triviality import Unknowns, compare_tables, numeric_table, solve_rows, solve_triviality  # noqa: E402


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def setup(n):
    doc1, doc2 = load(f"C_{n}_structure.json"), load(f"C_{n}_gamma.json")
    return doc1["basis"]["pbw_order"], doc1["parity"], bracket_table_from_schema1(doc1), doc2


def test_solver_basic():
    rows = [({0: Fraction(1), 1: Fraction(1)}, Fraction(3), "r1"), ({0: Fraction(1), 1: Fraction(-1)}, Fraction(1), "r2")]
    res = solve_rows(rows, 2)
    assert res["consistent"] and res["rank"] == 2 and res["solution"] == [2, 1]
    rows.append(({0: Fraction(2), 1: Fraction(2)}, Fraction(7), "r3"))
    res = solve_rows(rows, 2)
    assert not res["consistent"] and res["inconsistent_at"] == ["r3"]


@pytest.mark.parametrize("n", [1, 2])
def test_layer3_equals_layer4(n):
    g3 = numeric_table(load(f"C_{n}_evaluated.json")["evaluated_gamma"])
    g4 = numeric_table(load(f"C_{n}_coboundary.json")["coboundary"])
    cmp = compare_tables(g3, g4)
    assert cmp["equal"] == cmp["pairs"] and not cmp["mismatch_g"] and not cmp["mismatch_K"]


@pytest.mark.parametrize("n", [1, 2])
@pytest.mark.parametrize("profile", ["all_plus_one", "alternating", "unit:gb_a1m_b1p"])
def test_general_solve(n, profile):
    labels, parity, br, doc2 = setup(n)
    gam = evaluate_gamma(doc2, gb_profile(n, profile))
    r_K = solve_triviality(labels, parity, br, gam, allow_K=True)
    assert r_K["consistent"] and r_K["verified"] and r_K["nullity"] == 4 * n
    r_g = solve_triviality(labels, parity, br, gam, allow_K=False)
    assert not r_g["consistent"]                       # only K-rows obstruct ...
    assert all(tag[2] == "K" for tag in r_g["inconsistent_at"])
    gam_mod = {k: {z: c for z, c in v.items() if z != "K"} for k, v in gam.items()}
    gam_mod = {k: v for k, v in gam_mod.items() if v}
    r_mod = solve_triviality(labels, parity, br, gam_mod, allow_K=False)
    assert r_mod["consistent"] and r_mod["verified"]   # ... trivial modulo K


def test_unknown_counts():
    labels, parity, _, _ = setup(2)
    assert len(Unknowns(labels, parity, False)) == 2 * 11 * 8
    assert len(Unknowns(labels, parity, True)) == 2 * 11 * 8 + 8
