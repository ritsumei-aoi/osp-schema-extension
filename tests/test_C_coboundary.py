import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_coboundary import (_roundtrip_ok, build_schema4, check_coboundary,  # noqa: E402
                          coboundary_forms, load_coboundary, unknowns)
from verify_C_structure import bracket_table, load_structure  # noqa: E402


def setup(n):
    s1 = load_structure(n)
    return s1["basis"]["ordering"], s1["parity"], bracket_table(s1["structure_constants"])


@pytest.mark.parametrize("n", [1, 2])
def test_coboundary_is_cocycle(n):
    basis, parity, tab = setup(n)
    unk, forms = coboundary_forms(basis, parity, tab)
    fails, jac = check_coboundary(n, basis, parity, tab, unk, forms)
    assert not fails and jac == 0


def test_wrong_sign_convention_detected():
    basis, parity, tab = setup(1)
    unk, forms = coboundary_forms(basis, parity, tab, term_signs=(1, 1, -1))
    fails, jac = check_coboundary(1, basis, parity, tab, unk, forms)
    assert fails or jac > 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_unknown_count(n):
    basis, parity, _ = setup(n)
    e, o = 2 * n * n + n + 1, 4 * n
    assert len(unknowns(basis, parity)) == 2 * e * o + o
    assert len(unknowns(basis, parity, include_K=False)) == 2 * e * o


@pytest.mark.parametrize("n", [1, 2, 3])
def test_file_matches_and_roundtrips(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_coboundary.json")) as fh:
        stored = json.load(fh)
    fresh = build_schema4(n, date=stored["metadata"]["generation_date"])
    assert stored == json.loads(json.dumps(fresh))
    basis, parity, tab = setup(n)
    unk, forms = coboundary_forms(basis, parity, tab)
    _, _, labels, forms_file = load_coboundary(n)
    assert len(labels) == len(unk)
    assert _roundtrip_ok(unk, forms, forms_file)
