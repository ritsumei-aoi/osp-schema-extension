import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.verify_C_structure import load_structure, verify_antisymmetry, verify_super_jacobi

@pytest.mark.parametrize("n", [1, 2, 3])
def test_c_structure_super_jacobi(n):
    json_path = f"data/C_{n}_structure.json"
    assert os.path.exists(json_path)
    basis, parity, brackets = load_structure(json_path)
    
    antisym_err = verify_antisymmetry(basis, parity, brackets)
    assert len(antisym_err) == 0, f"Anti-symmetry errors found for n={n}: {antisym_err}"
    
    triples_count, jacobi_err = verify_super_jacobi(basis, parity, brackets)
    assert len(jacobi_err) == 0, f"Super Jacobi errors found for n={n}: {jacobi_err}"
