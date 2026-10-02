import json
from pathlib import Path

import pytest

from src.C_gamma_generator import build_gamma_schema, validate_consistency


@pytest.mark.parametrize("rank", [1, 2, 3])
def test_gamma_schema_matches_structure_and_gb_matrix(rank):
    data_dir = Path(__file__).resolve().parents[1] / "data"
    structure_path = data_dir / f"C_{rank}_structure.json"
    gamma_path = data_dir / f"C_{rank}_gamma.json"
    structure = json.loads(structure_path.read_text(encoding="utf-8"))
    gamma = json.loads(gamma_path.read_text(encoding="utf-8"))

    validate_consistency(gamma, structure)
    assert gamma["gb_matrix"]["shape"] == [2, 2 * rank]
    assert sum(map(len, gamma["gb_matrix"]["entries"])) == 4 * rank
    assert gamma["source_schema"] == structure_path.name
    assert gamma["inhomogeneous_deformation"]["gamma_coefficients"]

    regenerated = build_gamma_schema(rank, structure, gamma["metadata"]["generation_date"])
    assert regenerated == gamma


def test_gamma_coefficients_may_target_declared_central_identity():
    gamma = json.loads(
        (Path(__file__).resolve().parents[1] / "data/C_1_gamma.json").read_text(
            encoding="utf-8"
        )
    )
    records = gamma["inhomogeneous_deformation"]["gamma_coefficients"]
    assert any(record["Z"] == "K" for record in records)
