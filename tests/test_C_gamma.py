"""
Tests for Schema 2 (gamma structure) for C(n+1) across n=1, 2, 3.
"""

import json
import pytest
from fractions import Fraction
from src.C_gamma_generators import generate_all_schema2


@pytest.fixture(scope="module", autouse=True)
def ensure_schema2_generated():
    generate_all_schema2()


@pytest.mark.parametrize("n, expected_gb_count", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_schema2_gb_parameters(n, expected_gb_count):
    with open(f"data/C_{n}_gamma.json", "r") as f:
        data = json.load(f)
    
    assert data["schema_version"] == "5.0"
    assert data["algebra"]["family"] == "C"
    assert data["algebra"]["m"] == 1
    assert data["algebra"]["n"] == n
    assert data["gb_matrix"]["parameter_count"] == expected_gb_count
    assert len(data["gb_matrix"]["parameters"]) == expected_gb_count


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema2_parity_preservation(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json", "r") as f:
        s2 = json.load(f)

    parity = s1["parity"]
    for entry in s2["inhomogeneous_deformation"]["gamma_structure"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        pX, pY, pZ = parity[X], parity[Y], parity[Z]
        # Since p(kappa) = 1 and p(gb) = 1, [X, Y]_gamma has parity (pX + pY) % 2.
        # Thus kappa * gb * Z has parity (pX + pY) % 2, which means
        # p(Z) must satisfy pZ = (pX + pY + 1) % 2.
        assert pZ == (pX + pY + 1) % 2, f"Parity violation in gamma for ({X}, {Y}) -> {Z}: pX={pX}, pY={pY}, pZ={pZ}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema2_skew_symmetry(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        s1 = json.load(f)
    with open(f"data/C_{n}_gamma.json", "r") as f:
        s2 = json.load(f)

    parity = s1["parity"]
    
    # Store gamma as (param, X, Y) -> {Z: coeff}
    gamma_map = {}
    for entry in s2["inhomogeneous_deformation"]["gamma_structure"]:
        param = entry["gb_param"]
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        gamma_map.setdefault((param, X, Y), {})[Z] = c

    for (param, X, Y), z_dict in gamma_map.items():
        pX, pY = parity[X], parity[Y]
        expected_sign = -1 if (pX * pY == 0) else 1  # -(-1)^(pX*pY)

        yx_dict = gamma_map.get((param, Y, X), {})
        for Z, c in z_dict.items():
            assert Z in yx_dict, f"Missing opposite pair in gamma for ({param}, {Y}, {X}) -> {Z}"
            assert yx_dict[Z] == expected_sign * c, f"Skew symmetry failed in gamma for ({param}, {X}, {Y}) -> {Z}"
