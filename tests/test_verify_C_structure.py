"""
Unit tests running Super Jacobi and anti-symmetry verification on generated JSON.
"""

import pytest
from src.verify_C_structure import (
    load_structure_data,
    verify_antisymmetry,
    verify_super_jacobi,
)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_verify_structure_json(n):
    filepath = f"data/C_{n}_structure.json"
    data = load_structure_data(filepath)

    n_pairs, asym_fails = verify_antisymmetry(data)
    assert len(asym_fails) == 0, f"Anti-symmetry failed in {len(asym_fails)} pairs for n={n}: {asym_fails[:3]}"

    n_triples, jacobi_fails = verify_super_jacobi(data)
    assert len(jacobi_fails) == 0, f"Super Jacobi failed in {len(jacobi_fails)} triples for n={n}: {jacobi_fails[:3]}"
