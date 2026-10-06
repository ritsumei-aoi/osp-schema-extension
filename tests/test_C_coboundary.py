import json
import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import C_coboundary as CB  # noqa: E402
import verify_C_gamma as VG  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
NS = [1, 2, 3]


def _load(n):
    return json.load(open(os.path.join(DATA, f"C_{n}_coboundary.json")))


@pytest.mark.parametrize("n", NS)
def test_file_matches_generator(n):
    st = json.load(open(os.path.join(DATA, f"C_{n}_structure.json")))
    on_disk = _load(n)
    fresh = CB.build_schema4(n, st, date=on_disk["metadata"]["generation_date"])
    assert on_disk == json.loads(json.dumps(fresh, ensure_ascii=False))


@pytest.mark.parametrize("n", NS)
def test_f_is_odd_and_labels_in_layer1_basis(n):
    d = _load(n)
    par = dict(d["parity"])
    par["K"] = 0
    allowed = set(par)
    assert len(d["odd_linear_map"]["parameters"]) == 4 * n
    for e in d["odd_linear_map"]["f_structure"]:
        assert e["source"] in allowed and e["target"] in allowed
        assert par[e["target"]] == (par[e["source"]] + 1) % 2
    for e in d["coboundary_structure"]["entries"]:
        assert e["X"] in par and e["Y"] in par and e["Z"] in allowed
        assert par[e["Z"]] == (par[e["X"]] + par[e["Y"]] + 1) % 2


@pytest.mark.parametrize("n", NS)
def test_coboundary_is_cocycle_and_equals_gamma_under_correspondence(n):
    d = _load(n)
    dg, gparams, gam = VG.load_gamma(n)
    cparams = d["odd_linear_map"]["parameters"]
    delta = {c: {} for c in cparams}
    for e in d["coboundary_structure"]["entries"]:
        for c, v in e["coeff"].items():
            delta[c].setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(v)
    for c in cparams:
        (g, sgn), = ((k, Fraction(v)) for k, v in d["gb_correspondence"]["map"][c].items())
        expect = {k: {z: sgn * v for z, v in zs.items()} for k, zs in gam[g].items()}
        assert delta[c] == expect
    # delta f is a 2-cocycle by itself (delta^2 = 0), checked with the independent cocycle checker
    r = VG.verify(n, loaded=(dg, cparams, delta))
    assert r["cocycle_failures"] == [] and r["skew_failures"] == [] and r["label_parity_failures"] == []


def test_f_matches_oscillator_shift_example():
    # f(E_{eps+d1}) = f(a+ b1+) = l^+ b1+ ; with c[p,1,m]=1: l^+ = b1^-  ->  b1^- b1^+ = b1^+ b1^- + 1 = -H_{n+1} + 1/2 (n=1)
    d = _load(1)
    ent = {(e["source"], e["target"]): e["coeff"] for e in d["odd_linear_map"]["f_structure"]}
    assert ent[("E_eps1_del1_pp", "H_2")]["f_a_1_p_b_1_m"] == "-1"
    assert ent[("E_eps1_del1_pp", "K")]["f_a_1_p_b_1_m"] == "1/2"
