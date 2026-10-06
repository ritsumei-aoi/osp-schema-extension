import itertools
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_coboundary import load_coboundary  # noqa: E402
from C_triviality import (gamma_from_layer2, gamma_from_layer3,  # noqa: E402
                          gamma_K_formula_mismatches, inner_maps_in_kernel, solve)


def numeric_gamma(gsym, vals):
    out = {}
    for k, v in gsym.items():
        for Z, lin in v.items():
            c = sum((x * vals[g] for g, x in lin.items()), Fraction(0))
            if c:
                out.setdefault(k, {})[Z] = {"1": c}
    return out


def test_all_sign_vectors_n1():
    basis, _, labels, forms = load_coboundary(1)
    gsym = gamma_from_layer2(1)
    params = sorted({g for v in gsym.values() for lin in v.values() for g in lin})
    assert len(params) == 4
    for signs in itertools.product((1, -1), repeat=4):
        gam = numeric_gamma(gsym, dict(zip(params, map(Fraction, signs))))
        assert not solve(basis, labels, forms, gam, "A")["conditions"]
        assert solve(basis, labels, forms, gam, "B")["conditions"]


@pytest.mark.parametrize("n", [1, 2])
def test_layer3_default_profile(n):
    basis, _, labels, forms = load_coboundary(n)
    gam, _ = gamma_from_layer3(n, "allplus")
    rA = solve(basis, labels, forms, gam, "A")
    assert not rA["conditions"] and rA["nullity"] == 4 * n
    rB = solve(basis, labels, forms, gam, "B")
    assert all(Z == "K" for _, _, Z, _ in rB["witnesses"])


def test_solver_negative_control():
    """A perturbed (non-cocycle) γ must be reported as non-trivial even in mode A."""
    basis, _, labels, forms = load_coboundary(1)
    gam, _ = gamma_from_layer3(1, "allplus")
    gam[("E_2del1_p", "E_eps1_del1_pm")]["H_2"] = {"1": Fraction(5)}
    assert solve(basis, labels, forms, gam, "A")["conditions"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structural_facts(n):
    assert gamma_K_formula_mismatches(n) == 0
    assert inner_maps_in_kernel(n) == 0
