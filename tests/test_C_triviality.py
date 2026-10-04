from pathlib import Path

import pytest

from src.C_triviality import analyze_rank


@pytest.mark.parametrize(
    ("n", "central_terms"),
    ((1, 10), (2, 42), (3, 90)),
)
def test_layer_comparison_proves_all_plus_nontrivial(n, central_terms):
    root = Path(__file__).resolve().parents[1]
    report = analyze_rank(root / "data", n)
    assert report["profile"] == "all_plus"
    assert report["all_plus_status"] == "non-trivial"
    assert report["evaluated_nonzero_K_term_count"] == central_terms
    assert report["evaluated_terms_outside_coboundary_support"] >= central_terms
    assert report["central_constraint_rank"] == report["independent_gb_parameters"]
    assert report["zero_assignment_status"] == "trivial"
