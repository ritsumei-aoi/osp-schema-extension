"""Tests for Schema 4 (Issue I07)."""
import json
import os

import pytest

from conftest import DATA
from C_coboundary import build_schema4, load_coboundary, load_sc, phi_label, evaluate_linear
from verify_C_coboundary import verify


@pytest.mark.parametrize("n", (1, 2, 3))
def test_coboundary_checks(n):
    r = verify(n, seed=n)
    assert r["ok"], r


@pytest.mark.parametrize("n", (1, 2, 3))
def test_coboundary_reproducible(n):
    with open(os.path.join(DATA, f"C_{n}_coboundary.json")) as f:
        d = json.load(f)
    assert build_schema4(n, date=d["metadata"]["generation_date"]) == d
    E, O = 2 * n * n + n + 1, 4 * n
    assert d["coboundary"]["odd_map"]["phi_unknowns"] == 2 * E * O
    assert d["coboundary"]["odd_map"]["psi_unknowns"] == O


def test_wrong_sign_map_is_not_a_cocycle_kernel_element():
    """Negative control: f(Y) = [Y, Z] (instead of [Z, Y]) is not killed by delta."""
    basis, par, sc = load_sc(1)
    _, sym = load_coboundary(1)
    Z = "E_eps1_del1_pp"
    vals = {phi_label(W, j): c for j in basis for W, c in sc.get((j, Z), {}).items()}
    assert evaluate_linear(sym, vals)
