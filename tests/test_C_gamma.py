"""I05 tests: Schema 2 gamma structure."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_gamma import build_gamma_json, compute_gamma, check_consistency, gb_labels  # noqa: E402
from verify_C_structure import BracketTable  # noqa: E402

NS = [1, 2, 3]


@pytest.fixture(scope="module")
def docs():
    return {n: build_gamma_json(n) for n in NS}


@pytest.mark.parametrize("n", NS)
def test_gb_matrix_shape_and_labels(docs, n):
    gbm = docs[n][0]["inhomogeneous_deformation"]["gb_matrix"]
    assert gbm["shape"] == [2, 2 * n] and gbm["parameter_count"] == 4 * n
    assert gbm["rows"] == ["a_1_p", "a_1_m"]
    assert gbm["columns"] == [f"b_{k}_{s}" for k in range(1, n + 1) for s in ("p", "m")]
    assert gbm["entries"][0][0] == "gb_a_1_p_b_1_p" and gbm["entries"][1][-1] == f"gb_a_1_m_b_{n}_m"


@pytest.mark.parametrize("n", NS)
def test_consistency_flags(docs, n):
    doc, rep = docs[n]
    assert rep["pass"], rep
    c = doc["consistency"]
    assert c["kappa_free_part_equals_schema1"] and c["parity_rule_ok"] and c["linear_in_gb"] and c["cocycle_identity_ok"]
    assert c["triples_checked"] == len(doc_basis(n)) ** 3


def doc_basis(n):
    return json.load(open(os.path.join(ROOT, "data", f"C_{n}_structure.json")))["basis"]["pbw_order"]


@pytest.mark.parametrize("n", NS)
def test_gamma_records_well_formed(docs, n):
    doc = docs[n][0]
    _, _, entries = gb_labels(n)
    allowed = {e for row in entries for e in row}
    labels = set(doc_basis(n))
    seen = set()
    for e in doc["inhomogeneous_deformation"]["gamma"]:
        assert e["X"] in labels and e["Y"] in labels and e["Z"] in labels
        assert isinstance(e["coeff"], dict) and e["coeff"]
        for sym, val in e["coeff"].items():
            assert sym in allowed
            assert Fraction(val) != 0
        key = (e["X"], e["Y"], e["Z"])
        assert key not in seen
        seen.add(key)


def test_hand_computed_n1_gamma():
    gamma, consts, _ = compute_gamma(1)

    def g(x, y):
        return {z: c.to_json() for z, c in gamma.get((x, y), {}).items()}

    # {a+b+, a+b+} = 2 (a+b+)^2 = 2 gb_{+,1,+} kappa a+b+
    assert g("E_eps1_del1_pp", "E_eps1_del1_pp") == {"E_eps1_del1_pp": {"gb_a_1_p_b_1_p": "2"}}
    # [a+b-, (b+)^2]: kappa-part -2 gb_{+,1,+} b+b- = -2 gb (N+1/2) + gb  -> gamma = -2 gb H_2, const = -gb
    assert g("E_eps1_del1_pm", "E_2del1_p") == {"H_2": {"gb_a_1_p_b_1_p": "-2"}}
    assert consts[("E_eps1_del1_pm", "E_2del1_p")].to_json() == {"gb_a_1_p_b_1_p": "-1"}
    # even-even brackets acquire odd gamma: [H_1, H_2]
    assert g("H_1", "H_2") == {"E_eps1_del1_pp": {"gb_a_1_m_b_1_m": "1"}, "E_eps1_del1_pm": {"gb_a_1_m_b_1_p": "1"},
                               "E_eps1_del1_mp": {"gb_a_1_p_b_1_m": "-1"}, "E_eps1_del1_mm": {"gb_a_1_p_b_1_p": "-1"}}
    # pure bosonic pairs are undeformed
    assert g("E_2del1_p", "E_2del1_m") == {}


@pytest.mark.parametrize("n", NS)
def test_data_files_match_generator(docs, n):
    path = os.path.join(ROOT, "data", f"C_{n}_gamma.json")
    on_disk = json.load(open(path))
    fresh = docs[n][0]
    on_disk["metadata"].pop("generation_date")
    fresh = json.loads(json.dumps(fresh))
    fresh["metadata"].pop("generation_date")
    assert on_disk == fresh


def test_negative_control_cocycle_check():
    """Perturbing gamma must violate the cocycle identity."""
    gamma, consts, base = compute_gamma(1)
    bt = BracketTable.load(1)
    from oscillator import LinPoly
    gamma[("E_eps1_del1_pp", "E_eps1_del1_pp")]["E_eps1_del1_pp"] = LinPoly.symbol("gb_a_1_p_b_1_p") * 3
    rep = check_consistency(1, gamma, consts, base, bt, verbose=False)
    assert rep["cocycle_failures"]
