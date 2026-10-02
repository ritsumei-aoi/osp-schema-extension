import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from C_triviality import analyze_rank


def test_every_gb_parameter_has_an_independent_central_obstruction():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    for n in (1, 2, 3):
        result = analyze_rank(n, data_dir)
        assert result["parameter_count"] == 4 * n
        assert len(result["isolated_parameter_witnesses"]) == 4 * n
        assert result["evaluated_central_obstructions"] > 0
        assert result["all_plus_is_trivial"] is False
        assert result["zero_assignment_is_trivial"] is True
        assert result["triviality_condition_conjecture"] == "all gb parameters vanish"
