from pathlib import Path

import pytest

from src.analyze_C_triviality import analyze_rank


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@pytest.mark.parametrize(("n", "parameters"), ((1, 4), (2, 8), (3, 12)))
def test_triviality_comparison_detects_injective_central_obstruction(n, parameters):
    report = analyze_rank(DATA_DIR, n)
    assert f"C_{n}: central obstruction matrix rank {parameters}/{parameters}" in report
    assert any("all-plus is non-trivial" in line for line in report)
    assert any("all-zero is trivial" in line for line in report)
