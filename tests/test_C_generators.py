"""
Unit tests for C_generators.py

Tests: parity, generator counts, basis completeness, basic bracket relations.
"""

import json
import os
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import (
    build_generators, build_basis_order, build_schema1,
    _graded_bracket, _normalize_word, _add, _scale, _single,
    compute_structure_constants
)
from fractions import Fraction


@pytest.mark.parametrize("n", [1, 2, 3])
def test_dimension_counts(n):
    """Even and odd basis counts match dimension formulas."""
    gens = build_generators(n)
    basis = build_basis_order(n)
    even_count = sum(1 for b in basis if gens[b][1] == 0)
    odd_count = sum(1 for b in basis if gens[b][1] == 1)
    assert even_count == 2 * n * n + n + 1, f"n={n}: even count wrong"
    assert odd_count == 4 * n, f"n={n}: odd count wrong"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_assignment(n):
    """All parity values are 0 or 1."""
    schema = build_schema1(n)
    for label, p in schema["parity"].items():
        assert p in (0, 1), f"Invalid parity {p} for {label}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_cartan_generators_present(n):
    """H_1 through H_{n+1} are in the basis."""
    gens = build_generators(n)
    for k in range(1, n + 2):
        assert f"H_{k}" in gens, f"H_{k} missing for n={n}"
        assert gens[f"H_{k}"][1] == 0, f"H_{k} should be even for n={n}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_odd_generators_present(n):
    """All 4n odd generators are present."""
    gens = build_generators(n)
    for k in range(1, n + 1):
        for sign in ["pp", "pm", "mp", "mm"]:
            label = f"E_eps1_del{k}_{sign}"
            assert label in gens, f"{label} missing for n={n}"
            assert gens[label][1] == 1, f"{label} should be odd"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema1_json_structure(n):
    """Schema 1 has all required top-level keys."""
    schema = build_schema1(n)
    required_keys = [
        "schema_version", "algebra", "central_elements",
        "oscillator_generators", "oscillator_relations",
        "basis", "parity", "generator_realization",
        "structure_constants", "metadata"
    ]
    for key in required_keys:
        assert key in schema, f"Missing key '{key}' for n={n}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_algebra_field(n):
    """Algebra field has correct family, m, and dimension formulas."""
    schema = build_schema1(n)
    alg = schema["algebra"]
    assert alg["family"] == "C"
    assert alg["m"] == 1
    assert alg["dimension"]["even"] == 2 * n * n + n + 1
    assert alg["dimension"]["odd"] == 4 * n
    assert alg["dimension"]["total"] == 2 * n * n + 5 * n + 1


@pytest.mark.parametrize("n", [1, 2, 3])
def test_central_elements(n):
    """Central elements key exists with kappa and K."""
    schema = build_schema1(n)
    ce = schema["central_elements"]
    assert "K" in ce
    assert "kappa" in ce
    assert ce["K"]["parity"] == 0
    assert ce["kappa"]["parity"] == 1


def test_normalize_word_bosons_n1():
    """[b_1^-, b_1^+] = 1 in PBW normalization (bosons, n=1)."""
    # b_1_m * b_1_p should give b_1_p * b_1_m + 1
    word = ("b_1_m", "b_1_p")
    result = _normalize_word(word, 1)
    # b_1_m has order 3, b_1_p has order 2 => inversion
    # b_1_m * b_1_p = b_1_p * b_1_m + [b_1_m, b_1_p]
    # [b_1_m, b_1_p] = 1
    assert ("b_1_p", "b_1_m") in result or () in result


def test_normalize_word_fermions_n1():
    """{a_1^-, a_1^+} = 1 => a_1_m * a_1_p = -a_1_p * a_1_m + 1."""
    word = ("a_1_m", "a_1_p")
    result = _normalize_word(word, 1)
    # Should contain scalar 1 and possibly -a_1_p * a_1_m
    # a_1_m has order 1, a_1_p has order 0 => inversion
    assert () in result or ("a_1_p", "a_1_m") in result


def test_h1_bracket_eps_root_n1():
    """[H_1, E_eps1_del1_pp] = 2 * E_eps1_del1_pp for C(2)."""
    n = 1
    gens = build_generators(n)
    H1, pH1 = gens["H_1"]
    E_pp, pE = gens["E_eps1_del1_pp"]
    bracket = _graded_bracket(H1, E_pp, pH1, pE, n)
    # Should equal 2 * E_eps1_del1_pp = 2 * a_1_p * b_1_p
    expected = _single(("a_1_p", "b_1_p"), Fraction(2))
    assert bracket == expected, f"Got {bracket}, expected {expected}"


def test_odd_bracket_even_n1():
    """[E_eps1_del1_pp, E_eps1_del1_mm] produces an even generator for C(2)."""
    n = 1
    gens = build_generators(n)
    E_pp, ppp = gens["E_eps1_del1_pp"]
    E_mm, pmm = gens["E_eps1_del1_mm"]
    bracket = _graded_bracket(E_pp, E_mm, ppp, pmm, n)
    # This should produce H_1 type combination (even element)
    assert bracket, "Bracket should be non-zero"
    # Check all words in bracket have even total oscillator parity
    for word in bracket:
        p = sum(1 for o in word if o in ("a_1_p", "a_1_m")) % 2
        assert p == 0, f"Odd parity word {word} in even bracket result"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constant_parity(n):
    """Each structure constant entry has consistent parity: p(X) + p(Y) = p(Z) mod 2."""
    schema = build_schema1(n)
    parity = schema["parity"]
    for sc in schema["structure_constants"]:
        pX = parity[sc["X"]]
        pY = parity[sc["Y"]]
        pZ = parity[sc["Z"]]
        assert (pX + pY) % 2 == pZ, (
            f"Parity violation: [{sc['X']},{sc['Y']}] -> {sc['Z']}: "
            f"p(X)={pX}, p(Y)={pY}, p(Z)={pZ}"
        )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_data_files_exist(n):
    """Check that the generated JSON data files exist."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", f"C_{n}_structure.json")
    assert os.path.exists(data_path), f"Missing data file: C_{n}_structure.json"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_data_file_loadable(n):
    """Generated JSON files are loadable and have correct structure."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", f"C_{n}_structure.json")
    with open(data_path) as f:
        schema = json.load(f)
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["n"] == n
