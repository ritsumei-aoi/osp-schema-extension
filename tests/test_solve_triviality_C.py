import pytest
from src.solve_triviality_C import TrivialitySolver

@pytest.mark.parametrize("n", [1, 2, 3])
def test_triviality_solver(n):
    solver = TrivialitySolver(n)
    
    # All zeros is trivial
    gb_zeros = {p: 0 for p in solver.gb_params}
    is_triv_zeros, _ = solver.analyze_triviality(gb_zeros)
    assert is_triv_zeros, f"All zeros profile should be trivial for n={n}"

    # All ones is non-trivial
    gb_ones = {p: 1 for p in solver.gb_params}
    is_triv_ones, _ = solver.analyze_triviality(gb_ones)
    assert not is_triv_ones, f"All ones profile should be non-trivial for n={n}"

    # Symbolic constraints enforce all gb parameters to be zero
    constraints = solver.solve_symbolic_conditions()
    assert len(constraints) > 0
