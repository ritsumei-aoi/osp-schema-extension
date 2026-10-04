"""
test_C_coboundary.py: Unit tests for Schema 4 (Coboundary Structure) for C(n+1).
"""

import json
import os
import pytest
from src.C_coboundary_generator import compute_coboundary


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema4_structure_and_parity_reversal(n):
    c_file = f"data/C_{n}_coboundary.json"
    s_file = f"data/C_{n}_structure.json"

    assert os.path.exists(c_file), f"Missing {c_file}"
    assert os.path.exists(s_file), f"Missing {s_file}"

    with open(c_file, "r") as f:
        cdata = json.load(f)
    with open(s_file, "r") as f:
        sdata = json.load(f)

    # Check top-level keys
    assert cdata["schema_version"] == "5.0"
    assert cdata["algebra"] == sdata["algebra"]
    assert cdata["basis"] == sdata["basis"]
    assert cdata["parity"] == sdata["parity"]

    # Check linear map f parity reversal
    parities = cdata["parity"]
    f_map = cdata["linear_map_f"]["mapping"]
    for src, targets in f_map.items():
        p_src = parities[src]
        for tgt, coeff in targets.items():
            assert parities[tgt] == 1 - p_src, f"Parity reversal failed for {src} -> {tgt}"

    # Check graded skew-symmetry of delta_f
    coboundary = cdata["coboundary"]["coefficients"]
    brackets = {}
    for entry in coboundary:
        key = (entry["X"], entry["Y"], entry["Z"])
        brackets[key] = int(entry["coeff"]) if "/" not in entry["coeff"] else float(entry["coeff"])

    all_pairs = set((entry["X"], entry["Y"]) for entry in coboundary)
    for X, Y in all_pairs:
        pX = parities[X]
        pY = parities[Y]
        expected_sign = - ((-1)**(pX * pY))

        for entry in coboundary:
            if entry["X"] == X and entry["Y"] == Y:
                Z = entry["Z"]
                c_XY = brackets.get((X, Y, Z), 0)
                c_YX = brackets.get((Y, X, Z), 0)
                assert c_YX == expected_sign * c_XY, f"Skew-symmetry failed in coboundary for ({X}, {Y}) -> {Z}"
