from fractions import Fraction
import json
import os
import pytest

from src.C_generators import get_C_generators
from src.C_coboundary import (
    compute_delta_f_coefficients,
    solve_triviality,
    build_schema_4_json,
    generate_and_save_all_coboundary
)


@pytest.mark.parametrize("n,expected_phi_count", [
    (1, 32),
    (2, 176),
    (3, 528),
])
def test_map_f_parameter_counts(n, expected_phi_count):
    delta_f_map, param_names, phi_params = compute_delta_f_coefficients(n)
    assert len(param_names) == expected_phi_count
    assert len(phi_params) == expected_phi_count


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_antisymmetry_and_parity(n):
    even_basis, odd_basis, parity, _, _ = get_C_generators(n)
    all_basis = odd_basis + even_basis
    delta_f_map, param_names, _ = compute_delta_f_coefficients(n)

    for p in param_names[:20]:  # check sample
        for x in all_basis:
            px = parity[x]
            for y in all_basis:
                py = parity[y]
                sign = -1 if (px == 1 and py == 1) else 1
                b_xy = delta_f_map[p].get((x, y), {})
                b_yx = delta_f_map[p].get((y, x), {})

                for z in all_basis:
                    c_xy = b_xy.get(z, Fraction(0))
                    c_yx = b_yx.get(z, Fraction(0))
                    expected_yx = - Fraction(sign) * c_xy
                    assert c_yx == expected_yx, f"Coboundary antisymmetry failed for ({x}, {y}) on {z}, param {p}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_triviality_verification_all_ones(n):
    res = solve_triviality(n)
    assert res["is_trivial"] is True
    assert res["residual_norm"] < 1e-6


def test_schema_4_generation():
    generate_and_save_all_coboundary("data")
    for n in [1, 2, 3]:
        file_path = f"data/C_{n}_coboundary.json"
        assert os.path.exists(file_path)
        with open(file_path, "r") as f:
            d = json.load(f)
        assert d["schema_version"] == "5.0"
        assert d["algebra"]["family"] == "C"
        assert d["triviality_verification"]["is_trivial"] is True
