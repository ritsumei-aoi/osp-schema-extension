import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from C_triviality import analyze_rank


def test_exact_search_finds_only_zero_trivial_gb_profile():
    expected = {
        1: (8, 28, 4),
        2: (19, 168, 8),
        3: (34, 516, 12),
    }
    for rank, (generators, coboundary_rank, gb_count) in expected.items():
        report = analyze_rank(rank, ROOT / "data")
        assert report["generator_count"] == generators
        assert report["coboundary_dimension"] == coboundary_rank
        assert report["quotient_rank"] == gb_count
        assert report["trivial_gb_subspace_dimension"] == 0
        assert report["trivial_gb_subspace_basis"] == []
        comparison = report["pair_comparison"]
        assert comparison["equal"]
        assert comparison["different"]
        assert len(comparison["equal"]) + len(comparison["different"]) == (
            generators * (generators + 1) // 2
        )
