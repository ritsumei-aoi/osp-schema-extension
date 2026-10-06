import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import verify_C_structure as V  # noqa: E402


@pytest.mark.parametrize("n", (1, 2, 3))
def test_antisymmetry_and_jacobi(n):
    r = V.verify(n)
    assert r["triples"] == r["dim"] ** 3
    assert r["antisymmetry_failures"] == []
    assert r["jacobi_failures"] == []


def test_verifier_detects_corruption():
    labels, par, sc = V.load_structure(os.path.join(V.DATA_DIR, "C_1_structure.json"))
    key = next(k for k, v in sc.items() if par[k[0]] == 0 and par[k[1]] == 0 and v)
    z = next(iter(sc[key]))
    sc[key][z] += 1
    assert V.check_antisymmetry(labels, par, sc)
    bad, _ = V.check_jacobi(labels, par, sc)
    assert bad
