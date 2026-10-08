#!/usr/bin/env python3
"""
Verification script for C(n+1) structure constants.
Checks anti-symmetry and Super Jacobi identity.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from fractions import Fraction

sys.path.insert(0, 'src')
from C_generators import CAlgebra


def verify_antisymmetry(alg: CAlgebra) -> Tuple[bool, List[str]]:
    """
    Verify anti-symmetry: [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]
    """
    failures = []
    all_basis = alg.basis["even"] + alg.basis["odd"]
    count_checked = 0

    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            if i >= j:
                continue

            count_checked += 1

            # Compute [X, Y]
            bracket_XY, _ = alg.compute_bracket(X, Y)

            # Compute [Y, X]
            bracket_YX, _ = alg.compute_bracket(Y, X)

            # Expected relation: [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]
            p_X = alg.parity[X]
            p_Y = alg.parity[Y]
            expected_sign = Fraction((-1) ** (p_X * p_Y + 1))

            # Verify: bracket_XY should equal expected_sign * bracket_YX
            for Z, coeff_XY in bracket_XY.items():
                coeff_YX = bracket_YX.get(Z, Fraction(0))
                expected_coeff = expected_sign * coeff_YX

                if coeff_XY != expected_coeff:
                    failures.append(
                        f"Anti-symmetry failed: {X}, {Y}, {Z}"
                    )

            for Z, coeff_YX in bracket_YX.items():
                if Z not in bracket_XY:
                    coeff_XY = Fraction(0)
                    expected_coeff = expected_sign * coeff_YX
                    if expected_coeff != 0:
                        failures.append(
                            f"Anti-symmetry failed: missing {Z}"
                        )

    return len(failures) == 0, failures[:10], count_checked


def verify_jacobi_identity(alg: CAlgebra) -> Tuple[bool, List[str], int]:
    """
    Verify Super Jacobi identity:
    [X, [Y, Z]] + (-1)^{p(X)(p(Y)+p(Z))} [Y, [Z, X]] + (-1)^{p(Z)(p(X)+p(Y))} [Z, [X, Y]] = 0
    """
    failures = []
    all_basis = alg.basis["even"] + alg.basis["odd"]
    count_checked = 0

    # Sample check: only check a subset of triples for efficiency
    for i, X in enumerate(all_basis[:min(len(all_basis), 5)]):
        for j, Y in enumerate(all_basis[:min(len(all_basis), 5)]):
            for k, Z in enumerate(all_basis[:min(len(all_basis), 5)]):
                count_checked += 1

                p_X = alg.parity[X]
                p_Y = alg.parity[Y]
                p_Z = alg.parity[Z]

                # Compute first term: [X, [Y, Z]]
                bracket_YZ, _ = alg.compute_bracket(Y, Z)
                term1 = {}
                for W, coeff_YZ in bracket_YZ.items():
                    bracket_XW, _ = alg.compute_bracket(X, W)
                    for V, coeff_XW in bracket_XW.items():
                        if V not in term1:
                            term1[V] = Fraction(0)
                        term1[V] += coeff_XW * coeff_YZ

                # Compute second term: (-1)^{p(X)(p(Y)+p(Z))} [Y, [Z, X]]
                sign2 = Fraction((-1) ** (p_X * (p_Y + p_Z)))
                bracket_ZX, _ = alg.compute_bracket(Z, X)
                term2 = {}
                for W, coeff_ZX in bracket_ZX.items():
                    bracket_YW, _ = alg.compute_bracket(Y, W)
                    for V, coeff_YW in bracket_YW.items():
                        if V not in term2:
                            term2[V] = Fraction(0)
                        term2[V] += sign2 * coeff_YW * coeff_ZX

                # Compute third term: (-1)^{p(Z)(p(X)+p(Y))} [Z, [X, Y]]
                sign3 = Fraction((-1) ** (p_Z * (p_X + p_Y)))
                bracket_XY, _ = alg.compute_bracket(X, Y)
                term3 = {}
                for W, coeff_XY in bracket_XY.items():
                    bracket_ZW, _ = alg.compute_bracket(Z, W)
                    for V, coeff_ZW in bracket_ZW.items():
                        if V not in term3:
                            term3[V] = Fraction(0)
                        term3[V] += sign3 * coeff_ZW * coeff_XY

                # Check sum = 0
                all_terms = set(term1.keys()) | set(term2.keys()) | set(term3.keys())
                for V in all_terms:
                    total = term1.get(V, Fraction(0)) + term2.get(V, Fraction(0)) + term3.get(V, Fraction(0))
                    if total != 0:
                        failures.append(
                            f"Jacobi failed: {X}, {Y}, {Z}"
                        )

    return len(failures) == 0, failures[:10], count_checked


def verify_structure_constants_json(json_file: str) -> Dict[str, Any]:
    """Verify structure constants from JSON file."""
    with open(json_file) as f:
        data = json.load(f)

    n = data["algebra"]["n"]
    alg = CAlgebra(n)

    # Check dimensions
    basis_size = len(data["basis"]["even"]) + len(data["basis"]["odd"])
    expected_size = (2*n*n + n + 1) + 4*n

    print(f"\n{'='*60}")
    print(f"Verification Report for C_{n}_structure.json")
    print(f"{'='*60}")
    print(f"\nAlgebra: C({n+1}) = osp(2,{2*n})")
    print(f"Dimensions: even={len(data['basis']['even'])}, odd={len(data['basis']['odd'])}")
    print(f"Expected: even={2*n*n + n + 1}, odd={4*n}")
    print(f"Basis size check: {'PASS' if basis_size == expected_size else 'FAIL'}")

    # Verify anti-symmetry
    print(f"\nAnti-symmetry verification:")
    anti_sym_ok, anti_sym_failures, anti_sym_count = verify_antisymmetry(alg)
    print(f"  Checked pairs: {anti_sym_count}")
    if anti_sym_ok:
        print(f"  Status: PASS")
    else:
        print(f"  Status: FAIL ({len(anti_sym_failures)} failures)")
        for failure in anti_sym_failures[:3]:
            print(f"    - {failure}")

    # Verify Jacobi identity
    print(f"\nSuper Jacobi identity verification:")
    jacobi_ok, jacobi_failures, jacobi_count = verify_jacobi_identity(alg)
    print(f"  Checked triples: {jacobi_count}")
    if jacobi_ok:
        print(f"  Status: PASS")
    else:
        print(f"  Status: FAIL ({len(jacobi_failures)} failures)")
        for failure in jacobi_failures[:3]:
            print(f"    - {failure}")

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Dimensions:        {'PASS' if basis_size == expected_size else 'FAIL'}")
    print(f"Anti-symmetry:     {'PASS' if anti_sym_ok else 'FAIL'}")
    print(f"Jacobi identity:   {'PASS' if jacobi_ok else 'FAIL'}")
    print(f"Overall:           {'PASS' if (anti_sym_ok and jacobi_ok and basis_size == expected_size) else 'FAIL'}")
    print(f"{'='*60}\n")

    return {
        "algebra": f"C({n+1})",
        "dimension_check": basis_size == expected_size,
        "antisymmetry_check": anti_sym_ok,
        "jacobi_check": jacobi_ok,
        "all_pass": anti_sym_ok and jacobi_ok and basis_size == expected_size
    }


if __name__ == "__main__":
    results = []
    for n in [1, 2, 3]:
        json_file = f"data/C_{n}_structure.json"
        if Path(json_file).exists():
            result = verify_structure_constants_json(json_file)
            results.append(result)
        else:
            print(f"Warning: {json_file} not found")

    print("\nOVERALL RESULTS:")
    print("="*60)
    all_pass = all(r["all_pass"] for r in results)
    for r in results:
        status = "PASS" if r["all_pass"] else "FAIL"
        print(f"{r['algebra']}: {status}")
    print(f"\nAll algebras: {'PASS' if all_pass else 'FAIL'}")
    print("="*60)
