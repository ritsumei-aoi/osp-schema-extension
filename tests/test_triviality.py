import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import coboundary as cb  # noqa: E402
import gamma  # noqa: E402
import triviality_search as ts  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_layers_coincide_for_every_profile(n):
    rows = ts.compare_layers(n)
    assert all(r[3] == 0 and r[4] for r in rows)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_all_gb_trivial_and_restricted_classes(n):
    T, _, npar = ts.trivial_subspace(n, ts.CLASSES["all odd maps f"])
    assert len(T) == npar == 4 * n
    for name in ("f vanishing on even generators (odd -> even only)",
                 "f vanishing on odd generators (even -> odd only)",
                 "f vanishing on Cartan generators"):
        assert len(ts.trivial_subspace(n, ts.CLASSES[name])[0]) == 0
    name = "f vanishing on E_2del / E_del_del (long and short even roots)"
    assert len(ts.trivial_subspace(n, ts.CLASSES[name])[0]) == 4 * n


@pytest.mark.parametrize("n", [1, 2])
def test_kernel_of_delta_is_inner_odd_derivations(n):
    L = cb.Layer1(n)
    maps = L.odd_map_basis()
    dec = ts.make_decomposer([cb.delta_elementary(L, *m) for m in maps], skip_dependent=True)
    assert len(maps) - dec.rank == 4 * n  # = number of odd generators (f = ad u)


@pytest.mark.parametrize("n", [1, 2])
def test_central_residual_formula(n):
    """Un-symmetrised odd generators: kappa*K coefficient of [X,Y} is -(1/2) sum_{Z odd} c_XY^Z gb_Z."""
    L = cb.Layer1(n)
    for key in gamma.param_keys(n):
        cen, _ = ts.central_residual(n, key)
        z = "E_eps1_del%d_%s%s" % (key[1], key[0], key[2])
        pred = {}
        for X in L.labels:
            for Y in L.labels:
                c = L.br.get((X, Y), {}).get(z, 0)
                if c:
                    pred[(X, Y)] = -Fraction(1, 2) * c
        assert cen == pred
