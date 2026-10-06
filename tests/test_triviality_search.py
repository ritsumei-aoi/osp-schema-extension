import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import C_evaluate as ev  # noqa: E402
import triviality_search as ts  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("name", ev.PROFILE_NAMES)
def test_layers_agree_on_g_part_and_k_identity(n, name):
    r = ts.compare_layers(n, name)
    assert r["g_mismatches"] == []
    assert r["k_identity_ok"]
    assert (r["n_central"] == 0) == (name == "zero")


@pytest.mark.parametrize("n", [1, 2])
def test_search_dimensions(n):
    r = ts.search(n)
    assert r["g_part"] == 4 * n          # g-valued γ trivial for every gb
    assert r["extended"] == 4 * n        # f into g ⊕ CK: trivial for every gb
    assert r["strict"] == 0              # f into g: only gb = 0
    assert r["rank_K_residue_map"] == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_fK_closed_form(n):
    """f_K(E_{σ,j,s}) = gb_{σ,j,s}/2 on the odd generators."""
    import json
    d = json.load(open(ROOT / "data" / f"C_{n}_coboundary_alt.json"))
    vals = {k: F(v) for k, v in d["profile"]["gb_values"].items()}
    fK = {e["X"]: F(e["coeff"]) for e in d["odd_map"]["central_component"]}
    assert len(fK) == 4 * n
    for X, v in fK.items():
        tail = X.split("_")  # E, eps1, del{k}, {σ}{s}
        k, sg, s = int(tail[2][3:]), tail[3][0], tail[3][1]
        assert v == vals[f"gb_a_1_{sg}_b_{k}_{s}"] / 2
