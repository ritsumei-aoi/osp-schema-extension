import json
from pathlib import Path

import pytest

from src.C_gamma import build_gamma_schema, validate_against_structure


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_schema_matches_base_structure(n):
    gamma_schema = build_gamma_schema(n)
    structure = json.loads((ROOT / "data" / f"C_{n}_structure.json").read_text())
    assert not validate_against_structure(gamma_schema, structure)
    assert gamma_schema["gb_matrix"]["shape"] == [2, 2 * n]
    assert gamma_schema["gb_matrix"]["parameter_count"] == 4 * n
    assert gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]
    assert len(gamma_schema["inhomogeneous_deformation"]["oscillator_exchange_relations"]) == 4 * n
    assert "parity-discrepant" in gamma_schema["inhomogeneous_deformation"]["parity_note"]
    assert any(
        entry["Z"] == "K"
        for entry in gamma_schema["inhomogeneous_deformation"]["gamma_coefficients"]
    )
    json.dumps(gamma_schema)
