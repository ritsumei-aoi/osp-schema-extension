"""Tests for Schema 3 (evaluated structure) of C(n+1) (Issue I06)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_evaluate import build_schema3, check_schema3, evaluate_gamma, gb_profile  # noqa: E402
from C_gamma import gamma_table_from_records  # noqa: E402

NS = [1, 2, 3]


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def test_profiles():
    gb = gb_profile(2, "all_plus_one")
    assert len(gb) == 8 and all(v == 1 for v in gb.values())
    gb = gb_profile(2, "alternating")
    assert gb["gb_a1p_b1p"] == 1 and gb["gb_a1p_b1m"] == -1 and gb["gb_a1m_b2p"] == -1 and gb["gb_a1m_b2m"] == 1
    gb = gb_profile(1, "unit:gb_a1m_b1p")
    assert gb == {"gb_a1p_b1p": 0, "gb_a1p_b1m": 0, "gb_a1m_b1p": 1, "gb_a1m_b1m": 0}
    gb = gb_profile(1, "custom", {"gb_a1p_b1m": "-3/2"})
    assert gb["gb_a1p_b1m"] == Fraction(-3, 2) and gb["gb_a1p_b1p"] == 0
    with pytest.raises(KeyError):
        gb_profile(1, "unit:gb_a1p_b9p")


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("suffix", ["", "_alternating"])
def test_schema3_consistency(n, suffix):
    doc3 = load(f"C_{n}_evaluated{suffix}.json")
    doc1, doc2 = load(f"C_{n}_structure.json"), load(f"C_{n}_gamma.json")
    assert doc3["schema_layer"] == 3 and doc3["schema_version"] == "5.0"
    assert set(doc3["gb_assignment"]["values"]) == {l for row in doc2["inhomogeneous_deformation"]["gb_matrix"]["labels"] for l in row}
    rep = check_schema3(doc3, doc1, doc2)
    assert rep["passed"], rep["failures"]


@pytest.mark.parametrize("n", NS)
def test_schema3_files_are_current(n):
    doc3 = load(f"C_{n}_evaluated.json")
    fresh = build_schema3(n, "all_plus_one", today=doc3["metadata"]["generation_date"])
    assert fresh == doc3


def test_evaluated_values_n1():
    doc3 = load("C_1_evaluated.json")
    t = gamma_table_from_records(doc3["evaluated_gamma"], key="coeff")
    val = lambda x, y: {z: p.const_value() for z, p in t.get((x, y), {}).items()}
    # gamma(H_1, E_{ε+δ1}) = -gb_pp H_1 - gb_pm E_{2δ} - gb_pp K  with all gb = 1
    assert val("H_1", "E_eps1_del1_pp") == {"H_1": -1, "E_2del1_p": -1, "K": -1}
    assert val("E_eps1_del1_pm", "E_eps1_del1_mp") == {"E_eps1_del1_pp": 1, "E_eps1_del1_mm": 1}


def test_linearity_in_gb():
    """gamma(all_plus_one) == sum over unit profiles (gamma is linear in gb)."""
    doc2 = load("C_1_gamma.json")
    total = evaluate_gamma(doc2, gb_profile(1, "all_plus_one"))
    acc = {}
    for lab in gb_profile(1, "all_plus_one"):
        for key, comps in evaluate_gamma(doc2, gb_profile(1, f"unit:{lab}")).items():
            for z, c in comps.items():
                acc.setdefault(key, {})[z] = acc.get(key, {}).get(z, 0) + c
    acc = {k: {z: c for z, c in v.items() if c != 0} for k, v in acc.items()}
    acc = {k: v for k, v in acc.items() if v}
    assert acc == total
