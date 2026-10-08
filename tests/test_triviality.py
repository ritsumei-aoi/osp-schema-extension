"""Tests for the triviality analysis (src/triviality_search.py), with an independent solver (sympy)."""

import os
import sys

import pytest
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'src'))

from triviality_search import analyse, load_inputs  # noqa: E402


def _rank_with(vectors, extra):
    keys = sorted(set().union(*[set(v) for v in vectors + [extra]]))
    matrix = sp.Matrix([[v.get(k, 0) for v in vectors] for k in keys])
    column = sp.Matrix([extra.get(k, 0) for k in keys])
    return matrix.rank(), matrix.row_join(column).rank()


def test_each_g_valued_gamma_is_a_coboundary_n1():
    inp = load_inputs(1)
    for label in inp['gb_labels']:
        r_before, r_after = _rank_with(inp['coboundary'], inp['g_vectors'][label])
        assert r_before == r_after, label


def test_perturbed_gamma_is_not_a_coboundary_n1():
    # Negative control: a single extra component must leave the coboundary span, so the
    # independent solver can detect a non-trivial deformation.
    inp = load_inputs(1)
    label = inp['gb_labels'][0]
    x = 'E_eps1_del1_pp'
    z = next(z for z in inp['labels']
             if inp['parity'][z] == (inp['parity'][x] + inp['parity'][x] + 1) % 2 and z != 'H_1')
    extra = dict(inp['g_vectors'][label])
    extra[(x, x, z)] = extra.get((x, x, z), 0) + 1
    r_before, r_after = _rank_with(inp['coboundary'], extra)
    assert r_after > r_before


def test_k_part_is_a_k_coboundary_n1():
    inp = load_inputs(1)
    for label in inp['gb_labels']:
        vec = inp['k_vectors'][label]
        if not vec:
            continue
        r_before, r_after = _rank_with(inp['k_coboundary'], vec)
        assert r_before == r_after, label


@pytest.mark.parametrize('n', (1, 2))
def test_layer3_matches_delta_of_trivialiser_at_gb_one(n):
    from triviality_search import layer3_vs_layer4, trivialisers
    g_cert, k_cert = trivialisers(n)
    comparison = layer3_vs_layer4(n, g_cert, k_cert)
    assert comparison['g_mismatches'] == 0
    assert comparison['K_mismatches'] == 0
    assert comparison['g_entries_compared'] > 0


@pytest.mark.parametrize('n', (1, 2))
def test_triviality_subspace_is_whole_space(n):
    result = analyse(n)
    assert result['dim_T_g'] == 4 * n
    assert result['dim_T_K'] == 4 * n
    assert result['constraints_g'] == []
