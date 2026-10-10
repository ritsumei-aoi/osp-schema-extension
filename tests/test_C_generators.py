"""Unit tests for the C(n+1) basis and structure-constant generator (I03)."""

import json
import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from oscillator_algebra import Element, super_bracket, normal_order
from C_generators import (
    _basis_cache,
    compute_structure_constants,
    decompose,
    even_basis_labels,
    odd_basis_labels,
    schema1,
)

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


# ---------- engine-level checks ----------

def test_car_relation():
    # a_1_m a_1_p = 1 - a_1_p a_1_m
    t, _ = normal_order((1, 0), 1, False)
    assert t == {(): Fraction(1), (0, 1): Fraction(-1)}


def test_fermion_squares_vanish():
    for l in (0, 1):
        t, _ = normal_order((l, l), 1, False)
        assert t == {}


def test_ccr_relation():
    # b_1_m b_1_p = b_1_p b_1_m + 1
    t, _ = normal_order((3, 2), 1, False)
    assert t == {(2, 3): Fraction(1), (): Fraction(1)}


# ---------- basis-level checks ----------

@pytest.mark.parametrize("n", [1, 2, 3])
def test_dimensions_and_parity(n):
    labels, parity, elems = _basis_cache(n)
    even = [l for l in labels if parity[l] == 0]
    odd = [l for l in labels if parity[l] == 1]
    assert len(even) == 2 * n * n + n + 1
    assert len(odd) == 4 * n
    assert len(labels) == 2 * n * n + 5 * n + 1
    # realization parity matches declared parity
    for l in labels:
        assert elems[l].parity() == parity[l], l


@pytest.mark.parametrize("n", [1, 2, 3])
def test_basis_labels_unique(n):
    labels = odd_basis_labels(n) + even_basis_labels(n)
    assert len(labels) == len(set(labels))


def bracket_dec(n, x, y):
    labels, parity, elems = _basis_cache(n)
    return decompose(super_bracket(elems[x], elems[y], parity[x], parity[y]), n)


def test_key_brackets_n1():
    assert bracket_dec(1, "E_2del1_m", "E_2del1_p") == {"H_1": Fraction(4)}
    assert bracket_dec(1, "E_eps_del1_pp", "E_eps_del1_mm") == {
        "H_1": Fraction(1),
        "H_eps": Fraction(-1),
    }
    assert bracket_dec(1, "E_eps_del1_pm", "E_eps_del1_mp") == {
        "H_1": Fraction(1),
        "H_eps": Fraction(1),
    }
    assert bracket_dec(1, "H_eps", "E_eps_del1_pp") == {"E_eps_del1_pp": Fraction(1)}
    assert bracket_dec(1, "E_eps_del1_pp", "E_eps_del1_mp") == {"E_2del1_p": Fraction(1)}
    assert bracket_dec(1, "E_eps_del1_pp", "E_eps_del1_pm") == {}


def test_cross_rank_bracket_n2():
    # {E_eps_del1_pp, E_eps_del2_mp} = {a+ b1+, a- b2+} = b1+ b2+ = E_del1_del2_pp
    assert bracket_dec(2, "E_eps_del1_pp", "E_eps_del2_mp") == {
        "E_del1_del2_pp": Fraction(1)
    }
    # even sector: [E_del1_del2_pm, E_del1_del2_mp] = [b1+b2-, b1-b2+] = H_1 - H_2
    assert bracket_dec(2, "E_del1_del2_pm", "E_del1_del2_mp") == {
        "H_1": Fraction(1),
        "H_2": Fraction(-1),
    }


@pytest.mark.parametrize("n", [1, 2, 3])
def test_closure(n):
    """Every bracket of basis elements decomposes exactly (no residual scalar)."""
    compute_structure_constants(n)  # decompose() raises on closure failure


# ---------- JSON-level checks ----------

@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_files_conform(n):
    path = os.path.join(DATA, f"C_{n}_structure.json")
    with open(path) as f:
        data = json.load(f)
    assert data["schema_version"] == "5.0"
    alg = data["algebra"]
    assert alg["family"] == "C" and alg["m"] == 1 and alg["n"] == n
    assert alg["dimension"]["even"] == 2 * n * n + n + 1
    assert alg["dimension"]["odd"] == 4 * n
    og = data["oscillator_generators"]
    assert set(og.keys()) == {"fermions", "bosons"}
    assert og["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert og["fermions"]["m"] == 1
    ce = data["central_elements"]
    assert ce["kappa"]["parity"] == 1 and ce["K"]["parity"] == 0
    assert len(data["basis"]["even"]) == alg["dimension"]["even"]
    assert len(data["basis"]["odd"]) == alg["dimension"]["odd"]
    # parity map covers every basis label
    for l in data["basis"]["even"]:
        assert data["parity"][l] == 0
    for l in data["basis"]["odd"]:
        assert data["parity"][l] == 1
    # structure constants reference only basis labels
    basis = set(data["basis"]["even"]) | set(data["basis"]["odd"])
    for rec in data["structure_constants"]:
        assert rec["X"] in basis and rec["Y"] in basis and rec["Z"] in basis
        Fraction(rec["coeff"])  # parses as exact rational


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_matches_regeneration(n):
    path = os.path.join(DATA, f"C_{n}_structure.json")
    with open(path) as f:
        on_disk = json.load(f)
    fresh = schema1(n)
    assert on_disk["structure_constants"] == fresh["structure_constants"]
