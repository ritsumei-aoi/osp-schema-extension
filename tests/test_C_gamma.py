"""
Unit and Consistency Tests for C(n+1) Schema 2 (Gamma Structure)
Validates data/C_{n}_gamma.json against Schema 1 data and mathematical consistency.
"""

import json
import os
import pytest
from fractions import Fraction
from collections import defaultdict

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema2_file_existence(n):
    gamma_file = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
    assert os.path.exists(gamma_file), f"Missing {gamma_file}"

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_consistency(n):
    structure_file = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    gamma_file = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
    
    with open(structure_file, "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(gamma_file, "r", encoding="utf-8") as f:
        s2 = json.load(f)

    assert s2["schema_version"] == "5.0"
    assert s2["algebra"] == s1["algebra"]
    assert s2["central_elements"] == s1["central_elements"]
    assert s2["basis"] == s1["basis"]
    assert s2["parity"] == s1["parity"]

@pytest.mark.parametrize("n", [1, 2, 3])
def test_deformation_parameters(n):
    gamma_file = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
    with open(gamma_file, "r", encoding="utf-8") as f:
        s2 = json.load(f)

    dp = s2["deformation_parameters"]
    assert dp["count"] == 4 * n
    assert dp["matrix_shape"] == [2, 2 * n]
    assert dp["rows"] == ["a_1_p", "a_1_m"]
    assert len(dp["columns"]) == 2 * n
    assert len(dp["labels"]) == 4 * n
    assert dp["parity"] == 1
    assert "kappa" in dp["exchange_relations"]

@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_entries_validity_and_skew_symmetry(n):
    gamma_file = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
    with open(gamma_file, "r", encoding="utf-8") as f:
        s2 = json.load(f)

    parity = s2["parity"]
    all_basis = set(s2["basis"]["even"] + s2["basis"]["odd"])
    all_params = set(s2["deformation_parameters"]["labels"])

    entries = s2["inhomogeneous_deformation"]
    assert len(entries) > 0

    # Build mapping (X, Y, param, Z) -> Fraction
    gamma_map = defaultdict(lambda: Fraction(0, 1))
    
    for entry in entries:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        param = entry["param"]
        coeff_str = entry["coeff"]
        
        assert X in all_basis, f"Unknown X generator: {X}"
        assert Y in all_basis, f"Unknown Y generator: {Y}"
        assert Z in all_basis, f"Unknown Z generator: {Z}"
        assert param in all_params, f"Unknown deformation parameter: {param}"
        
        coeff = Fraction(coeff_str)
        assert coeff != 0, f"Zero coefficient recorded for ({X}, {Y}) -> {Z}"
        
        gamma_map[(X, Y, param, Z)] += coeff

    # Check graded skew-symmetry:
    # gamma(Y, X) = -(-1)^{p(X) p(Y)} gamma(X, Y)
    checked_pairs = set()
    for (X, Y, param, Z), c_XY in gamma_map.items():
        pair_key = (X, Y, param, Z)
        reverse_key = (Y, X, param, Z)
        
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1
        expected_c_YX = -sign * c_XY
        actual_c_YX = gamma_map[reverse_key]
        
        assert actual_c_YX == expected_c_YX, (
            f"Graded skew-symmetry failed for ({X}, {Y}) vs ({Y}, {X}) on Z={Z}, param={param}: "
            f"c(X,Y)={c_XY}, c(Y,X)={actual_c_YX}, expected={expected_c_YX}"
        )
