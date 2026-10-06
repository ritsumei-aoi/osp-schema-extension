import json
import os
import random
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
import C_gamma as GM  # noqa: E402
import C_generators as G  # noqa: E402

NS = (1, 2, 3)


def rand_gb(n, seed):
    rng = random.Random(seed)
    return {k: Fraction(rng.randint(-5, 5), rng.randint(1, 3)) for k in GM.gb_keys(n)}


@pytest.mark.parametrize("n", NS)
def test_gb_matrix_shape(n):
    m = GM.gb_matrix(n)
    assert m["shape"] == [2, 2 * n]
    assert len(m["entries"]) == 2 and all(len(r) == 2 * n for r in m["entries"])
    assert len(GM.gb_keys(n)) == 4 * n


@pytest.mark.parametrize("n", NS)
def test_json_consistent_with_schema1(n):
    d, lin = GM.load_gamma(n)
    with open(os.path.join(ROOT, "data", f"C_{n}_structure.json")) as fh:
        s1 = json.load(fh)
    assert d["basis"] == s1["basis"] and d["parity"] == s1["parity"]
    par = s1["parity"]
    labels = set(par)
    names = set(d["inhomogeneous_deformation"]["parameters"]["names"])
    for (X, Y), v in lin.items():
        assert X in labels and Y in labels
        for Z, terms in v.items():
            assert set(terms) <= names
            pz = 0 if Z == GM.K_LABEL else par[Z]
            assert pz == (par[X] + par[Y] + 1) % 2


@pytest.mark.parametrize("n", NS)
def test_linearity_matches_direct_evaluation(n):
    _, lin = GM.load_gamma(n)
    gb = rand_gb(n, 7 + n)
    direct, sc0 = GM.gamma_sparse(n, gb)
    names = {GM.gb_name(k): v for k, v in gb.items()}
    assert GM.evaluate(lin, names) == {xy: d for xy, d in direct.items() if d}
    base, _, _ = G.structure_constants(n)
    assert sc0 == base  # undeformed part is gb-independent


@pytest.mark.parametrize("n", NS)
def test_zero_gb_gives_zero_gamma(n):
    _, lin = GM.load_gamma(n)
    assert GM.evaluate(lin, {}) == {}


@pytest.mark.parametrize("n", NS)
def test_cocycle_condition(n):
    _, lin = GM.load_gamma(n)
    for seed in (1, 2):
        gb = {GM.gb_name(k): v for k, v in rand_gb(n, seed).items()}
        assert GM.cocycle_failures(n, GM.evaluate(lin, gb)) == []


def test_cocycle_detects_violation():
    _, lin = GM.load_gamma(1)
    gb = {GM.gb_name(k): 1 for k in GM.gb_keys(1)}
    g = GM.evaluate(lin, gb)
    xy = next(iter(g))
    g[xy] = {z: v + 1 for z, v in g[xy].items()}
    assert GM.cocycle_failures(1, g)
