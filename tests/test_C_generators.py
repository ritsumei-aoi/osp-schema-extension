import pytest
from src.C_generators import get_generators, get_structure_constants

@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_counts(n):
    gens, pbw = get_generators(n)
    dim_even = 2*n**2 + n + 1
    dim_odd = 4*n
    assert len(gens) == dim_even + dim_odd
    assert len(pbw) == len(gens)

@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_generation(n):
    sc = get_structure_constants(n)
    assert len(sc) > 0
    # Consistency check: Ensure all coefficients are strings (rational fractions)
    for c in sc:
        assert isinstance(c["coeff"], str)
