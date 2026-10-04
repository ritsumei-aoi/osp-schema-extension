import json
import pytest
from src.C_gamma_generators import generate_schema_2

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_2_structure(n):
    schema2 = generate_schema_2(n)
    assert schema2["schema_version"] == "5.0"
    assert "inhomogeneous_deformation" in schema2
    
    inhom = schema2["inhomogeneous_deformation"]
    gb_matrix = inhom["gb_matrix"]
    assert gb_matrix["dimensions"] == [2, 2 * n]
    assert len(gb_matrix["parameters"]) == 4 * n
    
    gamma_sc = inhom["gamma_structure_constants"]
    assert len(gamma_sc) > 0

    # Check consistency of fields with Schema 1
    assert schema2["algebra"]["n"] == n
    assert schema2["algebra"]["family"] == "C"
