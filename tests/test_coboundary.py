import itertools
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import coboundary as cb  # noqa: E402
import gamma  # noqa: E402
from gauge_f import trivializing_f  # noqa: E402


def cocycle_errors(L, gam):
    """First-order super Jacobi of [,]_0 + kappa*gam on g + kappa g (all triples in g)."""
    g = {}
    for (x, y, z), c in gam.items():
        g.setdefault((x, y), {})[z] = c
    par = L.par

    def bb(x, y):
        (X, ex), (Y, ey) = x, y
        out = {}
        if ex == 0 and ey == 0:
            for Z, c in L.br.get((X, Y), {}).items():
                out[(Z, 0)] = c
            for Z, c in g.get((X, Y), {}).items():
                out[(Z, 1)] = out.get((Z, 1), 0) + c
        elif ex == 0:
            for Z, c in L.br.get((X, Y), {}).items():
                out[(Z, 1)] = (-1) ** par[X] * c
        elif ey == 0:
            for Z, c in L.br.get((X, Y), {}).items():
                out[(Z, 1)] = c
        return {k: v for k, v in out.items() if v}

    def br(A, B):
        o = {}
        for x, cx in A.items():
            for y, cy in B.items():
                cb._add(o, bb(x, y), cx * cy)
        return o

    errs = 0
    for X, Y, Z in itertools.product(L.labels, repeat=3):
        x, y, z = (X, 0), (Y, 0), (Z, 0)
        lhs = br({x: 1}, br({y: 1}, {z: 1}))
        rhs = br(br({x: 1}, {y: 1}), {z: 1})
        cb._add(rhs, br({y: 1}, br({x: 1}, {z: 1})), (-1) ** (par[X] * par[Y]))
        errs += lhs != rhs
    return errs


def test_elementary_coboundaries_are_cocycles_n1():
    L = cb.Layer1(1)
    for m in L.odd_map_basis():
        assert cocycle_errors(L, cb.delta_elementary(L, *m)) == 0


def test_elementary_coboundaries_are_cocycles_n2_sample():
    L = cb.Layer1(2)
    maps = L.odd_map_basis()
    for m in maps[::17]:
        assert cocycle_errors(L, cb.delta_elementary(L, *m)) == 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_delta_has_graded_symmetry_and_parity(n):
    L = cb.Layer1(n)
    for m in L.odd_map_basis()[::7]:
        d = cb.delta_elementary(L, *m)
        for (X, Y, Z), c in d.items():
            assert L.par[Z] == (L.par[X] + L.par[Y] + 1) % 2
            assert d.get((Y, X, Z)) == -(-1) ** (L.par[X] * L.par[Y]) * c


@pytest.mark.parametrize("n", [1, 2, 3])
def test_closed_form_f_trivializes_every_unit_gb_and_is_odd(n):
    L = cb.Layer1(n)
    elem = {m: cb.delta_elementary(L, *m) for m in L.odd_map_basis()}
    labels = L.labels
    for key in gamma.param_keys(n):
        f = trivializing_f(n, {key: 1})
        assert all(L.par[to] != L.par[frm] for (to, frm) in f)
        df = cb.delta_of_f(f, elem)
        alg = gamma.DeformedC(n, {key: 1})
        direct = {}
        for X in labels:
            for Y in labels:
                for Z, c in alg.bracket(X, Y)[1].items():
                    direct[(X, Y, Z)] = c
        assert df == direct  # delta f = gamma, gamma computed independently from the oscillator algebra


@pytest.mark.parametrize("n", [1, 2, 3])
def test_data_file(n):
    d = json.load(open(os.path.join(cb.DATA, f"C_{n}_coboundary.json")))
    assert d == json.loads(json.dumps(cb.schema4(n)))
    assert all(p["trivial"] and p["residual"] == [] for p in d["profiles"])
