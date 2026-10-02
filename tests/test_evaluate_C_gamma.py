import json
from pathlib import Path

import pytest

from src.evaluate_C_gamma import (
    evaluate_gamma_schema,
    validate_evaluated_schema,
)


@pytest.mark.parametrize("rank", [1, 2, 3])
def test_evaluated_schema_substitutes_all_plus_and_matches_sources(rank):
    data_dir = Path(__file__).resolve().parents[1] / "data"
    structure = json.loads(
        (data_dir / f"C_{rank}_structure.json").read_text(encoding="utf-8")
    )
    gamma = json.loads(
        (data_dir / f"C_{rank}_gamma.json").read_text(encoding="utf-8")
    )
    evaluated = json.loads(
        (data_dir / f"C_{rank}_evaluated.json").read_text(encoding="utf-8")
    )

    validate_evaluated_schema(evaluated, structure, gamma)
    assert len(evaluated["gb_assignment"]["values"]) == 4 * rank
    assert set(evaluated["gb_assignment"]["values"].values()) == {1}

    regenerated = evaluate_gamma_schema(
        structure,
        gamma,
        assignment_name=evaluated["gb_assignment"]["name"],
        generation_date=evaluated["metadata"]["generation_date"],
    )
    assert regenerated == evaluated
