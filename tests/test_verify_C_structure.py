"""Tests for src/verify_C_structure.py (Issue I04), including a mutation check."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

import verify_C_structure as V  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_passes(n):
    rep = V.verify(n, verbose=False)
    assert rep["status"] == "PASS"
    assert rep["failures"] == []
    assert rep["triples_checked"] == rep["dim"] ** 3


def test_verifier_detects_corruption(tmp_path, monkeypatch):
    src = os.path.join(V.DATA_DIR, "C_1_structure.json")
    d = json.load(open(src))
    # corrupt one coefficient: [E_2del1_p, E_2del1_m] = 4 H_2  ->  3 H_2
    for e in d["structure_constants"]:
        if e["X"] == "E_2del1_p" and e["Y"] == "E_2del1_m":
            e["coeff"] = "3"
    os.makedirs(tmp_path / "data", exist_ok=True)
    json.dump(d, open(tmp_path / "data" / "C_1_structure.json", "w"))
    monkeypatch.setattr(V, "DATA_DIR", str(tmp_path / "data"))
    rep = V.verify(1, verbose=False)
    kinds = {f[0] for f in rep["failures"]}
    assert rep["status"] == "FAIL"
    assert "antisymmetry" in kinds and "jacobi" in kinds
