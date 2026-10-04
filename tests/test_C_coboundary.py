"""
test_C_coboundary.py: Unit tests for Schema 4 (Coboundary Structure) for C(n+1).
Tests parity reversal of odd linear map f, consistency with Schema 1, and coboundary parity.
"""

import json
import os
import pytest


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema4_file_existence_and_keys(n):
    filepath = os.path.join("data", f"C_{n}_coboundary.json")
    assert os.path.exists(filepath), f"{filepath} must exist"

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["schema_version"] == "5.0"
    assert data["layer"] == "4_coboundary"
    assert "odd_linear_map_f" in data
    assert "coboundary_structure" in data
    assert data["coboundary_structure"]["num_canonical_terms"] == len(data["coboundary_structure"]["terms"])


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema4_consistency_with_schema1(n):
    path1 = os.path.join("data", f"C_{n}_structure.json")
    path4 = os.path.join("data", f"C_{n}_coboundary.json")

    with open(path1, "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(path4, "r", encoding="utf-8") as f:
        s4 = json.load(f)

    assert s1["algebra"] == s4["algebra"]
    assert s1["basis"] == s4["basis"]
    assert s1["parity"] == s4["parity"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_odd_linear_map_reverses_parity(n):
    path4 = os.path.join("data", f"C_{n}_coboundary.json")
    with open(path4, "r", encoding="utf-8") as f:
        s4 = json.load(f)

    parities = s4["parity"]
    f_mapping = s4["odd_linear_map_f"]["mapping"]

    for src, targets in f_mapping.items():
        p_src = parities[src]
        for tgt in targets.keys():
            p_tgt = parities[tgt]
            assert p_tgt == 1 - p_src, (
                f"Map f on {src} (p={p_src}) produced {tgt} (p={p_tgt}), which does not reverse parity!"
            )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_parity_condition(n):
    path4 = os.path.join("data", f"C_{n}_coboundary.json")
    with open(path4, "r", encoding="utf-8") as f:
        s4 = json.load(f)

    parities = s4["parity"]
    for term in s4["coboundary_structure"]["terms"]:
        p_x = parities[term["X"]]
        p_y = parities[term["Y"]]
        p_z = parities[term["Z"]]
        expected_pz = (p_x + p_y + 1) % 2
        assert p_z == expected_pz, (
            f"Coboundary term ({term['X']}, {term['Y']} -> {term['Z']}) violates parity condition!"
        )
