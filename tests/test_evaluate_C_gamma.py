import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import pytest

from src.evaluate_C_gamma import evaluate_schema


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluation_substitutes_all_positive_profile(n):
    data_dir = Path(__file__).parents[1] / "data"
    schema = evaluate_schema(n, data_dir)
    symbolic = json.loads((data_dir / f"C_{n}_gamma.json").read_text())
    structure = json.loads((data_dir / f"C_{n}_structure.json").read_text())
    assignment = schema["evaluation"]["gb_assignment"]

    assert schema["evaluation"]["profile"] == "all_positive"
    assert len(assignment) == 4 * n
    assert set(assignment.values()) == {1}
    assert schema["basis"] == structure["basis"]
    assert schema["parity"] == structure["parity"]

    expected_gamma = defaultdict(Fraction)
    for term in symbolic["inhomogeneous_deformation"]["gamma_coefficients"]:
        expected_gamma[(term["X"], term["Y"], term["Z"])] += Fraction(
            term["coeff"]
        ) * assignment[term["gb_parameter"]]
    actual_gamma = {
        (term["X"], term["Y"], term["Z"]): Fraction(term["coeff"])
        for term in schema["inhomogeneous_deformation"]["evaluated_gamma_coefficients"]
    }
    assert actual_gamma == {
        key: coeff for key, coeff in expected_gamma.items() if coeff
    }

    actual_constants = {
        (term["X"], term["Y"], term["Z"]): term
        for term in schema["structure_constants"]
    }
    for term in structure["structure_constants"]:
        key = (term["X"], term["Y"], term["Z"])
        assert Fraction(actual_constants[key]["undeformed_coeff"]) == Fraction(
            term["coeff"]
        )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_files_match_generated_schema(n):
    data_dir = Path(__file__).parents[1] / "data"
    path = data_dir / f"C_{n}_evaluated.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    assert schema["algebra"]["n"] == n
    assert schema["evaluation"]["profile"] == "all_positive"
    assert schema["inhomogeneous_deformation"]["evaluated_term_count"] > 0


def test_invalid_rank_is_rejected():
    with pytest.raises(ValueError, match="positive integer"):
        evaluate_schema(0)
