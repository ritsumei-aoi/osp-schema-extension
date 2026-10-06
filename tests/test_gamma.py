import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import gamma  # noqa: E402
import verify_gamma  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gamma_consistency(n):
    assert verify_gamma.check(n)["errors"] == []


@pytest.mark.parametrize("n", [1, 2, 3])
def test_gb_matrix_shape(n):
    d = gamma.schema2(n)["inhomogeneous_deformation"]["gb_matrix"]
    assert d["shape"] == [2, 2 * n] and len(d["parameters"]) == 4 * n


def test_gamma_linear_in_gb_n1():
    keys = gamma.param_keys(1)
    labels = gamma.CAlgebra(1).labels
    gb = {k: i + 1 for i, k in enumerate(keys)}
    full = gamma.DeformedC(1, gb)
    units = [gamma.DeformedC(1, {k: v}) for k, v in gb.items()]
    for X in labels:
        for Y in labels:
            tot = {}
            for u in units:
                for Z, c in u.bracket(X, Y)[1].items():
                    tot[Z] = tot.get(Z, 0) + c
            tot = {k: v for k, v in tot.items() if v}
            assert full.bracket(X, Y)[1] == tot
