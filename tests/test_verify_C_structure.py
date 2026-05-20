from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import verify_C_structure as vcs


class VerifyCStructureTestCase(unittest.TestCase):
    def test_verification_passes_for_generated_files(self) -> None:
        expected = {
            "C_1_structure.json": (1, 8, 8 * 8, 8 * 8 * 8),
            "C_2_structure.json": (2, 19, 19 * 19, 19 * 19 * 19),
            "C_3_structure.json": (3, 34, 34 * 34, 34 * 34 * 34),
        }
        data_dir = ROOT / "data"
        for filename, (n, basis_size, pair_checks, triple_checks) in expected.items():
            summary = vcs.verify_schema(data_dir / filename)
            self.assertTrue(summary.passed, filename)
            self.assertEqual(summary.n, n)
            self.assertEqual(summary.basis_size, basis_size)
            self.assertEqual(summary.pair_checks, pair_checks)
            self.assertEqual(summary.triple_checks, triple_checks)
            self.assertEqual(summary.antisymmetry_failures, [])
            self.assertEqual(summary.jacobi_failures, [])


if __name__ == "__main__":
    unittest.main()
