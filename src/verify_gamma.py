"""
Systematic cross-verification of gamma coefficients for C(n+1).

For each selected generator pair (X, Y), we derive the expected gamma(X, Y)
analytically from the deformed commutation relation
    [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa
and compare against the stored data/C_{n}_gamma.json.

Representative pairs are chosen to cover:
  - odd-odd brackets (eps-del roots with themselves)
  - odd-even brackets (eps-del with Cartan or bosonic root generators)
  - different parities (pp/pm/mp/mm) and different gb parameters
  - n=1, n=2 cases to check the gb_matrix extension

Run this script to reproduce the cross-check:
    python src/verify_gamma.py
"""

import json
import sys
import os
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, build_parity_dict, build_generator_realizations, express_in_basis
from C_gamma import _normalize_deformed, get_all_gb_labels, compute_gamma


def load_gamma_json(n):
    with open(f"data/C_{n}_gamma.json") as f:
        data = json.load(f)
    pairs = data["inhomogeneous_deformation"]["gamma_coefficients"]
    gamma = {}
    for p in pairs:
        key = (p["X"], p["Y"])
        gamma[key] = {gb: {Z: Fraction(c) for Z, c in zmap.items()}
                      for gb, zmap in p["gamma_coeffs"].items()}
    return gamma


def check_pair(X, Y, expected_gb_coeffs, n, gamma_json):
    """Compare expected gamma coefficients against JSON for (X, Y)."""
    key = (X, Y)
    actual = gamma_json.get(key, {})
    errors = []
    for gb, zmap in expected_gb_coeffs.items():
        for Z, coeff in zmap.items():
            actual_coeff = actual.get(gb, {}).get(Z, Fraction(0))
            if actual_coeff != Fraction(coeff):
                errors.append(
                    f"  MISMATCH gamma({X},{Y})[{Z}] for {gb}: "
                    f"expected {coeff}, got {actual_coeff}"
                )
    for gb, zmap in actual.items():
        for Z, coeff in zmap.items():
            exp_coeff = expected_gb_coeffs.get(gb, {}).get(Z, Fraction(0))
            if coeff != exp_coeff:
                errors.append(
                    f"  EXTRA gamma({X},{Y})[{Z}] for {gb}: "
                    f"actual {coeff}, expected {exp_coeff}"
                )
    return errors


def run_checks():
    print("=== Systematic gamma cross-verification ===\n")
    total_checks = 0
    total_errors = 0

    # -----------------------------------------------------------------------
    # n=1 checks
    # -----------------------------------------------------------------------
    n = 1
    gamma_json = load_gamma_json(n)
    print(f"--- n={n} ---")

    # Pair 1: gamma(E_eps_del1_pp, E_eps_del1_pp)
    # Analytic derivation:
    #   [X, X]_deformed = 2 X*X  (odd-odd)
    #   X = a_1^+ b_1^+; X*X = a_1^+ b_1^+ a_1^+ b_1^+
    #   b_1^+ passes a_1^+ via [b_1^+, a_1^+] = -gb_a1p_b1p * kappa
    #   => X*X = -gb_a1p_b1p * kappa * (a_1^+)^0 b_1^+ ... after (a_1^+)^2=0 kills the swap term
    #   kappa coeff: -gb_a1p_b1p * a_1^+ b_1^+ = -gb_a1p_b1p * E_eps_del1_pp
    #   [X, X]_deformed kappa: 2 * (-gb_a1p_b1p * E_eps_del1_pp)
    # => gamma(E_eps_del1_pp, E_eps_del1_pp)[E_eps_del1_pp] = -2 for gb_a1p_b1p
    expected = {"gb_a1p_b1p": {"E_eps_del1_pp": Fraction(-2)}}
    errs = check_pair("E_eps_del1_pp", "E_eps_del1_pp", expected, n, gamma_json)
    total_checks += 1
    if errs:
        print(f"FAIL: gamma(E_eps_del1_pp, E_eps_del1_pp)")
        for e in errs:
            print(e)
        total_errors += 1
    else:
        print(f"PASS: gamma(E_eps_del1_pp, E_eps_del1_pp)"
              f" [gb_a1p_b1p: E_eps_del1_pp = -2]")

    # Pair 2: gamma(E_eps_del1_pm, H_1)
    # Analytic derivation:
    #   X = a_1^+ b_1^- (pX=1), Y = a_1^+ a_1^- + b_1^+ b_1^- (pY=0)
    #   [X, Y]_deformed = XY - YX
    #
    #   XY: a_1^+ b_1^- * a_1^+ a_1^- = a_1^+(b_1^-)(a_1^+)a_1^-
    #     b_1^- passes a_1^+: b_1^- a_1^+ = a_1^+ b_1^- - gb_a1p_b1m * kappa
    #     => a_1^+(a_1^+ b_1^- - gb_a1p_b1m kappa)a_1^-
    #        = (a_1^+)^2 b_1^- a_1^- - gb_a1p_b1m kappa a_1^+ a_1^-
    #        = -gb_a1p_b1m kappa (a_1^+ a_1^-)   [(a_1^+)^2=0]
    #   XY kappa for H1-monomial: -gb_a1p_b1m * a_1^+ a_1^-
    #
    #   YX (b_1^+ b_1^- monomial): b_1^+ b_1^- * a_1^+ b_1^-
    #     b_1^- passes a_1^+: b_1^- a_1^+ = a_1^+ b_1^- - gb_a1p_b1m kappa
    #     => b_1^+(a_1^+ b_1^- - gb_a1p_b1m kappa)b_1^-
    #        = b_1^+ a_1^+ (b_1^-)^2 - gb_a1p_b1m kappa b_1^+ b_1^-
    #   YX kappa: -gb_a1p_b1m * b_1^+ b_1^-  (with -sign=-1 overall => +)
    #
    #   Total for gb_a1p_b1m: kappa*(-a_1^+a_1^- + b_1^+b_1^-)
    #   Expressed in basis (ignoring scalar parts):
    #     -a_1^+a_1^- = -H_1 monomial contribution => c_H1=-1
    #     b_1^+b_1^- = -H_2 monomial (non-scalar H_2=-b_1^+b_1^-) => c_H2=-2
    #   => gamma[H_1]=-1, gamma[H_2]=-2  for gb_a1p_b1m
    #
    #   For gb_a1p_b1p (from YX b_1^+b_1^- monomial extra swap):
    #     Additional kappa: (b_1^-)^2 => 2*E_2del1_m
    #   => gamma[E_2del1_m]=2 for gb_a1p_b1p
    expected = {
        "gb_a1p_b1m": {"H_1": Fraction(-1), "H_2": Fraction(-2)},
        "gb_a1p_b1p": {"E_2del1_m": Fraction(2)},
    }
    errs = check_pair("E_eps_del1_pm", "H_1", expected, n, gamma_json)
    total_checks += 1
    if errs:
        print(f"FAIL: gamma(E_eps_del1_pm, H_1)")
        for e in errs:
            print(e)
        total_errors += 1
    else:
        print(f"PASS: gamma(E_eps_del1_pm, H_1)"
              f" [gb_a1p_b1m: H1=-1,H2=-2; gb_a1p_b1p: E_2del1_m=2]")

    # Pair 3: gamma(E_eps_del1_pp, E_2del1_m)
    # Analytic derivation:
    #   X = a_1^+ b_1^+ (pX=1), Y = (1/2)(b_1^-)^2 (pY=0)
    #   XY: a_1^+ b_1^+ (b_1^-)^2 -- a_1^+ is before b_1^+, no deformed swap; only CCR swaps
    #     => no kappa contribution from XY
    #   YX: (1/2)(b_1^-)^2 * a_1^+ b_1^+
    #     First b_1^-: b_1^- a_1^+ = a_1^+ b_1^- - gb_a1p_b1m kappa
    #     Second b_1^-: b_1^- a_1^+ = a_1^+ b_1^- - gb_a1p_b1m kappa
    #     Total kappa from (b_1^-)^2 passing a_1^+:
    #       -2 gb_a1p_b1m kappa * b_1^-  (after collecting both terms)
    #     Then * b_1^+: b_1^- b_1^+ = b_1^+ b_1^- + 1 (CCR)
    #       => -gb_a1p_b1m kappa (b_1^+ b_1^- + 1)  (with 1/2 factor applied)
    #   [X,Y] kappa = -(YX kappa) = gb_a1p_b1m * kappa * (b_1^+ b_1^- + 1)
    #   Non-scalar: b_1^+ b_1^- = -H_2 (non-scalar basis expression)
    #   => gamma[H_2] = -1 for gb_a1p_b1m
    expected = {"gb_a1p_b1m": {"H_2": Fraction(-1)}}
    errs = check_pair("E_eps_del1_pp", "E_2del1_m", expected, n, gamma_json)
    total_checks += 1
    if errs:
        print(f"FAIL: gamma(E_eps_del1_pp, E_2del1_m)")
        for e in errs:
            print(e)
        total_errors += 1
    else:
        print(f"PASS: gamma(E_eps_del1_pp, E_2del1_m)"
              f" [gb_a1p_b1m: H_2=-1]")

    # Pair 4: gamma(E_eps_del1_mm, E_2del1_m)
    # Analytic derivation:
    #   X = a_1^- b_1^- (pX=1), Y = (1/2)(b_1^-)^2 (pY=0)
    #   XY: a_1^- b_1^- (b_1^-)^2 -- a_1^- before b_1^-, in order, no deformed swap
    #     => no kappa
    #   YX: (1/2)(b_1^-)^2 * a_1^- b_1^-
    #     b_1^- passes a_1^-: [b_1^-, a_1^-] = -gb_a1m_b1m kappa
    #     Both b_1^- in (b_1^-)^2 each contribute a kappa when passing a_1^-:
    #       total: -2 gb_a1m_b1m kappa * b_1^-  (per the same calculation as pair 3)
    #     Then * b_1^-: kappa * b_1^- * b_1^- = kappa * (b_1^-)^2
    #   YX kappa = (1/2) * (-2) * gb_a1m_b1m * kappa * (b_1^-)^2
    #            = -gb_a1m_b1m * kappa * (b_1^-)^2
    #   [X,Y] kappa = -(YX kappa) = gb_a1m_b1m * kappa * (b_1^-)^2
    #   (b_1^-)^2 = 2 * E_2del1_m  (since E_2del1_m = (1/2)(b_1^-)^2)
    #   => gamma[E_2del1_m] = 2 for gb_a1m_b1m
    expected = {"gb_a1m_b1m": {"E_2del1_m": Fraction(2)}}
    errs = check_pair("E_eps_del1_mm", "E_2del1_m", expected, n, gamma_json)
    total_checks += 1
    if errs:
        print(f"FAIL: gamma(E_eps_del1_mm, E_2del1_m)")
        for e in errs:
            print(e)
        total_errors += 1
    else:
        print(f"PASS: gamma(E_eps_del1_mm, E_2del1_m)"
              f" [gb_a1m_b1m: E_2del1_m=2]")

    # Pair 5: gamma(E_eps_del1_mm, E_2del1_p) -- test H_2 component
    # X = a_1^- b_1^- (pX=1), Y = (1/2)(b_1^+)^2 (pY=0)
    # XY: a_1^- b_1^- (b_1^+)^2
    #   b_1^- b_1^+ = b_1^+ b_1^- + 1 (CCR), no kappa in XY
    # YX: (1/2)(b_1^+)^2 * a_1^- b_1^-
    #   b_1^+ a_1^- = a_1^- b_1^+ - gb_a1m_b1p kappa [b_1^+, a_1^-] = -gb_a1m_b1p kappa
    #   Each b_1^+ passes a_1^-:
    #     total kappa: -2 gb_a1m_b1p kappa * b_1^+   => * b_1^-: b_1^+ b_1^- = N_b
    #     (1/2)*(-2)*gb_a1m_b1p * kappa * b_1^+ b_1^- = -gb_a1m_b1p kappa (b_1^+ b_1^-)
    #   [X,Y] kappa = +gb_a1m_b1p kappa * b_1^+ b_1^-
    #   Non-scalar: b_1^+ b_1^- => c_H2*(-1)=1 => H_2 coefficient = -1
    #   => gamma[H_2] = -1 for gb_a1m_b1p
    expected = {"gb_a1m_b1p": {"H_2": Fraction(-1)}}
    errs = check_pair("E_eps_del1_mm", "E_2del1_p", expected, n, gamma_json)
    total_checks += 1
    if errs:
        print(f"FAIL: gamma(E_eps_del1_mm, E_2del1_p)")
        for e in errs:
            print(e)
        total_errors += 1
    else:
        print(f"PASS: gamma(E_eps_del1_mm, E_2del1_p)"
              f" [gb_a1m_b1p: H_2=-1]")

    # -----------------------------------------------------------------------
    # n=2 check: cross-root pair involving b_2 oscillator
    # -----------------------------------------------------------------------
    n = 2
    gamma_json_2 = load_gamma_json(n)
    print(f"\n--- n={n} ---")

    # Pair 6 (n=2): gamma(E_eps_del2_pp, E_eps_del2_pp)
    # X = a_1^+ b_2^+ (pX=1)
    # [X, X]_deformed = 2 X*X
    # X*X = a_1^+ b_2^+ a_1^+ b_2^+
    #   b_2^+ a_1^+: [b_2^+, a_1^+] = -gb_a1p_b2p kappa
    #   => a_1^+(b_2^+ a_1^+)b_2^+ = a_1^+(a_1^+ b_2^+ - gb_a1p_b2p kappa)b_2^+
    #   = (a_1^+)^2 b_2^+ b_2^+ - gb_a1p_b2p kappa a_1^+ b_2^+
    #   = -gb_a1p_b2p kappa * E_eps_del2_pp   [(a_1^+)^2=0]
    # [X,X] kappa = 2 * (-gb_a1p_b2p) * E_eps_del2_pp
    # => gamma[E_eps_del2_pp] = -2 for gb_a1p_b2p
    expected = {"gb_a1p_b2p": {"E_eps_del2_pp": Fraction(-2)}}
    errs = check_pair("E_eps_del2_pp", "E_eps_del2_pp", expected, n, gamma_json_2)
    total_checks += 1
    if errs:
        print(f"FAIL: gamma(E_eps_del2_pp, E_eps_del2_pp) [n=2]")
        for e in errs:
            print(e)
        total_errors += 1
    else:
        print(f"PASS: gamma(E_eps_del2_pp, E_eps_del2_pp) [n=2]"
              f" [gb_a1p_b2p: E_eps_del2_pp=-2]")

    # Pair 7 (n=2): gamma(E_eps_del1_pp, E_eps_del1_pp) should still hold at n=2
    expected = {"gb_a1p_b1p": {"E_eps_del1_pp": Fraction(-2)}}
    errs = check_pair("E_eps_del1_pp", "E_eps_del1_pp", expected, n, gamma_json_2)
    total_checks += 1
    if errs:
        print(f"FAIL: gamma(E_eps_del1_pp, E_eps_del1_pp) [n=2]")
        for e in errs:
            print(e)
        total_errors += 1
    else:
        print(f"PASS: gamma(E_eps_del1_pp, E_eps_del1_pp) [n=2]"
              f" [gb_a1p_b1p: E_eps_del1_pp=-2]")

    # Pair 8 (n=2): gamma(E_eps_del2_mm, E_2del2_m)
    # Mirrors pair 4 with j=2: gamma[E_2del2_m] = 2 for gb_a1m_b2m
    expected = {"gb_a1m_b2m": {"E_2del2_m": Fraction(2)}}
    errs = check_pair("E_eps_del2_mm", "E_2del2_m", expected, n, gamma_json_2)
    total_checks += 1
    if errs:
        print(f"FAIL: gamma(E_eps_del2_mm, E_2del2_m) [n=2]")
        for e in errs:
            print(e)
        total_errors += 1
    else:
        print(f"PASS: gamma(E_eps_del2_mm, E_2del2_m) [n=2]"
              f" [gb_a1m_b2m: E_2del2_m=2]")

    print(f"\n=== Summary: {total_checks - total_errors}/{total_checks} checks passed ===")
    return total_errors == 0


if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1)
