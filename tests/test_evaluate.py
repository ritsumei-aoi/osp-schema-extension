import json
import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import evaluate  # noqa: E402
import gamma  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def as_map(entries):
    return {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in entries}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated_matches_direct_deformed_computation(n):
    """Schema 3 (from Schema 2 JSON) == gamma computed directly in the oscillator algebra."""
    d = json.load(open(os.path.join(DATA, f"C_{n}_evaluated.json")))
    labels = d["basis"]["odd"] + d["basis"]["even"]
    keys = {gamma.param_name(k): k for k in gamma.param_keys(n)}
    names = ["all_plus", "alternating"] + ["unit_" + gamma.param_name(gamma.param_keys(n)[0])]
    by_name = {p["name"]: p for p in d["profiles"]}
    for name in names:
        prof = by_name[name]
        alg = gamma.DeformedC(n, {keys[p]: v for p, v in prof["gb"].items()})
        direct = {}
        for X in labels:
            for Y in labels:
                for Z, c in alg.bracket(X, Y)[1].items():
                    direct[(X, Y, Z)] = c
        assert direct == as_map(prof["gamma_evaluated"])


@pytest.mark.parametrize("n", [1, 2, 3])
def test_data_file_current(n):
    assert json.load(open(os.path.join(DATA, f"C_{n}_evaluated.json"))) == json.loads(json.dumps(evaluate.schema3(n)))


def test_n1_has_all_sixteen_sign_profiles():
    d = evaluate.schema3(1)
    assert len([p for p in d["profiles"] if p["name"].startswith("sign_")]) == 16
