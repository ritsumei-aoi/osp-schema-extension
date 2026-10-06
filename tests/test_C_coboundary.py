import os
import random
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
import C_coboundary as CB  # noqa: E402
import C_evaluate as EV  # noqa: E402
import C_gamma as GM  # noqa: E402
import C_generators as G  # noqa: E402

NS = (1, 2, 3)


@pytest.mark.parametrize("n", NS)
def test_f_is_odd_and_uses_layer1_labels(n):
    for prof in EV.profiles(n):
        d, f, _ = CB.load_coboundary(n, prof)
        par = G.parity_map(n)
        par["K"] = 0
        labels = set(par)
        for zj, tgt in f.items():
            assert zj in labels
            for zi, v in tgt.items():
                assert zi in labels and par[zi] != par[zj] and v != 0


@pytest.mark.parametrize("n", NS)
def test_basis_matches_layer1(n):
    d, _, _ = CB.load_coboundary(n)
    assert d["basis"]["even"] == G.even_basis(n) and d["basis"]["odd"] == G.odd_basis(n)
    _, _, df = CB.load_coboundary(n)
    labels = set(G.all_labels(n)) | {"K"}
    for (X, Y), v in df.items():
        assert X in labels and Y in labels and set(v) <= labels


@pytest.mark.parametrize("n", NS)
def test_coboundary_equals_gamma_for_matching_profiles(n):
    for prof in EV.profiles(n):
        _, f, df = CB.load_coboundary(n, prof)
        _, gam, _ = EV.load_evaluated(n, prof)
        assert df == gam
        assert df == CB.delta_f(n, f)


@pytest.mark.parametrize("n", NS)
def test_random_c_gives_matching_gamma(n):
    _, lin = GM.load_gamma(n)
    rng = random.Random(100 + n)
    gb = {GM.gb_name(k): Fraction(rng.randint(-4, 4), rng.randint(1, 3)) for k in GM.gb_keys(n)}
    f = CB.f_from_c(n, CB.c_from_gb(n, gb))
    assert CB.delta_f(n, f) == GM.evaluate(lin, gb)


def test_mismatched_profiles_differ_n1():
    _, _, df_plus = CB.load_coboundary(1, "all_plus")
    _, gam_minus, _ = EV.load_evaluated(1, "all_minus")
    assert df_plus != gam_minus
