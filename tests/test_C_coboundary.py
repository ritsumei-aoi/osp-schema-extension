from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.C_coboundary import build_coboundary_schema


EXPECTED_COUNTS = {
    1: (4, 4, 32),
    2: (11, 8, 176),
    3: (22, 12, 528),
}


@pytest.mark.parametrize("n", (1, 2, 3))
def test_odd_map_and_coboundary_match_layer1(n: int) -> None:
    schema = build_coboundary_schema(n)
    generated = json.loads(
        (Path("data") / f"C_{n}_coboundary.json").read_text(encoding="utf-8")
    )
    even_count, odd_count, parameter_count = EXPECTED_COUNTS[n]
    map_data = schema["linear_map_f"]
    even_to_odd = map_data["even_to_odd"]
    odd_to_even = map_data["odd_to_even"]
    source = json.loads(
        (Path("data") / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    generators = set(source["basis"]["even"] + source["basis"]["odd"])
    parameters = {
        parameter
        for block in (even_to_odd, odd_to_even)
        for row in block["coefficients"]
        for parameter in row
    }

    assert map_data["parity"] == 1
    assert map_data["normalization"] == "unit"
    assert generated == schema
    assert len(even_to_odd["row_labels"]) == odd_count
    assert len(even_to_odd["column_labels"]) == even_count
    assert len(odd_to_even["row_labels"]) == even_count
    assert len(odd_to_even["column_labels"]) == odd_count
    assert len(parameters) == parameter_count
    assert all(
        entry["X"] in generators
        and entry["Y"] in generators
        and entry["Z"] in generators
        for entry in schema["coboundary_coefficients"]
    )
