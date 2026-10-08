"""Unit tests for C(n+1) structure Schema 1."""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import build_basis, build_schema1, parity_of, cartan_eigenvalue
from fractions import Fraction

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


@pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34),
])
def test_basis_dimensions(n, expected_even, expected_odd, expected_total):
    be, bo = build_basis(n)
    assert len(be) == expected_even, f"n={n}: expected {expected_even} even, got {len(be)}"
    assert len(bo) == expected_odd, f"n={n}: expected {expected_odd} odd, got {len(bo)}"
    assert len(be) + len(bo) == expected_total


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_consistency(n):
    be, bo = build_basis(n)
    for g in be:
        assert parity_of(g) == 0, f"{g} should be even"
    for g in bo:
        assert parity_of(g) == 1, f"{g} should be odd"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_cartan_eigenvalues_Hk_on_Ek(n):
    # Verify H_{n+1} on E_2del{n}_p gives eigenvalue -2
    ev = cartan_eigenvalue(n + 1, f"E_2del{n}_p", n)
    assert ev == Fraction(-2), f"n={n}: H_{{n+1}} on E_2del{{n}}_p should be -2, got {ev}"
    # H_1 on E_eps1_del1_pp (ε+δ1) should give eigenvalue 2
    ev2 = cartan_eigenvalue(1, "E_eps1_del1_pp", n)
    assert ev2 == Fraction(2), f"n={n}: H_1 on E_eps1_del1_pp should be 2, got {ev2}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_file_exists_and_valid(n):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    assert os.path.exists(path), f"Missing {path}"
    with open(path) as f:
        data = json.load(f)
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert data["algebra"]["dimension"]["even"] == 2 * n * n + n + 1
    assert data["algebra"]["dimension"]["odd"] == 4 * n
    assert "central_elements" in data
    assert "K" in data["central_elements"]
    assert "kappa" in data["central_elements"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_no_trivial_zero(n):
    """All listed structure constant entries should have nonzero coefficients."""
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as f:
        data = json.load(f)
    for entry in data["structure_constants"]:
        assert entry["result"], f"Empty result in {entry}"
        for term in entry["result"]:
            c = Fraction(term["coeff"])
            assert c != 0, f"Zero coefficient in {entry}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_basis_labels_unique(n):
    be, bo = build_basis(n)
    all_labels = be + bo
    assert len(all_labels) == len(set(all_labels)), "Duplicate basis labels"
