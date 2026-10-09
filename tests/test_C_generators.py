"""Tests for C(n+1) structure constant generator."""

import json
import os
import sys
import pytest
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import (
    build_basis, get_parity, get_realization, compute_bracket,
    generate_schema1_json, compute_product
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


class TestBasisCounts:
    @pytest.mark.parametrize("n,expected_even,expected_odd,expected_total", [
        (1, 4, 4, 8),
        (2, 11, 8, 19),
        (3, 22, 12, 34),
    ])
    def test_dimensions(self, n, expected_even, expected_odd, expected_total):
        even, odd = build_basis(n)
        assert len(even) == expected_even
        assert len(odd) == expected_odd
        assert len(even) + len(odd) == expected_total

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_dimension_formulas(self, n):
        even, odd = build_basis(n)
        assert len(even) == 2 * n * n + n + 1
        assert len(odd) == 4 * n


class TestParity:
    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_even_generators_have_parity_0(self, n):
        even, _ = build_basis(n)
        for label in even:
            assert get_parity(label) == 0, f"{label} should have parity 0"

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_odd_generators_have_parity_1(self, n):
        _, odd = build_basis(n)
        for label in odd:
            assert get_parity(label) == 1, f"{label} should have parity 1"


class TestRealizations:
    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_all_generators_have_realizations(self, n):
        even, odd = build_basis(n)
        for label in even + odd:
            real = get_realization(label, n)
            assert len(real) > 0, f"{label} has no realization"

    def test_H1_realization(self):
        real = get_realization("H_1", 1)
        assert (Fraction(1), ("a_1_p", "a_1_m")) in real
        assert (Fraction(1), ("b_1_p", "b_1_m")) in real

    def test_odd_generator_realization(self):
        real = get_realization("E_eps1_del1_pp", 1)
        assert real == [(Fraction(1), ("a_1_p", "b_1_p"))]

    def test_E2del_realization(self):
        real = get_realization("E_2del1_p", 1)
        assert real == [(Fraction(1, 2), ("b_1_p", "b_1_p"))]


class TestOscillatorAlgebra:
    def test_fermion_anticommutator(self):
        result = compute_product(("a_1_p",), ("a_1_m",))
        result2 = compute_product(("a_1_m",), ("a_1_p",))
        total = {}
        for w, c in list(result.items()) + list(result2.items()):
            total[w] = total.get(w, Fraction(0)) + c
        total = {w: c for w, c in total.items() if c != 0}
        assert total == {(): Fraction(1)}

    def test_fermion_self_anticommutator(self):
        result = compute_product(("a_1_p",), ("a_1_p",))
        result2 = compute_product(("a_1_p",), ("a_1_p",))
        total = {}
        for w, c in list(result.items()) + list(result2.items()):
            total[w] = total.get(w, Fraction(0)) + c
        total = {w: c for w, c in total.items() if c != 0}
        assert total == {}

    def test_boson_commutator(self):
        r1 = compute_product(("b_1_m",), ("b_1_p",))
        r2 = compute_product(("b_1_p",), ("b_1_m",))
        diff = {}
        for w, c in r1.items():
            diff[w] = diff.get(w, Fraction(0)) + c
        for w, c in r2.items():
            diff[w] = diff.get(w, Fraction(0)) - c
        diff = {w: c for w, c in diff.items() if c != 0}
        assert diff == {(): Fraction(1)}


class TestBrackets:
    def test_cartan_on_root_generator(self):
        result = compute_bracket("H_1", "E_eps1_del1_pp", 1)
        assert ("a_1_p", "b_1_p") in result
        assert result[("a_1_p", "b_1_p")] == Fraction(2)

    def test_anticommutator_odd_odd(self):
        result = compute_bracket("E_eps1_del1_pm", "E_eps1_del1_mp", 1)
        assert ("a_1_p", "a_1_m") in result or ("b_1_p", "b_1_m") in result

    def test_sp2_sl2_triple(self):
        result = compute_bracket("E_2del1_p", "E_2del1_m", 1)
        expected_words = {("b_1_p", "b_1_m"), ()}
        assert set(result.keys()).issubset(expected_words)


class TestSchemaOutput:
    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_schema_generation(self, n):
        schema = generate_schema1_json(n)
        assert schema["schema_version"] == "5.0"
        assert schema["algebra"]["family"] == "C"
        assert schema["algebra"]["m"] == 1
        assert schema["algebra"]["n"] == n
        assert schema["algebra"]["dimension"]["even"] == 2 * n * n + n + 1
        assert schema["algebra"]["dimension"]["odd"] == 4 * n

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_structure_constants_nonempty(self, n):
        schema = generate_schema1_json(n)
        assert len(schema["structure_constants"]) > 0

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_parity_consistency(self, n):
        schema = generate_schema1_json(n)
        all_labels = schema["basis"]["odd"] + schema["basis"]["even"]
        for label in all_labels:
            assert label in schema["parity"]

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_json_files_exist(self, n):
        path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
        assert os.path.exists(path), f"Missing {path}"
        with open(path) as f:
            data = json.load(f)
        assert data["algebra"]["n"] == n

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_central_elements(self, n):
        schema = generate_schema1_json(n)
        assert "central_elements" in schema
        assert schema["central_elements"]["kappa"]["parity"] == 1
        assert schema["central_elements"]["K"]["parity"] == 0
