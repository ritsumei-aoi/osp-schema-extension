"""
Unit tests for C(n+1) structure generator src/C_generators.py
"""

import pytest
import os
import json
from src.C_generators import get_C_basis, get_C_structure, compute_graded_bracket_numeric

def test_basis_dimensions():
    # n=1: C(2) = osp(2|2), dim = 4 | 4 (total 8)
    b1 = get_C_basis(1)
    assert len(b1["even"]) == 4
    assert len(b1["odd"]) == 4
    assert b1["even"] == ["H_0", "H_1", "E_2del1_p", "E_2del1_m"]
    assert b1["odd"] == ["E_eps1_del1_pp", "E_eps1_del1_pm", "E_eps1_del1_mp", "E_eps1_del1_mm"]

    # n=2: C(3) = osp(2|4), dim = 11 | 8 (total 19)
    b2 = get_C_basis(2)
    assert len(b2["even"]) == 11
    assert len(b2["odd"]) == 8

    # n=3: C(4) = osp(2|6), dim = 22 | 12 (total 34)
    b3 = get_C_basis(3)
    assert len(b3["even"]) == 22
    assert len(b3["odd"]) == 12

def test_parity_map():
    for n in [1, 2, 3]:
        basis = get_C_basis(n)
        p_map = basis["parity"]
        for g in basis["even"]:
            assert p_map[g] == 0
        for g in basis["odd"]:
            assert p_map[g] == 1

def test_graded_anti_symmetry():
    for n in [1, 2, 3]:
        basis = get_C_basis(n)
        all_gen = basis["even"] + basis["odd"]
        p_map = basis["parity"]
        
        for X in all_gen:
            for Y in all_gen:
                res_XY = compute_graded_bracket_numeric(X, Y, n)
                res_YX = compute_graded_bracket_numeric(Y, X, n)
                
                pX = p_map[X]
                pY = p_map[Y]
                
                # Graded anti-symmetry: [Y, X} = -(-1)^(pX*pY) [X, Y}
                expected_factor = -1 if (pX * pY == 0) else -1  # wait: if pX=1 and pY=1, {Y,X} = {X,Y}, so factor is +1
                # Graded bracket definition: [X,Y} = XY - (-1)^(pX pY) YX.
                # So [Y,X} = YX - (-1)^(pX pY) XY = -(-1)^(pX pY) [X,Y}.
                # For pX=0, pY=0: [Y,X] = -[X,Y] factor -1
                # For pX=0, pY=1: [Y,X] = -[X,Y] factor -1
                # For pX=1, pY=1: {Y,X} = {X,Y} factor +1
                sign = 1 if (pX == 1 and pY == 1) else -1
                
                all_keys = set(res_XY.keys()) | set(res_YX.keys())
                for z in all_keys:
                    val_XY = res_XY.get(z, 0)
                    val_YX = res_YX.get(z, 0)
                    assert val_YX == sign * val_XY, f"Graded anti-symmetry failed for {X}, {Y} on {z}: {val_YX} != {sign} * {val_XY}"

def test_schema_compliance():
    for n in [1, 2, 3]:
        s = get_C_structure(n)
        assert s["schema_version"] == "5.0"
        assert s["algebra"]["family"] == "C"
        assert s["algebra"]["m"] == 1
        assert s["algebra"]["n"] == n
        assert s["algebra"]["dimension"]["total"] == 2 * n**2 + 5 * n + 1
        assert s["algebra"]["dimension"]["even"] == 2 * n**2 + n + 1
        assert s["algebra"]["dimension"]["odd"] == 4 * n
        assert "central_elements" in s
        assert "kappa" in s["central_elements"]
        assert "K" in s["central_elements"]
        assert len(s["structure_constants"]) > 0

def test_json_files_exist():
    for n in [1, 2, 3]:
        filepath = os.path.join("data", f"C_{n}_structure.json")
        assert os.path.isfile(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["algebra"]["family"] == "C"
