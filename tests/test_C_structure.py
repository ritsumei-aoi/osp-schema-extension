"""
Unit tests for C(n+1) structure constant generator (src/C_generators.py).
"""

import json
import os
import sys
import pytest
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import (
    build_basis, parity_of, build_parity_dict,
    build_generator_realizations, compute_structure_constants, build_schema1
)


# ---------------------------------------------------------------------------
# Parametrize over n=1,2,3
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3])
class TestBasisCounts:
    def test_even_count(self, n):
        even, odd = build_basis(n)
        assert len(even) == 2 * n * n + n + 1, f"Even dim mismatch for n={n}"

    def test_odd_count(self, n):
        even, odd = build_basis(n)
        assert len(odd) == 4 * n, f"Odd dim mismatch for n={n}"

    def test_total_count(self, n):
        even, odd = build_basis(n)
        assert len(even) + len(odd) == 2 * n * n + 5 * n + 1

    def test_parity_consistency(self, n):
        even, odd = build_basis(n)
        parity = build_parity_dict(even, odd)
        for g in even:
            assert parity[g] == 0
        for g in odd:
            assert parity[g] == 1


@pytest.mark.parametrize("n", [1, 2, 3])
class TestGeneratorCounts:
    def test_generator_realization_count(self, n):
        gens = build_generator_realizations(n)
        even, odd = build_basis(n)
        total = len(even) + len(odd)
        assert len(gens) == total, f"Generator count mismatch for n={n}"

    def test_all_basis_elements_have_realizations(self, n):
        even, odd = build_basis(n)
        gens = build_generator_realizations(n)
        for g in even + odd:
            assert g in gens, f"Missing realization for {g}"


@pytest.mark.parametrize("n", [1, 2, 3])
class TestStructureConstants:
    def test_structure_constants_nonempty(self, n):
        sc = compute_structure_constants(n)
        assert len(sc) > 0

    def test_structure_constant_fields(self, n):
        sc = compute_structure_constants(n)
        for entry in sc:
            assert "X" in entry
            assert "Y" in entry
            assert "Z" in entry
            assert "coeff" in entry
            assert entry["sign_rule"] == "graded"

    def test_coeff_nonzero(self, n):
        sc = compute_structure_constants(n)
        for entry in sc:
            assert Fraction(entry["coeff"]) != 0


@pytest.mark.parametrize("n", [1, 2, 3])
class TestSchemaConformance:
    def test_schema_version(self, n):
        schema = build_schema1(n)
        assert schema["schema_version"] == "5.0"

    def test_algebra_family(self, n):
        schema = build_schema1(n)
        assert schema["algebra"]["family"] == "C"
        assert schema["algebra"]["m"] == 1
        assert schema["algebra"]["n"] == n

    def test_central_elements_present(self, n):
        schema = build_schema1(n)
        assert "central_elements" in schema
        assert "kappa" in schema["central_elements"]
        assert "K" in schema["central_elements"]
        assert schema["central_elements"]["kappa"]["parity"] == 1
        assert schema["central_elements"]["K"]["parity"] == 0

    def test_oscillator_generators_keys(self, n):
        schema = build_schema1(n)
        og = schema["oscillator_generators"]
        assert "fermions" in og
        assert "bosons" in og
        assert "supplementary_fermion" not in og

    def test_dimensions_match(self, n):
        schema = build_schema1(n)
        dim = schema["algebra"]["dimension"]
        basis = schema["basis"]
        assert len(basis["even"]) == dim["even"]
        assert len(basis["odd"]) == dim["odd"]
        assert dim["even"] + dim["odd"] == dim["total"]


@pytest.mark.parametrize("n", [1, 2, 3])
class TestJSONFiles:
    def test_json_files_exist(self, n):
        fname = f"data/C_{n}_structure.json"
        assert os.path.exists(fname), f"Missing {fname}"

    def test_json_loadable(self, n):
        fname = f"data/C_{n}_structure.json"
        if not os.path.exists(fname):
            pytest.skip("JSON file not yet generated")
        with open(fname) as f:
            data = json.load(f)
        assert data["schema_version"] == "5.0"
        assert data["algebra"]["family"] == "C"
