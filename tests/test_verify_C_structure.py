"""Tests for src/verify_C_structure.py (I04)."""

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import verify_C_structure as V  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_pass(n):
    r = V.check(n)
    assert r["failures"] == []
    assert r["antisymmetry_pairs"] == r["basis"] ** 2
    assert r["jacobi_triples"] == r["basis"] ** 3


def test_verifier_detects_perturbed_realization(monkeypatch):
    # Sensitivity check: changing one oscillator coefficient must be caught.
    orig = V.load

    def mutated(n):
        d = copy.deepcopy(orig(n))
        d["generator_realization"]["E_2del1_p"]["standard_form"][0]["coeff"] = "1"
        return d

    monkeypatch.setattr(V, "load", mutated)
    r = V.check(1)
    assert r["failures"], "perturbed realization should break consistency"


def test_verifier_detects_perturbed_stored_constant(monkeypatch):
    orig = V.load

    def mutated(n):
        d = copy.deepcopy(orig(n))
        d["structure_constants"][0]["coeff"] = "7"
        return d

    monkeypatch.setattr(V, "load", mutated)
    r = V.check(1)
    assert any("stored" in f for f in r["failures"])
