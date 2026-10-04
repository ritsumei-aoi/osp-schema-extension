import json
from pathlib import Path

import pytest

from src.C_coboundary import build_coboundary_schema, validate_against_structure


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_map_and_coefficients_match_basis(n):
    structure = json.loads((ROOT / "data" / f"C_{n}_structure.json").read_text())
    coboundary = build_coboundary_schema(structure)
    even = len(structure["basis"]["even"])
    odd = len(structure["basis"]["odd"])
    assert coboundary["odd_linear_map"]["parameter_count"] == 2 * even * odd
    assert not validate_against_structure(coboundary, structure)
    assert coboundary["coboundary_coefficients"]
    assert all(
        term["terms"]
        for term in coboundary["coboundary_coefficients"]
    )
    json.dumps(coboundary)
