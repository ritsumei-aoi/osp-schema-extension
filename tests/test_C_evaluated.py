"""
Unit and Consistency Tests for C(n+1) Schema 3 (Evaluated Structure)
Validates data/C_{n}_evaluated.json against Schema 1 & Schema 2 and verifies algebraic consistency.
"""

import json
import os
import sys
import pytest
from fractions import Fraction
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.evaluate_C_structure import build_schema3_json, PROFILES

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_file_existence(n):
    primary = os.path.join(DATA_DIR, f"C_{n}_evaluated.json")
    profile_specific = os.path.join(DATA_DIR, f"C_{n}_evaluated_all_plus.json")
    assert os.path.exists(primary), f"Missing {primary}"
    assert os.path.exists(profile_specific), f"Missing {profile_specific}"

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema3_consistency_with_schema1_and_schema2(n):
    structure_file = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    gamma_file = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
    evaluated_file = os.path.join(DATA_DIR, f"C_{n}_evaluated.json")

    with open(structure_file, "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(gamma_file, "r", encoding="utf-8") as f:
        s2 = json.load(f)
    with open(evaluated_file, "r", encoding="utf-8") as f:
        s3 = json.load(f)

    # Consistency with Schema 1
    assert s3["schema_version"] == "5.0"
    assert s3["algebra"] == s1["algebra"]
    assert s3["central_elements"] == s1["central_elements"]
    assert s3["basis"] == s1["basis"]
    assert s3["parity"] == s1["parity"]

    # Consistency with Schema 2
    dp = s2["deformation_parameters"]
    eval_params = s3["evaluation_profile"]["parameters"]
    assert set(eval_params.keys()) == set(dp["labels"])
    assert len(eval_params) == 4 * n

    # Check evaluated_deformation matches substitution of parameters into Schema 2
    expected_gamma = defaultdict(Fraction)
    for entry in s2["inhomogeneous_deformation"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        param = entry["param"]
        coeff = Fraction(entry["coeff"])
        val = Fraction(eval_params[param])
        expected_gamma[(X, Y, Z)] += coeff * val

    expected_nonzero = {k: v for k, v in expected_gamma.items() if v != 0}
    actual_gamma = {
        (e["X"], e["Y"], e["Z"]): Fraction(e["coeff"])
        for e in s3["evaluated_deformation"]
    }
    assert actual_gamma == expected_nonzero

@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_gamma_graded_skew_symmetry(n):
    evaluated_file = os.path.join(DATA_DIR, f"C_{n}_evaluated.json")
    with open(evaluated_file, "r", encoding="utf-8") as f:
        s3 = json.load(f)

    parity = s3["parity"]
    gamma_map = {
        (e["X"], e["Y"], e["Z"]): Fraction(e["coeff"])
        for e in s3["evaluated_deformation"]
    }

    for (X, Y, Z), c_XY in gamma_map.items():
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1
        expected_c_YX = -sign * c_XY
        actual_c_YX = gamma_map.get((Y, X, Z), Fraction(0, 1))
        assert actual_c_YX == expected_c_YX, (
            f"Evaluated gamma skew-symmetry failed for ({X}, {Y}) vs ({Y}, {X}) on Z={Z}: "
            f"c(X,Y)={c_XY}, c(Y,X)={actual_c_YX}, expected={expected_c_YX}"
        )

@pytest.mark.parametrize("n", [1, 2, 3])
def test_deformed_structure_constants_skew_symmetry(n):
    evaluated_file = os.path.join(DATA_DIR, f"C_{n}_evaluated.json")
    with open(evaluated_file, "r", encoding="utf-8") as f:
        s3 = json.load(f)

    parity = s3["parity"]
    base_map = {}
    kappa_map = {}
    for e in s3["deformed_structure_constants"]:
        key = (e["X"], e["Y"], e["Z"])
        base_map[key] = Fraction(e["coeff_base"])
        kappa_map[key] = Fraction(e["coeff_kappa"])

    for (X, Y, Z) in set(base_map.keys()) | set(kappa_map.keys()):
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1

        c0_XY = base_map.get((X, Y, Z), Fraction(0, 1))
        c0_YX = base_map.get((Y, X, Z), Fraction(0, 1))
        assert c0_YX == -sign * c0_XY, f"Base bracket skew-symmetry failed for ({X}, {Y}) on Z={Z}"

        ck_XY = kappa_map.get((X, Y, Z), Fraction(0, 1))
        ck_YX = kappa_map.get((Y, X, Z), Fraction(0, 1))
        assert ck_YX == -sign * ck_XY, f"Kappa bracket skew-symmetry failed for ({X}, {Y}) on Z={Z}"

@pytest.mark.parametrize("profile_name", list(PROFILES.keys()))
def test_all_supported_profiles(profile_name):
    # Tests that all profiles can be evaluated without error for n=1
    data = build_schema3_json(1, profile_name=profile_name)
    assert data["evaluation_profile"]["name"] == profile_name
    assert len(data["evaluation_profile"]["parameters"]) == 4
    assert len(data["evaluated_deformation"]) > 0
    assert len(data["deformed_structure_constants"]) > 0
