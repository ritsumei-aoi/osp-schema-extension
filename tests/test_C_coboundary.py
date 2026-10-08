"""Tests for src/C_coboundary.py (I07)."""

import json
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import C_coboundary as CB  # noqa: E402


@pytest.mark.parametrize("n,expected", [(1, 32), (2, 176), (3, 528)])
def test_parameter_count(n, expected):
    # Odd maps: f_{ij} with p(Z_i) != p(Z_j), so 2 * (#even) * (#odd).
    _, params = CB.coboundary_basis(n)
    assert len(params) == expected


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_of_coboundary(n):
    alg, params = CB.coboundary_basis(n)
    for i, j in params[:40]:  # full check is in to_json; sample here
        for (X, Y), terms in CB.elementary_coboundary(alg, i, j).items():
            for Z in terms:
                assert alg.parity[Z] == (alg.parity[X] + alg.parity[Y] + 1) % 2


def test_known_value_n1():
    # f_{ij} with j = E_2del1_p and i = E_eps1_del1_pm, so f(E_2del1_p) = E_pm.
    # For X = H_1, Y = E_2del1_p (p(X)=0):
    #   term 1: (+1) [H_1, f(E_2del1_p)] = [H_1, E_pm] = -E_pm
    #           (stored [E_pm, H_1] = +E_pm, and H_1 is even, so [H_1, E_pm] = -E_pm)
    #   term 2: absent, since X != j
    #   term 3: -f([H_1, E_2del1_p]) = -f(2 E_2del1_p) = -2 E_pm
    # Total: -3 E_pm.
    alg = CB.Schema1(1)
    delta = CB.elementary_coboundary(alg, "E_eps1_del1_pm", "E_2del1_p")
    assert delta[("H_1", "E_2del1_p")] == {"E_eps1_del1_pm": Fraction(-3)}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_file_matches_fresh_run(n):
    data = json.loads((ROOT / "data" / f"C_{n}_coboundary.json").read_text())
    assert data == CB.to_json(n)
