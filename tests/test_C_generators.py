import json
import os
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
import C_generators as G  # noqa: E402

NS = (1, 2, 3)


def load(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_structure.json")) as fh:
        return json.load(fh)


@pytest.mark.parametrize("n", NS)
def test_generator_counts(n):
    d = load(n)
    assert len(G.even_basis(n)) == 2 * n * n + n + 1
    assert len(G.odd_basis(n)) == 4 * n
    assert d["basis"]["even"] == G.even_basis(n)
    assert d["basis"]["odd"] == G.odd_basis(n)
    dim = d["algebra"]["dimension"]
    assert (dim["even"], dim["odd"], dim["total"]) == (2 * n * n + n + 1, 4 * n, 2 * n * n + 5 * n + 1)
    assert d["algebra"]["family"] == "C" and d["algebra"]["m"] == 1
    assert len(set(G.all_labels(n))) == dim["total"]


@pytest.mark.parametrize("n", NS)
def test_schema_keys(n):
    d = load(n)
    assert d["schema_version"] == "5.0"
    assert set(d["oscillator_generators"]) == {"fermions", "bosons"}
    assert d["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert d["central_elements"]["kappa"]["parity"] == 1
    assert d["central_elements"]["K"]["parity"] == 0
    assert set(d["parity"]) == set(G.all_labels(n))


@pytest.mark.parametrize("n", NS)
def test_parity_of_structure_constants(n):
    d = load(n)
    par = d["parity"]
    for e in d["structure_constants"]:
        assert par[e["Z"]] == (par[e["X"]] + par[e["Y"]]) % 2


@pytest.mark.parametrize("n", NS)
def test_json_matches_generator(n):
    sc0, sc1, resid = G.structure_constants(n)
    assert not sc1 and not resid
    d = load(n)
    from_json = {}
    for e in d["structure_constants"]:
        from_json[(e["X"], e["Y"], e["Z"])] = e["coeff"]
    from_gen = {(X, Y, Z): G.fstr(c) for (X, Y), v in sc0.items() for Z, c in v.items()}
    assert from_json == from_gen


@pytest.mark.parametrize("n", NS)
def test_known_brackets(n):
    sc0, _, _ = G.structure_constants(n)
    # {a+ b_1^+, a- b_1^-} contains H-type terms; [E_2del1_p, E_2del1_m] = -(4 b+b- + 2)
    assert sc0[("E_2del1_p", "E_2del1_m")]
    # odd-odd bracket of same-type elements vanishes: {a+ b+, a+ b+} = 0
    assert ("E_eps1_del1_pp", "E_eps1_del1_pp") not in sc0
    # [E_eps1_del1_pp, E_eps1_del1_mm] ∝ H_1 + ... : parity even and non-empty
    assert sc0[("E_eps1_del1_pp", "E_eps1_del1_mm")]


def test_cartan_weights_n1():
    sc0, _, _ = G.structure_constants(1)
    # H_2 = -(b+b- + 1/2) acts on a+ b+ by -1 (weight of b+ is +delta)
    assert sc0[("H_2", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": -1}
    assert sc0[("H_2", "E_eps1_del1_pm")] == {"E_eps1_del1_pm": 1}
    # H_1 = a+a- + b+b- : a+ b+ eigenvalue 2, a+ b- eigenvalue 0
    assert sc0[("H_1", "E_eps1_del1_pp")] == {"E_eps1_del1_pp": 2}
    assert ("H_1", "E_eps1_del1_pm") not in sc0
