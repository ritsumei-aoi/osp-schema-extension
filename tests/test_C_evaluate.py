import json
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import C_evaluate as ev  # noqa: E402
import C_gamma as cgm  # noqa: E402
import C_generators as cg  # noqa: E402


def as_maps(d):
    e = d["evaluated_deformation"]
    g = {(x["X"], x["Y"], x["Z"]): F(x["coeff"]) for x in e["gamma"]}
    c = {(x["X"], x["Y"]): F(x["coeff"]) for x in e["central_component"]}
    return g, c


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("name", ev.PROFILE_NAMES)
def test_evaluated_matches_independent_substitution(n, name):
    """Layer 3 file == numeric substitution done directly on the generator-level gamma table."""
    d = json.load(open(ev.output_path(n, name)))
    assert d["layer"] == 3 and d["structure_file"] == f"C_{n}_structure.json"
    vals = {s: F(v) for s, v in d["profile"]["gb_values"].items()}
    assert set(vals) == set(cg.gb_names(n))
    gamma, central = cg.gamma_table(cg.CAlgebra(n))
    exp_g, exp_c = {}, {}
    for (X, Y), comps in gamma.items():
        for Z, cm in comps.items():
            v = sum((c * vals[s] for s, c in cm.items()), F(0))
            if v:
                exp_g[(X, Y, Z)] = v
    for (X, Y), cm in central.items():
        v = sum((c * vals[s] for s, c in cm.items()), F(0))
        if v:
            exp_c[(X, Y)] = v
    g, c = as_maps(d)
    assert g == exp_g and c == exp_c


@pytest.mark.parametrize("n", [1, 2, 3])
def test_zero_profile_is_empty_and_default_is_plus(n):
    z = json.load(open(ev.output_path(n, "zero")))
    assert z["evaluated_deformation"]["gamma"] == [] and z["evaluated_deformation"]["central_component"] == []
    p = json.load(open(DATA_PATH(n)))
    assert p["profile"]["name"] == "plus" and set(p["profile"]["gb_values"].values()) == {"1"}


def DATA_PATH(n):
    return ROOT / "data" / f"C_{n}_evaluated.json"


@pytest.mark.parametrize("n", [1, 2])
def test_evaluated_is_cocycle_and_odd(n):
    s1, s2 = cgm.load_gamma(n)
    d = json.load(open(ev.output_path(n, "alt")))
    par = s1["parity"]
    for x in d["evaluated_deformation"]["gamma"]:
        assert par[x["Z"]] == (par[x["X"]] + par[x["Y"]] + 1) % 2
    # numeric cocycle check: rebuild a Schema 2 style dict whose single "symbol" is the evaluated value
    s2n = {"inhomogeneous_deformation": {
        "gamma": [{"X": x["X"], "Y": x["Y"], "Z": x["Z"], "coeff": {"v": x["coeff"]}}
                  for x in d["evaluated_deformation"]["gamma"]],
        "central_component": {"entries": [{"X": x["X"], "Y": x["Y"], "coeff": {"v": x["coeff"]}}
                                          for x in d["evaluated_deformation"]["central_component"]]}}}
    assert cgm.check_cocycle(s1, s2n) == []
