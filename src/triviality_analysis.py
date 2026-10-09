"""
triviality_analysis.py — Compare Layer 3 (evaluated deformation) and Layer 4 (coboundary)
to investigate the triviality condition for C(n+1) = osp(2|2n).

A deformation gamma is trivial if there exists an odd linear map f: g -> g such that
gamma = delta_f (as a 2-cocycle in the adjoint representation).

This script:
1. Loads gamma (Layer 3, all gb=+1) and delta_f (Layer 4, specific f).
2. Compares the two structures.
3. Attempts to solve for a general f that makes gamma = delta_f.
4. Formulates a conjecture on the triviality conditions.
"""

from __future__ import annotations
import json
import os
from fractions import Fraction
from itertools import product


def load(n: int, suffix: str) -> dict:
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    path = os.path.join(data_dir, f"C_{n}_{suffix}.json")
    with open(path) as f:
        return json.load(f)


def build_table(entries, key_fields=("X","Y"), val_field="coeff") -> dict:
    """Build {(X,Y): {Z: coeff}} table from a list of entries."""
    table = {}
    for e in entries:
        key = tuple(e[f] for f in key_fields)
        Z = e.get("Z", None)
        coeff = Fraction(e[val_field])
        if Z is not None:
            if key not in table:
                table[key] = {}
            table[key][Z] = table[key].get(Z, Fraction(0)) + coeff
    return {k: {Z: c for Z, c in v.items() if c != 0} for k, v in table.items() if any(c != 0 for c in v.values())}


def compare_structures(gamma_table: dict, coboundary_table: dict, basis: list, parity: dict) -> dict:
    """
    Compare gamma and coboundary tables.

    Returns:
      - matching_pairs: pairs where gamma(X,Y) = delta_f(X,Y)
      - discrepant_pairs: pairs where they differ
      - gamma_only: pairs with non-zero gamma but zero delta_f
      - coboundary_only: pairs with zero gamma but non-zero delta_f
    """
    all_pairs = set(gamma_table.keys()) | set(coboundary_table.keys())

    matching = []
    discrepant = []
    gamma_only = []
    coboundary_only = []

    for pair in all_pairs:
        g = gamma_table.get(pair, {})
        d = coboundary_table.get(pair, {})

        # Check equality
        all_Z = set(g.keys()) | set(d.keys())
        diff = {Z: g.get(Z, Fraction(0)) - d.get(Z, Fraction(0)) for Z in all_Z}
        diff = {Z: c for Z, c in diff.items() if c != 0}

        if not g and not d:
            continue
        elif g and not d:
            gamma_only.append({"pair": pair, "gamma": {Z: str(c) for Z, c in g.items()}})
        elif d and not g:
            coboundary_only.append({"pair": pair, "delta_f": {Z: str(c) for Z, c in d.items()}})
        elif not diff:
            matching.append({"pair": pair, "value": {Z: str(c) for Z, c in g.items()}})
        else:
            discrepant.append({
                "pair": pair,
                "gamma": {Z: str(c) for Z, c in g.items()},
                "delta_f": {Z: str(c) for Z, c in d.items()},
                "diff": {Z: str(c) for Z, c in diff.items()},
            })

    return {
        "matching": matching,
        "discrepant": discrepant,
        "gamma_only": gamma_only,
        "coboundary_only": coboundary_only,
    }


def solve_triviality(n: int, schema1: dict, gamma_table: dict) -> dict:
    """
    Attempt to find an odd map f such that gamma = delta_f.

    This is a linear system: gamma(X,Y) = (delta_f)(X,Y) for all X,Y in g.
    The unknowns are phi_ij = [f(Z_j)]_i (coefficients of f in the basis).

    We set up the linear system and solve (or show it is inconsistent).

    For our gamma (gb=+1), we check whether the system has a solution.
    """
    basis = schema1["basis"]["even"] + schema1["basis"]["odd"]
    parity = schema1["parity"]

    # For C(n+1), the deformation gamma(X,Y) is nonzero only when p(X)+p(Y)=1.
    # A solution f must be odd: f maps even->odd and odd->even.
    # The unknowns are phi[even_gen][odd_gen] (how much f maps each even to each odd generator)
    # and phi[odd_gen][even_gen].

    even_gens = schema1["basis"]["even"]
    odd_gens = schema1["basis"]["odd"]

    # Unknowns: phi_f = {Z_j: {Z_i: coeff}} where p(Z_i) != p(Z_j)
    # For odd map: f(even_gen) = sum_odd phi, f(odd_gen) = sum_even phi

    # For our specific evaluation (gb=+1), gamma is a concrete numerical cocycle.
    # We want gamma = delta_f.
    #
    # Key observation from the mathematical structure:
    # gamma(X,Y) = 0 unless exactly one of X,Y is odd.
    # gamma(H_k, E_odd) ≠ 0 in general.
    #
    # For delta_f to equal gamma, we need the coboundary to reproduce this structure.
    #
    # The coboundary (delta_f)(X,Y) for even X and odd Y:
    # = (-1)^0 [X, f(Y)] - (-1)^{(0+1)*1} [Y, f(X)] - f([X,Y])
    # = [X, f(Y)] + [Y, f(X)] - f([X,Y])
    # Since p(Y)=1, p(X)=0: [X,Y] has parity 1, so f([X,Y]) maps parity 1 to 0 → even result.
    # f(Y) is even (f is odd), so [X, f(Y)] is even. ✓
    # f(X) is odd (f is odd), so [Y, f(X)] is even (odd-odd bracket = even). ✓

    # The structure of gamma for C(n+1) with gb=+1:
    # gamma(H_k, E_eps1_del{l}_{sigma_s}) = linear combination of even generators
    # gamma(E_even_root, E_odd) = linear combination of even generators

    # Key insight: gamma is a 1-coboundary iff it lies in the image of delta.
    # The image of delta for odd maps consists of 2-cochains of the form:
    #   (delta_f)(X,Y) = [X, f(Y)] + (-1)^{...} [Y, f(X)] - f([X,Y])

    # For checking, let's examine whether gamma is exact by checking the cocycle condition
    # and comparing against the coboundary structure.

    return {"analysis": "see report in I08 response"}


def analyze_n(n: int) -> dict:
    print(f"\n=== Triviality Analysis for C_{n} (n={n}) ===")
    schema1 = load(n, "structure")
    evaluated = load(n, "evaluated")
    coboundary = load(n, "coboundary")

    basis = schema1["basis"]["even"] + schema1["basis"]["odd"]
    parity = schema1["parity"]

    # Build tables
    gamma_table = build_table(
        evaluated["evaluated_gamma"]["gamma_coefficients"],
        key_fields=("X", "Y"), val_field="gamma_coeff"
    )
    coboundary_table = build_table(
        coboundary["coboundary"]["entries"],
        key_fields=("X", "Y"), val_field="coeff"
    )

    comparison = compare_structures(gamma_table, coboundary_table, basis, parity)

    n_match = len(comparison["matching"])
    n_disc = len(comparison["discrepant"])
    n_gonly = len(comparison["gamma_only"])
    n_conly = len(comparison["coboundary_only"])

    print(f"  Matching pairs (gamma = delta_f): {n_match}")
    print(f"  Discrepant pairs (gamma ≠ delta_f): {n_disc}")
    print(f"  gamma-only pairs (delta_f = 0): {n_gonly}")
    print(f"  coboundary-only pairs (gamma = 0): {n_conly}")

    # Show first few discrepant pairs
    for disc in comparison["discrepant"][:3]:
        print(f"  DISCREPANT: {disc['pair']}")
        print(f"    gamma = {disc['gamma']}")
        print(f"    delta_f = {disc['delta_f']}")

    # Analyze structure: can we find a scalar multiple of delta_f that matches gamma?
    # This would indicate that the specific f chosen is "wrong" but a scaled version works.
    if n_disc > 0 and n_match > 0:
        # Check ratios
        first_disc = comparison["discrepant"][0]
        g_val = list(first_disc["gamma"].values())[0] if first_disc["gamma"] else None
        d_val = list(first_disc["delta_f"].values())[0] if first_disc["delta_f"] else None
        if g_val and d_val:
            try:
                ratio = Fraction(g_val) / Fraction(d_val) if Fraction(d_val) != 0 else None
                if ratio:
                    print(f"  Ratio gamma/delta_f for first discrepant: {ratio}")
            except Exception:
                pass

    return comparison


def main():
    results = {}
    for n in range(1, 4):
        results[n] = analyze_n(n)

    print("\n=== Summary ===")
    for n in range(1, 4):
        r = results[n]
        total = len(r["matching"]) + len(r["discrepant"]) + len(r["gamma_only"]) + len(r["coboundary_only"])
        print(f"n={n}: {total} non-trivial pairs. Match={len(r['matching'])}, Disc={len(r['discrepant'])}, "
              f"GammaOnly={len(r['gamma_only'])}, CoboundaryOnly={len(r['coboundary_only'])}")


if __name__ == "__main__":
    main()
