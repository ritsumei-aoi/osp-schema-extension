import json
from pathlib import Path

import pytest

from src.C_gamma import build_gamma_schema

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_schema_matches_structure_and_gb_dimensions(n):
    gamma = build_gamma_schema(n)
    with (ROOT / "data" / f"C_{n}_structure.json").open(encoding="utf-8") as stream:
        structure = json.load(stream)

    matrix = gamma["gb_matrix"]
    assert matrix["shape"] == [2, 2 * n]
    assert matrix["rows"] == ["a_1_p", "a_1_m"]
    assert matrix["columns"] == structure["oscillator_generators"]["bosons"]["labels"]
    assert all(len(row) == 2 * n for row in matrix["parameters"])

    basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
    parameters = {parameter for row in matrix["parameters"] for parameter in row}
    for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        assert entry["X"] in basis
        assert entry["Y"] in basis
        assert entry["Z"] in basis | {"K"}
        assert entry["coefficients"]
        assert all(term["parameter"] in parameters for term in entry["coefficients"])


def test_rank_one_known_gamma_coefficient():
    gamma = build_gamma_schema(1)
    match = [
        entry
        for entry in gamma["inhomogeneous_deformation"]["gamma_coefficients"]
        if (entry["X"], entry["Y"], entry["Z"])
        == ("E_2del1_p", "E_eps1_del1_mp", "E_2del1_p")
    ]

    assert match == [{
        "X": "E_2del1_p",
        "Y": "E_eps1_del1_mp",
        "Z": "E_2del1_p",
        "coefficients": [{"parameter": "gb_a1_m_b1_p", "coeff": "-2"}],
    }]
