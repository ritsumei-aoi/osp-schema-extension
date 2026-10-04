"""
Verification script for C(n+1) structure constants.

Checks:
  1. Graded anti-symmetry: [X, Y} + (-1)^{p(X)p(Y)} [Y, X} = 0
  2. Super Jacobi identity:
     (-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0

Brackets are computed directly from the oscillator algebra (not from the stored table),
to avoid circular reasoning.
"""

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from C_generators import (
    build_basis, build_parity_dict, build_generator_realizations,
    graded_bracket, express_in_basis
)


# ---------------------------------------------------------------------------
# Helper: compute [X, Y} and express result in basis
# ---------------------------------------------------------------------------

def compute_bracket_in_basis(X, Y, gens, parity, n):
    """
    Compute [X, Y} directly using oscillator algebra, return as {Z: Fraction}.
    """
    pX, pY = parity[X], parity[Y]
    bracket_osc = graded_bracket(gens[X], pX, gens[Y], pY, n)
    if not bracket_osc:
        return {}
    result = express_in_basis(bracket_osc, gens, n)
    if result is None:
        return None  # Unexpressible in basis
    return result


def add_elements(e1, e2):
    result = dict(e1)
    for Z, c in e2.items():
        result[Z] = result.get(Z, Fraction(0)) + c
    return {Z: c for Z, c in result.items() if c != 0}


def scale_element(e, scalar):
    if scalar == 0:
        return {}
    return {Z: scalar * c for Z, c in e.items() if scalar * c != 0}


# ---------------------------------------------------------------------------
# Anti-symmetry check
# ---------------------------------------------------------------------------

def check_antisymmetry(basis, parity, gens, n, verbose=False):
    """
    Check [X, Y} + (-1)^{p(X)p(Y)} [Y, X} = 0 for all pairs (X, Y).
    """
    failures = []
    for X in basis:
        for Y in basis:
            pX, pY = parity[X], parity[Y]
            bXY = compute_bracket_in_basis(X, Y, gens, parity, n) or {}
            bYX = compute_bracket_in_basis(Y, X, gens, parity, n) or {}
            sign = Fraction((-1) ** (pX * pY))
            combined = add_elements(bXY, scale_element(bYX, sign))
            if combined:
                failures.append((X, Y, combined))
                if verbose:
                    print(f"  Antisymmetry FAIL: [{X},{Y}] + {sign}*[{Y},{X}] = {combined}")
    return failures


# ---------------------------------------------------------------------------
# Super Jacobi check
# ---------------------------------------------------------------------------

def bracket_of_element(e, Y, gens, parity, n):
    """Compute [e, Y} where e = {Z: coeff}."""
    result = {}
    for Z, cZ in e.items():
        bZY = compute_bracket_in_basis(Z, Y, gens, parity, n) or {}
        result = add_elements(result, scale_element(bZY, cZ))
    return result


def X_bracket_element(X, e, gens, parity, n):
    """Compute [X, e} where e = {Z: coeff}."""
    result = {}
    for Z, cZ in e.items():
        bXZ = compute_bracket_in_basis(X, Z, gens, parity, n) or {}
        result = add_elements(result, scale_element(bXZ, cZ))
    return result


def check_jacobi(basis, parity, gens, n, verbose=False):
    """
    Super Jacobi identity for all triples.
    """
    failures = []
    nb = len(basis)
    total = 0

    for xi in range(nb):
        for yi in range(nb):
            for zi in range(nb):
                X, Y, Z = basis[xi], basis[yi], basis[zi]
                pX, pY, pZ = parity[X], parity[Y], parity[Z]

                bYZ = compute_bracket_in_basis(Y, Z, gens, parity, n) or {}
                bZX = compute_bracket_in_basis(Z, X, gens, parity, n) or {}
                bXY = compute_bracket_in_basis(X, Y, gens, parity, n) or {}

                term1 = X_bracket_element(X, bYZ, gens, parity, n)
                term2 = X_bracket_element(Y, bZX, gens, parity, n)
                term3 = X_bracket_element(Z, bXY, gens, parity, n)

                s1 = Fraction((-1) ** (pX * pZ))
                s2 = Fraction((-1) ** (pY * pX))
                s3 = Fraction((-1) ** (pZ * pY))

                total_elem = add_elements(
                    add_elements(scale_element(term1, s1), scale_element(term2, s2)),
                    scale_element(term3, s3)
                )

                total += 1
                if total_elem:
                    failures.append((X, Y, Z, total_elem))
                    if verbose:
                        print(f"  Jacobi FAIL: ({X},{Y},{Z}): {total_elem}")

    return failures, total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def verify_n(n, verbose=False):
    print(f"\n=== Verifying n={n} (C({n+1}) = osp(2|{2*n})) ===")
    even_basis, odd_basis = build_basis(n)
    basis = odd_basis + even_basis
    parity = build_parity_dict(even_basis, odd_basis)
    gens = build_generator_realizations(n)

    print(f"  Basis size: {len(basis)} generators ({len(odd_basis)} odd, {len(even_basis)} even)")

    asym_failures = check_antisymmetry(basis, parity, gens, n, verbose=verbose)
    if asym_failures:
        print(f"  Anti-symmetry: FAIL ({len(asym_failures)} failures)")
        if verbose:
            for X, Y, res in asym_failures[:3]:
                print(f"    [{X},{Y}] check: {res}")
    else:
        print(f"  Anti-symmetry: PASS")

    jac_failures, total_triples = check_jacobi(basis, parity, gens, n, verbose=verbose)
    if jac_failures:
        print(f"  Super Jacobi: FAIL ({len(jac_failures)}/{total_triples} triples failed)")
        if verbose:
            for X, Y, Z, res in jac_failures[:3]:
                print(f"    ({X},{Y},{Z}): {res}")
    else:
        print(f"  Super Jacobi: PASS ({total_triples} triples checked)")

    return len(asym_failures) == 0 and len(jac_failures) == 0


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv
    all_pass = True
    # n=3 is expensive; run n=1,2 by default, add n=3 with --all
    ns = [1, 2, 3] if "--all" in sys.argv else [1, 2]
    for n in ns:
        ok = verify_n(n, verbose=verbose)
        all_pass = all_pass and ok

    print()
    if all_pass:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED")
        sys.exit(1)
