import json
import os
import random
from fractions import Fraction

import pytest

from conftest import DATA
from C_coboundary import build_schema4, coboundary, evaluate, load_schema4
from C_gamma import deformed_jacobi_failures, load_schema1
from C_oscillator import lin


@pytest.mark.parametrize("n", [1, 2])
def test_schema4_file(n):
    with open(os.path.join(DATA, f"C_{n}_coboundary.json")) as fh:
        d = json.load(fh)
    fresh = build_schema4(n)
    d["metadata"].pop("generation_date")
    fresh["metadata"].pop("generation_date")
    assert d == fresh


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema4_checks(n):
    d, basis, parity, df, dh = load_schema4(n)
    c = d["consistency_checks"]
    assert c["labels_in_layer1_basis"] and c["odd_parity_shift"] and c["graded_antisymmetric"]
    assert c["delta_squared_zero_random_f_failures"] == 0
    nev, nodd = len(d["basis"]["even"]), len(d["basis"]["odd"])
    assert d["odd_linear_map"]["parameter_count"] == 2 * nev * nodd
    # restored ordered pairs agree with a fresh computation
    _, sc = load_schema1(n)
    df2, dh2 = coboundary(basis, parity, sc)
    assert df == df2 and dh == dh2


def test_delta_squared_check_is_not_vacuous():
    """A random odd cochain (not a coboundary) must violate the cocycle identity."""
    d, basis, parity, df, _ = load_schema4(1)
    _, sc = load_schema1(1)
    rng = random.Random(0)
    gam = {}
    for x in basis:
        for y in basis:
            for z in basis:
                if parity[z] == (parity[x] + parity[y] + 1) % 2 and rng.random() < 0.3:
                    gam.setdefault((x, y), {})[z] = lin(rng.randint(1, 3))
    assert deformed_jacobi_failures(1, sc, gam, {}, parity, basis, with_central=False)


def test_example_inner_odd_derivation_in_kernel():
    """An inner odd derivation f(X) = ±[E, X] (E odd; sign either 1 or (-1)^{p(X)}) is a cocycle,
    so delta f = 0 for one of the two sign choices."""
    d, basis, parity, df, _ = load_schema4(1)
    _, sc = load_schema1(1)
    idx = {x: i for i, x in enumerate(basis)}
    E = "E_eps1_del1_pp"
    found = False
    for sign_rule in (lambda p: 1, lambda p: (-1) ** p):
        vals = {}
        for y in basis:
            for z, c in sc.get((E, y), {}).items():
                vals[f"phi_{idx[z]}_{idx[y]}"] = Fraction(c) * sign_rule(parity[y])
        if not evaluate(df, vals):
            found = True
    assert found
