import json
import pytest
from src.evaluate_C_structure import evaluate_schema_3

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_3_structure(n):
    schema3 = evaluate_schema_3(n)
    assert schema3["schema_version"] == "5.0"
    assert "evaluated_structure" in schema3
    
    eval_struct = schema3["evaluated_structure"]
    assert len(eval_struct["gb_assignments"]) == 4 * n
    assert len(eval_struct["evaluated_structure_constants"]) > 0

    # Verify consistency with Schema 2
    assert schema3["algebra"]["n"] == n
    assert "inhomogeneous_deformation" in schema3
