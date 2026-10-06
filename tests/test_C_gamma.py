import copy
from fractions import Fraction

import pytest

from C_gamma import build_schema2, check_consistency, cocycle_failures, gb_matrix, load_gamma
from verify_C_structure import load_structure


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gb_matrix_shape(n):
    rows, cols, ent = gb_matrix(n)
    assert len(rows) == 2 and len(cols) == 2 * n
    assert len({g for r in ent for g in r}) == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_consistency_with_schema1(n):
    r = check_consistency(n)
    assert r["parity_failures"] == r["label_failures"] == 0
    assert r["undeformed_mismatch"] == 0
    assert r["cocycle_failures"] == 0


@pytest.mark.parametrize("n", [1, 2])
def test_json_matches_generator(n):
    d, _ = load_gamma(n)
    fresh = build_schema2(n)
    assert d["inhomogeneous_deformation"] == fresh["inhomogeneous_deformation"]


def test_hand_computed_entry():
    # [a^+ b^-, a^- b^+]_gamma, n=1: contractions [a^+, b^+] = gb_p_1_p kappa etc.
    _, gam = load_gamma(1)
    g = gam[("E_eps1_del1_pp", "H_1")]
    # [a+b+, a+a- + b+b-]: the a+ / b+ contraction leaves b+ b- = (b+b- + 1/2) - 1/2
    assert g["H_1"] == {"gb_p_1_p": Fraction(1)}
    assert g["K"] == {"gb_p_1_p": Fraction(1)}


def test_cocycle_check_detects_corruption():
    basis, par, sc = load_structure(1)
    _, gam = load_gamma(1)
    bad = copy.deepcopy(gam)
    key = next(k for k, v in bad.items() if "H_1" in v)
    g = next(iter(bad[key]["H_1"]))
    bad[key]["H_1"][g] += 1
    assert cocycle_failures(basis, par, sc, bad, [g]) > 0
