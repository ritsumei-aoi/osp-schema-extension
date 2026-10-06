import json
import os
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
import C_evaluate as EV  # noqa: E402
import C_gamma as GM  # noqa: E402

NS = (1, 2, 3)


@pytest.mark.parametrize("n", NS)
def test_default_file_is_all_plus(n):
    d, gamma, gb = EV.load_evaluated(n)
    assert d["gb_assignment"]["profile"] == "all_plus"
    assert len(gb) == 4 * n and set(gb.values()) == {1}
    assert gamma


@pytest.mark.parametrize("n", NS)
def test_all_profiles_match_schema2_and_engine(n):
    _, lin = GM.load_gamma(n)
    for prof, vals in EV.profiles(n).items():
        _, gamma, gb = EV.load_evaluated(n, prof)
        assert gb == vals
        assert gamma == GM.evaluate(lin, vals)
        assert EV.check_against_engine(n, prof, vals)


@pytest.mark.parametrize("n", NS)
def test_zero_profile_is_empty_and_schema1_part_embedded(n):
    d, gamma, _ = EV.load_evaluated(n, "zero")
    assert gamma == {}
    with open(os.path.join(ROOT, "data", f"C_{n}_structure.json")) as fh:
        s1 = json.load(fh)
    assert d["evaluated_structure"]["undeformed_structure_constants"] == s1["structure_constants"]
    assert d["basis"] == s1["basis"]
