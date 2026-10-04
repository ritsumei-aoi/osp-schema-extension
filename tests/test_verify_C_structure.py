import pytest
from src.verify_C_structure import StructureConstantVerifier

@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_verification(n):
    verifier = StructureConstantVerifier(f"data/C_{n}_structure.json")
    results = verifier.verify_all()
    assert results["antisymmetry_pass"], f"Anti-symmetry failed for n={n}: {results['antisymmetry_errors']}"
    assert results["super_jacobi_pass"], f"Super-Jacobi failed for n={n}: {results['super_jacobi_errors']}"
    assert results["overall_pass"]
