import json
from pathlib import Path

import pytest

from src.evaluate_C import evaluate_schema, validate_evaluation


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_schema_is_exact_substitution(n):
    data = ROOT / "data"
    structure = json.loads((data / f"C_{n}_structure.json").read_text())
    gamma_schema = json.loads((data / f"C_{n}_gamma.json").read_text())
    evaluated = evaluate_schema(structure, gamma_schema)
    assert evaluated["assignment_profile"] == "all_plus_one"
    assert set(evaluated["parameter_assignment"].values()) == {1}
    assert not validate_evaluation(evaluated, structure, gamma_schema)
    assert len(evaluated["parameter_assignment"]) == 4 * n


def test_evaluation_requires_all_parameters():
    data = ROOT / "data"
    structure = json.loads((data / "C_1_structure.json").read_text())
    gamma_schema = json.loads((data / "C_1_gamma.json").read_text())
    with pytest.raises(ValueError, match="exactly all"):
        evaluate_schema(structure, gamma_schema, {})
