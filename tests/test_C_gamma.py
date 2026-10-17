"""
Unit tests for C_gamma.py (Schema 2: gamma structure).
Tests gb_matrix dimensions, inhomogeneous_deformation field,
parity consistency, graded anti-symmetry, and consistency with Schema 1.
"""

import json
import os
import pytest
from fractions import Fraction


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_2_structure_and_disk_files(n):
    gamma_path = os.path.join("data", f"C_{n}_gamma.json")
    struct_path = os.path.join("data", f"C_{n}_structure.json")

    assert os.path.exists(gamma_path), f"File {gamma_path} does not exist"
    assert os.path.exists(struct_path), f"File {struct_path} does not exist"

    with open(gamma_path, "r", encoding="utf-8") as f:
        data_gamma = json.load(f)

    with open(struct_path, "r", encoding="utf-8") as f:
        data_struct = json.load(f)

    # 1. Consistency with Schema 1
    assert data_gamma["schema_version"] == "5.0"
    assert data_gamma["algebra"] == data_struct["algebra"]
    assert data_gamma["central_elements"] == data_struct["central_elements"]
    assert data_gamma["basis"] == data_struct["basis"]
    assert data_gamma["parity"] == data_struct["parity"]
    assert data_gamma["generator_realization"] == data_struct["generator_realization"]
    assert data_gamma["oscillator_generators"] == data_struct["oscillator_generators"]
    assert data_gamma["oscillator_relations"] == data_struct["oscillator_relations"]

    # 2. Inhomogeneous deformation and gb_matrix fields
    assert "inhomogeneous_deformation" in data_gamma
    inhom = data_gamma["inhomogeneous_deformation"]
    assert "gb_matrix" in inhom
    assert "gamma_structure_constants" in inhom

    gb = inhom["gb_matrix"]
    assert gb["dimensions"] == [2, 2 * n]
    assert gb["row_labels"] == ["a_1_p", "a_1_m"]
    assert len(gb["col_labels"]) == 2 * n
    assert gb["parity"] == 1

    # Check total parameters
    flat_params = [p for row in gb["parameter_names"] for p in row]
    assert len(flat_params) == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_parity_and_graded_anti_symmetry(n):
    gamma_path = os.path.join("data", f"C_{n}_gamma.json")
    with open(gamma_path, "r", encoding="utf-8") as f:
        data_gamma = json.load(f)

    parity = data_gamma["parity"]
    gamma_list = data_gamma["gamma_structure_constants"]
    assert len(gamma_list) > 0

    table = {}
    for entry in gamma_list:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        par = entry["param"]
        coeff = Fraction(entry["coeff"])
        table[(X, Y, Z, par)] = coeff

        # Parity check: p(kappa * gamma(X, Y)) = p(X) + p(Y)
        # Since p(kappa) = 1: p(Z) = (p(X) + p(Y) + 1) % 2
        pX = parity[X]
        pY = parity[Y]
        pZ = parity[Z]
        assert pZ == (pX + pY + 1) % 2, f"Parity mismatch in gamma: [{X}, {Y}] -> {Z} with param {par}"

    # Graded anti-symmetry of gamma: gamma(Y, X) = -(-1)^{pX pY} gamma(X, Y)
    for (X, Y, Z, par), coeff in table.items():
        pX, pY = parity[X], parity[Y]
        sign = -1 if (pX * pY) % 2 == 1 else 1
        expected_coeff_yx = -sign * coeff
        actual_coeff_yx = table.get((Y, X, Z, par), Fraction(0))
        assert actual_coeff_yx == expected_coeff_yx, (
            f"Graded anti-symmetry violated for gamma({X}, {Y}) vs gamma({Y}, {X}) on {Z} ({par})"
        )
