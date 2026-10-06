import json
import os

import pytest

from conftest import DATA
from C_gamma import build_schema2, compute_gamma, deformed_jacobi_failures, load_schema1
from C_oscillator import lin


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema2_file_and_checks(n):
    with open(os.path.join(DATA, f"C_{n}_gamma.json")) as fh:
        d = json.load(fh)
    fresh = build_schema2(n)
    for o in (d, fresh):
        o["metadata"].pop("generation_date")
    assert d == fresh
    c = d["consistency_checks"]
    assert c["undeformed_part_equals_schema1"] and c["gamma_parity_odd"]
    assert c["gamma_graded_antisymmetric"] and c["linear_in_gb"]
    assert c["cocycle_gamma_g_valued_failures"] == 0
    assert c["cocycle_gamma_with_central_failures"] == 0
    assert d["inhomogeneous_deformation"]["gb_matrix"]["shape"] == [2, 2 * n]
    assert len(d["inhomogeneous_deformation"]["parameters"]) == 4 * n


def test_hand_computed_gamma_n1():
    _, _, gam, cen = compute_gamma(1)
    # [H_1, a+b+]_gamma = 2 a+b+ - kappa (gb_pp H_1 + gb_pm E_2del1_p + gb_pp K)
    assert gam[("H_1", "E_eps1_del1_pp")] == {"H_1": lin(-1, "gb_a1p_b1p"),
                                              "E_2del1_p": lin(-1, "gb_a1p_b1m")}
    assert cen[("H_1", "E_eps1_del1_pp")] == lin(-1, "gb_a1p_b1p")
    # {a+b+, a+b+} = 2 (a+b+)^2 = 2 gb_pp kappa a+b+
    assert gam[("E_eps1_del1_pp", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": lin(2, "gb_a1p_b1p")}


def test_cocycle_check_detects_corruption():
    alg, _, gam, cen = compute_gamma(1)
    _, sc = load_schema1(1)
    gam = dict(gam)
    gam[("H_1", "E_eps1_del1_pp")] = {"H_1": lin(-2, "gb_a1p_b1p")}
    gam[("E_eps1_del1_pp", "H_1")] = {"H_1": lin(2, "gb_a1p_b1p")}
    assert deformed_jacobi_failures(1, sc, gam, cen, alg.parity, alg.basis)
