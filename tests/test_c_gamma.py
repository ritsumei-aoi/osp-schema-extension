import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_gamma import generate_gamma_schema


def test_gamma_schemas_match_schema1_basis_and_parameter_matrix():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    for n in (1, 2, 3):
        gamma = generate_gamma_schema(n)
        with (data_dir / f"C_{n}_structure.json").open(encoding="utf-8") as source:
            structure = json.load(source)
        expected_basis = set(structure["basis"]["even"] + structure["basis"]["odd"])
        deformation = gamma["inhomogeneous_deformation"]
        parameters = set(gamma["gb_matrix"]["parameters"])
        terms = deformation["gamma_coefficients"]

        assert gamma["algebra"]["n"] == structure["algebra"]["n"] == n
        assert gamma["algebra"]["schema1_file"] == f"C_{n}_structure.json"
        assert gamma["gb_matrix"]["shape"] == [2, 2 * n]
        assert len(parameters) == 4 * n
        assert {relation["parameter"] for relation in deformation["relations"]} == parameters
        assert {term["parameter"] for term in terms} == parameters
        assert len({
            (term["X"], term["Y"], term["Z"], term["parameter"])
            for term in terms
        }) == len(terms)
        assert all(term["X"] in expected_basis and term["Y"] in expected_basis
                   for term in terms)
        assert all(term["Z"] in expected_basis | {"K"} for term in terms)
        assert all(Fraction(term["coeff"]) != 0 for term in terms)
