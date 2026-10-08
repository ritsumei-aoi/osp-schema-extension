"""Issue I05: Schema 2 (gamma structure) consistency tests."""
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_common import LieSuperalgebra  # noqa: E402
from C_gamma import (build_schema2, check_L_jacobi, check_gamma_antisymmetry,  # noqa: E402
                     compute_gamma, load_gamma)


@pytest.fixture(scope="module")
def gammas():
    return {n: compute_gamma(n) for n in [1, 2, 3]}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gb_matrix_and_linearity(n, gammas):
    gamma, alg = gammas[n]
    assert len(alg.params) == 4 * n
    params = set(alg.params)
    for (X, Y), entry in gamma.items():
        for Z, lf in entry.items():
            assert "" not in lf  # homogeneous linear in gb: vanishes at gb = 0
            assert set(lf) <= params


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_only_between_mixed_sectors(n, gammas):
    """gamma(X,Y) != 0 requires a fermionic factor in X or Y (purely bosonic pairs undeformed)."""
    gamma, _ = gammas[n]
    g = LieSuperalgebra.load(n)
    for (X, Y) in gamma:
        assert g.parity[X] == 1 or g.parity[Y] == 1 or X == "H_1" or Y == "H_1"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_antisymmetry_and_L_jacobi(n, gammas):
    gamma, _ = gammas[n]
    g = LieSuperalgebra.load(n)
    assert check_gamma_antisymmetry(gamma, g.parity, g.labels) == []
    count, failures = check_L_jacobi(gamma, g)
    assert count == len(g.labels) ** 3 and failures == []


def test_gamma_n1_hand_values(gammas):
    gamma, _ = gammas[1]
    assert gamma[("E_eps1_del1_pp", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": {"gb_a1p_b1p": Fraction(2)}}
    assert gamma[("E_eps1_del1_pm", "H_2")]["K"] == {"gb_a1p_b1m": Fraction(1, 2)}
    assert "K" not in gamma[("E_eps1_del1_pm", "H_1")]
    assert gamma[("E_eps1_del1_pp", "H_1")]["K"] == {"gb_a1p_b1p": Fraction(1)}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema2_file_matches(n, gammas):
    doc, on_disk = load_gamma(n)
    gamma, _ = gammas[n]
    assert on_disk == gamma
    assert doc["schema_layer"] == 2 and doc["algebra"]["family"] == "C"
    gb = doc["inhomogeneous_deformation"]["gb_matrix"]
    assert gb["shape"] == [2, 2 * n] and gb["count"] == 4 * n and gb["parity"] == 1
    fresh, _ = build_schema2(n)
    assert fresh["inhomogeneous_deformation"]["gamma"] == doc["inhomogeneous_deformation"]["gamma"]
