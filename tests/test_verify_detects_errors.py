import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import verify_C_structure as v  # noqa: E402


def test_verifier_detects_corrupted_constant(monkeypatch):
    orig = v.load

    def corrupted(n):
        labels, par, br = orig(n)
        br[("H_1", "E_eps1_del1_pp")] = {"E_eps1_del1_pp": Fraction(3)}
        return labels, par, br

    monkeypatch.setattr(v, "load", corrupted)
    r = v.verify(1)
    assert r["antisym_failures"] and r["jacobi_failures"]
