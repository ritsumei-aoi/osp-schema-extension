"""Issue I06: Schema 3 (evaluated structure) tests."""
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_evaluate import (check_consistency_with_schema2, evaluate_gamma, gb_profiles,  # noqa: E402
                        load_evaluated)
from C_gamma import load_gamma  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_profiles_have_4n_parameters(n):
    for values in gb_profiles(n).values():
        assert len(values) == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("profile", ["all_plus", "fermion_sign", "single_a1p_b1m", "zero"])
def test_schema3_consistent_with_schema2(n, profile):
    assert check_consistency_with_schema2(n, profile)
    doc, ev = load_evaluated(n, profile)
    assert doc["schema_layer"] == 3 and doc["gb_assignment"]["profile"] == profile
    assert doc["evaluated_deformation"]["count"] == sum(len(e) for e in ev.values())
    if profile == "zero":
        assert ev == {}


def test_evaluated_n1_values():
    _, gamma_sym = load_gamma(1)
    ev = evaluate_gamma(gamma_sym, gb_profiles(1)["all_plus"])
    assert ev[("E_eps1_del1_pm", "H_2")] == {"H_2": Fraction(1), "E_2del1_m": Fraction(-1), "K": Fraction(1, 2)}
    ev1 = evaluate_gamma(gamma_sym, gb_profiles(1)["single_a1p_b1m"])
    assert ev1[("E_eps1_del1_pm", "H_2")] == {"H_2": Fraction(1), "K": Fraction(1, 2)}
