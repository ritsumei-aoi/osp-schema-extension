import os
import json
import pytest
from src.C_generators import build_C_basis, generate_C_structure_json, save_all_C_json
from src.verify_C_structure import verify_structure_file

def test_basis_dimensions():
    # C(2): n=1 -> even 4, odd 4, total 8
    even_1, odd_1, parity_1, _ = build_C_basis(1)
    assert len(even_1) == 4
    assert len(odd_1) == 4
    assert len(even_1) + len(odd_1) == 8

    # C(3): n=2 -> even 11, odd 8, total 19
    even_2, odd_2, parity_2, _ = build_C_basis(2)
    assert len(even_2) == 11
    assert len(odd_2) == 8
    assert len(even_2) + len(odd_2) == 19

    # C(4): n=3 -> even 22, odd 12, total 34
    even_3, odd_3, parity_3, _ = build_C_basis(3)
    assert len(even_3) == 22
    assert len(odd_3) == 12
    assert len(even_3) + len(odd_3) == 34

def test_parity_consistency():
    for n in (1, 2, 3):
        data = generate_C_structure_json(n)
        parity = data["parity"]
        for entry in data["structure_constants"]:
            px = parity[entry["X"]]
            py = parity[entry["Y"]]
            pz = parity[entry["Z"]]
            assert pz == (px + py) % 2, f"Parity mismatch in bracket [{entry['X']}, {entry['Y']}] = {entry['Z']}"

def test_graded_antisymmetry():
    for n in (1, 2, 3):
        data = generate_C_structure_json(n)
        parity = data["parity"]
        sc_map = {}
        for entry in data["structure_constants"]:
            sc_map[(entry["X"], entry["Y"], entry["Z"])] = entry["coeff"]

        basis = data["basis"]["odd"] + data["basis"]["even"]
        for x in basis:
            for y in basis:
                px = parity[x]
                py = parity[y]
                sign = -1 if (px == 1 and py == 1) else 1
                
                for z in basis:
                    c1_str = sc_map.get((x, y, z), "0")
                    c2_str = sc_map.get((y, x, z), "0")
                    
                    from fractions import Fraction
                    c1 = Fraction(c1_str)
                    c2 = Fraction(c2_str)
                    
                    assert c1 == -sign * c2, f"Graded antisymmetry violation for [{x}, {y}] vs [{y}, {x}] on {z}"

def test_super_jacobi_identity():
    save_all_C_json()
    for n in (1, 2, 3):
        filepath = f"data/C_{n}_structure.json"
        res = verify_structure_file(filepath)
        assert res["status"] == "PASS", f"Super Jacobi verification failed for n={n}"
        assert res["antisymmetry_failures"] == 0
        assert res["jacobi_failures"] == 0

def test_json_schema_conformance():
    save_all_C_json()
    for n in (1, 2, 3):
        filepath = f"data/C_{n}_structure.json"
        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            data = json.load(f)

        assert data["schema_version"] == "5.0"
        assert data["algebra"]["family"] == "C"
        assert data["algebra"]["m"] == 1
        assert data["algebra"]["n"] == n
        assert data["algebra"]["dimension"]["even"] == 2 * n**2 + n + 1
        assert data["algebra"]["dimension"]["odd"] == 4 * n
        assert data["algebra"]["dimension"]["total"] == 2 * n**2 + 5 * n + 1

        assert "fermions" in data["oscillator_generators"]
        assert data["oscillator_generators"]["fermions"]["m"] == 1
        assert data["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]

        assert "central_elements" in data
        assert "kappa" in data["central_elements"]
        assert data["central_elements"]["kappa"]["parity"] == 1
        assert "K" in data["central_elements"]
        assert data["central_elements"]["K"]["parity"] == 0

def test_specific_bracket_values():
    data1 = generate_C_structure_json(1)
    sc_map = {(e["X"], e["Y"], e["Z"]): e["coeff"] for e in data1["structure_constants"]}

    # Check [H_1, E_eps1_del1_pp] = 2 E_eps1_del1_pp
    assert sc_map.get(("H_1", "E_eps1_del1_pp", "E_eps1_del1_pp")) == "2"

    # Check [E_eps1_del1_pp, E_eps1_del1_mm] = -H_1 - 2 H_2
    assert sc_map.get(("E_eps1_del1_pp", "E_eps1_del1_mm", "H_1")) == "-1"
    assert sc_map.get(("E_eps1_del1_pp", "E_eps1_del1_mm", "H_2")) == "-2"
