"""Tests for src/C_generators.py."""

from fractions import Fraction

from src.C_generators import (
    build_basis,
    build_structure_json,
    project,
    recombine,
    structure_constants,
)
from src.C_oscillator import graded_bracket, mono, poly_add


def test_dimensions():
    for n in (1, 2, 3):
        even, odd, reals, pars = build_basis(n)
        assert len(even) == 2 * n * n + n + 1
        assert len(odd) == 4 * n
        assert all(pars[l] == 0 for l in even)
        assert all(pars[l] == 1 for l in odd)
        assert set(reals.keys()) == set(even + odd)


def test_H1_bracket_with_root():
    # [H_1, E_eps1_del1_pp] = 2 * E_eps1_del1_pp
    even, odd, reals, pars = build_basis(1)
    br = graded_bracket(reals["H_1"], reals["E_eps1_del1_pp"], 0, 1)
    coeffs = project(br, 1)
    assert coeffs == {"E_eps1_del1_pp": Fraction(2)}


def test_closure_n1_n2_n3():
    for n in (1, 2, 3):
        _, _, _, _, _, errors = structure_constants(n)
        assert errors == [], f"non-closing brackets for n={n}: {errors[:2]}"


def test_structure_json_shape_n1():
    obj = build_structure_json(1)
    assert obj["algebra"]["family"] == "C"
    assert obj["algebra"]["m"] == 1
    assert obj["algebra"]["dimension"] == {"even": 4, "odd": 4, "total": 8}
    assert "central_elements" in obj
    assert set(obj["central_elements"].keys()) == {"kappa", "K"}
    assert obj["central_elements"]["kappa"]["parity"] == 1
    labels = obj["basis"]["even"] + obj["basis"]["odd"]
    assert set(obj["parity"].keys()) == set(labels)


def test_antisymmetry_sample():
    # Pick a bosonic-bosonic bracket and verify [X,Y] = -[Y,X]
    _, _, reals, pars = build_basis(2)
    br1 = graded_bracket(
        reals["E_del1_del2_pm"], reals["E_del1_del2_mp"], 0, 0
    )
    br2 = graded_bracket(
        reals["E_del1_del2_mp"], reals["E_del1_del2_pm"], 0, 0
    )
    assert poly_add(br1, br2) == {}


def test_recombine_projection_roundtrip():
    _, _, reals, pars = build_basis(2)
    # Nontrivial bracket
    br = graded_bracket(reals["H_2"], reals["E_del1_del2_pp"], 0, 0)
    cf = project(br, 2)
    rec = recombine(cf, reals)
    assert poly_add(br, rec, Fraction(-1)) == {}
