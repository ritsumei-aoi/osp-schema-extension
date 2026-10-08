import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from C_triviality import load_equations, trivial_subspace_numeric  # noqa: E402


@pytest.mark.parametrize("n", [1, 2])
def test_kernel_of_delta_is_odd_inner_derivations(n):
    # ker(delta) on odd maps = odd inner derivations ad(E_odd), dimension 4n
    _, _, _, A, _, _, _ = load_equations(n)
    assert A.shape[1] - np.linalg.matrix_rank(A) == 4 * n


@pytest.mark.parametrize("n", [1, 2])
def test_synthetic_trivial_deformation_is_detected(n):
    # gamma = delta(f0) for some f0 makes every gb trivial; checks the projection code
    _, gb, _, A, _, _, _ = load_equations(n)
    rng = np.random.default_rng(0)
    R = rng.integers(-3, 4, size=(A.shape[1], len(gb))).astype(float)
    assert trivial_subspace_numeric(A, A @ R).shape[0] == len(gb)


@pytest.mark.parametrize("n", [1, 2])
def test_only_zero_gb_is_trivial(n):
    keys, gb, _, A, B, _, _ = load_equations(n)
    assert trivial_subspace_numeric(A, B).shape[0] == 0
    K_rows = [i for i, k in enumerate(keys) if k[2] == "K"]
    assert np.linalg.matrix_rank(B[K_rows]) == len(gb)
