"""Issue I05: Schema 2 (gamma structure) tests."""
import json
import os
import random
from fractions import Fraction

import pytest

import C_gamma as CG
import C_generators as G
import verify_C_structure as V
from oscillator_algebra import gb_labels

NS = [1, 2, 3]


def load(n):
    assert os.path.exists(CG.gamma_path(n)), "run python src/C_gamma.py"
    return CG.load_schema2(n)


def unit(n, lab):
    return {l: Fraction(int(l == lab)) for l in gb_labels(n)}


def random_gb(n, seed):
    rng = random.Random(seed)
    return {l: Fraction(rng.randint(-5, 5), rng.randint(1, 3)) for l in gb_labels(n)}


@pytest.mark.parametrize("n", NS)
def test_gb_matrix_layout(n):
    d = load(n)
    gbm = d["gb_matrix"]
    assert gbm["shape"] == [2, 2 * n] and gbm["count"] == 4 * n
    assert [lab for row in gbm["labels"] for lab in row] == gb_labels(n)
    assert gbm["labels"][0][0] == "gb_a1p_b1p" and gbm["labels"][1][-1] == f"gb_a1m_b{n}m"


@pytest.mark.parametrize("n", NS)
def test_gamma_entries_well_formed(n):
    d = load(n)
    s1 = json.load(open(G.structure_path(n)))
    par = dict(s1["parity"])
    par["K"] = 0
    labels = set(G.basis(n))
    for e in d["inhomogeneous_deformation"]["gamma"]:
        assert e["X"] in labels and e["Y"] in labels
        assert e["Z"] in labels or e["Z"] == "K"
        # gamma is an odd cochain
        assert par[e["Z"]] == (par[e["X"]] + par[e["Y"]] + 1) % 2
        assert e["linear_form"], "zero entry stored"
        assert set(e["linear_form"]) <= set(gb_labels(n))


@pytest.mark.parametrize("n", NS)
def test_gamma_matches_recomputation(n):
    d = load(n)
    gamma, k0 = CG.compute_gamma(n)
    assert gamma == d["inhomogeneous_deformation"]["gamma"]
    s1 = json.load(open(G.structure_path(n)))
    assert k0 == s1["structure_constants"]  # kappa^0 part == Schema 1


@pytest.mark.parametrize("n", NS)
def test_gamma_graded_antisymmetry(n):
    d = load(n)
    gb = random_gb(n, seed=n)
    tab = CG.gamma_table(d, gb)
    par = json.load(open(G.structure_path(n)))["parity"]
    for X in G.basis(n):
        for Y in G.basis(n):
            sign = -1 if (par[X] and par[Y]) else 1
            lhs = tab.get((X, Y), {})
            rhs = {Z: -sign * c for Z, c in tab.get((Y, X), {}).items()}
            assert lhs == rhs, (X, Y)


@pytest.mark.parametrize("n", [1, 2])
def test_cocycle_condition_unit_vectors(n):
    """Super Jacobi for L = g~ (+) kappa g~ at each unit gb vector (gamma is linear in gb)."""
    for lab in gb_labels(n):
        basis, parity, table = CG.extended_algebra(n, unit(n, lab))
        res = V.verify(basis, parity, table)
        assert res["pass"], (lab, res["jacobi_failures"][:3])


@pytest.mark.parametrize("n", NS)
def test_cocycle_condition_random_vector(n):
    basis, parity, table = CG.extended_algebra(n, random_gb(n, seed=10 + n))
    res = V.verify(basis, parity, table)
    assert res["pass"], res["jacobi_failures"][:3]


def test_hand_checked_gamma_n1():
    d = load(1)
    tab = CG.gamma_table(d, {l: Fraction(1) for l in gb_labels(1)})
    # gamma(H_1, E_{eps+delta_1}) = -gb_pp (H_1 + K) - gb_pm E_2del1_p
    assert tab[("H_1", "E_eps1_del1_pp")] == {"H_1": -1, "K": -1, "E_2del1_p": -1}
    # gamma(E_{eps-delta_1}, E_{-eps+delta_1}) = gb_mm E_{eps+delta_1} + gb_pp E_{-eps-delta_1}
    assert tab[("E_eps1_del1_pm", "E_eps1_del1_mp")] == {"E_eps1_del1_pp": 1, "E_eps1_del1_mm": 1}
