"""Issue I07: Schema 4 (coboundary structure) tests."""
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_common import LieSuperalgebra  # noqa: E402
from C_coboundary import (coboundary, evaluate_f, generic_f, load_coboundary, numeric,  # noqa: E402
                          shift_map_symbolic)
from C_evaluate import gb_profiles, load_evaluated  # noqa: E402


def _ad(g, W):
    """Inner derivation ad(W) as an FMap (constant linear forms)."""
    return {src: {Z: {"": c} for Z, c in g.bracket(W, src).items()} for src in g.labels}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generic_parameterization_counts(n):
    g = LieSuperalgebra.load(n)
    _, unk = generic_f(g, allow_K=True)
    ev, od = 2 * n * n + n + 1, 4 * n
    assert len(unk) == 2 * ev * od + od  # odd targets for even sources, even(+K) targets for odd sources
    _, unk0 = generic_f(g, allow_K=False)
    assert len(unk0) == 2 * ev * od


@pytest.mark.parametrize("n", [1, 2])
def test_inner_odd_derivations_are_cocycles(n):
    """delta(ad W) = 0 for odd W: checks the sign conventions of the coboundary formula."""
    g = LieSuperalgebra.load(n)
    for W in g.labels:
        if g.parity[W] == 1:
            assert numeric(coboundary(g, _ad(g, W))) == {}, W


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("profile", ["all_plus", "fermion_sign", "boson_sign", "single_a1p_b1m", "row_a1p_only"])
def test_representative_f_reproduces_gamma(n, profile):
    g = LieSuperalgebra.load(n)
    f_sym = shift_map_symbolic(n)
    f = evaluate_f(f_sym, gb_profiles(n)[profile])
    _, gamma_eval = load_evaluated(n, profile)
    assert numeric(coboundary(g, f)) == gamma_eval


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema4_file(n):
    doc = load_coboundary(n)
    g = LieSuperalgebra.load(n)
    assert doc["schema_layer"] == 4
    assert doc["comparison_with_layer3"]["delta_f_equals_gamma"] is True
    labs = set(g.labels) | {"K"}
    for m in doc["representative_f"]["map"]:
        assert m["source"] in g.labels and m["target"] in labs
        assert g.parity[m["source"]] != g.parity[m["target"]]
    assert len(doc["representative_f"]["K_components"]) == 4 * n
    # evaluated coboundary in the file equals Layer 3
    _, gamma_eval = load_evaluated(n, "all_plus")
    stored = {}
    for e in doc["coboundary_evaluated"]:
        stored.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    assert stored == gamma_eval


def test_representative_f_n1_values():
    f = shift_map_symbolic(1)
    assert f["E_eps1_del1_pm"]["K"] == {"gb_a1p_b1m": Fraction(1, 2)}
    assert f["E_eps1_del1_pm"]["H_2"] == {"gb_a1p_b1m": Fraction(1)}
    assert f["H_1"]["E_eps1_del1_mm"] == {"gb_a1p_b1p": Fraction(1)}
    assert "H_2" not in f and "E_2del1_p" not in f or f.get("H_2", {}) == {}
