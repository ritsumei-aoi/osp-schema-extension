"""Tests for the triviality analysis (Issue I08)."""
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from C_triviality import SparseEliminator, analyse  # noqa: E402
from C_evaluate import PROFILES  # noqa: E402


def test_sparse_eliminator_small_system():
    # x + y = 1 (rhs a), x - y = 1 (a) ; third row 2x = 2 consistent, 2x = 3 inconsistent (rhs b)
    el = SparseEliminator()
    el.add_row({0: Fraction(1), 1: Fraction(1), "a": Fraction(1), "b": Fraction(1)}, "e1")
    el.add_row({0: Fraction(1), 1: Fraction(-1), "a": Fraction(1), "b": Fraction(1)}, "e2")
    el.add_row({0: Fraction(2), "a": Fraction(2), "b": Fraction(3)}, "e3")
    assert el.rank == 2
    assert "a" not in el.inconsistent
    assert el.inconsistent["b"] == ["e3"]


@pytest.mark.parametrize("n", [1, 2, 3])
def test_triviality_conclusions(n):
    rep = analyse(n, os.path.join(ROOT, "data"), verbose=False)
    assert rep["K_part_closed_form_verified"]
    for prof in PROFILES:
        c = rep["candidate_map"][prof]
        assert c["exact_match_with_K_targets"] and c["match_modulo_K"]
        assert c["f_without_K_targets_mismatch_only_in_K"]
        assert c["f_without_K_targets_mismatching_pairs"] == c["K_entries_in_gamma"] > 0
    S1, S2, S3 = (rep["linear_solve"][k] for k in ("S1_f_to_g_modulo_K", "S2_f_to_g_exact", "S3_f_to_g_plus_K_exact"))
    assert all(S1["solvable"].values()) and all(S3["solvable"].values())
    assert not any(S2["solvable"].values())
    assert all(v["all_in_K"] for v in S2["inconsistent_equations"].values())
    # kernel of delta on odd maps g -> g = odd inner derivations (dimension 4n)
    assert S1["kernel_dim"] == S2["kernel_dim"] == S3["kernel_dim"] == 4 * n
    assert S3["rank_of_delta"] == S2["rank_of_delta"] + 4 * n  # K-valued maps add 4n independent directions


def test_report_file_exists():
    with open(os.path.join(ROOT, "data", "C_triviality_report.json")) as fh:
        reps = json.load(fh)
    assert [r["n"] for r in reps] == [1, 2, 3]
