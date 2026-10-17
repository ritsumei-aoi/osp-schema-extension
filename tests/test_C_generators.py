"""
Unit tests for C(n+1) structure constant generator and Schema 1 JSON.
"""

import pytest
from fractions import Fraction
from collections import defaultdict
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.C_generators import get_generators, build_schema1_json

@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34)
])
def test_generator_counts(n, expected_even, expected_odd, expected_total):
    eb, ob, real, ff, notes, par = get_generators(n)
    assert len(eb) == expected_even
    assert len(ob) == expected_odd
    assert len(eb) + len(ob) == expected_total

@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_parities(n):
    eb, ob, real, ff, notes, par = get_generators(n)
    for g in eb:
        assert par[g] == 0
    for g in ob:
        assert par[g] == 1

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_keys(n):
    schema = build_schema1_json(n)
    expected_keys = {
        "schema_version", "algebra", "central_elements",
        "oscillator_generators", "oscillator_relations", "basis",
        "parity", "generator_realization", "structure_constants", "metadata"
    }
    assert set(schema.keys()) == expected_keys
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n
    assert "kappa" in schema["central_elements"]
    assert "K" in schema["central_elements"]
    assert "fermions" in schema["oscillator_generators"]
    assert "bosons" in schema["oscillator_generators"]
    assert schema["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert schema["metadata"]["generated_by"] == "src/C_generators.py"

    # Check that frappat_form is present in realizations
    for g, r_entry in schema["generator_realization"]["realizations"].items():
        assert "standard_form" in r_entry
        assert "frappat_form" in r_entry
        assert len(r_entry["frappat_form"]) > 0

@pytest.mark.parametrize("n", [1, 2, 3])
def test_graded_skew_symmetry(n):
    schema = build_schema1_json(n)
    parity = schema["parity"]
    brackets = schema["structure_constants"]
    
    b_map = {}
    for entry in brackets:
        b_map[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    for (X, Y, Z), coeff in b_map.items():
        pX = parity[X]
        pY = parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1
        opp_coeff = b_map.get((Y, X, Z), Fraction(0, 1))
        assert opp_coeff == -sign * coeff

@pytest.mark.parametrize("n", [1, 2, 3])
def test_super_jacobi_identity(n):
    schema = build_schema1_json(n)
    all_basis = schema["basis"]["even"] + schema["basis"]["odd"]
    parity = schema["parity"]
    
    tensor = defaultdict(dict)
    for entry in schema["structure_constants"]:
        tensor[(entry["X"], entry["Y"])][entry["Z"]] = Fraction(entry["coeff"])

    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            for Z in all_basis:
                pZ = parity[Z]
                sum_decomp = defaultdict(Fraction)
                for W, c_YZ_W in tensor.get((Y, Z), {}).items():
                    for V, c_XW_V in tensor.get((X, W), {}).items():
                        s = -1 if (pX * pZ) % 2 == 1 else 1
                        sum_decomp[V] += s * c_YZ_W * c_XW_V
                for W, c_ZX_W in tensor.get((Z, X), {}).items():
                    for V, c_YW_V in tensor.get((Y, W), {}).items():
                        s = -1 if (pY * pX) % 2 == 1 else 1
                        sum_decomp[V] += s * c_ZX_W * c_YW_V
                for W, c_XY_W in tensor.get((X, Y), {}).items():
                    for V, c_ZW_V in tensor.get((Z, W), {}).items():
                        s = -1 if (pZ * pY) % 2 == 1 else 1
                        sum_decomp[V] += s * c_XY_W * c_ZW_V
                for V, val in sum_decomp.items():
                    assert val == 0, f"Jacobi failed for ({X}, {Y}, {Z}) at {V}"
