import json
import pytest
from src.C_generators import generate_schema_1, CAlgebra

@pytest.mark.parametrize("n, expected_even, expected_odd, expected_total", [
    (1, 4, 4, 8),
    (2, 11, 8, 19),
    (3, 22, 12, 34)
])
def test_basis_dimensions(n, expected_even, expected_odd, expected_total):
    alg = CAlgebra(n)
    assert len(alg.basis_even) == expected_even
    assert len(alg.basis_odd) == expected_odd
    assert len(alg.basis_all) == expected_total

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_fields(n):
    schema = generate_schema_1(n)
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n
    assert "central_elements" in schema
    assert "kappa" in schema["central_elements"]
    assert "K" in schema["central_elements"]
    assert schema["central_elements"]["kappa"]["parity"] == 1
    assert schema["central_elements"]["K"]["parity"] == 0
    assert len(schema["structure_constants"]) > 0

def test_bracket_example_c2():
    alg = CAlgebra(1)
    # Check {E_eps1_del1_pm, E_eps1_del1_mp} == H_1
    b = alg.compute_bracket("E_eps1_del1_pm", "E_eps1_del1_mp")
    coeffs = alg.express_in_basis(b)
    assert coeffs == {"H_1": 1}
