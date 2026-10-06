import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import verify_C_structure as v  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_passes(n):
    r = v.verify(n)
    assert r["passed"], r


def test_checker_detects_faults():
    """Negative controls: the verifier must reject a corrupted table."""
    basis, parity, table = v.load_structure(v.DATA / "C_1_structure.json")
    bad = {k: dict(c) for k, c in table.items()}
    bad[("E_2del1_p", "E_2del1_m")] = {"H_2": F(5)}  # breaks antisymmetry and Jacobi
    r = v.verify(1, table_override=bad)
    assert not r["passed"] and r["antisymmetry_failures"] > 0
    bad2 = {k: dict(c) for k, c in table.items()}
    bad2[("E_2del1_p", "E_2del1_m")] = {"H_2": F(5)}
    bad2[("E_2del1_m", "E_2del1_p")] = {"H_2": F(-5)}  # antisymmetric but not Jacobi
    r2 = v.verify(1, table_override=bad2)
    assert r2["antisymmetry_failures"] == 0 and r2["jacobi_failures_shown"]
