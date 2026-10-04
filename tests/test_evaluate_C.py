from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.evaluate_C import build_evaluated_schema


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("rank", (1, 2, 3))
def test_all_plus_evaluation_matches_schema_1_and_schema_2(rank: int) -> None:
    data_dir = ROOT / "data"
    structure = json.loads(
        (data_dir / f"C_{rank}_structure.json").read_text(encoding="utf-8")
    )
    gamma = json.loads(
        (data_dir / f"C_{rank}_gamma.json").read_text(encoding="utf-8")
    )
    evaluated = build_evaluated_schema(rank, structure, gamma)
    expected: dict[tuple[str, str, str], list[Fraction]] = {}
    for entry in structure["structure_constants"]:
        key = entry["X"], entry["Y"], entry["Z"]
        expected.setdefault(key, [Fraction(0), Fraction(0)])[0] += Fraction(
            entry["coeff"]
        )
    for entry in gamma["gamma_structure"]:
        key = entry["X"], entry["Y"], entry["Z"]
        expected.setdefault(key, [Fraction(0), Fraction(0)])[1] += Fraction(
            entry["coeff"]
        )

    actual = {
        (entry["X"], entry["Y"], entry["Z"]): (
            Fraction(entry["coeff"]),
            Fraction(entry["kappa_coeff"]),
        )
        for entry in evaluated["structure_constants"]
    }
    assert evaluated["schema_layer"] == 3
    assert evaluated["gb_assignment"]["profile"] == "all_plus"
    assert set(evaluated["gb_assignment"]["values"].values()) == {1}
    assert len(evaluated["gb_assignment"]["values"]) == 4 * rank
    assert actual == {key: tuple(value) for key, value in expected.items() if any(value)}


def test_evaluation_rejects_mismatched_rank() -> None:
    structure = json.loads(
        (ROOT / "data" / "C_1_structure.json").read_text(encoding="utf-8")
    )
    gamma = json.loads(
        (ROOT / "data" / "C_1_gamma.json").read_text(encoding="utf-8")
    )
    with pytest.raises(ValueError, match="does not match"):
        build_evaluated_schema(2, structure, gamma)
