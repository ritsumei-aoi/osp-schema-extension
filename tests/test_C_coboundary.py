import json
import os
import random
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

import C_coboundary as B  # noqa: E402
import C_evaluate as E  # noqa: E402
import C_gamma as CG  # noqa: E402
import C_generators as G  # noqa: E402

NS = [1, 2, 3]


def load(n, suffix=""):
    with open(os.path.join(ROOT, "data", f"C_{n}_coboundary{suffix}.json")) as f:
        return json.load(f)


@pytest.mark.parametrize("n", NS)
def test_ad_of_odd_element_has_zero_coboundary(n):
    """Sign-convention check: ad(Z0) is an odd derivation, so delta f = 0."""
    br = B.load_bracket(n)
    for Z0 in G.odd_names(n):
        f = B.ad_map(n, Z0, br)
        assert B.f_is_odd(f)
        assert B.delta_f(n, f, br) == {}


@pytest.mark.parametrize("n", NS)
def test_coboundary_graded_antisymmetry_and_parity(n):
    rnd = random.Random(n)
    f = dict()
    for X, Z in B.phi_slots(n, True):
        if rnd.random() < 0.3:
            f.setdefault(X, {})[Z] = Fraction(rnd.randint(-2, 2))
    f = dict((X, dict((z, c) for z, c in zs.items() if c)) for X, zs in f.items())
    d = B.delta_f(n, f)
    for (X, Y), zs in d.items():
        s = -1 if G.parity_of(X) * G.parity_of(Y) == 0 else 1
        assert d.get((Y, X), {}) == dict((z, s * c) for z, c in zs.items())
        for Z in zs:
            assert G.parity_of(Z) == (G.parity_of(X) + G.parity_of(Y) + 1) % 2


@pytest.mark.parametrize("n", NS)
def test_trivializing_map_reproduces_gamma(n):
    rnd = random.Random(10 + n)
    gb = dict((k, rnd.randint(-3, 3)) for k in CG.gb_keys(n))
    f = B.trivializing_map(n, gb)
    _, gam = CG.gamma_table(n, gb)
    assert B.f_is_odd(f)
    assert B.delta_f(n, f) == gam


@pytest.mark.parametrize("n", NS)
def test_files_match_regeneration_and_layer3(n):
    for profile in E.PROFILES:
        suffix = "" if profile == "all_plus" else f"_{profile}"
        d = load(n, suffix)
        assert B.build_schema4(n, profile)["coboundary"] == d["coboundary"]
        with open(os.path.join(ROOT, "data", f"C_{n}_evaluated{suffix}.json")) as fh:
            l3 = json.load(fh)["evaluated_deformation"]["gamma"]
        l4 = d["coboundary"]["delta_f"]
        key = lambda e: (e["X"], e["Y"], e["Z"], e["coeff"])  # noqa: E731
        assert sorted(map(key, l3)) == sorted(map(key, l4))


@pytest.mark.parametrize("n", NS)
def test_strict_f_does_not_reproduce_gamma(n):
    d = load(n, "_strictg")
    with open(os.path.join(ROOT, "data", f"C_{n}_evaluated.json")) as fh:
        l3 = json.load(fh)["evaluated_deformation"]["gamma"]
    assert d["coboundary"]["K_component_count"] == 0
    key = lambda e: (e["X"], e["Y"], e["Z"], e["coeff"])  # noqa: E731
    assert sorted(map(key, l3)) != sorted(map(key, d["coboundary"]["delta_f"]))


@pytest.mark.parametrize("n", NS)
def test_phi_indices_in_layer1_basis(n):
    names = set(G.basis_names(n))
    for e in load(n)["coboundary"]["odd_linear_map"]["phi"]:
        assert e["from"] in names and e["to"] in names | {"K"}
