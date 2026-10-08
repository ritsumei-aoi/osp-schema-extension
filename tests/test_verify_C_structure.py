import json
import unittest
from pathlib import Path

from src.verify_C_structure import verify_schema


class VerifyCStructureTests(unittest.TestCase):
    def test_generated_structures_pass_all_checks(self):
        data_dir = Path(__file__).resolve().parents[1] / "data"
        for n in (1, 2, 3):
            with self.subTest(n=n):
                schema = json.loads((data_dir / f"C_{n}_structure.json").read_text())
                errors, stats = verify_schema(schema)
                self.assertEqual(errors, [])
                self.assertEqual(stats["triple_checks"], stats["generators"] ** 3)
                self.assertEqual(stats["pair_checks"], stats["generators"] ** 2)


if __name__ == "__main__":
    unittest.main()
