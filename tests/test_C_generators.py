#!/usr/bin/env python3
"""
Unit tests for C(n+1) structure constant generator.
"""

import sys
import json
import unittest
sys.path.insert(0, 'src')

from C_generators import CAlgebra


class TestCGeneratorDimensions(unittest.TestCase):
    """Test dimension calculations for C(n+1)."""

    def test_C2_dimensions(self):
        """Test C(2) = osp(2|2) dimensions."""
        alg = CAlgebra(1)
        self.assertEqual(len(alg.basis["even"]), 4, "C(2) even dimension should be 4")
        self.assertEqual(len(alg.basis["odd"]), 4, "C(2) odd dimension should be 4")
        total = len(alg.basis["even"]) + len(alg.basis["odd"])
        self.assertEqual(total, 8, "C(2) total dimension should be 8")

    def test_C3_dimensions(self):
        """Test C(3) = osp(2|4) dimensions."""
        alg = CAlgebra(2)
        self.assertEqual(len(alg.basis["even"]), 11, "C(3) even dimension should be 11")
        self.assertEqual(len(alg.basis["odd"]), 8, "C(3) odd dimension should be 8")
        total = len(alg.basis["even"]) + len(alg.basis["odd"])
        self.assertEqual(total, 19, "C(3) total dimension should be 19")

    def test_C4_dimensions(self):
        """Test C(4) = osp(2|6) dimensions."""
        alg = CAlgebra(3)
        self.assertEqual(len(alg.basis["even"]), 22, "C(4) even dimension should be 22")
        self.assertEqual(len(alg.basis["odd"]), 12, "C(4) odd dimension should be 12")
        total = len(alg.basis["even"]) + len(alg.basis["odd"])
        self.assertEqual(total, 34, "C(4) total dimension should be 34")

    def test_dimension_formula(self):
        """Test dimension formula: even = 2n² + n + 1, odd = 4n."""
        for n in [1, 2, 3]:
            alg = CAlgebra(n)
            expected_even = 2*n*n + n + 1
            expected_odd = 4*n
            self.assertEqual(len(alg.basis["even"]), expected_even,
                           f"C({n+1}) even dimension mismatch")
            self.assertEqual(len(alg.basis["odd"]), expected_odd,
                           f"C({n+1}) odd dimension mismatch")


class TestCGeneratorParity(unittest.TestCase):
    """Test parity assignments for C(n+1)."""

    def test_even_parity(self):
        """Test that even generators have parity 0."""
        for n in [1, 2, 3]:
            alg = CAlgebra(n)
            for elem in alg.basis["even"]:
                self.assertEqual(alg.parity[elem], 0,
                               f"{elem} in C({n+1}) should have parity 0")

    def test_odd_parity(self):
        """Test that odd generators have parity 1."""
        for n in [1, 2, 3]:
            alg = CAlgebra(n)
            for elem in alg.basis["odd"]:
                self.assertEqual(alg.parity[elem], 1,
                               f"{elem} in C({n+1}) should have parity 1")

    def test_all_parity_assigned(self):
        """Test that all basis elements have parity assigned."""
        for n in [1, 2, 3]:
            alg = CAlgebra(n)
            all_basis = alg.basis["even"] + alg.basis["odd"]
            for elem in all_basis:
                self.assertIn(elem, alg.parity, f"Parity not assigned for {elem}")


class TestCGeneratorBasis(unittest.TestCase):
    """Test basis structure for C(n+1)."""

    def test_cartan_elements(self):
        """Test that Cartan elements are present."""
        for n in [1, 2, 3]:
            alg = CAlgebra(n)
            for i in range(1, n + 2):
                self.assertIn(f"H_{i}", alg.basis["even"],
                            f"H_{i} should be in C({n+1}) basis")

    def test_even_roots_2delta(self):
        """Test E_{±2δₖ} generators."""
        for n in [1, 2, 3]:
            alg = CAlgebra(n)
            for k in range(1, n + 1):
                self.assertIn(f"E_2del{k}_p", alg.basis["even"],
                            f"E_2del{k}_p should be in C({n+1})")
                self.assertIn(f"E_2del{k}_m", alg.basis["even"],
                            f"E_2del{k}_m should be in C({n+1})")

    def test_odd_generators_epsilon_delta(self):
        """Test E_{ε±δₖ} generators."""
        for n in [1, 2, 3]:
            alg = CAlgebra(n)
            for k in range(1, n + 1):
                for s1 in ["p", "m"]:
                    for s2 in ["p", "m"]:
                        elem = f"E_eps1_del{k}_{s1}{s2}"
                        self.assertIn(elem, alg.basis["odd"],
                                    f"{elem} should be in C({n+1}) odd basis")

    def test_basis_uniqueness(self):
        """Test that all basis elements are unique."""
        for n in [1, 2, 3]:
            alg = CAlgebra(n)
            all_basis = alg.basis["even"] + alg.basis["odd"]
            self.assertEqual(len(all_basis), len(set(all_basis)),
                           f"C({n+1}) basis contains duplicates")


class TestCGeneratorRealizations(unittest.TestCase):
    """Test oscillator realizations for C(n+1)."""

    def test_realizations_exist(self):
        """Test that all basis elements have oscillator realizations."""
        for n in [1, 2, 3]:
            alg = CAlgebra(n)
            all_basis = alg.basis["even"] + alg.basis["odd"]
            for elem in all_basis:
                self.assertIn(elem, alg.realizations,
                            f"Realization missing for {elem} in C({n+1})")

    def test_H1_realization(self):
        """Test H_1 = a_1^+ a_1^- + b_1^+ b_1^-."""
        for n in [1, 2, 3]:
            alg = CAlgebra(n)
            real = alg.realizations["H_1"]
            std_form = real.to_standard_form()
            # Should have two terms with coefficient 1
            self.assertEqual(len(std_form), 2, "H_1 should have 2 terms")


class TestJSONSchema(unittest.TestCase):
    """Test generated JSON schema compliance."""

    def test_json_files_exist(self):
        """Test that JSON files are generated."""
        for n in [1, 2, 3]:
            try:
                with open(f"data/C_{n}_structure.json") as f:
                    json.load(f)
            except FileNotFoundError:
                self.fail(f"data/C_{n}_structure.json not found")

    def test_json_structure(self):
        """Test JSON schema has required keys."""
        required_keys = {
            "schema_version", "algebra", "oscillator_generators",
            "oscillator_relations", "central_elements", "basis",
            "parity", "generator_realization", "structure_constants", "metadata"
        }

        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json") as f:
                data = json.load(f)
                for key in required_keys:
                    self.assertIn(key, data,
                                f"Missing key '{key}' in C_{n}_structure.json")

    def test_algebra_field(self):
        """Test algebra field configuration."""
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json") as f:
                data = json.load(f)
                alg = data["algebra"]
                self.assertEqual(alg["family"], "C", "Family should be 'C'")
                self.assertEqual(alg["m"], 1, "m should be 1 for C(n+1)")
                self.assertEqual(alg["n"], n, f"n should be {n}")

    def test_dimensions_in_json(self):
        """Test dimensions recorded in JSON match formula."""
        for n in [1, 2, 3]:
            with open(f"data/C_{n}_structure.json") as f:
                data = json.load(f)
                expected_even = 2*n*n + n + 1
                expected_odd = 4*n
                self.assertEqual(data["algebra"]["dimension"]["even"], expected_even)
                self.assertEqual(data["algebra"]["dimension"]["odd"], expected_odd)


if __name__ == "__main__":
    unittest.main(verbosity=2)
