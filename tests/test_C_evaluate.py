"""I06 tests: Schema 3 evaluated structure."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_evaluate import DEFAULT_PROFILE, PROFILES, build_evaluated_json, profile_values  # noqa: E402

NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
def test_profiles_have_4n_values(n):
    for prof in PROFILES:
        vals = profile_values(n, prof)
        assert len(vals) == 4 * n
    assert all(v == 1 for v in profile_values(n, "all_plus").values())
    assert sum(1 for v in profile_values(n, "unit_a1p_b1p").values() if v != 0) == 1


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("prof", list(PROFILES))
def test_schema3_consistent_with_schema2(n, prof):
    doc, ok = build_evaluated_json(n, prof)
    assert ok and doc["consistency"]["matches_direct_recomputation"]
    assert doc["layer"] == 3 and doc["gb_profile"]["name"] == prof
    assert len(doc["gb_profile"]["matrix"]) == 2 and len(doc["gb_profile"]["matrix"][0]) == 2 * n
    labels = set(json.load(open(os.path.join(ROOT, "data", f"C_{n}_structure.json")))["basis"]["pbw_order"])
    for e in doc["evaluated_gamma"]:
        assert e["X"] in labels and e["Y"] in labels and e["Z"] in labels
        assert Fraction(e["coeff"]) != 0
    for e in doc["evaluated_structure_constants"]:
        Fraction(e["coeff"]), Fraction(e["kappa_coeff"])
        assert Fraction(e["coeff"]) != 0 or Fraction(e["kappa_coeff"]) != 0


def test_default_file_is_all_plus():
    for n in NS:
        d = json.load(open(os.path.join(ROOT, "data", f"C_{n}_evaluated.json")))
        assert d["gb_profile"]["name"] == DEFAULT_PROFILE
        d2 = json.load(open(os.path.join(ROOT, "data", f"C_{n}_evaluated_all_plus.json")))
        assert d == d2


def test_hand_values_n1_all_plus():
    doc, _ = build_evaluated_json(1, "all_plus")
    ev = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in doc["evaluated_gamma"]}
    assert ev[("E_eps1_del1_pp", "E_eps1_del1_pp", "E_eps1_del1_pp")] == 2
    assert ev[("E_eps1_del1_pm", "E_2del1_p", "H_2")] == -2
    # gamma(H_1,H_2) = E_pp + E_pm - E_mp - E_mm at all gb = 1
    assert ev[("H_1", "H_2", "E_eps1_del1_pp")] == 1 and ev[("H_1", "H_2", "E_eps1_del1_mm")] == -1


@pytest.mark.parametrize("n", NS)
def test_data_files_match_generator(n):
    for prof in PROFILES:
        on_disk = json.load(open(os.path.join(ROOT, "data", f"C_{n}_evaluated_{prof}.json")))
        fresh, _ = build_evaluated_json(n, prof)
        fresh = json.loads(json.dumps(fresh))
        on_disk["metadata"].pop("generation_date")
        fresh["metadata"].pop("generation_date")
        assert on_disk == fresh
