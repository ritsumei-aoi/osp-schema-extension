"""
Tests for Layer 4 (coboundary structure) for C(n+1) across n=1, 2, 3.
"""

import json
import pytest
from fractions import Fraction
from src.C_coboundary_generators import generate_all_schema4


@pytest.fixture(scope="module", autouse=True)
def ensure_schema4_generated():
    generate_all_schema4()


@pytest.mark.parametrize("n, expected_even, expected_odd, expected_phi_count", [
    (1, 4, 4, 32),
    (2, 11, 8, 176),
    (3, 22, 12, 528),
])
def test_schema4_linear_map_parameters(n, expected_even, expected_odd, expected_phi_count):
    with open(f"data/C_{n}_coboundary.json", "r") as f:
        s4 = json.load(f)

    assert s4["schema_version"] == "5.0"
    assert s4["algebra"]["family"] == "C"
    assert s4["algebra"]["n"] == n
    assert s4["linear_map_parameters"]["parameter_count"] == expected_phi_count
    assert len(s4["linear_map_parameters"]["parameters"]) == expected_phi_count


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema4_parity_and_skew_symmetry(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_coboundary.json", "r") as f:
        s4 = json.load(f)

    parity = s1["parity"]

    # Check parity and collect entries
    cob_map = {}
    for entry in s4["coboundary_structure"]["entries"]:
        param = entry["phi_param"]
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        pX, pY, pZ = parity[X], parity[Y], parity[Z]
        assert pZ == (pX + pY + 1) % 2, f"Parity violation in coboundary for ({X}, {Y}) -> {Z}"

        c = Fraction(entry["coeff"])
        cob_map.setdefault((param, X, Y), {})[Z] = c

    # Check graded skew-symmetry
    for (param, X, Y), z_dict in cob_map.items():
        pX, pY = parity[X], parity[Y]
        expected_sign = -1 if (pX * pY == 0) else 1  # -(-1)^(pX*pY)

        yx_dict = cob_map.get((param, Y, X), {})
        for Z, c in z_dict.items():
            assert Z in yx_dict, f"Missing opposite pair in coboundary for ({param}, {Y}, {X}) -> {Z}"
            assert yx_dict[Z] == expected_sign * c, f"Skew symmetry failed in coboundary for ({param}, {X}, {Y}) -> {Z}"
