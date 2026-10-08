from fractions import Fraction

import pytest

from src.C_gamma import build_gamma_schema
from src.C_generators import build_schema


@pytest.mark.parametrize(("n", "gamma_count"), [(1, 60), (2, 334), (3, 932)])
def test_gamma_schema_references_schema1_basis(n, gamma_count):
    gamma_schema = build_gamma_schema(n, generation_date="2026-10-08")
    structure = build_schema(n, generation_date="2026-10-08")
    deformation = gamma_schema["inhomogeneous_deformation"]
    parameters = {
        item["label"]
        for item in deformation["gb_matrix"]["parameters"]
    }
    output_labels = set(structure["parity"]) | {"K"}
    entries = deformation["gamma_coefficients"]

    assert deformation["gb_matrix"]["shape"] == [2, 2 * n]
    assert len(parameters) == 4 * n
    assert len(entries) == gamma_count
    assert deformation["nonzero_gamma_count"] == gamma_count
    assert gamma_schema["source_schema1"] == f"C_{n}_structure.json"
    assert len({(e["X"], e["Y"], e["Z"]) for e in entries}) == len(entries)
    for entry in entries:
        assert entry["X"] in structure["parity"]
        assert entry["Y"] in structure["parity"]
        assert entry["Z"] in output_labels
        assert entry["coefficients"]
        for term in entry["coefficients"]:
            assert term["parameter"] in parameters
            assert Fraction(term["coeff"]) != 0
