import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_gamma import (build_schema2, check_against_schema1, check_deformed_jacobi,  # noqa: E402
                     check_gamma_symmetry, compute_gamma, gb_labels)


@pytest.fixture(scope="module", params=[1, 2, 3])
def computed(request):
    return (request.param,) + compute_gamma(request.param)


def test_gb_count():
    for n in (1, 2, 3):
        assert len(gb_labels(n)) == len(set(gb_labels(n))) == 4 * n


def test_consistency_with_schema1(computed):
    n, calg, und, gam = computed
    assert check_against_schema1(n, und)
    assert not check_gamma_symmetry(calg.basis, calg.parity, gam)


def test_deformed_jacobi(computed):
    n, calg, und, gam = computed
    _, fails = check_deformed_jacobi(calg.basis, calg.parity, und, gam)
    assert not fails


def test_deformed_jacobi_negative_control():
    _, calg, und, gam = (1,) + compute_gamma(1)
    gam[("E_2del1_p", "E_eps1_del1_pm")]["H_2"] = {"gb_a1p_b1p": Fraction(3)}  # true: 2
    gam[("E_eps1_del1_pm", "E_2del1_p")]["H_2"] = {"gb_a1p_b1p": Fraction(-3)}
    _, fails = check_deformed_jacobi(calg.basis, calg.parity, und, gam)
    assert fails


def test_hand_computed_value():
    # [(b^+)^2, a^+ b^-] kappa-part = -2 g b^+b^- = 2g H_2 + g K,  g = gb_{a1+, b1+}
    _, calg, und, gam = (1,) + compute_gamma(1)
    v = gam[("E_2del1_p", "E_eps1_del1_pm")]
    assert v == {"H_2": {"gb_a1p_b1p": 2}, "K": {"gb_a1p_b1p": 1}}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_data_file_matches(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_gamma.json")) as fh:
        stored = json.load(fh)
    fresh = build_schema2(n, date=stored["metadata"]["generation_date"])
    assert stored == json.loads(json.dumps(fresh))
