"""
tests/test_C_generators.py

Unit tests for C(n+1) = osp(2|2n) structure constant generator.
"""

import sys
import os
import json
import pytest
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from C_generators import (
    build_generators,
    bracket,
    express,
    build_schema,
    dim_even,
    dim_odd,
    dim_total,
)


# ── 1. Dimension checks ───────────────────────────────────────────────────────

@pytest.mark.parametrize("n,ev,od,tot", [
    (1,  4,  4,  8),
    (2, 11,  8, 19),
    (3, 22, 12, 34),
])
def test_dimension_formulas(n, ev, od, tot):
    assert dim_even(n) == ev
    assert dim_odd(n) == od
    assert dim_total(n) == tot


@pytest.mark.parametrize("n", [1, 2, 3])
def test_basis_count_matches_dimension(n):
    gens, par, basis = build_generators(n)
    even_count = sum(1 for l in basis if par[l] == 0)
    odd_count  = sum(1 for l in basis if par[l] == 1)
    assert even_count == dim_even(n), f"n={n}: even count {even_count} != {dim_even(n)}"
    assert odd_count  == dim_odd(n),  f"n={n}: odd count {odd_count} != {dim_odd(n)}"


# ── 2. Parity checks ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_assignment(n):
    gens, par, basis = build_generators(n)
    for lbl in basis:
        if "eps1" in lbl:
            assert par[lbl] == 1, f"{lbl} should be odd (parity 1)"
        elif lbl.startswith("H_") or lbl.startswith("E_2del") or lbl.startswith("E_del"):
            assert par[lbl] == 0, f"{lbl} should be even (parity 0)"


# ── 3. Specific structure constants ──────────────────────────────────────────

@pytest.mark.parametrize("n", [1, 2, 3])
def test_cartan_brackets_zero(n):
    """[H_i, H_j] = 0 for all i, j."""
    gens, par, basis = build_generators(n)
    cartans = [l for l in basis if l.startswith("H_")]
    for i, hi in enumerate(cartans):
        for j, hj in enumerate(cartans):
            if j < i:
                continue
            br = bracket(gens[hi], gens[hj], 0, 0)
            result = express(br, n, gens)
            assert not result, f"n={n}: [{hi},{hj}] = {result}, expected 0"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_H1_eps_pp_eigenvalue(n):
    """[H_1, E_eps1_del1_pp] = 2 * E_eps1_del1_pp."""
    gens, par, _ = build_generators(n)
    br = bracket(gens["H_1"], gens["E_eps1_del1_pp"], 0, 1)
    result = express(br, n, gens)
    assert result == {"E_eps1_del1_pp": Fraction(2)}, f"n={n}: got {result}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_H1_eps_pm_zero(n):
    """[H_1, E_eps1_del1_pm] = 0  (ε−δ_1 is isotropic w.r.t. H_1)."""
    gens, par, _ = build_generators(n)
    br = bracket(gens["H_1"], gens["E_eps1_del1_pm"], 0, 1)
    result = express(br, n, gens)
    assert not result, f"n={n}: [{{'H_1','E_eps1_del1_pm'}}] = {result}, expected 0"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_Hn1_E2deln_p_eigenvalue(n):
    """[H_{n+1}, E_2del{n}_p] = -2 * E_2del{n}_p."""
    gens, par, _ = build_generators(n)
    lbl_H = f"H_{n + 1}"
    lbl_E = f"E_2del{n}_p"
    br = bracket(gens[lbl_H], gens[lbl_E], 0, 0)
    result = express(br, n, gens)
    assert result == {lbl_E: Fraction(-2)}, f"n={n}: got {result}"


def test_eps_pp_mm_bracket_n1():
    """[E_eps1_del1_pp, E_eps1_del1_mm] = -H_1 - 2*H_2  for n=1."""
    n = 1
    gens, par, _ = build_generators(n)
    br = bracket(gens["E_eps1_del1_pp"], gens["E_eps1_del1_mm"], 1, 1)
    result = express(br, n, gens)
    expected = {"H_1": Fraction(-1), "H_2": Fraction(-2)}
    assert result == expected, f"Got {result}"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_E2del1p_E2del1m_bracket(n):
    """[E_2del1_p, E_2del1_m] should be a Cartan element (non-zero)."""
    gens, par, _ = build_generators(n)
    br = bracket(gens["E_2del1_p"], gens["E_2del1_m"], 0, 0)
    result = express(br, n, gens)
    assert result, f"n={n}: [E_2del1_p, E_2del1_m] is unexpectedly 0"
    # All non-zero contributions should be Cartan
    for lbl in result:
        assert lbl.startswith("H_"), f"n={n}: unexpected non-Cartan term {lbl}"


# ── 4. Graded antisymmetry ────────────────────────────────────────────────────

@pytest.mark.parametrize("n", [1, 2, 3])
def test_graded_antisymmetry(n):
    """[X, Y} = -(-1)^{px*py} [Y, X}."""
    gens, par, basis = build_generators(n)
    test_pairs = [
        ("H_1", "E_eps1_del1_pp"),
        ("E_eps1_del1_pp", "E_eps1_del1_mm"),
        ("H_1", "E_2del1_p"),
        ("E_eps1_del1_pp", "E_eps1_del1_pm"),
    ]
    for lx, ly in test_pairs:
        px, py = par[lx], par[ly]
        r_xy = express(bracket(gens[lx], gens[ly], px, py), n, gens)
        r_yx = express(bracket(gens[ly], gens[lx], py, px), n, gens)
        sign = (-1) ** (px * py)
        all_keys = set(r_xy) | set(r_yx)
        for k in all_keys:
            v_xy = r_xy.get(k, Fraction(0))
            v_yx = r_yx.get(k, Fraction(0))
            assert v_xy == -sign * v_yx, (
                f"n={n}: antisymmetry [{lx},{ly}] fails on {k}: "
                f"{v_xy} != {-sign}*{v_yx}"
            )


# ── 5. Jacobi identity ────────────────────────────────────────────────────────

def _jacobi_triple(gens, par, n, lx, ly, lz):
    """Compute the Jacobi sum for (X, Y, Z); should be zero."""
    X, Y, Z = gens[lx], gens[ly], gens[lz]
    px, py, pz = par[lx], par[ly], par[lz]

    def br_expr(A, pA, B, pB):
        return express(bracket(A, B, pA, pB), n, gens)

    def gen_poly(coeffs):
        res: dict = {}
        for lbl, c in coeffs.items():
            for mono, v in gens[lbl].items():
                res[mono] = res.get(mono, Fraction(0)) + c * v
        return {k: v for k, v in res.items() if v}

    # [X, [Y, Z}]
    yz = bracket(Y, Z, py, pz)
    xyz = express(bracket(X, gen_poly(express(yz, n, gens)), px, par.get(next(iter(express(yz, n, gens)), "H_1"), 0)), n, gens)

    # This approach is complex; instead compute directly in poly form
    yz_poly = bracket(Y, Z, py, pz)
    xyz_poly = bracket(X, yz_poly, px, 0)  # parity of [Y,Z] = py^py (wrong)

    # Use correct parity: p([Y,Z]) = py + pz mod 2 for Lie superalgebras
    pyz = (py + pz) % 2
    xyz_poly = bracket(X, yz_poly, px, pyz)

    zx_poly  = bracket(Z, X, pz, px)
    pzx = (pz + px) % 2
    yzx_poly = bracket(Y, zx_poly, py, pzx)

    xy_poly  = bracket(X, Y, px, py)
    pxy = (px + py) % 2
    zxy_poly = bracket(Z, xy_poly, pz, pxy)

    sign1 = (-1) ** (px * pz)
    sign2 = (-1) ** (py * px)
    sign3 = (-1) ** (pz * py)

    total: dict = {}
    for poly, sign in [(xyz_poly, sign1), (yzx_poly, sign2), (zxy_poly, sign3)]:
        for k, v in poly.items():
            total[k] = total.get(k, Fraction(0)) + sign * v
    return {k: v for k, v in total.items() if v}


@pytest.mark.parametrize("n", [1, 2])
def test_jacobi_identity(n):
    """Jacobi identity: (-1)^{xz}[X,[Y,Z]] + (-1)^{yx}[Y,[Z,X]] + (-1)^{zy}[Z,[X,Y]] = 0."""
    gens, par, basis = build_generators(n)
    triples = [
        ("H_1", "E_eps1_del1_pp", "E_eps1_del1_mm"),
        ("H_1", "E_2del1_p", "E_2del1_m"),
        ("E_eps1_del1_pp", "E_eps1_del1_mp", "H_1"),
    ]
    for lx, ly, lz in triples:
        total = _jacobi_triple(gens, par, n, lx, ly, lz)
        result = express(total, n, gens) if total else {}
        assert not result, (
            f"n={n}: Jacobi [{lx},{ly},{lz}] = {result}, expected 0"
        )


# ── 6. JSON schema output ─────────────────────────────────────────────────────

@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_keys(n):
    """Schema 1 JSON has all required top-level keys in correct order."""
    schema = build_schema(n)
    required = [
        "schema_version", "algebra", "central_elements",
        "oscillator_generators", "oscillator_relations",
        "basis", "parity", "generator_realization",
        "structure_constants", "metadata",
    ]
    for key in required:
        assert key in schema, f"n={n}: missing key '{key}'"
    assert schema["schema_version"] == "5.0"
    assert schema["algebra"]["family"] == "C"
    assert schema["algebra"]["m"] == 1
    assert schema["algebra"]["n"] == n


@pytest.mark.parametrize("n", [1, 2, 3])
def test_schema_dimensions(n):
    schema = build_schema(n)
    dim = schema["algebra"]["dimension"]
    assert dim["even"] == dim_even(n)
    assert dim["odd"]  == dim_odd(n)
    assert dim["total"] == dim_total(n)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_structure_constants_nonempty(n):
    schema = build_schema(n)
    assert len(schema["structure_constants"]) > 0


@pytest.mark.parametrize("n", [1, 2, 3])
def test_both_orderings_present(n):
    """Every (X,Y) entry with X≠Y must have a corresponding (Y,X) entry."""
    schema = build_schema(n)
    sc = schema["structure_constants"]
    # Build a set of all (X,Y) pairs that appear
    pairs = {(e["X"], e["Y"]) for e in sc}
    for x, y in list(pairs):
        if x != y:
            assert (y, x) in pairs, (
                f"n={n}: found ({x},{y}) in structure constants but not ({y},{x})"
            )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_reverse_pair_sign(n):
    """[Y,X} = -(-1)^{px*py} [X,Y} — check one concrete pair."""
    schema = build_schema(n)
    gens, par, _ = build_generators(n)
    sc = schema["structure_constants"]

    def get_coeffs(x, y):
        return {e["Z"]: Fraction(e["coeff"]) for e in sc if e["X"] == x and e["Y"] == y}

    lx, ly = "H_1", "E_eps1_del1_pp"
    px, py = par[lx], par[ly]
    sign = (-1) ** (px * py)
    fwd = get_coeffs(lx, ly)
    rev = get_coeffs(ly, lx)
    for z in set(fwd) | set(rev):
        assert fwd.get(z, Fraction(0)) == -sign * rev.get(z, Fraction(0)), (
            f"n={n}: sign rule failed on Z={z}"
        )


@pytest.mark.parametrize("n", [1, 2, 3])
def test_parity_map_complete(n):
    """Every basis element appears in the parity map."""
    schema = build_schema(n)
    basis_all = schema["basis"]["odd"] + schema["basis"]["even"]
    for lbl in basis_all:
        assert lbl in schema["parity"], f"n={n}: {lbl} missing from parity map"


@pytest.mark.parametrize("n", [1, 2, 3])
def test_central_elements_present(n):
    schema = build_schema(n)
    ce = schema["central_elements"]
    assert "kappa" in ce and ce["kappa"]["parity"] == 1
    assert "K" in ce and ce["K"]["parity"] == 0
