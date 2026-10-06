"""Issue I06: tests for the Schema 3 (evaluated) layer."""

from __future__ import annotations

import json
import os
import sys

import pytest
import sympy as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "src"))

import C_evaluate as ev  # noqa: E402

NS = [1, 2, 3]
PROFILES = list(ev.PROFILES)


def load(n, profile):
    path = os.path.join(REPO, "data", f"C_{n}_evaluated_{profile}.json")
    if not os.path.exists(path):
        ev.write_schema3(n, profile)
    with open(path) as fh:
        return json.load(fh)


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("profile", PROFILES)
def test_consistency_flags(n, profile):
    c = load(n, profile)["consistency"]
    assert c["substitution_matches_direct_recomputation"] is True
    assert c["cocycle_condition_holds"] is True
    assert c["cocycle_triples_checked"] == (2 * n * n + 5 * n + 1) ** 3


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("profile", PROFILES)
def test_gb_values_complete_and_numeric(n, profile):
    doc = load(n, profile)
    gv = doc["gb_values"]
    assert set(gv) == set(doc["gb_matrix"]["parameters"])
    assert len(gv) == 4 * n
    for v in gv.values():
        assert sp.sympify(v).is_rational


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("profile", PROFILES)
def test_coefficients_are_numeric_and_nonzero(n, profile):
    for e in load(n, profile)["evaluated_deformation"]["entries"]:
        c = sp.sympify(e["coeff"])
        assert c.is_rational and c != 0


@pytest.mark.parametrize("n", NS)
def test_zero_profile_has_no_deformation(n):
    doc = load(n, "zero")
    assert doc["evaluated_deformation"]["entries"] == []
    assert all(sp.sympify(v) == 0 for v in doc["gb_values"].values())


@pytest.mark.parametrize("n", NS)
def test_evaluated_is_substitution_of_schema2(n):
    """Layer 3 == Layer 2 with gb substituted, for the primary profile."""
    path2 = os.path.join(REPO, "data", f"C_{n}_gamma.json")
    with open(path2) as fh:
        doc2 = json.load(fh)
    doc3 = load(n, ev.PRIMARY)
    subs = {sp.Symbol(k): sp.sympify(v) for k, v in doc3["gb_values"].items()}

    expected = {}
    for e in doc2["inhomogeneous_deformation"]["entries"]:
        c = sp.expand(sp.sympify(e["coeff"]).subs(subs))
        if c != 0:
            expected[(e["X"], e["Y"], e["Z"])] = c
    got = {
        (e["X"], e["Y"], e["Z"]): sp.sympify(e["coeff"])
        for e in doc3["evaluated_deformation"]["entries"]
    }
    assert got == expected


@pytest.mark.parametrize("n", NS)
def test_primary_alias_file_matches(n):
    with open(os.path.join(REPO, "data", f"C_{n}_evaluated.json")) as fh:
        alias = json.load(fh)
    assert alias["profile"]["name"] == ev.PRIMARY
    assert alias["profile"]["is_primary"] is True
    assert alias == load(n, ev.PRIMARY)


@pytest.mark.parametrize("n", NS)
def test_schema3_shares_basis_with_schema1(n):
    with open(os.path.join(REPO, "data", f"C_{n}_structure.json")) as fh:
        doc1 = json.load(fh)
    doc3 = load(n, ev.PRIMARY)
    assert doc3["basis"]["pbw_order"] == doc1["basis"]["pbw_order"]
    assert doc3["parity"] == doc1["parity"]
    assert doc3["algebra"] == doc1["algebra"]
