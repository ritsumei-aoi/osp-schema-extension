import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_evaluate import all_positive_assignment, evaluate_schema


@pytest.mark.parametrize("n", [1, 2, 3])
def test_all_positive_evaluation_matches_gamma_data(n):
    data_dir = Path(__file__).resolve().parents[1] / "data"
    evaluated = evaluate_schema(
        data_dir / f"C_{n}_structure.json",
        data_dir / f"C_{n}_gamma.json",
    )
    schema2 = json.loads((data_dir / f"C_{n}_gamma.json").read_text())

    assert len(all_positive_assignment(n)) == 4 * n
    assert len(evaluated["evaluation"]["gb_assignment"]) == 4 * n
    assert evaluated["base_structure_constants"] == json.loads(
        (data_dir / f"C_{n}_structure.json").read_text()
    )["structure_constants"]
    assert evaluated["consistency"]["schema1_closed"] == schema2[
        "inhomogeneous_deformation"
    ]["consistency"]["schema1_closed"]
    assert evaluated["evaluated_gamma_coefficients"]


def test_invalid_rank_is_rejected():
    with pytest.raises(ValueError, match="positive integer"):
        all_positive_assignment(0)
