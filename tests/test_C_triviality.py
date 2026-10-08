"""I08 tests: triviality analysis (fast parts only: n=1,2)."""
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_triviality import SparseEchelon, part_A, part_B, part_D, part_E, solve_sparse  # noqa: E402
from verify_C_structure import BracketTable  # noqa: E402

NS = [1, 2]


def test_sparse_solver_basics():
    # x + y = 3, x - y = 1  -> x = 2, y = 1 ; and an inconsistent system
    rows = [{0: Fraction(1), 1: Fraction(1)}, {0: Fraction(1), 1: Fraction(-1)}, {0: Fraction(2)}]
    rank, cons, sols = solve_sparse(rows, 2, [{0: Fraction(3), 1: Fraction(1), 2: Fraction(4)},
                                              {0: Fraction(3), 1: Fraction(1), 2: Fraction(5)}])
    assert rank == 2 and cons == [True, False]
    assert sols[0] == {0: Fraction(2), 1: Fraction(1)} and sols[1] is None
    e = SparseEchelon()
    assert e.add({0: Fraction(1)}) and not e.add({0: Fraction(5)}) and e.rank == 1


@pytest.mark.parametrize("n", NS)
def test_layer3_equals_minus_layer4_for_all_profiles(n):
    A = part_A(n)
    for prof, r in A.items():
        assert r["coincide_up_to_sign"] and r["residual_entries"] == 0, (prof, r)
        assert r["gamma_entries"] == r["delta_f_entries"] == r["common_support"]


@pytest.mark.parametrize("n", NS)
def test_every_gb_direction_is_a_coboundary(n):
    B = part_B(n, BracketTable.load(n))
    assert B["dim_ker_delta1"] == 4 * n            # ker delta_1 = inner odd derivations ad(g_odd)
    for d, r in B["directions"].items():
        assert r["consistent"] and r["verified_delta_f_eq_minus_gamma"], d
    assert all(B["profiles_consistent"].values())


@pytest.mark.parametrize("n", NS)
def test_K_retained_identity(n):
    D = part_D(n, BracketTable.load(n))
    assert D["gamma_K_equals_f_K_of_bracket"], D["mismatches"]


@pytest.mark.parametrize("n", NS)
def test_weights_and_vanishing_H2_odd(n):
    E = part_E(n, BracketTable.load(n))
    assert E["Q_eigenvalues_equal_eps_component"]
    for d, ws in E["direction_weights_(eps,del1..deln)"].items():
        assert len(ws) == 1 and ws[0][0] in (1, -1)      # homogeneous, non-zero so(2) charge
    for d, h in E["Q_homotopy"].items():
        assert h.startswith("charge"), (d, h)
    assert E["weight_zero_odd_2cochains"] == 0 and E["dim_H2_odd"] == 0
