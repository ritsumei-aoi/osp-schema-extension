from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from src.C_coboundary import build_coboundary_schema


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("rank", "expected_coefficient_count"),
    ((1, 32), (2, 176), (3, 528)),
)
def test_coboundary_map_and_coefficients_match_schema_1(
    rank: int, expected_coefficient_count: int
) -> None:
    structure = json.loads(
        (ROOT / "data" / f"C_{rank}_structure.json").read_text(encoding="utf-8")
    )
    coboundary = build_coboundary_schema(rank, structure)
    parity = structure["parity"]
    basis = list(parity)
    phi_names = set()

    assert coboundary["schema_layer"] == 4
    assert coboundary["algebra"]["n"] == rank
    assert coboundary["source_schema"] == f"C_{rank}_structure.json"
    assert coboundary["f"]["parity"] == 1
    assert coboundary["f"]["coefficient_count"] == expected_coefficient_count
    for item in coboundary["f"]["map"]:
        assert item["source"] in parity
        assert item["target"] in parity
        assert parity[item["source"]] != parity[item["target"]]
        assert item["coefficient"] == f"phi_{item['target']}_{item['source']}"
        phi_names.add(item["coefficient"])
    assert len(phi_names) == expected_coefficient_count

    index = {
        label: position
        for position, label in enumerate(
            structure["generator_realization"]["realizations"]
        )
    }
    for entry in coboundary["coboundary"]["entries"]:
        assert entry["X"] in parity and entry["Y"] in parity and entry["Z"] in parity
        assert index[entry["X"]] <= index[entry["Y"]]
        assert parity[entry["Z"]] == (
            parity[entry["X"]] + parity[entry["Y"]] + 1
        ) % 2
        assert entry["sign_rule"] == "graded"
        for term in entry["terms"]:
            assert term["phi"] in phi_names
            assert Fraction(term["coeff"])


def test_coboundary_rejects_mismatched_rank() -> None:
    structure = json.loads(
        (ROOT / "data" / "C_1_structure.json").read_text(encoding="utf-8")
    )
    with pytest.raises(ValueError, match="does not match"):
        build_coboundary_schema(2, structure)
