import json
from pathlib import Path

import pytest

from src.C_coboundary import build_coboundary_schema

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_map_and_outputs_match_schema_one(n):
    coboundary = build_coboundary_schema(n)
    with (ROOT / "data" / f"C_{n}_structure.json").open(encoding="utf-8") as stream:
        structure = json.load(stream)

    basis = structure["basis"]["even"] + structure["basis"]["odd"]
    parity = structure["parity"]
    assert coboundary["source_schema"] == f"C_{n}_structure.json"
    assert set(coboundary["odd_linear_map"]["coefficients"]) == set(basis)

    parameter_names = set()
    for source, mappings in coboundary["odd_linear_map"]["coefficients"].items():
        assert mappings
        for mapping in mappings:
            assert mapping["target"] in basis
            assert parity[mapping["target"]] == 1 - parity[source]
            parameter_names.add(mapping["parameter"])

    for entry in coboundary["coboundary_definition"]["coboundary_coefficients"]:
        assert entry["X"] in basis
        assert entry["Y"] in basis
        assert entry["Z"] in basis
        assert parity[entry["Z"]] == (parity[entry["X"]] + parity[entry["Y"]] + 1) % 2
        assert entry["coefficients"]
        assert all(term["parameter"] in parameter_names for term in entry["coefficients"])


def test_coboundary_of_equal_even_inputs_cancels():
    coboundary = build_coboundary_schema(1)
    equal_even_terms = [
        entry
        for entry in coboundary["coboundary_definition"]["coboundary_coefficients"]
        if entry["X"] == entry["Y"] == "H_1"
    ]

    assert equal_even_terms == []
