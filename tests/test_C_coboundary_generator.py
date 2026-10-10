import json
from pathlib import Path

import pytest
import sympy as sp

from src.C_coboundary_generator import build_coboundary_schema


@pytest.mark.parametrize(("n", "even_count", "odd_count"), [(1, 4, 4), (2, 11, 8), (3, 22, 12)])
def test_odd_map_parameters_reverse_parity(n, even_count, odd_count):
    structure = json.loads(
        (Path("data") / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    schema = build_coboundary_schema(n, structure)
    parameters = schema["odd_linear_map"]["parameters"]

    assert len(parameters) == 2 * even_count * odd_count
    assert schema["odd_linear_map"]["coefficient_parity"] == 0
    assert all(item["input_parity"] != item["output_parity"] for item in parameters)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_coboundary_coefficients_are_parity_correct_and_skew(n):
    structure = json.loads(
        (Path("data") / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    schema = build_coboundary_schema(n, structure)
    entries = schema["coboundary_coefficients"]
    parity = structure["parity"]
    coefficients = {
        (entry["X"], entry["Y"], entry["Z"]): sp.sympify(entry["coeff"])
        for entry in entries
    }
    allowed_symbols = {
        sp.Symbol(parameter["symbol"])
        for parameter in schema["odd_linear_map"]["parameters"]
    }

    assert entries
    for (left, right, output), coefficient in coefficients.items():
        assert parity[output] == (
            parity[left] + parity[right] + 1
        ) % 2
        factor = 1 if parity[left] * parity[right] % 2 else -1
        assert coefficients[(right, left, output)] == factor * coefficient
        assert coefficient.free_symbols <= allowed_symbols
        symbols = tuple(sorted(coefficient.free_symbols, key=str))
        assert sp.Poly(coefficient, *symbols).total_degree() == 1


def test_coboundary_schema_references_matching_structure_file():
    structure = json.loads(
        Path("data/C_1_structure.json").read_text(encoding="utf-8")
    )
    schema = build_coboundary_schema(1, structure, generation_date="2026-01-01")

    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["source_structure_file"] == "C_1_structure.json"
    assert schema["odd_linear_map"]["global_scale"] == "absorbed_into_phi_ij"
    assert schema["metadata"]["generation_date"] == "2026-01-01"
