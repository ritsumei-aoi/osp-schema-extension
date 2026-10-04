"""
C_triviality.py
Triviality analysis: compare Layer 3 (evaluated gamma) with Layer 4 (coboundary)
to determine when the inhomogeneous deformation of C(n+1) is trivial.

A deformation gamma is trivial if there exists an odd linear map f such that
gamma = delta f. We check this by solving the linear system: for all (X,Y,Z),
  gamma_evaluated(X,Y)_Z = (delta f)(X,Y)_Z.

The coboundary (delta f) depends linearly on the phi_{ij} coefficients.
We set up the linear system in those phi coefficients and check solvability.
"""

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import build_basis, build_parity_dict


def load_json(path):
    with open(path) as f:
        return json.load(f)


def compare_structures(n, data_dir="data"):
    """
    Compare evaluated gamma (Layer 3) and coboundary (Layer 4) for rank n.
    Returns analysis dict.
    """
    eval_data = load_json(os.path.join(data_dir, f"C_{n}_evaluated.json"))
    cob_data = load_json(os.path.join(data_dir, f"C_{n}_coboundary.json"))

    # Build lookup for evaluated gamma: (X,Y,Z) -> Fraction
    eval_sc = {}
    for entry in eval_data["evaluated_gamma"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        eval_sc[key] = Fraction(entry["coeff"])

    # Build lookup for coboundary (symbolic): (X,Y,Z) -> dict {gb_label: Fraction}
    cob_sc = {}
    for entry in cob_data["coboundary_delta_f"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        cob_sc[key] = {k: Fraction(v) for k, v in entry["coeff_expr"].items()}

    # All keys in either dataset
    all_keys = set(eval_sc.keys()) | set(cob_sc.keys())

    # For each key, compute: eval(X,Y,Z) - cob(X,Y,Z)
    # gamma is trivial if eval_sc = delta_f for SOME phi assignment.
    # Since our coboundary uses gb params directly as phi,
    # we evaluate cob_sc with all gb=1 (same as eval_data gb_assignment) and compare.
    gb_assignment = {k: Fraction(v) for k, v in eval_data["gb_assignment"].items()}

    cob_evaluated = {}
    for key, expr in cob_sc.items():
        total = sum(Fraction(coeff) * gb_assignment.get(gb, Fraction(0))
                    for gb, coeff in expr.items())
        if total != 0:
            cob_evaluated[key] = total

    # Find matching and mismatching entries
    exact_matches = []
    only_in_gamma = []
    only_in_coboundary = []
    discrepancies = []

    for key in all_keys:
        g_val = eval_sc.get(key, Fraction(0))
        c_val = cob_evaluated.get(key, Fraction(0))

        if g_val == c_val:
            if g_val != 0:
                exact_matches.append((key, g_val))
        else:
            if g_val != 0 and c_val == 0:
                only_in_gamma.append((key, g_val))
            elif g_val == 0 and c_val != 0:
                only_in_coboundary.append((key, c_val))
            else:
                discrepancies.append((key, g_val, c_val))

    return {
        "n": n,
        "total_gamma_entries": len(eval_sc),
        "total_cob_entries": len(cob_evaluated),
        "exact_matches": len(exact_matches),
        "only_in_gamma": len(only_in_gamma),
        "only_in_coboundary": len(only_in_coboundary),
        "discrepancies": len(discrepancies),
        "exact_matches_sample": exact_matches[:5],
        "only_in_gamma_sample": only_in_gamma[:5],
        "only_in_coboundary_sample": only_in_coboundary[:5],
        "discrepancies_sample": discrepancies[:5],
    }


def analyze_triviality_condition(n, data_dir="data"):
    """
    Perform linear algebra analysis to find necessary and sufficient conditions
    on gb parameters for the deformation to be trivial.

    We solve: For each (X,Y,Z), gamma_expr(X,Y)_Z = (delta f)_expr(X,Y)_Z
    as a system of linear equations in gb parameters (treating the phi as
    linearly determined by gb in our coboundary parametrization).

    Since both gamma and coboundary are linear in gb, the equation
    gamma - coboundary = 0 is a linear constraint on gb.
    """
    eval_data = load_json(os.path.join(data_dir, f"C_{n}_gamma.json"))
    cob_data = load_json(os.path.join(data_dir, f"C_{n}_coboundary.json"))

    # gamma(X,Y)_Z is a linear form in gb params
    gamma_forms = {}
    for entry in eval_data["inhomogeneous_deformation"]["gamma_coefficients"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        gamma_forms[key] = {k: Fraction(v) for k, v in entry["gamma_expr"].items()}

    # (delta f)(X,Y)_Z is also a linear form in gb params
    cob_forms = {}
    for entry in cob_data["coboundary_delta_f"]:
        key = (entry["X"], entry["Y"], entry["Z"])
        cob_forms[key] = {k: Fraction(v) for k, v in entry["coeff_expr"].items()}

    # Difference: for triviality, gamma - delta_f = 0 for all (X,Y,Z)
    all_keys = set(gamma_forms.keys()) | set(cob_forms.keys())

    constraints = {}  # Each constraint is a linear form in gb that must equal 0
    for key in all_keys:
        g = gamma_forms.get(key, {})
        c = cob_forms.get(key, {})

        # Difference: g - c
        diff = {}
        all_gbs = set(g.keys()) | set(c.keys())
        for gb in all_gbs:
            val = g.get(gb, Fraction(0)) - c.get(gb, Fraction(0))
            if val != 0:
                diff[gb] = val

        if diff:
            constraints[key] = diff

    return constraints


def run_full_analysis(n, data_dir="data"):
    """Run both comparison and constraint analysis."""
    print(f"\n{'='*60}")
    print(f"C({n+1}) = osp(2|{2*n}), n={n}")
    print(f"{'='*60}")

    comp = compare_structures(n, data_dir)
    print(f"Evaluated gamma entries: {comp['total_gamma_entries']}")
    print(f"Coboundary entries (at gb=1): {comp['total_cob_entries']}")
    print(f"Exact matches (gb=1): {comp['exact_matches']}")
    print(f"Only in gamma: {comp['only_in_gamma']}")
    print(f"Only in coboundary: {comp['only_in_coboundary']}")
    print(f"Discrepancies: {comp['discrepancies']}")

    if comp['exact_matches_sample']:
        print(f"\nSample exact matches (gb=1):")
        for (X,Y,Z), v in comp['exact_matches_sample']:
            print(f"  gamma({X},{Y})_{Z} = cob = {v}")

    if comp['only_in_gamma_sample']:
        print(f"\nSample gamma-only entries (not reproduced by coboundary at gb=1):")
        for (X,Y,Z), v in comp['only_in_gamma_sample']:
            print(f"  gamma({X},{Y})_{Z} = {v} (no cob match)")

    if comp['only_in_coboundary_sample']:
        print(f"\nSample coboundary-only entries:")
        for (X,Y,Z), v in comp['only_in_coboundary_sample']:
            print(f"  cob({X},{Y})_{Z} = {v} (no gamma match)")

    # Symbolic constraint analysis
    constraints = analyze_triviality_condition(n, data_dir)
    print(f"\nSymbolic constraint analysis (gamma - delta_f = 0):")
    print(f"  Number of non-trivial constraints: {len(constraints)}")

    # Extract which gb parameters appear in constraints
    all_gbs_in_constraints = set()
    for diff in constraints.values():
        all_gbs_in_constraints.update(diff.keys())

    if all_gbs_in_constraints:
        print(f"  GB parameters appearing in constraints: {sorted(all_gbs_in_constraints)}")
        print(f"\nSample constraints (must = 0 for triviality):")
        count = 0
        for key, diff in list(constraints.items())[:5]:
            X, Y, Z = key
            print(f"  [gamma-cob]({X},{Y})_{Z}: {dict(diff)}")
            count += 1
    else:
        print("  No constraints on gb -> deformation is ALWAYS trivial for this f!")

    return comp, constraints


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

    all_results = {}
    for n in [1, 2, 3]:
        comp, constraints = run_full_analysis(n, data_dir)
        all_results[n] = {"comparison": comp, "constraints": constraints}

    print("\n" + "="*60)
    print("GENERAL CONJECTURE ON TRIVIALITY CONDITIONS")
    print("="*60)

    for n, results in all_results.items():
        constraints = results["constraints"]
        print(f"\nC({n+1}) = osp(2|{2*n}):")
        if len(constraints) == 0:
            print("  Deformation is ALWAYS trivial (coboundary = gamma for all gb).")
        else:
            # Identify the structure of constraints
            gb_in_constraints = set()
            for diff in constraints.values():
                gb_in_constraints.update(diff.keys())
            print(f"  {len(constraints)} non-trivial constraints involving gb params: {sorted(gb_in_constraints)}")
            # Check if constraints are all proportional to single gb params
            # (meaning individual gb values must satisfy linear equations)
            gb_ranks = {}
            for diff in constraints.values():
                for gb, coeff in diff.items():
                    if gb not in gb_ranks:
                        gb_ranks[gb] = 0
                    gb_ranks[gb] += 1
            print(f"  GB param constraint frequencies: {gb_ranks}")
