"""
Unit tests for C(n+1) structure constant generator.
Tests: basis dimensions, parity, generator counts, Jacobi identity (sample),
and key structure constant values.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from build_C_structure_constants import (
    build_basis, build_generators, graded_bracket, label_parity, decompose,
    compute_structure_constants, osc_parity
)
from fractions import Fraction
import json

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_bracket_coeff(sc_list, X, Y, Z):
    """Return coefficient of Z in [X, Y}, 0 if absent."""
    total = Fraction(0)
    for r in sc_list:
        if r["X"] == X and r["Y"] == Y and r["Z"] == Z:
            total += Fraction(r["coeff"])
    return total


def full_bracket(X_lbl, Y_lbl, n, gens):
    """Return the full bracket as a dict {label: Fraction}."""
    Xp = label_parity(X_lbl)
    Yp = label_parity(Y_lbl)
    raw = graded_bracket(gens[X_lbl], Xp, gens[Y_lbl], Yp, n)
    odd, even = build_basis(n)
    return decompose(raw, n, odd + even, gens) if raw else {}


# ---------------------------------------------------------------------------
# Tests: basis dimensions
# ---------------------------------------------------------------------------

def test_basis_dimensions():
    for n, expected_odd, expected_even, expected_total in [
        (1, 4, 4, 8),
        (2, 8, 11, 19),
        (3, 12, 22, 34),
    ]:
        odd, even = build_basis(n)
        assert len(odd) == expected_odd, f"n={n}: odd {len(odd)} != {expected_odd}"
        assert len(even) == expected_even, f"n={n}: even {len(even)} != {expected_even}"
        assert len(odd) + len(even) == expected_total
        print(f"  [OK] n={n}: dim ({expected_odd}|{expected_even}) = {expected_total}")


# ---------------------------------------------------------------------------
# Tests: parity
# ---------------------------------------------------------------------------

def test_parities():
    for n in [1, 2, 3]:
        odd, even = build_basis(n)
        for lbl in odd:
            assert label_parity(lbl) == 1, f"n={n}: {lbl} should be odd"
        for lbl in even:
            assert label_parity(lbl) == 0, f"n={n}: {lbl} should be even"
        print(f"  [OK] n={n}: parities correct")


# ---------------------------------------------------------------------------
# Tests: generator counts (oscillator monomials)
# ---------------------------------------------------------------------------

def test_generator_counts():
    for n in [1, 2, 3]:
        odd, even = build_basis(n)
        gens = build_generators(n)
        # All basis labels have a generator
        for lbl in odd + even:
            assert lbl in gens, f"n={n}: missing generator {lbl}"
        # No extra generators
        assert set(gens.keys()) == set(odd + even), f"n={n}: generator key mismatch"
        print(f"  [OK] n={n}: {len(gens)} generators")


# ---------------------------------------------------------------------------
# Tests: key structure constants for n=1 (C(2) = osp(2|2))
# ---------------------------------------------------------------------------

def test_n1_key_brackets():
    n = 1
    gens = build_generators(n)
    sc = compute_structure_constants(n)

    tests = [
        # [odd, odd} -> even (Cartan or root)
        ("E_eps1_del1_pp", "E_eps1_del1_mm", "H_1",  Fraction(-1)),
        ("E_eps1_del1_pp", "E_eps1_del1_mm", "H_2",  Fraction(-2)),
        ("E_eps1_del1_pp", "E_eps1_del1_mp", "E_2del1_p", Fraction(2)),
        ("E_eps1_del1_pm", "E_eps1_del1_mm", "E_2del1_m", Fraction(2)),
        ("E_eps1_del1_pm", "E_eps1_del1_mp", "H_1",  Fraction(1)),
        # [even, even} -> even
        ("E_2del1_p", "E_2del1_m", "H_2",  Fraction(1)),
        ("H_1", "E_2del1_p", "E_2del1_p", Fraction(2)),
        ("H_1", "E_2del1_m", "E_2del1_m", Fraction(-2)),
        ("H_2", "E_2del1_p", "E_2del1_p", Fraction(-2)),
        ("H_2", "E_2del1_m", "E_2del1_m", Fraction(2)),
        # Cartan action: [X, H} = -eigenvalue * X (since [H,X] = ev*X implies [X,H} = -ev*X for even H)
        # H_1 eigenvalues: (eps+del1)=2, (eps-del1)=0, (-eps+del1)=0, (-eps-del1)=-2
        ("E_eps1_del1_pp", "H_1", "E_eps1_del1_pp", Fraction(-2)),
        ("E_eps1_del1_mm", "H_1", "E_eps1_del1_mm", Fraction(2)),
        # H_2 eigenvalues: (eps+del1)=-1, (eps-del1)=1, (-eps+del1)=-1, (-eps-del1)=1
        ("E_eps1_del1_pp", "H_2", "E_eps1_del1_pp", Fraction(1)),
        ("E_eps1_del1_pm", "H_2", "E_eps1_del1_pm", Fraction(-1)),
        ("E_eps1_del1_mp", "H_2", "E_eps1_del1_mp", Fraction(1)),
        ("E_eps1_del1_mm", "H_2", "E_eps1_del1_mm", Fraction(-1)),
        # Zero brackets: (eps-del1)(H_1) = 0, (-eps+del1)(H_1) = 0
        ("E_eps1_del1_pm", "H_1", "E_eps1_del1_pm", Fraction(0)),
        ("E_eps1_del1_mp", "H_1", "E_eps1_del1_mp", Fraction(0)),
    ]

    for X, Y, Z, expected in tests:
        got = get_bracket_coeff(sc, X, Y, Z)
        if got == 0:
            # Try reversed (antisymmetry)
            got_rev = get_bracket_coeff(sc, Y, X, Z)
            pX = label_parity(X); pY = label_parity(Y)
            got = -Fraction((-1) ** (pX * pY)) * got_rev
        assert got == expected, (
            f"n=1: [{X}, {Y}]_Z={Z}: expected {expected}, got {got}"
        )
    print(f"  [OK] n=1: {len(tests)} key brackets verified")


# ---------------------------------------------------------------------------
# Tests: graded antisymmetry [X, Y} = -(-1)^{p(X)p(Y)} [Y, X}
# ---------------------------------------------------------------------------

def test_graded_antisymmetry():
    """Verify [X,Y} = -(-1)^{pX*pY} [Y,X} by computing both brackets directly."""
    for n in [1, 2, 3]:
        odd, even = build_basis(n)
        all_labels = odd + even
        gens = build_generators(n)

        violations = 0
        for i, X in enumerate(all_labels):
            pX = label_parity(X)
            for j, Y in enumerate(all_labels):
                if j <= i:
                    continue
                pY = label_parity(Y)
                sign = Fraction((-1) ** (pX * pY))

                # Compute both brackets directly
                bXY = graded_bracket(gens[X], pX, gens[Y], pY, n)
                bYX = graded_bracket(gens[Y], pY, gens[X], pX, n)

                # Verify bXY == -sign * bYX
                expected = {m: -sign * c for m, c in bYX.items()}
                # Merge and check all monomials
                all_monomials = set(bXY) | set(expected)
                for m in all_monomials:
                    c_got = bXY.get(m, Fraction(0))
                    c_exp = expected.get(m, Fraction(0))
                    if c_got != c_exp:
                        print(f"  ANTISYMMETRY FAIL: n={n}, [{X},{Y}]_m={m}: "
                              f"got={c_got}, expected={c_exp}")
                        violations += 1

        assert violations == 0, f"n={n}: {violations} antisymmetry violations"
        print(f"  [OK] n={n}: graded antisymmetry holds")


# ---------------------------------------------------------------------------
# Tests: Jacobi identity (sample for n=1)
# ---------------------------------------------------------------------------

def test_jacobi_identity_n1():
    n = 1
    gens = build_generators(n)
    odd, even = build_basis(n)
    all_labels = odd + even

    def bracket_decomp(X_lbl, Y_lbl):
        return full_bracket(X_lbl, Y_lbl, n, gens)

    def add_decomp(d1, d2):
        result = dict(d1)
        for k, v in d2.items():
            result[k] = result.get(k, Fraction(0)) + v
        return {k: v for k, v in result.items() if v != 0}

    def scale_decomp(d, s):
        return {k: v * s for k, v in d.items()}

    # Test Jacobi for a sample of triples
    triples = [
        ("E_eps1_del1_pp", "E_eps1_del1_mm", "H_1"),
        ("E_eps1_del1_pp", "E_eps1_del1_mp", "E_eps1_del1_mm"),
        ("H_1", "E_2del1_p", "E_2del1_m"),
        ("E_eps1_del1_pp", "H_2", "E_2del1_m"),
    ]

    violations = 0
    for A_lbl, B_lbl, C_lbl in triples:
        pA = label_parity(A_lbl)
        pB = label_parity(B_lbl)
        pC = label_parity(C_lbl)

        # Super Jacobi: (-1)^{pA*pC} [A,[B,C}] + cyclic = 0
        def jacobi_term(X, Y, Z, pX, pZ):
            BC = bracket_decomp(Y, Z)
            # [X, BC} = sum coeff_Z' [X, Z'}
            result = {}
            for Z_prime, c in BC.items():
                pZp = label_parity(Z_prime)
                XZp = bracket_decomp(X, Z_prime)
                # Sign from [X, c*Z'} = c [X, Z'}
                for W, d in XZp.items():
                    result[W] = result.get(W, Fraction(0)) + Fraction((-1) ** (pX * pZ)) * c * d
            return result

        term1 = jacobi_term(A_lbl, B_lbl, C_lbl, pA, pC)
        term2 = jacobi_term(B_lbl, C_lbl, A_lbl, pB, pA)
        term3 = jacobi_term(C_lbl, A_lbl, B_lbl, pC, pB)

        total = add_decomp(add_decomp(term1, term2), term3)
        if total:
            print(f"  JACOBI FAIL: [{A_lbl},[{B_lbl},{C_lbl}]] + cyc = {total}")
            violations += 1

    assert violations == 0, f"n=1: {violations} Jacobi violations"
    print(f"  [OK] n=1: Jacobi identity holds for {len(triples)} sampled triples")


# ---------------------------------------------------------------------------
# Tests: schema structure
# ---------------------------------------------------------------------------

def test_schema_structure():
    from build_C_structure_constants import build_schema1
    required_keys = [
        "schema_version", "algebra", "oscillator_generators",
        "oscillator_relations", "central_elements",
        "basis", "parity", "generator_realization", "structure_constants", "metadata"
    ]
    for n in [1, 2, 3]:
        schema = build_schema1(n)
        assert schema["schema_version"] == "5.0"
        assert schema["algebra"]["family"] == "C"
        assert schema["algebra"]["m"] == 1
        assert schema["algebra"]["n"] == n
        for key in required_keys:
            assert key in schema, f"n={n}: missing key {key}"
        # Verify basis counts match dimension formulas
        dim = schema["algebra"]["dimension"]
        assert len(schema["basis"]["odd"]) == dim["odd"]
        assert len(schema["basis"]["even"]) == dim["even"]
        assert dim["even"] == 2*n*n + n + 1
        assert dim["odd"] == 4*n
        print(f"  [OK] n={n}: schema structure valid")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== Test: basis dimensions ===")
    test_basis_dimensions()

    print("\n=== Test: parities ===")
    test_parities()

    print("\n=== Test: generator counts ===")
    test_generator_counts()

    print("\n=== Test: schema structure ===")
    test_schema_structure()

    print("\n=== Test: n=1 key brackets ===")
    test_n1_key_brackets()

    print("\n=== Test: graded antisymmetry ===")
    test_graded_antisymmetry()

    print("\n=== Test: Jacobi identity (n=1 sample) ===")
    test_jacobi_identity_n1()

    print("\n=== All tests passed ===")
