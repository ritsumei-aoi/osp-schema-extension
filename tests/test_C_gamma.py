import copy
import json
import os

import pytest

from C_gamma import build_gamma, check_consistency, extended_structure, gb_symbols
from C_generators import DATA_DIR
from verify_C_structure import verify


def load(name):
    with open(os.path.join(DATA_DIR, name)) as fh:
        return json.load(fh)


def entries_for(gam, x, y):
    return {e["Z"]: e["coeff"] for e in gam["inhomogeneous_deformation"]["gamma"] if (e["X"], e["Y"]) == (x, y)}


def test_hand_computed_gamma_n1():
    gam = load("C_1_gamma.json")
    # [H_2, a+b+]: kappa-part = gb_{+,1,-} (b+)^2 + gb_{+,1,+} (b+b- + 1) = gb_pm E_2del1_p - gb_pp H_2 + gb_pp/2
    assert entries_for(gam, "H_2", "E_eps1_del1_pp") == {
        "H_2": "-gb_p_1_p", "E_2del1_p": "gb_p_1_m", "K": "1/2*gb_p_1_p"}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gb_matrix_and_file(n):
    gam = load(f"C_{n}_gamma.json")
    gm = gam["inhomogeneous_deformation"]["gb_matrix"]
    assert gm["count"] == 4 * n == len(gb_symbols(n))
    assert len(gm["symbols"]) == 2 and all(len(r) == 2 * n for r in gm["symbols"])
    fresh = build_gamma(n)
    fresh["metadata"].pop("generation_date")
    gam["metadata"].pop("generation_date")
    assert fresh == gam


@pytest.mark.parametrize("n", [1, 2])
def test_consistency(n):
    assert check_consistency(n, load(f"C_{n}_gamma.json"), load(f"C_{n}_structure.json"))["passed"]


def test_cocycle_check_negative_control():
    struct = load("C_1_structure.json")
    ent = copy.deepcopy(load("C_1_gamma.json")["inhomogeneous_deformation"]["gamma"])
    for e in ent:
        if (e["X"], e["Y"], e["Z"]) == ("H_2", "E_eps1_del1_pp", "E_2del1_p"):
            e["coeff"] = "2*gb_p_1_m"
    vals = {s: 0 for s in gb_symbols(1)}
    vals["gb_p_1_m"] = 1
    assert not verify(extended_structure(struct, ent, vals))["passed"]
