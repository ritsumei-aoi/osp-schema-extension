"""Unit tests for Schema 2 (gamma deformation structure) for C(n+1)."""

from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import pytest


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema2_json_conformance_and_consistency_with_schema1(n):
    gamma_path = Path(f"data/C_{n}_gamma.json")
    struct_path = Path(f"data/C_{n}_structure.json")
    assert gamma_path.exists()
    assert struct_path.exists()

    with open(gamma_path, "r", encoding="utf-8") as f:
        gdata = json.load(f)
    with open(struct_path, "r", encoding="utf-8") as f:
        sdata = json.load(f)

    # Check top-level keys
    required_keys = [
        "schema_version",
        "algebra",
        "central_elements",
        "gb_matrix",
        "basis",
        "parity",
        "inhomogeneous_deformation",
        "metadata",
    ]
    for k in required_keys:
        assert k in gdata, f"Missing top-level key {k} in Schema 2"

    # Consistency with Schema 1
    assert gdata["schema_version"] == sdata["schema_version"]
    assert gdata["algebra"] == sdata["algebra"]
    assert gdata["central_elements"] == sdata["central_elements"]
    assert gdata["basis"] == sdata["basis"]
    assert gdata["parity"] == sdata["parity"]

    # gb_matrix check
    gb_info = gdata["gb_matrix"]
    assert gb_info["dimensions"] == [2, 2 * n]
    assert gb_info["total_parameters"] == 4 * n
    assert gb_info["fermionic_oscillators"] == ["a_1_p", "a_1_m"]
    assert len(gb_info["bosonic_oscillators"]) == 2 * n
    assert len(gb_info["matrix"]) == 2
    assert len(gb_info["matrix"][0]) == 2 * n
    assert len(gb_info["matrix"][1]) == 2 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_properties(n):
    with open(f"data/C_{n}_gamma.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    parities = data["parity"]
    all_gens = set(data["basis"]["odd"] + data["basis"]["even"])
    valid_gbs = set(p for row in data["gb_matrix"]["matrix"] for p in row)

    gamma_table = defaultdict(dict)
    for entry in data["inhomogeneous_deformation"]["gamma_coefficients"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        gb = entry["gb"]
        coeff = Fraction(entry["coeff"])

        assert x in all_gens
        assert y in all_gens
        assert z in all_gens
        assert gb in valid_gbs

        # Parity check: p(Z) = p(X) + p(Y) + 1 (mod 2)
        px, py, pz = parities[x], parities[y], parities[z]
        expected_pz = (px + py + 1) % 2
        assert pz == expected_pz, f"Parity mismatch for ({x}, {y}) -> {z}"

        gamma_table[(x, y, gb)][z] = coeff

    # Anti-symmetry check: gamma(Y, X) = -(-1)^(p(X)p(Y)) gamma(X, Y)
    all_gen_list = data["basis"]["odd"] + data["basis"]["even"]
    for x in all_gen_list:
        for y in all_gen_list:
            px, py = parities[x], parities[y]
            sign = -1 if (px * py == 1) else 1
            for gb in valid_gbs:
                d_xy = gamma_table.get((x, y, gb), {})
                d_yx = gamma_table.get((y, x, gb), {})
                all_targets = set(d_xy.keys()) | set(d_yx.keys())
                for z in all_targets:
                    c_xy = d_xy.get(z, Fraction(0))
                    c_yx = d_yx.get(z, Fraction(0))
                    assert c_yx == -sign * c_xy, f"Gamma anti-symmetry failure for [{x}, {y}] with {gb} -> {z}"
