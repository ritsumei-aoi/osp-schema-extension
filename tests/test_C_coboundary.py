"""
Unit and Consistency Tests for C(n+1) Schema 4 (Coboundary Structure)
Validates data/C_{n}_coboundary.json against Schema 1 and verifies coboundary properties.
"""

import json
import os
import sys
import pytest
from fractions import Fraction
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.compute_C_coboundary import compute_coboundary_structure

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema4_file_existence(n):
    primary = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
    alias = os.path.join(DATA_DIR, f"C_{n}_coboundary_all_plus.json")
    assert os.path.exists(primary), f"Missing {primary}"
    assert os.path.exists(alias), f"Missing {alias}"

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema4_consistency_with_schema1(n):
    structure_file = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    coboundary_file = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")

    with open(structure_file, "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(coboundary_file, "r", encoding="utf-8") as f:
        s4 = json.load(f)

    assert s4["schema_version"] == "5.0"
    assert s4["algebra"] == s1["algebra"]
    assert s4["central_elements"] == s1["central_elements"]
    assert s4["basis"] == s1["basis"]
    assert s4["parity"] == s1["parity"]

@pytest.mark.parametrize("n", [1, 2, 3])
def test_map_f_parity_reversal(n):
    coboundary_file = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
    with open(coboundary_file, "r", encoding="utf-8") as f:
        s4 = json.load(f)

    parity = s4["parity"]
    all_basis = set(s4["basis"]["even"] + s4["basis"]["odd"])
    dim_g = len(all_basis)

    map_f = s4["map_f"]
    assert map_f["type"] == "odd_linear_map"
    assert map_f["matrix_shape"] == [dim_g, dim_g]

    components = map_f["non_zero_components"]
    assert len(components) > 0

    for comp in components:
        src = comp["source"]
        tgt = comp["target"]
        coeff = Fraction(comp["coeff"])
        assert src in all_basis
        assert tgt in all_basis
        assert coeff != 0
        # Check strict parity reversal: p(tgt) == 1 - p(src)
        assert parity[tgt] == 1 - parity[src], f"Map f failed to reverse parity: {src} -> {tgt}"

@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_graded_skew_symmetry(n):
    coboundary_file = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
    with open(coboundary_file, "r", encoding="utf-8") as f:
        s4 = json.load(f)

    parity = s4["parity"]
    all_basis = set(s4["basis"]["even"] + s4["basis"]["odd"])

    coboundary_map = {}
    for e in s4["coboundary_structure"]:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        assert X in all_basis
        assert Y in all_basis
        assert Z in all_basis
        coeff = Fraction(e["coeff"])
        assert coeff != 0
        # Graded parity rule for delta f: p(Z) = p(X) + p(Y) + 1 mod 2
        assert parity[Z] == (parity[X] + parity[Y] + 1) % 2
        coboundary_map[(X, Y, Z)] = coeff

    # Check graded skew-symmetry across all recorded entries
    for (X, Y, Z), c_XY in coboundary_map.items():
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1
        expected_c_YX = -sign * c_XY
        actual_c_YX = coboundary_map.get((Y, X, Z), Fraction(0, 1))
        assert actual_c_YX == expected_c_YX, (
            f"Coboundary skew-symmetry failed for ({X}, {Y}) vs ({Y}, {X}) on Z={Z}: "
            f"c(X,Y)={c_XY}, c(Y,X)={actual_c_YX}, expected={expected_c_YX}"
        )

@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_independent_formula_verification(n):
    structure_file = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    coboundary_file = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")

    with open(structure_file, "r", encoding="utf-8") as f:
        s1 = json.load(f)
    with open(coboundary_file, "r", encoding="utf-8") as f:
        s4 = json.load(f)

    all_basis = s1["basis"]["even"] + s1["basis"]["odd"]
    parity = s1["parity"]

    c_base = defaultdict(Fraction)
    for entry in s1["structure_constants"]:
        c_base[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    f_map = defaultdict(Fraction)
    for comp in s4["map_f"]["non_zero_components"]:
        f_map[(comp["source"], comp["target"])] = Fraction(comp["coeff"])

    # Formula: (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    def bracket(X, Y, Z):
        return c_base.get((X, Y, Z), Fraction(0, 1))

    # Verify a representative subset of brackets
    for entry in s4["coboundary_structure"][:50]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        pX, pY = parity[X], parity[Y]
        expected_coeff = Fraction(entry["coeff"])

        val = Fraction(0, 1)
        s1_sign = -1 if pX == 1 else 1
        s2_sign = - (-1 if ((pX + 1) * pY) % 2 == 1 else 1)

        # Term 1: (-1)^pX [X, f(Y)]
        for i in all_basis:
            phi_Yi = f_map.get((Y, i), Fraction(0, 1))
            if phi_Yi != 0:
                val += s1_sign * phi_Yi * bracket(X, i, Z)

        # Term 2: - (-1)^{(pX+1)pY} [Y, f(X)]
        for i in all_basis:
            phi_Xi = f_map.get((X, i), Fraction(0, 1))
            if phi_Xi != 0:
                val += s2_sign * phi_Xi * bracket(Y, i, Z)

        # Term 3: - f([X, Y])
        for k in all_basis:
            c_XY_k = bracket(X, Y, k)
            if c_XY_k != 0:
                phi_kZ = f_map.get((k, Z), Fraction(0, 1))
                val -= c_XY_k * phi_kZ

        assert val == expected_coeff, f"Independent coboundary formula check failed for ({X}, {Y}) -> {Z}"
