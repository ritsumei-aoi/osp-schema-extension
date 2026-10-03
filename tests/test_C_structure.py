"""
Tests for C(n+1) Schema 1 structure constants.
Checks parity, generator counts, antisymmetry, and super Jacobi identity.
"""

import json
import os
import pytest
from fractions import Fraction


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_schema(n):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def make_bracket_dict(sc_list):
    """Return dict {(X, Y): {Z: Fraction}} from structure_constants list."""
    d = {}
    for entry in sc_list:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        coeff = Fraction(entry["coeff"])
        if (X, Y) not in d:
            d[(X, Y)] = {}
        d[(X, Y)][Z] = d[(X, Y)].get(Z, Fraction(0)) + coeff
    # Remove zeros
    return {k: {z: c for z, c in v.items() if c != 0} for k, v in d.items()}


def bracket(bd, X, Y):
    """Return {Z: coeff} for [X,Y}, or {}."""
    return dict(bd.get((X, Y), {}))


@pytest.mark.parametrize("n", [1, 2, 3])
def test_generator_counts(n):
    schema = load_schema(n)
    expected_even = 2 * n**2 + n + 1
    expected_odd = 4 * n
    expected_total = 2 * n**2 + 5 * n + 1
    even_basis = schema["basis"]["even"]
    odd_basis = schema["basis"]["odd"]
    assert len(even_basis) == expected_even, f"n={n}: expected {expected_even} even, got {len(even_basis)}"
    assert len(odd_basis) == expected_odd, f"n={n}: expected {expected_odd} odd, got {len(odd_basis)}"
    assert len(even_basis) + len(odd_basis) == expected_total


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_consistency(n):
    schema = load_schema(n)
    parity = schema["parity"]
    even_basis = schema["basis"]["even"]
    odd_basis = schema["basis"]["odd"]
    for g in even_basis:
        assert parity[g] == 0, f"Even generator {g} has parity {parity[g]}"
    for g in odd_basis:
        assert parity[g] == 1, f"Odd generator {g} has parity {parity[g]}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_antisymmetry(n):
    """
    [X, Y} = -(-1)^{p(X)p(Y)} [Y, X}
    """
    schema = load_schema(n)
    parity = schema["parity"]
    sc_list = schema["structure_constants"]
    bd = make_bracket_dict(sc_list)
    all_basis = schema["basis"]["even"] + schema["basis"]["odd"]

    failures = []
    for X in all_basis:
        for Y in all_basis:
            xy = bracket(bd, X, Y)
            yx = bracket(bd, Y, X)
            sign = (-1) ** (parity[X] * parity[Y])
            # [X,Y} = -sign * [Y,X}
            for Z in set(list(xy.keys()) + list(yx.keys())):
                lhs = xy.get(Z, Fraction(0))
                rhs = -Fraction(sign) * yx.get(Z, Fraction(0))
                if lhs != rhs:
                    failures.append(f"n={n}: antisymmetry fail ['{X}','{Y}'] -> '{Z}': {lhs} != {rhs}")

    assert not failures, "\n".join(failures[:5])


@pytest.mark.parametrize("n", [1, 2, 3])
def test_super_jacobi(n):
    """
    Super Jacobi: [X, [Y, Z}} - (-1)^{p(X)p(Y)} [Y, [X, Z}} - [[X, Y}, Z} = 0
    Equivalently: [X, [Y, Z}} + (-1)^{p(X)(p(Y)+p(Z))} [Y, [Z, X}} + (-1)^{p(Z)(p(X)+p(Y))} [Z, [X, Y}} = 0
    """
    schema = load_schema(n)
    parity = schema["parity"]
    sc_list = schema["structure_constants"]
    bd = make_bracket_dict(sc_list)
    all_basis = schema["basis"]["even"] + schema["basis"]["odd"]

    def bkt(X, Y):
        return bracket(bd, X, Y)

    def apply_bracket(X, res_dict):
        """Compute [X, sum_Z c_Z * Z} = sum_Z c_Z * [X, Z}."""
        out = {}
        for Z, c in res_dict.items():
            bXZ = bkt(X, Z)
            for W, d in bXZ.items():
                out[W] = out.get(W, Fraction(0)) + c * d
        return {k: v for k, v in out.items() if v != 0}

    failures = []
    for X in all_basis:
        for Y in all_basis:
            for Z in all_basis:
                pX, pY, pZ = parity[X], parity[Y], parity[Z]
                # Term 1: [X, [Y, Z}}
                t1 = apply_bracket(X, bkt(Y, Z))
                # Term 2: (-1)^{pX*(pY+pZ)} [Y, [Z, X}}
                t2_raw = apply_bracket(Y, bkt(Z, X))
                sign2 = (-1) ** (pX * (pY + pZ))
                t2 = {k: Fraction(sign2) * v for k, v in t2_raw.items()}
                # Term 3: (-1)^{pZ*(pX+pY)} [Z, [X, Y}}
                t3_raw = apply_bracket(Z, bkt(X, Y))
                sign3 = (-1) ** (pZ * (pX + pY))
                t3 = {k: Fraction(sign3) * v for k, v in t3_raw.items()}

                # Sum
                total = {}
                for d in [t1, t2, t3]:
                    for W, c in d.items():
                        total[W] = total.get(W, Fraction(0)) + c

                bad = {W: c for W, c in total.items() if c != 0}
                if bad:
                    failures.append(
                        f"n={n}: Jacobi fail ['{X}','[{Y},{Z}]'] + ... != 0: {bad}"
                    )
                    if len(failures) >= 5:
                        break
            if len(failures) >= 5:
                break
        if len(failures) >= 5:
            break

    assert not failures, "\n".join(failures)
