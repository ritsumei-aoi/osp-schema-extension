"""Tests for Schema 2 (Issue I05)."""
import copy
from fractions import Fraction

import pytest

from C_gamma import build_schema2, evaluate_gamma
from verify_C_gamma import verify, load_gamma, extended_structure, jacobi_on_g
from verify_C_structure import load_structure


@pytest.mark.parametrize("n", (1, 2, 3))
def test_gamma_consistency(n):
    r = verify(n)
    assert r["ok"], r


@pytest.mark.parametrize("n", (1, 2, 3))
def test_gamma_file_reproducible_and_shaped(n):
    d, _ = load_gamma(n)
    assert build_schema2(n, date=d["metadata"]["generation_date"]) == d
    gm = d["inhomogeneous_deformation"]["gb_matrix"]
    assert gm["shape"] == [2, 2 * n] and gm["count"] == 4 * n
    assert len({s for row in gm["symbols"] for s in row}) == 4 * n


def test_hand_computed_entry():
    """[a+b+, a+b+] = 2 a+ b+ a+ b+ = 2 a+(a+ b+ - gb kappa) b+ = 2 gb kappa a+ b+."""
    _, gamma = load_gamma(1)
    assert gamma[("E_eps1_del1_pp", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": {"gb_p_1_p": Fraction(2)}}


def test_deformed_jacobi_detects_corruption():
    basis, par, sc = load_structure(1)
    _, gamma = load_gamma(1)
    bad = copy.deepcopy(gamma)
    pair = ("H_1", "H_2")
    rev = ("H_2", "H_1")
    for Z in bad[pair]:
        bad[pair][Z] = {g: 3 * c for g, c in bad[pair][Z].items()}
        bad[rev][Z] = {g: 3 * c for g, c in bad[rev][Z].items()}
    Lpar, Lsc = extended_structure(basis, par, sc, evaluate_gamma(bad, {"gb_m_1_m": 1}))
    assert jacobi_on_g(basis, Lpar, Lsc) > 0
