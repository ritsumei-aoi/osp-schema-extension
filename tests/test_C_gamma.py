"""Tests for I05: gamma structure (Schema 2)."""
import json
import os

import pytest

from oscillator_algebra import Poly
from C_gamma import compute_gamma, check_consistency, build_schema2, load_json, DATA_DIR

NS = [1, 2, 3]


@pytest.fixture(scope="module")
def gammas():
    return {n: compute_gamma(n) for n in NS}


@pytest.mark.parametrize("n", NS)
def test_consistency_with_schema1(gammas, n):
    B, table, gamma = gammas[n]
    rep = check_consistency(n, B, table, gamma, load_json(f"C_{n}_structure.json"))
    assert rep["passed"], rep


def test_hand_checked_gamma_n1(gammas):
    B, table, gamma = gammas[1]
    # {a+ b-, a- b+}_gb : kappa-part = gb_{--} a+b+ + gb_{++} a-b-
    assert gamma[("E_eps1_del1_pm", "E_eps1_del1_mp")] == {
        "E_eps1_del1_pp": Poly.var("gb_a1m_b1m"), "E_eps1_del1_mm": Poly.var("gb_a1p_b1p")}
    # {E_pp, E_pp}_gb = 2 gb_{++} kappa E_pp
    assert gamma[("E_eps1_del1_pp", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": 2 * Poly.var("gb_a1p_b1p")}
    # [N_a, a+ b-]  with N_a = H_1 + H_2 (n=1): kappa-part = -gb_{+-} a+a- = -gb_{+-}(H_1 + H_2 + K/2)
    g = {}
    for h in ("H_1", "H_2"):
        for z, c in gamma.get((h, "E_eps1_del1_pm"), {}).items():
            g[z] = g.get(z, Poly()) + c
    g = {z: c for z, c in g.items() if c}
    v = Poly.var("gb_a1p_b1m")
    assert g == {"H_1": -v, "H_2": -v, "K": -v * Poly.const("1/2")}
    # purely bosonic pairs are undeformed
    assert ("E_2del1_p", "E_2del1_m") not in gamma


@pytest.mark.parametrize("n", NS)
def test_gamma_uses_every_parameter_and_only_linear(gammas, n):
    B, table, gamma = gammas[n]
    used = set()
    for comps in gamma.values():
        for c in comps.values():
            assert c.degree() == 1 and c.constant() == 0
            used |= c.variables()
    assert used == set(B.alg.gb_labels())
    assert len(used) == 4 * n


@pytest.mark.parametrize("n", NS)
def test_schema2_file(n):
    path = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
    with open(path) as fh:
        d = json.load(fh)
    assert d == build_schema2(n, date=d["metadata"]["generation_date"])
    gb = d["gb_matrix"]
    assert gb["shape"] == [2, 2 * n] and len(gb["entries"]) == 2 and all(len(r) == 2 * n for r in gb["entries"])
    assert gb["parameter_count"] == 4 * n
    for e in d["inhomogeneous_deformation"]["gamma"]:
        assert set(e) == {"X", "Y", "Z", "coeff", "coeff_terms"}
        assert str(Poly.from_terms_dict(e["coeff_terms"])) == e["coeff"]
