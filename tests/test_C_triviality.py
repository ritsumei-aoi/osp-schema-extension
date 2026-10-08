"""Issue I08: triviality analysis tests (Layer 3 vs Layer 4)."""
import json
import os
from fractions import Fraction

import pytest

import C_evaluate as CE
import C_triviality as CT
from oscillator_algebra import gb_labels

NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
def test_trivial_for_all_gb_when_K_allowed(n):
    rank, cons, _ = CT.TrivialitySystem(n, "K").solvability_conditions()
    assert cons == []
    # kernel of delta on odd 1-cochains = inner odd derivations ad_Y, Y odd: dimension 4n
    assert CT.TrivialitySystem(n, "K").m - rank == 4 * n


@pytest.mark.parametrize("n", NS)
def test_strictly_trivial_only_for_gb_zero(n):
    rank, cons, _ = CT.TrivialitySystem(n, "strict").solvability_conditions()
    assert len(cons) == 4 * n
    assert {next(iter(c)) for c in cons} == set(gb_labels(n))
    assert all(len(c) == 1 for c in cons)


@pytest.mark.parametrize("n", NS)
def test_trivial_modulo_K(n):
    _, cons, _ = CT.TrivialitySystem(n, "mod_K").solvability_conditions()
    assert cons == []


@pytest.mark.parametrize("n", NS)
@pytest.mark.parametrize("name", ["all_plus", "checkerboard", "single_pp"])
def test_layer3_equals_layer4_at_solution(n, name):
    gb, l3 = CT.layer3_gamma_table(n, name)
    sys_ = CT.TrivialitySystem(n, "K")
    ok, phi, bad = sys_.solve(gb)
    assert ok and not bad
    assert sys_.check_solution(gb, phi, gamma_table=l3) == []
    strict = CT.TrivialitySystem(n, "strict")
    ok_s, _, bad_s = strict.solve(gb)
    assert not ok_s and all(k[2] == "K" for k, _ in bad_s)   # obstruction sits in the K components only


@pytest.mark.parametrize("n", NS)
def test_shift_map_trivializes_gamma(n):
    for name in ("all_plus", "row_sign"):
        gb = CE.profile(name, n)
        phi, residual, mism = CT.check_shift_map(n, gb)
        assert residual == [] and mism == []
        # closed form: f_shift,K(E_eps1_del{k}_{st}) = -gb_{s,k,t}/2 ; no K-component on even elements
        for lab in gb_labels(n):
            sg, rest = lab[len("gb_a1"):].split("_b")
            k, s = rest[:-1], rest[-1]
            assert phi.get(f"phi__K__E_eps1_del{k}_{sg}{s}", Fraction(0)) == -gb[lab] / 2
        assert not any(k.startswith("phi__K__H_") or k.startswith("phi__K__E_2del") or k.startswith("phi__K__E_del")
                       for k in phi)


def test_results_file_matches(tmp_path):
    for n in NS:
        d = json.load(open(os.path.join(CT.DATA_DIR, f"C_{n}_triviality.json")))
        assert d["variants"]["K"]["trivial_subspace_dim"] == 4 * n
        assert d["variants"]["strict"]["trivial_subspace_dim"] == 0
        assert all(rec["K"]["solvable"] for rec in d["profiles"].values())
        assert all((not rec["strict"]["solvable"]) == (name != "zero") for name, rec in d["profiles"].items())


def test_odd_H2_vanishes_for_C2():
    import C_cohomology as CH
    n_unknowns, rank_J = CH.cocycle_rank(1)
    b2 = CT.TrivialitySystem(1, "K").solvability_conditions()[0]
    assert n_unknowns - rank_J == b2 == 32
