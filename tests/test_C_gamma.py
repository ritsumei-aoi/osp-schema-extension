import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_gamma import build_gamma_schema


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_matrix_and_terms(n):
    schema = build_gamma_schema(n)
    deformation = schema["inhomogeneous_deformation"]
    parameter_labels = {item["label"] for item in deformation["parameters"]}

    assert len(deformation["parameters"]) == 4 * n
    assert len(schema["gb_matrix"]["entries"]) == 2
    assert all(len(row) == 2 * n for row in schema["gb_matrix"]["entries"])
    assert all(item["parity"] == 1 for item in deformation["parameters"])
    assert deformation["gamma_coefficients"]
    assert all(item["parameter"] in parameter_labels for item in deformation["gamma_coefficients"])
    assert all(item["coeff"] != "0" for item in deformation["gamma_coefficients"])
    assert deformation["consistency"]["schema1_closed"] is False
    assert deformation["consistency"]["off_basis_terms"]
    assert deformation["consistency"]["grading_consistent"] is False
    coefficients = {
        (item["X"], item["Y"], item["Z"], item["parameter"]): Fraction(item["coeff"])
        for item in deformation["gamma_coefficients"]
    }
    for (x, y, z, parameter), coefficient in coefficients.items():
        parity_x = int(x.startswith("E_eps1_"))
        parity_y = int(y.startswith("E_eps1_"))
        sign = -1 if parity_x * parity_y == 0 else 1
        assert coefficients[(y, x, z, parameter)] == sign * coefficient


def test_invalid_gamma_rank_is_rejected():
    with pytest.raises(ValueError, match="positive integer"):
        build_gamma_schema(0)
