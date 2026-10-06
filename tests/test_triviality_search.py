import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import triviality_search as TS  # noqa: E402
from C_triviality import System, solve_gb_subspace  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("prof", TS.PROFILES)
def test_layer3_equals_layer4_including_K(n, prof):
    r = TS.compare(n, prof)
    assert r["full_coincide"] and r["g_part_coincide"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_K_component_injective_exact(n):
    rank, P = TS.K_functional_rank(n)
    assert rank == P == 4 * n


@pytest.mark.parametrize("n", [1, 2])
def test_subspace_dimensions(n):
    S = System(n)
    P = 4 * n
    assert solve_gb_subspace(S, "strict")[0].shape[1] == 0
    assert solve_gb_subspace(S, "gonly")[0].shape[1] == P
    assert solve_gb_subspace(S, "const")[0].shape[1] == P


def test_wrong_c_is_detected():
    """Layer 4 at c=0 does not reproduce a non-zero Layer 3 (the comparison is not vacuous)."""
    gbv, l3 = TS.layer3(1, "all_plus")
    zero = {k: 0 for k in gbv}
    _, l4 = TS.layer4_at(1, zero)
    assert l4 == {} and l3 != l4
