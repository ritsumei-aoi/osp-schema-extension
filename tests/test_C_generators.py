"""
Unit tests for C(n+1) structure constant generator.
Tests parity, generator counts, and schema consistency.
"""

import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import get_basis, get_parity, build_schema1


@pytest.mark.parametrize("n,exp_even,exp_odd", [(1, 4, 4), (2, 11, 8), (3, 22, 12)])
def test_basis_counts(n, exp_even, exp_odd):
    even, odd = get_basis(n)
    assert len(even) == exp_even, f"n={n}: expected {exp_even} even, got {len(even)}"
    assert len(odd) == exp_odd, f"n={n}: expected {exp_odd} odd, got {len(odd)}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_basis_no_duplicates(n):
    even, odd = get_basis(n)
    all_gens = even + odd
    assert len(all_gens) == len(set(all_gens)), f"n={n}: duplicate generators found"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_values(n):
    even, odd = get_basis(n)
    parity = get_parity(even, odd)
    for g in even:
        assert parity[g] == 0, f"n={n}: {g} should have parity 0"
    for g in odd:
        assert parity[g] == 1, f"n={n}: {g} should have parity 1"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_dimensions(n):
    schema = build_schema1(n)
    dim = schema["algebra"]["dimension"]
    assert dim["even"] == 2 * n * n + n + 1
    assert dim["odd"] == 4 * n
    assert dim["total"] == dim["even"] + dim["odd"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_algebra_fields(n):
    schema = build_schema1(n)
    alg = schema["algebra"]
    assert alg["family"] == "C"
    assert alg["m"] == 1
    assert alg["n"] == n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_central_elements(n):
    schema = build_schema1(n)
    ce = schema["central_elements"]
    assert "kappa" in ce and ce["kappa"]["parity"] == 1
    assert "K" in ce and ce["K"]["parity"] == 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_oscillator_generators(n):
    schema = build_schema1(n)
    osc = schema["oscillator_generators"]
    assert "fermions" in osc
    assert osc["fermions"]["m"] == 1
    assert set(osc["fermions"]["labels"]) == {"a_1_p", "a_1_m"}
    assert "bosons" in osc
    assert osc["bosons"]["n"] == n
    assert osc["bosons"]["count"] == 2 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_in_basis(n):
    schema = build_schema1(n)
    basis = set(schema["basis"]["even"] + schema["basis"]["odd"])
    for sc in schema["structure_constants"]:
        assert sc["X"] in basis, f"X={sc['X']} not in basis for n={n}"
        assert sc["Y"] in basis, f"Y={sc['Y']} not in basis for n={n}"
        assert sc["Z"] in basis, f"Z={sc['Z']} not in basis for n={n}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_nonzero(n):
    schema = build_schema1(n)
    for sc in schema["structure_constants"]:
        from fractions import Fraction
        assert Fraction(sc["coeff"]) != 0, f"Zero coefficient in structure constant: {sc}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_json_files_exist(n):
    path = f"data/C_{n}_structure.json"
    assert os.path.exists(path), f"Missing {path}"
    with open(path) as f:
        data = json.load(f)
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
