import json
from pathlib import Path

import pytest

from src.C_coboundary import generate_coboundary_schema


@pytest.mark.parametrize(
    ("n", "even_count", "odd_count"),
    [(1, 4, 4), (2, 11, 8), (3, 22, 12)],
)
def test_odd_map_parameterization_and_coboundary_closure(
    n, even_count, odd_count
):
    data_dir = Path(__file__).parents[1] / "data"
    schema = generate_coboundary_schema(n, data_dir)
    basis = set(schema["basis"]["even"] + schema["basis"]["odd"])
    parameters = schema["odd_linear_map"]["parameters"]

    assert schema["odd_linear_map"]["parity"] == 1
    assert schema["odd_linear_map"]["coefficient_parity"] == 0
    assert len(parameters) == 2 * even_count * odd_count
    assert all(item["source"] in basis and item["target"] in basis for item in parameters)
    assert all(
        schema["parity"][item["source"]] != schema["parity"][item["target"]]
        for item in parameters
    )
    assert schema["coboundary_coefficients"]
    assert all(
        record["X"] in basis
        and record["Y"] in basis
        and record["Z"] in basis
        and record["sign_rule"] == "graded"
        and record["terms"]
        for record in schema["coboundary_coefficients"]
    )
    known_parameters = {item["name"] for item in parameters}
    assert all(
        term["phi_parameter"] in known_parameters
        for record in schema["coboundary_coefficients"]
        for term in record["terms"]
    )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generated_coboundary_files_match_schema_contract(n):
    path = Path(__file__).parents[1] / "data" / f"C_{n}_coboundary.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    assert schema["algebra"]["n"] == n
    assert schema["odd_linear_map"]["parity"] == 1
    assert schema["coboundary_coefficients"]


def test_invalid_rank_is_rejected():
    with pytest.raises(ValueError, match="positive integer"):
        generate_coboundary_schema(0)
