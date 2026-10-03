"""
verify_C_structure.py
Verifies the Super Jacobi identity and graded antisymmetry for C(n+1) structure constants.

Super Jacobi identity:
  (-1)^{p(X)p(Z)} [X, [Y, Z]] + (-1)^{p(Y)p(X)} [Y, [Z, X]] + (-1)^{p(Z)p(Y)} [Z, [X, Y]] = 0

Graded antisymmetry:
  [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]

Both are verified by computing brackets in the oscillator algebra.
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict
from itertools import combinations_with_replacement

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from C_generators import CnPlus1, graded_bracket


def get_bracket(alg, X, Y):
    """Compute [X, Y] using oscillator algebra. Returns decomp dict."""
    p_X = alg.parity_map[X]
    p_Y = alg.parity_map[Y]
    osc_br = graded_bracket(alg.realizations[X], alg.realizations[Y], p_X, p_Y, alg.osc_idx)
    if not osc_br:
        return {}
    return alg.decompose(osc_br)


def bracket_from_sc(sc_dict, alg, X, Y):
    """Get [X, Y] from precomputed structure constant dict."""
    key = (X, Y)
    result = sc_dict.get(key, {})
    if not result:
        # Check antisymmetry: [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]
        rev_key = (Y, X)
        rev = sc_dict.get(rev_key, {})
        if rev:
            sign = -Fraction((-1) ** (alg.parity_map[X] * alg.parity_map[Y]))
            result = {k: sign * v for k, v in rev.items()}
    return result


def nested_bracket(sc_dict, alg, X, Y, Z):
    """Compute [X, [Y, Z]] using structure constants."""
    inner = bracket_from_sc(sc_dict, alg, Y, Z)
    result = defaultdict(Fraction)
    for W, c_inner in inner.items():
        outer = bracket_from_sc(sc_dict, alg, X, W)
        for V, c_outer in outer.items():
            result[V] += c_inner * c_outer
    return {k: v for k, v in result.items() if v != 0}


def check_antisymmetry(alg):
    """
    Check [X, Y] = -(-1)^{p(X)p(Y)} [Y, X] for all pairs.
    Returns (n_checked, n_failed, failures).
    """
    n_checked = 0
    n_failed = 0
    failures = []

    basis = alg.basis
    for i in range(len(basis)):
        for j in range(i + 1, len(basis)):
            X, Y = basis[i], basis[j]
            p_X = alg.parity_map[X]
            p_Y = alg.parity_map[Y]

            xy = get_bracket(alg, X, Y)
            yx = get_bracket(alg, Y, X)

            # [X, Y] + (-1)^{p(X)p(Y)} [Y, X] should = 0
            sign = Fraction((-1) ** (p_X * p_Y))
            combined = defaultdict(Fraction)
            for k, v in xy.items():
                combined[k] += v
            for k, v in yx.items():
                combined[k] += sign * v
            combined = {k: v for k, v in combined.items() if v != 0}

            n_checked += 1
            if combined:
                n_failed += 1
                failures.append((X, Y, combined))

    return n_checked, n_failed, failures


def check_super_jacobi(alg):
    """
    Check the super Jacobi identity for all triples (X, Y, Z).
    Uses precomputed structure constants for efficiency.
    Returns (n_checked, n_failed, failures).
    """
    # Build SC dict: (X, Y) -> decomp for i < j
    sc_dict = {}
    basis = alg.basis
    for i in range(len(basis)):
        for j in range(i + 1, len(basis)):
            X, Y = basis[i], basis[j]
            br = get_bracket(alg, X, Y)
            if br:
                sc_dict[(X, Y)] = br

    n_checked = 0
    n_failed = 0
    failures = []

    for i in range(len(basis)):
        for j in range(i, len(basis)):
            for k in range(j, len(basis)):
                X, Y, Z = basis[i], basis[j], basis[k]
                p_X = alg.parity_map[X]
                p_Y = alg.parity_map[Y]
                p_Z = alg.parity_map[Z]

                # Jacobi: (-1)^{p_X p_Z} [X,[Y,Z]] + (-1)^{p_Y p_X} [Y,[Z,X]] + (-1)^{p_Z p_Y} [Z,[X,Y]] = 0
                s1 = Fraction((-1) ** (p_X * p_Z))
                s2 = Fraction((-1) ** (p_Y * p_X))
                s3 = Fraction((-1) ** (p_Z * p_Y))

                term1 = nested_bracket(sc_dict, alg, X, Y, Z)
                term2 = nested_bracket(sc_dict, alg, Y, Z, X)
                term3 = nested_bracket(sc_dict, alg, Z, X, Y)

                combined = defaultdict(Fraction)
                for w, c in term1.items():
                    combined[w] += s1 * c
                for w, c in term2.items():
                    combined[w] += s2 * c
                for w, c in term3.items():
                    combined[w] += s3 * c
                combined = {k: v for k, v in combined.items() if v != 0}

                n_checked += 1
                if combined:
                    n_failed += 1
                    if len(failures) < 5:  # Limit output
                        failures.append((X, Y, Z, combined))

    return n_checked, n_failed, failures


def verify_n(n):
    """Run all checks for C(n+1) and return results dict."""
    alg = CnPlus1(n)
    print(f"\n=== C({n+1}) = osp(2|{2*n}), n={n} ===")
    print(f"  Basis: {len(alg.even_basis)} even + {len(alg.odd_basis)} odd = {len(alg.basis)} total")

    # Antisymmetry check
    n_as, n_as_fail, as_failures = check_antisymmetry(alg)
    print(f"  Antisymmetry: {n_as} pairs checked, {n_as_fail} failures")
    if as_failures:
        for X, Y, residual in as_failures[:3]:
            print(f"    FAIL [{X},{Y}] antisymmetry: {residual}")

    # Jacobi check
    n_jac, n_jac_fail, jac_failures = check_super_jacobi(alg)
    print(f"  Super Jacobi: {n_jac} triples checked, {n_jac_fail} failures")
    if jac_failures:
        for X, Y, Z, residual in jac_failures[:3]:
            print(f"    FAIL Jacobi({X},{Y},{Z}): {residual}")

    status = 'PASS' if n_as_fail == 0 and n_jac_fail == 0 else 'FAIL'
    print(f"  Overall: {status}")

    return {
        'n': n,
        'algebra': f'C({n+1}) = osp(2|{2*n})',
        'antisymmetry': {'checked': n_as, 'failed': n_as_fail},
        'super_jacobi': {'checked': n_jac, 'failed': n_jac_fail},
        'status': status
    }


def main():
    results = []
    for n in range(1, 4):
        results.append(verify_n(n))

    print("\n=== Summary ===")
    all_pass = all(r['status'] == 'PASS' for r in results)
    for r in results:
        print(f"  {r['algebra']}: antisymmetry {r['antisymmetry']['checked']} pairs, "
              f"Jacobi {r['super_jacobi']['checked']} triples → {r['status']}")
    print(f"\nOverall: {'ALL PASS' if all_pass else 'SOME FAILURES'}")
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
