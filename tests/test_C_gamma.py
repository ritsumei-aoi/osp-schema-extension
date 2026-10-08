"""Tests for src/C_gamma.py (I05)."""

import json
import sys
from pathlib import Path

import pytest
import sympy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import C_gamma as G  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_kappa_zero_part_matches_schema1(n):
    labels, parity, undeformed, _ = G.split_kappa(n)
    assert G.check_against_schema1(n, undeformed) == []


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_is_linear_in_gb(n):
    _, _, _, gamma = G.split_kappa(n)
    gb = [G.gb_symbol(r, c) for r in G.gb_labels(n)[0] for c in G.gb_labels(n)[1]]
    for terms in gamma.values():
        for c in terms.values():
            assert sympy.Poly(c, *gb).total_degree() == 1, c


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_antisymmetric(n):
    labels, parity, _, gamma = G.split_kappa(n)
    assert G.check_gamma_antisymmetry(labels, parity, gamma) == []


def test_n1_known_value():
    # [E_eps1_del1_pp, E_eps1_del1_pm] has gamma = -gb_{a_1^+, b_1^-} * E_pp.
    _, _, _, gamma = G.split_kappa(1)
    got = gamma[("E_eps1_del1_pp", "E_eps1_del1_pm")]
    assert sympy.simplify(got["E_eps1_del1_pp"] + G.gb_symbol("a_1_p", "b_1_m")) == 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_matches_generator(n):
    data = json.loads((ROOT / "data" / f"C_{n}_gamma.json").read_text())
    assert data == G.to_json(n)
    assert data["gb_matrix"]["shape"] == [2, 2 * n]
    assert data["inhomogeneous_deformation"]["kappa_parity"] == 1
