import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.compare_C_triviality import (
    _parse_linear_expression,
    analyze_triviality,
)


@pytest.mark.parametrize("rank", [1, 2, 3])
def test_triviality_conditions_and_central_obstructions(rank):
    data_dir = Path(__file__).resolve().parents[1] / "data"
    structure = json.loads(
        (data_dir / f"C_{rank}_structure.json").read_text(encoding="utf-8")
    )
    gamma = json.loads(
        (data_dir / f"C_{rank}_gamma.json").read_text(encoding="utf-8")
    )
    coboundary = json.loads(
        (data_dir / f"C_{rank}_coboundary.json").read_text(encoding="utf-8")
    )

    result = analyze_triviality(structure, gamma, coboundary)
    parameters = result["gb_parameters"]
    assert result["all_plus_trivial"] is False
    assert result["trivial_parameter_dimension"] == 0
    assert set(result["central_witnesses"]) == set(parameters)
    assert set(result["necessary_sufficient_conditions"]) == {
        f"{parameter} = 0" for parameter in parameters
    }

    records = gamma["inhomogeneous_deformation"]["gamma_coefficients"]
    for index in range(1, rank + 1):
        expected = [
            ("E_2del" + str(index) + "_p", f"E_eps_del{index}_pm",
             f"gb_a_1_p_b_{index}_p", Fraction(-1)),
            ("E_2del" + str(index) + "_m", f"E_eps_del{index}_pp",
             f"gb_a_1_p_b_{index}_m", Fraction(1)),
            (f"E_eps_del{index}_mm", "E_2del" + str(index) + "_p",
             f"gb_a_1_m_b_{index}_p", Fraction(1)),
            ("E_2del" + str(index) + "_m", f"E_eps_del{index}_mp",
             f"gb_a_1_m_b_{index}_m", Fraction(1)),
        ]
        for x, y, parameter, coefficient in expected:
            match = next(
                entry for entry in records
                if entry["X"] == x and entry["Y"] == y and entry["Z"] == "K"
            )
            assert _parse_linear_expression(match["coeff"], "gb_") == {
                parameter: coefficient
            }
