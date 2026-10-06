import json
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import C_coboundary as cb  # noqa: E402
import C_evaluate as ev  # noqa: E402
import C_generators as cg  # noqa: E402


def load4(n, name):
    return json.load(open(cb.output_path(n, name)))


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("name", ev.PROFILE_NAMES)
def test_f_is_odd_and_in_layer1_basis(n, name):
    d = load4(n, name)
    s1 = json.load(open(ROOT / "data" / f"C_{n}_structure.json"))
    par, basis = s1["parity"], set(s1["parity"])
    for e in d["odd_map"]["phi"]:
        assert e["X"] in basis and e["Z"] in basis
        assert par[e["Z"]] == (par[e["X"]] + 1) % 2
    for e in d["odd_map"]["central_component"]:
        assert par[e["X"]] == 1  # f maps odd -> even, K is even
    for e in d["coboundary"]["delta_f"]:
        assert e["X"] in basis and e["Y"] in basis and e["Z"] in basis
        assert par[e["Z"]] == (par[e["X"]] + par[e["Y"]] + 1) % 2


@pytest.mark.parametrize("n", [1, 2, 3])
def test_delta_f_matches_simplified_formula(n):
    """δf(X,Y) = (-1)^{p(X)}[X,fY] + [fX,Y] - f[X,Y] (equivalent form of the doc formula)."""
    alg = cg.CAlgebra(n)
    table = cg.structure_table(alg)
    phi, _ = cb.f_symbolic(alg)
    f = cb.eval_phi(phi, ev.profile("alt", n))
    df = cb.coboundary(alg, table, f)

    def lin(vec_terms):
        out = {}
        for c, v in vec_terms:
            for k, x in v.items():
                out[k] = out.get(k, F(0)) + c * x
        return {k: x for k, x in out.items() if x}

    for X in alg.basis:
        for Y in alg.basis:
            fY, fX = f.get(Y, {}), f.get(X, {})
            t1 = lin([(c, table.get((X, y), {})) for y, c in fY.items()])
            t2 = lin([(c, table.get((x, Y), {})) for x, c in fX.items()])
            t3 = lin([(c, f.get(z, {})) for z, c in table.get((X, Y), {}).items()])
            exp = lin([((-1) ** alg.parity[X], t1), (1, t2), (-1, t3)])
            assert df.get((X, Y), {}) == exp


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("name", ev.PROFILE_NAMES)
def test_delta_f_g_part_equals_layer3_gamma(n, name):
    d4 = load4(n, name)
    d3 = json.load(open(ev.output_path(n, name)))
    a = {(e["X"], e["Y"], e["Z"]): F(e["coeff"]) for e in d4["coboundary"]["delta_f"]}
    b = {(e["X"], e["Y"], e["Z"]): F(e["coeff"]) for e in d3["evaluated_deformation"]["gamma"]}
    assert a == b


def test_zero_profile_trivial_f():
    d = load4(1, "zero")
    assert d["odd_map"]["phi"] == [] and d["coboundary"]["delta_f"] == []
