"""Tests for src/C_triviality.py (I08)."""

import sys
from pathlib import Path

import sympy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import C_triviality as T  # noqa: E402


def synthetic_gamma(n, k, gb_index):
    """gamma = gb_{gb_index} * delta f_k, built from the Schema 4 file. No K part."""
    gb, _ = T.load_gamma(n)
    _, D = T.load_coboundary(n)
    G = {}
    for (X, Y, Z, kk), c in D.items():
        if kk == k:
            G[(X, Y, Z)] = G.get((X, Y, Z), 0) + gb[gb_index] * c
    return G, gb


def test_sensitivity_coboundary_is_trivial():
    # A deformation that is literally gb_0 * delta f_k must be trivial: its gb-subspace
    # contains e_0 (the first gb coordinate).
    G, gb = synthetic_gamma(1, k=3, gb_index=0)
    _, Tb, _ = T.trivial_subspace(1, include_K=True, G=G)
    e0 = sympy.Matrix([[1, 0, 0, 0]])
    assert Tb.rows >= 1
    assert sympy.Matrix.vstack(Tb, e0).rank() == Tb.rank()


def test_sensitivity_nontrivial_detected():
    # A deformation with a K component that no coboundary can cancel: the K row forces gb = 0.
    gb = T.load_gamma(1)[0]
    G = {("E_eps1_del1_pp", "H_eps", "K"): gb[0]}
    _, Tb, C = T.trivial_subspace(1, include_K=True, G=G)
    assert Tb.rows == 0 or Tb.rank() < 4
    assert C.rows >= 1


def test_n1_full_bracket_only_zero_is_trivial():
    _, Tb, C = T.trivial_subspace(1, include_K=True)
    assert Tb.rows == 0
    assert C.rows == 4


def test_n1_k_dropped_variant_runs():
    gb, Tb, C = T.trivial_subspace(1, include_K=False)
    assert Tb.cols == len(gb)
