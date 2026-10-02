import json
from pathlib import Path

import pytest

from src.C_coboundary_generator import (
    _add_symbolic,
    _bracket_table,
    _coboundary,
    _scale_symbolic,
    build_coboundary_schema,
    validate_coboundary_schema,
)


@pytest.mark.parametrize("rank", [1, 2, 3])
def test_coboundary_schema_is_generic_odd_map_on_structure_basis(rank):
    data_dir = Path(__file__).resolve().parents[1] / "data"
    structure = json.loads(
        (data_dir / f"C_{rank}_structure.json").read_text(encoding="utf-8")
    )
    coboundary = json.loads(
        (data_dir / f"C_{rank}_coboundary.json").read_text(encoding="utf-8")
    )

    validate_coboundary_schema(coboundary, structure)
    even_count = len(structure["basis"]["even"])
    odd_count = len(structure["basis"]["odd"])
    assert len(coboundary["odd_linear_map"]["entries"]) == 2 * even_count * odd_count
    assert coboundary["odd_linear_map"]["parity"] == 1
    for entry in coboundary["coboundary"]["coefficients"]:
        expected_parity = (
            structure["parity"][entry["X"]]
            + structure["parity"][entry["Y"]]
            + 1
        ) % 2
        assert structure["parity"][entry["Z"]] == expected_parity

    regenerated = build_coboundary_schema(
        structure, coboundary["metadata"]["generation_date"]
    )
    assert regenerated == coboundary

    labels, parity, bracket = _bracket_table(structure)
    targets = {
        value: [label for label in labels if parity[label] == value]
        for value in (0, 1)
    }
    for x in labels:
        for y in labels:
            sign = -1 if parity[x] and parity[y] else 1
            skew_sum = _add_symbolic(
                _coboundary(x, y, parity, targets, bracket),
                _scale_symbolic(_coboundary(y, x, parity, targets, bracket), sign),
            )
            assert not skew_sum
