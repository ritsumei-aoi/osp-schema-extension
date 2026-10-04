import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.evaluate_C_gamma import evaluate_schema1_schema2


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(params=(1, 2, 3))
def evaluated(request):
    n = request.param
    structure = json.loads(
        (DATA_DIR / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    gamma = json.loads(
        (DATA_DIR / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )
    return n, structure, gamma, evaluate_schema1_schema2(structure, gamma)


def test_evaluated_data_preserves_schema1_and_substitutes_every_parameter(evaluated):
    n, structure, gamma, result = evaluated
    values = result["gb_assignment"]["values"]
    expected_parameters = {
        parameter
        for row in gamma["gb_matrix"]["entries"]
        for parameter in row
    }
    assert result["gb_assignment"]["profile"] == "all_plus"
    assert set(values) == expected_parameters
    assert set(values.values()) == {1}
    assert result["algebra"] == structure["algebra"]
    assert result["source_schema1"] == f"C_{n}_structure.json"
    assert result["source_schema2"] == f"C_{n}_gamma.json"

    output_map = {
        (record["X"], record["Y"], record["Z"]): record
        for record in result["evaluated_structure_constants"]
    }
    base_map = {
        (record["X"], record["Y"], record["Z"]): Fraction(record["coeff"])
        for record in structure["structure_constants"]
    }
    gamma_map = {}
    for record in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (record["X"], record["Y"], record["Z"])
        gamma_map[key] = gamma_map.get(key, Fraction(0)) + sum(
            Fraction(term["coeff"]) * values[term["parameter"]]
            for term in record["coefficients"]
        )

    assert set(output_map) == {
        key for key in set(base_map) | set(gamma_map)
        if base_map.get(key, Fraction(0)) or gamma_map.get(key, Fraction(0))
    }
    for key, record in output_map.items():
        assert Fraction(record["coeff"]) == base_map.get(key, Fraction(0))
        assert Fraction(record["kappa_coeff"]) == gamma_map.get(key, Fraction(0))


def test_evaluated_files_match_substitution(evaluated):
    n, _, _, result = evaluated
    path = DATA_DIR / f"C_{n}_evaluated.json"
    assert json.loads(path.read_text(encoding="utf-8")) == result


@pytest.mark.parametrize("n", (1, 2, 3))
def test_zero_assignment_matches_zero_coboundary(n):
    structure = json.loads(
        (DATA_DIR / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    gamma = json.loads(
        (DATA_DIR / f"C_{n}_gamma.json").read_text(encoding="utf-8")
    )
    result = evaluate_schema1_schema2(structure, gamma, "all_zero")
    assert result["gb_assignment"]["profile"] == "all_zero"
    assert set(result["gb_assignment"]["values"].values()) == {0}
    assert all(
        record["kappa_coeff"] == "0"
        for record in result["evaluated_structure_constants"]
    )
    assert all(
        record["coeff"] == "0"
        for record in result["evaluated_structure_constants"]
        if record["Z"] == "K"
    )
    path = DATA_DIR / f"C_{n}_evaluated_zero.json"
    assert json.loads(path.read_text(encoding="utf-8")) == result
