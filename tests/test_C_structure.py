import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_generators import OscAlgebra, ONE  # noqa: E402
from C_structure import build  # noqa: E402


@pytest.mark.parametrize("n,even,odd", [(1, 4, 4), (2, 11, 8), (3, 22, 12)])
def test_generator_counts_and_parity(n, even, odd):
    alg = OscAlgebra(n)
    pairs = alg.basis_pairs()
    parities = [(alg.par[i] + alg.par[j]) % 2 for i, j in pairs]
    assert parities.count(0) == even
    assert parities.count(1) == odd
    assert even == 2 * n * n + n + 1
    assert odd == 4 * n


def test_fermion_square_vanishes_and_car():
    alg = OscAlgebra(1)
    assert alg.normal((0, 0)) == {}
    assert alg.normal((1, 1)) == {}
    # a1m a1p = -a1p a1m + 1
    assert alg.normal((1, 0)) == {(0, 1): (Fraction(-1), Fraction(0)), (): ONE}


def test_boson_ccr():
    alg = OscAlgebra(1)
    # b1m b1p = b1p b1m + 1
    assert alg.normal((3, 2)) == {(2, 3): ONE, (): ONE}


def test_weyl_symmetric_constants():
    alg = OscAlgebra(1)
    # W(b1p,b1m) = b1p b1m + 1/2 (no odd sign)
    assert alg.sym(2, 3) == {(2, 3): ONE, (): (Fraction(1, 2), Fraction(0))}
    # W(a1p,a1m) = a1p a1m - 1/2
    assert alg.sym(0, 1) == {(0, 1): ONE, (): (Fraction(-1, 2), Fraction(0))}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_closure_no_constant_terms(n):
    data = build(n)
    assert data["structure_constants"]["constant_terms"] == []
    assert all(e["kappa_coeff"] == "0" for e in data["structure_constants"]["brackets"])
    assert len(data["basis"]["odd"]) + len(data["basis"]["even"]) == 2 * n * n + 5 * n + 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_written_json_matches_builder(n):
    path = os.path.join(ROOT, "data", f"C_{n}_structure.json")
    with open(path) as fh:
        written = json.load(fh)
    assert written["algebra"]["n"] == n
    assert written["algebra"]["dimension"]["total"] == 2 * n * n + 5 * n + 1
    assert written["schema_version"] == "5.0"
    assert written["central_elements"]["K"]["parity"] == 0
