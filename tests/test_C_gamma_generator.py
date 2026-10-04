import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_gamma_generator import build_gamma_schema
from src.C_generators import build_schema


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(params=(1, 2, 3))
def gamma_data(request):
    n = request.param
    return n, build_gamma_schema(n)


def test_gamma_schema_matches_structure_and_gb_matrix(gamma_data):
    n, gamma = gamma_data
    structure = build_schema(n)
    basis = structure["basis"]["odd"] + structure["basis"]["even"]
    assert gamma["source_schema1"] == f"C_{n}_structure.json"
    assert gamma["algebra"] == structure["algebra"]
    matrix = gamma["gb_matrix"]
    assert matrix["shape"] == [2, 2 * n]
    assert matrix["parity"] == 0
    assert len(matrix["entries"]) == 2
    assert all(len(row) == 2 * n for row in matrix["entries"])
    assert len(
        {
            parameter
            for row in matrix["entries"]
            for parameter in row
        }
    ) == 4 * n
    assert len(gamma["inhomogeneous_deformation"]["deformed_mixed_commutators"]) == 4 * n

    known_parameters = {
        parameter
        for row in matrix["entries"]
        for parameter in row
    }
    used_parameters = set()
    for record in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        assert record["X"] in basis
        assert record["Y"] in basis
        assert record["Z"] in set(basis) | {"K"}
        assert basis.index(record["X"]) <= basis.index(record["Y"])
        assert record["sign_rule"] == "graded"
        expected_parity = (
            structure["parity"][record["X"]]
            + structure["parity"][record["Y"]]
            + 1
        ) % 2
        actual_parity = 0 if record["Z"] == "K" else structure["parity"][record["Z"]]
        assert actual_parity == expected_parity
        for term in record["coefficients"]:
            assert term["parameter"] in known_parameters
            assert Fraction(term["coeff"])
            used_parameters.add(term["parameter"])
    assert used_parameters == known_parameters


def test_gamma_files_match_generated_data(gamma_data):
    n, gamma = gamma_data
    path = DATA_DIR / f"C_{n}_gamma.json"
    assert json.loads(path.read_text(encoding="utf-8")) == gamma
