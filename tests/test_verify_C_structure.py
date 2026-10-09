"""Tests for the Schema 1 verifier (Issue I04)."""
import json
import os
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from verify_C_structure import verify  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_passes_jacobi(n):
    rep = verify(os.path.join(ROOT, "data", f"C_{n}_structure.json"), verbose=False)
    assert rep["pass"]
    assert rep["triples"] == (2 * n * n + 5 * n + 1) ** 3


def test_verifier_detects_corruption(tmp_path):
    with open(os.path.join(ROOT, "data", "C_1_structure.json")) as fh:
        d = json.load(fh)
    d["structure_constants"][0]["coeff"] = "7"
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(d))
    rep = verify(str(p), verbose=False)
    assert not rep["pass"]
    assert rep["antisymmetry_failures"] and rep["jacobi_failures"]
