import json
import os
import random
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

import C_gamma as CG  # noqa: E402
import C_generators as G  # noqa: E402

NS = [1, 2, 3]


def load(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_gamma.json")) as f:
        return json.load(f)


@pytest.mark.parametrize("n", NS)
def test_gb_matrix_shape(n):
    gm = load(n)["inhomogeneous_deformation"]["gb_matrix"]
    assert gm["shape"] == [2, 2 * n] and gm["count"] == 4 * n and gm["parity"] == 1
    assert len(gm["entries"]) == 2 and all(len(r) == 2 * n for r in gm["entries"])
    assert len(set(gm["parameters"])) == 4 * n


@pytest.mark.parametrize("n", NS)
def test_parity_rule_and_targets(n):
    d = load(n)["inhomogeneous_deformation"]["gamma"]
    allowed = set(G.basis_names(n)) | {"K"}
    for e in d:
        assert e["Z"] in allowed
        assert G.parity_of(e["Z"]) == (G.parity_of(e["X"]) + G.parity_of(e["Y"]) + 1) % 2


@pytest.mark.parametrize("n", NS)
def test_gamma_graded_antisymmetry(n):
    d = load(n)["inhomogeneous_deformation"]["gamma"]
    tab = {(e["X"], e["Y"], e["Z"]): {k: Fraction(v) for k, v in e["coeff"].items()} for e in d}
    for (X, Y, Z), c in tab.items():
        s = -1 if G.parity_of(X) * G.parity_of(Y) == 0 else 1
        assert tab[(Y, X, Z)] == {k: s * v for k, v in c.items()}


@pytest.mark.parametrize("n", NS)
def test_consistency_with_schema1_and_cocycle(n):
    sym = CG.symbolic_gamma(n)
    assert CG.check_zero_part_matches_schema1(n)
    assert CG.check_cocycle(n, sym) == []


@pytest.mark.parametrize("n", NS)
def test_linear_in_gb(n):
    rnd = random.Random(n)
    gb = {k: rnd.randint(-3, 3) for k in CG.gb_keys(n)}
    _, gam = CG.gamma_table(n, gb)
    sym = CG.symbolic_gamma(n)
    lin = {}
    for (X, Y, Z), cs in sym.items():
        v = sum(Fraction(gb[k]) * c for k, c in cs.items())
        if v:
            lin[(X, Y, Z)] = v
    direct = {(X, Y, Z): c for (X, Y), zs in gam.items() for Z, c in zs.items()}
    assert direct == lin


@pytest.mark.parametrize("n", NS)
def test_file_matches_regeneration(n):
    assert CG.build_schema2(n)["inhomogeneous_deformation"] == \
        load(n)["inhomogeneous_deformation"]


def test_hand_value_n1():
    # kappa part of [E_eps1_del1_pp, E_2del1_m] = 2 kappa (b+ b- + 1) = -2 kappa H_2 + kappa K
    # with gb_{p,1,m} (sigma=p, b_1^-): derived by hand from b^- a^+ = a^+ b^- - gb kappa.
    d = {(e["X"], e["Y"], e["Z"]): e["coeff"] for e in load(1)["inhomogeneous_deformation"]["gamma"]}
    assert d[("E_eps1_del1_pp", "E_2del1_m", "H_2")] == {"gb_a_1_p_b_1_m": "-2"}
    assert d[("E_eps1_del1_pp", "E_2del1_m", "K")] == {"gb_a_1_p_b_1_m": "1"}
