import json
import pytest
from src.C_coboundary_generators import compute_coboundary_coefficients

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_4_coboundary(n):
    schema4 = compute_coboundary_coefficients(n)
    assert schema4["schema_version"] == "5.0"
    assert "coboundary_structure" in schema4

    cob = schema4["coboundary_structure"]
    assert len(cob["map_parameters"]) > 0
    assert len(cob["coboundary_coefficients"]) > 0
    
    # Check data consistency with Schema 1
    assert schema4["algebra"]["n"] == n
    assert schema4["algebra"]["family"] == "C"
