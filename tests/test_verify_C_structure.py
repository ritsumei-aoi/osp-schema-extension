from pathlib import Path

import pytest

from src.verify_C_structure import verify_file


@pytest.mark.parametrize(
    ("n", "generators", "pairs", "triples"),
    ((1, 8, 64, 512), (2, 19, 361, 6859), (3, 34, 1156, 39304)),
)
def test_committed_structure_reports_pass(n, generators, pairs, triples):
    path = Path(__file__).resolve().parents[1] / "data" / f"C_{n}_structure.json"
    report = verify_file(path)
    assert report["pass"]
    assert report["generator_count"] == generators
    assert report["pair_checks"] == pairs
    assert report["triple_checks"] == triples
    assert report["failures"] == []
