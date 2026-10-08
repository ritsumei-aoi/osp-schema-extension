import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from C_generators import (  # noqa: E402
    build_basis,
    build_schema,
    bracket,
    element_from_terms,
    normal_order,
    structure_constants,
)

EXPECTED = {1: (8, 4, 4), 2: (19, 11, 8), 3: (34, 22, 12)}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_counts_and_parity(n):
    basis = build_basis(n)
    total, even, odd = EXPECTED[n]
    assert len(basis) == total
    assert sum(1 for b in basis if b["parity"] == 0) == even
    assert sum(1 for b in basis if b["parity"] == 1) == odd
    assert even == 2 * n * n + n + 1
    assert odd == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_odd_labels_are_eps_type(n):
    odd = [b["label"] for b in build_basis(n) if b["parity"] == 1]
    assert all(label.startswith("E_eps1_del") for label in odd)
    assert len(set(odd)) == 4 * n


def test_fermion_relations():
    assert normal_order(("a_1_p", "a_1_m")) == {
        ("a_1_m", "a_1_p"): Fraction(-1),
        (): Fraction(1),
    }
    assert normal_order(("a_1_p", "a_1_p")) == {}
    assert normal_order(("a_1_m", "a_1_m")) == {}


def test_boson_relations():
    # [b_1_m, b_1_p] = 1
    assert normal_order(("b_1_m", "b_1_p")) == {
        ("b_1_m", "b_1_p"): Fraction(1),
    }
    assert normal_order(("b_1_p", "b_1_m")) == {
        ("b_1_m", "b_1_p"): Fraction(1),
        (): Fraction(-1),
    }
    # different k commute
    assert normal_order(("b_2_p", "b_1_m")) == {("b_1_m", "b_2_p"): Fraction(1)}


@pytest.mark.parametrize("n", [1, 2, 3])
def test_brackets_close_and_are_graded_antisymmetric(n):
    # structure_constants raises if any bracket leaves the span; check it runs
    labels, parities, brackets = structure_constants(n)
    assert len(labels) == EXPECTED[n][0]
    index = {label: i for i, label in enumerate(labels)}
    for entry in brackets:
        assert index[entry["X"]] <= index[entry["Y"]]
        assert entry["sign_rule"] == "graded"
        assert Fraction(entry["coeff"]) != 0


def test_su2_sanity_for_n1():
    # [(b_1^+)^2, (b_1^-)^2] = 4 H_2 (H_2 = -b^+ b^- - 1/2)
    labels, _, brackets = structure_constants(1)
    hits = [
        b for b in brackets
        if {b["X"], b["Y"]} == {"E_2del1_p", "E_2del1_m"}
    ]
    assert hits == [
        {"X": "E_2del1_p", "Y": "E_2del1_m", "Z": "H_2",
         "coeff": "4", "sign_rule": "graded"}
    ]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_shape(n):
    schema = build_schema(n)
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert "central_elements" in schema
    assert set(schema["oscillator_generators"]) == {"fermions", "bosons"}
    assert len(schema["basis"]["odd"]) == 4 * n
    assert set(schema["parity"]) == set(schema["basis"]["even"] + schema["basis"]["odd"])
