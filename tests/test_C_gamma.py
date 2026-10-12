"""
Unit tests for Schema 2 (gamma structure) computation and consistency.
"""

import json
import os
import pytest
from src.C_gamma import compute_gamma_structure, get_gb_params, generate_all_gamma_schemas


@pytest.mark.parametrize("n, expected_params", [
    (1, 4),
    (2, 8),
    (3, 12),
])
def test_gb_params(n, expected_params):
    params = get_gb_params(n)
    assert len(params) == expected_params
    assert len(set(params)) == expected_params


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema2_consistency_with_schema1(n):
    # Load Schema 1 file
    with open(f"data/C_{n}_structure.json", "r", encoding="utf-8") as f:
        schema1 = json.load(f)

    schema2 = compute_gamma_structure(n)

    # Check that base schema 1 fields are identical
    for key in ("schema_version", "algebra", "central_elements", "oscillator_generators",
                "oscillator_relations", "basis", "parity", "generator_realization",
                "structure_constants"):
        assert schema1[key] == schema2[key], f"Schema 1 and 2 mismatch in key {key} for n={n}"

    # Check inhomogeneous deformation field
    assert "inhomogeneous_deformation" in schema2
    inhom = schema2["inhomogeneous_deformation"]
    assert inhom["parameters"]["count"] == 4 * n
    assert inhom["parameters"]["matrix_shape"] == [2, 2 * n]
    assert len(inhom["gamma_constants"]) > 0


def test_generated_gamma_json_files(tmp_path):
    out_dir = str(tmp_path)
    generate_all_gamma_schemas(output_dir=out_dir)
    for n in (1, 2, 3):
        filepath = os.path.join(out_dir, f"C_{n}_gamma.json")
        assert os.path.isfile(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["algebra"]["cartan_type"] == f"C({n+1})"
            assert "inhomogeneous_deformation" in data
            assert len(data["inhomogeneous_deformation"]["gamma_constants"]) > 0
