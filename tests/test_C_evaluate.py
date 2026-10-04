import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_evaluate import evaluate


@pytest.mark.parametrize("n", (1, 2, 3))
def test_all_plus_evaluation_is_consistent(n):
    root = Path(__file__).resolve().parents[1]
    data = root / "data"
    structure = json.loads(
        (data / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    gamma = json.loads((data / f"C_{n}_gamma.json").read_text(encoding="utf-8"))
    evaluated = evaluate(gamma, structure)

    parameters = gamma["gb_matrix"]["parameters"]
    assignment = evaluated["deformation_evaluation"]["parameter_assignment"]
    assert len(assignment) == 4 * n
    assert set(assignment) == {item["label"] for item in parameters}
    assert set(assignment.values()) == {1}
    assert evaluated["structure_constants"] == structure["structure_constants"]
    assert evaluated["algebra"] == structure["algebra"]

    expected = defaultdict(Fraction)
    for term in gamma["inhomogeneous_deformation"]["gamma_coefficients"]:
        expected[(term["X"], term["Y"], term["Z"])] += Fraction(term["coeff"])
    actual = {
        (term["X"], term["Y"], term["Z"]): Fraction(term["coeff"])
        for term in evaluated["deformation_evaluation"]["gamma_coefficients"]
    }
    assert actual == {key: value for key, value in expected.items() if value}
    assert evaluated["deformation_evaluation"]["parity_status"] == "formal_only"


@pytest.mark.parametrize("n", (1, 2, 3))
def test_committed_evaluated_files_match_substitution(n):
    root = Path(__file__).resolve().parents[1]
    data = root / "data"
    structure = json.loads(
        (data / f"C_{n}_structure.json").read_text(encoding="utf-8")
    )
    gamma = json.loads((data / f"C_{n}_gamma.json").read_text(encoding="utf-8"))
    committed = json.loads(
        (data / f"C_{n}_evaluated.json").read_text(encoding="utf-8")
    )
    generated = evaluate(gamma, structure)
    committed["metadata"]["generation_date"] = generated["metadata"]["generation_date"]
    assert committed == generated
