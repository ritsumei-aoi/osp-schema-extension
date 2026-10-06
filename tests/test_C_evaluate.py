import json
import os

import pytest

from C_evaluate import build_evaluated, check
from C_generators import DATA_DIR


def load(name):
    with open(os.path.join(DATA_DIR, name)) as fh:
        return json.load(fh)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_evaluated(n):
    gam, ev = load(f"C_{n}_gamma.json"), load(f"C_{n}_evaluated.json")
    assert check(n, ev, gam)["passed"]
    fresh = build_evaluated(n, gam)
    fresh["metadata"].pop("generation_date")
    ev["metadata"].pop("generation_date")
    assert fresh == ev
    for p in ev["profiles"]:
        assert len(p["gb_values"]) == 4 * n
