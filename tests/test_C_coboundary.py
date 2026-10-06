import json
import os

import pytest

from C_coboundary import build_coboundary, check, phi_name
from C_gamma import _parse_lin
from C_generators import DATA_DIR


def load(name):
    with open(os.path.join(DATA_DIR, name)) as fh:
        return json.load(fh)


@pytest.mark.parametrize("n", [1, 2])
def test_coboundary_file_and_checks(n):
    struct, cob = load(f"C_{n}_structure.json"), load(f"C_{n}_coboundary.json")
    fresh = build_coboundary(n, struct)
    fresh["metadata"].pop("generation_date")
    cob["metadata"].pop("generation_date")
    assert fresh == cob
    assert check(n, cob, struct, trials=1)["passed"]


@pytest.mark.parametrize("n", [1, 2])
@pytest.mark.parametrize("xi", ["E_eps1_del1_pp", "E_eps1_del1_mm"])
def test_inner_odd_derivation_is_closed(n, xi):
    """f = ad_xi (xi odd) is an odd derivation, so delta f must vanish identically (sign-convention test)."""
    struct, cob = load(f"C_{n}_structure.json"), load(f"C_{n}_coboundary.json")
    basis = struct["basis"]["ordered"]
    idx = {b: i for i, b in enumerate(basis, 1)}
    vals = {}
    for i in basis:
        for j in basis:
            if struct["parity"][i] != struct["parity"][j]:
                vals[phi_name(idx[i], idx[j])] = 0
    for e in struct["structure_constants"]:
        if e["X"] == xi:
            vals[phi_name(idx[e["Z"]], idx[e["Y"]])] = int(e["coeff"])
    vals.update({f"phi_K_{j}": 0 for j in range(1, len(basis) + 1)})
    nonzero = [e for e in cob["coboundary"] if _parse_lin(e["coeff"]).evaluate(vals) != 0]
    assert nonzero == []
