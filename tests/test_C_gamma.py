import copy
import json
import os
import random
import sys
from fractions import Fraction

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import C_gamma as CGm  # noqa: E402
import C_generators as CG  # noqa: E402
import osc_algebra as OA  # noqa: E402
import verify_C_gamma as VG  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
NS = [1, 2, 3]


@pytest.mark.parametrize("n", NS)
def test_consistency_with_schema1(n):
    r = VG.verify(n)
    assert r["label_parity_failures"] == [] and r["skew_failures"] == [] and r["cocycle_failures"] == []


@pytest.mark.parametrize("n", NS)
def test_gb_matrix_shape(n):
    d, params, _ = VG.load_gamma(n)
    m = d["gb_matrix"]
    assert m["shape"] == [2, 2 * n] and len(m["entries"]) == 2 and all(len(r) == 2 * n for r in m["entries"])
    assert len(params) == 4 * n == m["parameter_count"]
    assert d["gb_matrix"]["parity"] == 1


@pytest.mark.parametrize("n", NS)
def test_data_matches_generator(n):
    on_disk = json.load(open(os.path.join(DATA, f"C_{n}_gamma.json")))
    st = json.load(open(os.path.join(DATA, f"C_{n}_structure.json")))
    fresh = CGm.build_schema2(n, st, date=on_disk["metadata"]["generation_date"])
    assert on_disk == json.loads(json.dumps(fresh, ensure_ascii=False))


def test_cocycle_check_is_not_vacuous():
    n = 1
    d, params, gam = VG.load_gamma(n)
    bad = copy.deepcopy(gam)
    g = bad[params[0]]
    X, Y = next(k for k in g if k[0] != k[1])
    z = next(iter(g[(X, Y)]))
    g[(X, Y)][z] += Fraction(1)
    r = VG.verify(n, loaded=(d, params, bad))
    assert r["skew_failures"] or r["cocycle_failures"]
    # a corruption that preserves skew-symmetry must still be caught by the cocycle identity
    bad = copy.deepcopy(gam)
    g = bad[params[0]]
    X, Y = next(k for k in g if k[0] != k[1])
    z = next(iter(g[(X, Y)]))
    s = -((-1) ** 0)
    for (a, b) in ((X, Y), (Y, X)):
        if (a, b) in g and z in g[(a, b)]:
            g[(a, b)][z] *= 2
    r = VG.verify(n, loaded=(d, params, bad))
    assert r["cocycle_failures"] or r["skew_failures"]


def test_kappa_free_part_is_schema1_bracket():
    for n in (1, 2):
        names, par, R = CG.build_basis(n)
        gb = {p: Fraction(i + 1, 3) for i, p in enumerate(CGm.gb_params(n))}
        for X in names:
            for Y in names:
                br = OA.bracket(R[X], R[Y], n, par[X], par[Y], gb)
                p0 = {m: c for m, c in br.items() if m[0] == 0}
                assert p0 == OA.bracket(R[X], R[Y], n, par[X], par[Y])


def test_product_associative_to_first_order_in_kappa():
    rnd = random.Random(7)
    n = 2
    gb = {p: Fraction(rnd.randint(-3, 3)) for p in CGm.gb_params(n)}

    def rand_mono():
        return (0, rnd.randint(0, 1), rnd.randint(0, 1), tuple(rnd.randint(0, 2) for _ in range(2 * n)))

    for _ in range(300):
        x, y, z = ({rand_mono(): Fraction(1)} for _ in range(3))
        lhs = OA.mul(OA.mul(x, y, n, gb), z, n, gb)
        rhs = OA.mul(x, OA.mul(y, z, n, gb), n, gb)
        assert lhs == rhs
