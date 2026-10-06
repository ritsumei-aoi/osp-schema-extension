import json
import os

import pytest

from C_generators import (CAlgebra, DATA_DIR, build_structure, even_basis, odd_basis,
                          ordered_basis, parity_of, realization)
from C_osc import Lin

NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
def test_counts(n):
    assert len(even_basis(n)) == 2 * n * n + n + 1
    assert len(odd_basis(n)) == 4 * n
    assert len(set(ordered_basis(n))) == 2 * n * n + 5 * n + 1


@pytest.mark.parametrize("n", NS)
def test_parity(n):
    assert all(parity_of(b) == 0 for b in even_basis(n))
    assert all(parity_of(b) == 1 for b in odd_basis(n))
    # parity of every non-constant realization word equals the generator parity
    alg = CAlgebra(n)
    for b in alg.basis:
        for w, _ in realization(n, b):
            assert w == () or alg.osc.word_parity(w) == parity_of(b)


def test_pbw_order_n2():
    assert ordered_basis(2)[:2] == ["E_eps1_del1_pp", "E_eps1_del2_pp"]
    assert ordered_basis(2)[8:11] == ["H_1", "H_2", "H_3"]


def test_oscillator_relations():
    o = CAlgebra(1).osc
    one = {(): Lin.const(1)}
    am, ap = {("a_1_m",): Lin.const(1)}, {("a_1_p",): Lin.const(1)}
    bm, bp = {("b_1_m",): Lin.const(1)}, {("b_1_p",): Lin.const(1)}
    assert o.bracket(am, ap, 1, 1) == one  # {a-, a+} = 1
    assert o.bracket(ap, ap, 1, 1) == {}   # {a+, a+} = 0
    assert o.bracket(bm, bp, 0, 0) == one  # [b-, b+] = 1
    assert o.bracket(bp, ap, 0, 1) == {}   # undeformed [b, a] = 0


def test_hand_computed_brackets_n1():
    alg = CAlgebra(1)
    # {a+ b+, a- b-} = b+b- - a+a- + 1 = -H_1 - 2 H_2
    d = alg.bracket0("E_eps1_del1_pp", "E_eps1_del1_mm")
    assert {k: v.to_str() for k, v in d.items()} == {"H_1": "-1", "H_2": "-2"}
    # [(b+)^2, (b-)^2] = -4 b+b- - 2 = 4 H_2
    d = alg.bracket0("E_2del1_p", "E_2del1_m")
    assert {k: v.to_str() for k, v in d.items()} == {"H_2": "4"}


@pytest.mark.parametrize("n", NS)
def test_closure_and_json(n):
    s = build_structure(n)
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(path) as fh:
        on_disk = json.load(fh)
    on_disk["metadata"].pop("generation_date")
    s["metadata"].pop("generation_date")
    assert on_disk == s
    basis = set(s["basis"]["ordered"])
    for e in s["structure_constants"]:
        assert {e["X"], e["Y"], e["Z"]} <= basis
        assert s["parity"][e["Z"]] == (s["parity"][e["X"]] + s["parity"][e["Y"]]) % 2
    assert s["algebra"]["m"] == 1 and s["algebra"]["family"] == "C"
    assert s["central_elements"]["kappa"]["parity"] == 1
    assert s["central_elements"]["K"]["parity"] == 0
    assert set(s["oscillator_generators"]) == {"fermions", "bosons"}
