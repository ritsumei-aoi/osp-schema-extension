"""Tests for C(n+1) structure constant generator."""

import json
import os
import sys
import pytest
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from C_generators import (
    build_basis, get_parity, get_realization, compute_bracket,
    express_in_basis, generate_schema1, build_parity_map
)


class TestBasis:
    @pytest.mark.parametrize("n,expected_even,expected_odd", [
        (1, 4, 4),
        (2, 11, 8),
        (3, 22, 12),
    ])
    def test_generator_counts(self, n, expected_even, expected_odd):
        even, odd = build_basis(n)
        assert len(even) == expected_even
        assert len(odd) == expected_odd

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_dimension_formula(self, n):
        even, odd = build_basis(n)
        assert len(even) == 2 * n * n + n + 1
        assert len(odd) == 4 * n
        assert len(even) + len(odd) == 2 * n * n + 5 * n + 1

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_no_duplicate_labels(self, n):
        even, odd = build_basis(n)
        all_gens = even + odd
        assert len(all_gens) == len(set(all_gens))


class TestParity:
    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_parity_assignment(self, n):
        even, odd = build_basis(n)
        for g in even:
            assert get_parity(g) == 0, f"{g} should be even"
        for g in odd:
            assert get_parity(g) == 1, f"{g} should be odd"


class TestRealization:
    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_all_generators_have_realization(self, n):
        even, odd = build_basis(n)
        for g in even + odd:
            real = get_realization(g, n)
            assert len(real) > 0, f"No realization for {g}"

    def test_H1_realization(self):
        real = get_realization("H_1", 1)
        assert len(real) == 2
        words = {w for _, w in real}
        assert ("a_1_p", "a_1_m") in words
        assert ("b_1_p", "b_1_m") in words

    def test_odd_generator_realization(self):
        real = get_realization("E_eps1_del1_pp", 1)
        assert len(real) == 1
        assert real[0] == (Fraction(1), ("a_1_p", "b_1_p"))


class TestBrackets:
    def test_cartan_on_odd_n1(self):
        result = compute_bracket("H_1", "E_eps1_del1_pp", 1)
        gen = express_in_basis(result, 1)
        assert "E_eps1_del1_pp" in gen

    def test_anticommutator_odd_odd_n1(self):
        result = compute_bracket("E_eps1_del1_pp", "E_eps1_del1_mp", 1)
        gen = express_in_basis(result, 1)
        assert "E_2del1_p" in gen

    def test_anticommutator_gives_cartan(self):
        result = compute_bracket("E_eps1_del1_pp", "E_eps1_del1_mm", 1)
        gen = express_in_basis(result, 1)
        assert "H_1" in gen or "H_2" in gen


class TestSchema:
    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_schema_generation(self, n):
        schema = generate_schema1(n)
        assert schema["schema_version"] == "5.0"
        assert schema["algebra"]["family"] == "C"
        assert schema["algebra"]["m"] == 1
        assert schema["algebra"]["n"] == n
        assert schema["algebra"]["dimension"]["even"] == 2 * n * n + n + 1
        assert schema["algebra"]["dimension"]["odd"] == 4 * n

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_structure_constants_nonempty(self, n):
        schema = generate_schema1(n)
        assert len(schema["structure_constants"]) > 0

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_json_files_exist(self, n):
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        path = os.path.join(data_dir, f"C_{n}_structure.json")
        assert os.path.exists(path), f"{path} does not exist"
        with open(path) as f:
            data = json.load(f)
        assert data["schema_version"] == "5.0"

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_parity_consistency(self, n):
        schema = generate_schema1(n)
        for g in schema["basis"]["even"]:
            assert schema["parity"][g] == 0
        for g in schema["basis"]["odd"]:
            assert schema["parity"][g] == 1

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_structure_constant_generators_in_basis(self, n):
        schema = generate_schema1(n)
        all_gens = set(schema["basis"]["even"] + schema["basis"]["odd"])
        for sc in schema["structure_constants"]:
            assert sc["X"] in all_gens, f"X={sc['X']} not in basis"
            assert sc["Y"] in all_gens, f"Y={sc['Y']} not in basis"
            for term in sc["result"]:
                assert term["Z"] in all_gens, f"Z={term['Z']} not in basis"
