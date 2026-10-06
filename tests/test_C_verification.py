"""Issue I04: antisymmetry and super Jacobi identity as part of the test suite."""

from __future__ import annotations

import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "src"))

import C_generators as gen  # noqa: E402
import verify_C_structure as ver  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_full_verification_passes(n, capsys):
    path = os.path.join(REPO, "data", f"C_{n}_structure.json")
    if not os.path.exists(path):
        gen.write_schema1(n)
    assert ver.verify(n) is True
