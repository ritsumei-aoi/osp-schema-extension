"""Issue I08: triviality analysis tests."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_common import LieSuperalgebra  # noqa: E402
from C_evaluate import load_evaluated  # noqa: E402
from C_gamma import load_gamma  # noqa: E402
from C_triviality import check_perfect, solve_delta_f_eq_gamma, trivial_gb_subspace  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_g_is_perfect(n):
    r, d = check_perfect(LieSuperalgebra.load(n))
    assert r == d


@pytest.mark.parametrize("n", [1, 2, 3])
def test_strict_vs_extended_for_all_plus(n):
    g = LieSuperalgebra.load(n)
    _, gamma = load_evaluated(n, "all_plus")
    s1, bad1, *_ = solve_delta_f_eq_gamma(g, gamma, allow_K=False, project_K=False)
    s2, bad2, *_ = solve_delta_f_eq_gamma(g, gamma, allow_K=False, project_K=True)
    s3, bad3, *_ = solve_delta_f_eq_gamma(g, gamma, allow_K=True, project_K=False)
    assert s1 == "inconsistent" and bad1 and all(Z == "K" for (_, _, Z, _) in bad1)
    assert s2 == "consistent" and bad2 == []
    assert s3 == "consistent" and bad3 == []


@pytest.mark.parametrize("n", [1, 2, 3])
def test_trivial_gb_subspace(n):
    g = LieSuperalgebra.load(n)
    _, gamma_sym = load_gamma(n)
    names = [f"gb_a1{s}_b{j}{t}" for s in ("p", "m") for j in range(1, n + 1) for t in ("p", "m")]
    cons1, _ = trivial_gb_subspace(g, gamma_sym, allow_K=False, project_K=False, gb_names=names)
    assert set(cons1) == set(names) and all(row == {p: 1} for p, row in cons1.items())  # gb = 0 only
    cons2, _ = trivial_gb_subspace(g, gamma_sym, allow_K=False, project_K=True, gb_names=names)
    cons3, _ = trivial_gb_subspace(g, gamma_sym, allow_K=True, project_K=False, gb_names=names)
    assert cons2 == {} and cons3 == {}
