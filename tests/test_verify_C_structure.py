import json
from pathlib import Path

import pytest

from src.verify_C_structure import verify_schema


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generated_schema_passes_graded_verification(n):
    schema = json.loads((ROOT / "data" / f"C_{n}_structure.json").read_text())
    result = verify_schema(schema)
    assert result["passed"], result["errors"]
    count = (2 * n**2 + n + 1) + 4 * n
    assert result["antisymmetry_pairs"] == count**2
    assert result["jacobi_triples"] == count**3


def test_verifier_reports_incorrect_parity():
    schema = json.loads((ROOT / "data" / "C_1_structure.json").read_text())
    schema["parity"]["H_1"] = 1
    result = verify_schema(schema)
    assert not result["passed"]
    assert any("Parity keys" not in error for error in result["errors"])
