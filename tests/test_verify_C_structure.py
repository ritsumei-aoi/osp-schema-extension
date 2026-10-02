import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from verify_C_structure import verify_file


def test_generated_structures_pass_pair_and_jacobi_checks():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    expected_generators = {1: 8, 2: 19, 3: 34}
    for n, generator_count in expected_generators.items():
        result = verify_file(data_dir / f"C_{n}_structure.json")
        assert result["passed"], result["errors"]
        assert result["generator_count"] == generator_count
        assert result["pair_checks"] == generator_count**2
        assert result["jacobi_checks"] == generator_count**3
