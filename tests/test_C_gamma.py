import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import C_gamma as cgm  # noqa: E402
import C_generators as cg  # noqa: E402


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema2_consistent_with_schema1(n):
    s1, s2 = cgm.load_gamma(n)
    assert cgm.check_schema1_consistency(s1, s2) == []
    assert cgm.check_parity(s1, s2) == []
    assert s2["gb_matrix"]["shape"] == [2, 2 * n]
    assert len(s2["gb_matrix"]["parameters"]) == 4 * n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_cocycle_condition(n):
    s1, s2 = cgm.load_gamma(n)
    assert cgm.check_cocycle(s1, s2) == []


def test_cocycle_checker_rejects_corruption():
    s1, s2 = cgm.load_gamma(1)
    e = s2["inhomogeneous_deformation"]["gamma"][0]
    sym = next(iter(e["coeff"]))
    e["coeff"][sym] = str(F(e["coeff"][sym]) + 1)
    assert cgm.check_cocycle(s1, s2) != []


def test_oscillator_deformation_rule():
    # b a = a b - gb kappa  in normal form: kappa a_p ... check [b_1^+, a_1^+] = -gb_{p,1,p} kappa
    b, a = cg.boson_id(1, "p"), cg.AP
    res = cg.pmul({(b,): {"": F(1)}}, {(a,): {"": F(1)}})
    res = cg.padd_scaled(res, cg.pmul({(a,): {"": F(1)}}, {(b,): {"": F(1)}}), -1)
    assert res == {(cg.KAPPA,): {cg.gb_name("p", 1, "p"): F(-1)}}


def test_gamma_linear_and_matches_central_residue_example():
    s1, s2 = cgm.load_gamma(1)
    # H_1 and E_{e+d}: central residue -gb_{p,1,p} (computed by hand from a_p a_m part)
    ents = {(e["X"], e["Y"]): e["coeff"] for e in s2["inhomogeneous_deformation"]["central_component"]["entries"]}
    assert ents[("H_1", "E_eps1_del1_pp")] == {"gb_a_1_p_b_1_p": "-1"}
