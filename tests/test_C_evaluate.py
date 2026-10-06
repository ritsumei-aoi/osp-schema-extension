import json
import os
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import C_evaluate as CE  # noqa: E402
import C_gamma as CGm  # noqa: E402
import osc_algebra as OA  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def _load(n):
    st = json.load(open(os.path.join(DATA, f"C_{n}_structure.json")))
    gm = json.load(open(os.path.join(DATA, f"C_{n}_gamma.json")))
    return st, gm


@pytest.mark.parametrize("n", [1, 2, 3])
def test_files_match_generator(n):
    st, gm = _load(n)
    params = gm["inhomogeneous_deformation"]["parameters"]
    for prof, assign in CE.profiles(n, params).items():
        fn = f"C_{n}_evaluated.json" if prof == "all_plus" else f"C_{n}_evaluated_{prof}.json"
        on_disk = json.load(open(os.path.join(DATA, fn)))
        fresh = CE.evaluate(st, gm, assign, prof, date=on_disk["metadata"]["generation_date"])
        assert on_disk == json.loads(json.dumps(fresh, ensure_ascii=False))


@pytest.mark.parametrize("n", [1, 2])
@pytest.mark.parametrize("prof", ["all_plus", "alternating", "fermion_sign", "boson_sign"])
def test_matches_direct_oscillator_evaluation(n, prof):
    """Schema 3 (via Schema 2 JSON) == bracket computed directly in the deformed oscillator algebra."""
    st, gm = _load(n)
    params = gm["inhomogeneous_deformation"]["parameters"]
    assign = CE.profiles(n, params)[prof]
    d = CE.evaluate(st, gm, assign, prof)
    got = {(e["X"], e["Y"], e["Z"]): Fraction(e["kappa_coeff"]) for e in d["evaluated_structure"]["entries"]
           if e["kappa_coeff"] != "0"}
    names, parity, R, dec = CGm.extended_decomposer(n)
    gb = {CE.parse_name(p): Fraction(v) for p, v in assign.items()}
    want = {}
    for X in names:
        for Y in names:
            br = OA.bracket(R[X], R[Y], n, parity[X], parity[Y], gb)
            q = {(0,) + m[1:]: c for m, c in br.items() if m[0] == 1}
            if q:
                coef, res = dec.decompose(q)
                assert not res
                for Z, c in coef.items():
                    want[(X, Y, Z)] = c
    assert got == want


@pytest.mark.parametrize("n", [1, 2, 3])
def test_zero_profile_is_undeformed(n):
    d = json.load(open(os.path.join(DATA, f"C_{n}_evaluated_zero.json")))
    assert all(e["kappa_coeff"] == "0" for e in d["evaluated_structure"]["entries"])
    st, _ = _load(n)
    assert len(d["evaluated_structure"]["entries"]) == len(st["structure_constants"])
