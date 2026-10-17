"""
Unit tests for C_coboundary.py (Schema 4: Coboundary Structure).
Tests file existence, schema conformance, parity reversing of f,
graded anti-symmetry of delta f, and consistency with Layer 1 basis.
"""

import json
import os
import pytest
from fractions import Fraction
from src.C_coboundary import compute_coboundary, build_mode_paired_exchange_map


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_4_disk_files_and_structure_conformance(n):
    coboundary_path = os.path.join("data", f"C_{n}_coboundary.json")
    struct_path = os.path.join("data", f"C_{n}_structure.json")

    assert os.path.exists(coboundary_path), f"File {coboundary_path} does not exist"

    with open(coboundary_path, "r", encoding="utf-8") as f:
        data_cob = json.load(f)

    with open(struct_path, "r", encoding="utf-8") as f:
        data_struct = json.load(f)

    # 1. Top-level keys
    required_keys = [
        "schema_version", "algebra", "central_elements", "map_f",
        "basis", "parity", "coboundary_structure_constants", "metadata"
    ]
    for key in required_keys:
        assert key in data_cob, f"Missing key {key} in {coboundary_path}"

    assert data_cob["schema_version"] == "5.0"
    assert data_cob["algebra"] == data_struct["algebra"]
    assert data_cob["central_elements"] == data_struct["central_elements"]
    assert data_cob["basis"] == data_struct["basis"]
    assert data_cob["parity"] == data_struct["parity"]

    # 2. Map f configuration
    map_f = data_cob["map_f"]
    assert map_f["configuration"] == "mode_paired_exchange"
    assert map_f["scaling"] == "1"
    assert len(map_f["mapping"]) > 0

    parity = data_cob["parity"]
    for mapping in map_f["mapping"]:
        src = mapping["source"]
        tgt = mapping["target"]
        assert parity[src] != parity[tgt], f"Map f must reverse parity: {src} -> {tgt}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_graded_anti_symmetry_and_parity(n):
    coboundary_path = os.path.join("data", f"C_{n}_coboundary.json")
    with open(coboundary_path, "r", encoding="utf-8") as f:
        data_cob = json.load(f)

    parity = data_cob["parity"]
    cob_list = data_cob["coboundary_structure_constants"]
    assert len(cob_list) > 0

    table = {}
    for entry in cob_list:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        coeff = Fraction(entry["coeff"])
        table[(X, Y, Z)] = coeff

        # Parity check: p(Z) == (p(X) + p(Y) + 1) % 2
        pX = parity[X]
        pY = parity[Y]
        pZ = parity[Z]
        assert pZ == (pX + pY + 1) % 2, f"Parity mismatch in delta f: [{X}, {Y}] -> {Z}"

    # Graded anti-symmetry: (delta f)(Y, X) = -(-1)^{pX pY} (delta f)(X, Y)
    for (X, Y, Z), coeff in table.items():
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1
        expected_coeff_yx = -sign * coeff
        actual_coeff_yx = table.get((Y, X, Z), Fraction(0))
        assert actual_coeff_yx == expected_coeff_yx, (
            f"Graded anti-symmetry violated for delta f: ({X}, {Y}) vs ({Y}, {X}) on {Z}"
        )


def test_general_odd_map_support():
    # Test that compute_coboundary supports arbitrary odd linear map
    struct_path = os.path.join("data", "C_1_structure.json")
    with open(struct_path, "r", encoding="utf-8") as f:
        data_struct = json.load(f)

    basis = data_struct["basis"]["odd"] + data_struct["basis"]["even"]
    parity = data_struct["parity"]
    struct_consts = data_struct["structure_constants"]

    # Arbitrary odd map: H_1 -> E_eps1_del1_pm with coeff 3/2
    custom_f = {"H_1": {"E_eps1_del1_pm": Fraction(3, 2)}}
    delta_f = compute_coboundary(struct_consts, basis, parity, custom_f)
    assert len(delta_f) > 0

    table = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in delta_f}
    for (X, Y, Z), coeff in table.items():
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1
        expected_yx = -sign * coeff
        assert table.get((Y, X, Z), Fraction(0)) == expected_yx
