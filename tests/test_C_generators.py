import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import C_generators as cg  # noqa: E402

NS = [1, 2, 3]


@pytest.fixture(scope="module", params=NS)
def alg(request):
    return cg.CAlgebra(request.param)


def load(n):
    return json.load(open(ROOT / "data" / f"C_{n}_structure.json"))


@pytest.mark.parametrize("n", NS)
def test_generator_counts(n):
    even, odd = cg.basis_lists(n)
    assert len(even) == 2 * n * n + n + 1
    assert len(odd) == 4 * n
    assert len(set(even + odd)) == len(even) + len(odd)


@pytest.mark.parametrize("n", NS)
def test_parity_matches_realization(n):
    a = cg.CAlgebra(n)
    for b in a.basis:
        for w, _ in a.real[b]:
            n_odd = sum(1 for x in w if cg.is_odd_letter(x))
            assert n_odd % 2 == a.parity[b], b


@pytest.mark.parametrize("n", NS)
def test_structure_closes_and_graded(n):
    a = cg.CAlgebra(n)
    t = cg.structure_table(a)  # raises if a bracket leaves g (or has a K component)
    for X in a.basis:
        for Y in a.basis:
            sign = -1 if (a.parity[X] and a.parity[Y]) else 1
            lhs = t.get((X, Y), {})
            rhs = {z: -sign * c for z, c in t.get((Y, X), {}).items()}
            assert lhs == rhs, (X, Y)
            for Z in lhs:  # parity is additive
                assert a.parity[Z] == (a.parity[X] + a.parity[Y]) % 2


@pytest.mark.parametrize("n", NS)
def test_json_matches_generator_and_schema(n):
    d = load(n)
    a = cg.CAlgebra(n)
    assert d["schema_version"] == "5.0"
    assert d["algebra"]["family"] == "C" and d["algebra"]["m"] == 1 and d["algebra"]["n"] == n
    assert d["algebra"]["dimension"] == {"total": 2 * n * n + 5 * n + 1, "even": 2 * n * n + n + 1, "odd": 4 * n}
    assert set(d["oscillator_generators"]) == {"fermions", "bosons"}
    assert d["oscillator_generators"]["fermions"]["labels"] == ["a_1_p", "a_1_m"]
    assert len(d["oscillator_generators"]["bosons"]["labels"]) == 2 * n
    assert d["central_elements"]["kappa"]["parity"] == 1 and d["central_elements"]["K"]["parity"] == 0
    assert d["basis"]["even"] == a.even and d["basis"]["odd"] == a.odd
    assert set(d["parity"]) == set(a.basis) == set(d["generator_realization"]["realizations"])
    table = cg.structure_table(a)
    from_json = {}
    for e in d["structure_constants"]:
        from_json.setdefault((e["X"], e["Y"]), {})[e["Z"]] = cg.F(e["coeff"])
    assert from_json == table


def test_known_brackets():
    # C(2): {E_{e+d}, E_{-e-d}} = h_1 - h_a ; [E_2del_p, E_2del_m] = 4 H_{n+1}
    a = cg.CAlgebra(1)
    t = cg.structure_table(a)
    assert t[("E_2del1_p", "E_2del1_m")] == {"H_2": cg.F(4)}
    # h_1 - h_a = -H_1 ... check via realization: N_1 + 1 - a_p a_m = -H_1 + 2 N_1 + 1 = -H_1 - 2 H_2
    assert t[("E_eps1_del1_pp", "E_eps1_del1_mm")] == {"H_1": cg.F(-1), "H_2": cg.F(-2)}
