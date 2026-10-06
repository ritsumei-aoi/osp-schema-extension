import os
import sys
from fractions import Fraction

import numpy as np
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
import C_evaluate as EV  # noqa: E402
import C_gamma as GM  # noqa: E402
import C_triviality as T  # noqa: E402

NS = (1, 2, 3)


@pytest.mark.parametrize("n", NS)
def test_comparison_matrix(n):
    profs, M = T.comparison_matrix(n)
    for p in profs:
        assert M[(p, p)][0]
    assert M[("all_plus", "all_minus")] == (False, Fraction(-1))
    assert M[("all_plus", "alternating")][1] is None
    assert M[("alternating", "single_first")][1] is None


@pytest.mark.parametrize("n", NS)
def test_general_odd_map_solves_every_gamma_when_K_allowed(n):
    for reading in ("A", "B"):
        res = T.solve_reading(n, reading)
        assert res["kernel_dim"] == 4 * n  # inner odd derivations ad(g_1)
        assert max(res["cases"].values()) < 1e-9


@pytest.mark.parametrize("n", NS)
def test_strict_reading_nontrivial_for_every_nonzero_gb(n):
    res = T.solve_reading(n, "C")
    assert min(v for k, v in res["cases"].items()) > 1e-3


@pytest.mark.parametrize("n", NS)
def test_K_component_injective_in_gb(n):
    _, lin = GM.load_gamma(n)
    names = [GM.gb_name(k) for k in GM.gb_keys(n)]
    keys = sorted({xy for xy, d in lin.items() if GM.K_LABEL in d})
    M = np.array([[float(lin[xy][GM.K_LABEL].get(p, 0)) for p in names] for xy in keys])
    assert np.linalg.matrix_rank(M) == 4 * n
    assert np.linalg.matrix_rank(np.array([[float(lin[xy][z].get(p, 0)) for p in names]
                                           for xy, d in lin.items() for z in d])) == 4 * n
