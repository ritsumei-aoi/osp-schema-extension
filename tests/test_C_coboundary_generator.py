import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_coboundary_generator import build_coboundary_schema
from src.C_generators import build_schema


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(params=(1, 2, 3))
def coboundary_data(request):
    n = request.param
    structure = build_schema(n)
    return n, structure, build_coboundary_schema(structure)


def test_odd_map_and_coboundary_coefficients_use_schema1_basis(coboundary_data):
    n, structure, coboundary = coboundary_data
    basis = structure["basis"]["odd"] + structure["basis"]["even"]
    parameters = coboundary["linear_map_f"]["parameters"]
    expected_parameter_count = (
        len(structure["basis"]["even"]) * len(structure["basis"]["odd"]) * 2
    )
    assert len(parameters) == expected_parameter_count
    assert coboundary["linear_map_f"]["parity"] == 1
    for item in parameters:
        assert item["input"] in basis
        assert item["output"] in basis
        assert structure["parity"][item["input"]] != structure["parity"][item["output"]]
        assert item["parameter"] == (
            f"phi_{item['output']}_from_{item['input']}"
        )

    positions = {label: index for index, label in enumerate(basis)}
    parameter_names = {item["parameter"] for item in parameters}
    for record in coboundary["coboundary_coefficients"]:
        assert record["X"] in basis
        assert record["Y"] in basis
        assert record["Z"] in basis
        assert positions[record["X"]] <= positions[record["Y"]]
        assert record["sign_rule"] == "graded"
        expected_parity = (
            structure["parity"][record["X"]]
            + structure["parity"][record["Y"]]
            + 1
        ) % 2
        assert structure["parity"][record["Z"]] == expected_parity
        for term in record["coefficients"]:
            assert term["parameter"] in parameter_names
            assert Fraction(term["coeff"])


def test_coboundary_files_match_generator(coboundary_data):
    n, structure, coboundary = coboundary_data
    path = DATA_DIR / f"C_{n}_coboundary.json"
    assert json.loads(path.read_text(encoding="utf-8")) == coboundary
    assert coboundary["algebra"] == structure["algebra"]
