"""
C_triviality_analysis.py — Triviality condition analysis for C(n+1).

Answers: under what conditions on gb is the inhomogeneous deformation trivial?

Method:
  1. Build coboundary operator M (reusing C_coboundary.py)
  2. Load the symbolic gamma decomposition γ(gb) = Σ_k gb_k * γ_k from Schema 2
  3. Compute D = dim(proj_{coker(M)} span{γ_k}) = rank([M|γ_1|...|γ_K]) - rank(M)
  4. Test each individual γ_k for triviality
  5. Find the constraint(s) on gb for triviality via pairwise cancellation tests
  6. Identify the obstruction witness rows
"""

import json
import sys
import os
from fractions import Fraction
from typing import Dict, Tuple, List, Optional

sys.path.insert(0, "src")
from C_coboundary import build_system, gauss_rref


# ---------------------------------------------------------------------------
# Load symbolic gamma (each entry has exactly one gb label)
# ---------------------------------------------------------------------------

def load_gamma_symbolic(n: int) -> Dict[str, Dict[Tuple, Fraction]]:
    """
    Load gamma from Schema 2 as: {gb_label: {(X,Y,Z): coeff}}.
    Each γ entry belongs to exactly one gb parameter.
    """
    with open(f"data/C_{n}_gamma.json") as fh:
        d = json.load(fh)
    gm = d["inhomogeneous_deformation"]["gamma_matrix"]
    gb_labels = sorted(set(k for e in gm for k in e["coeff"]))

    result = {label: {} for label in gb_labels}
    for entry in gm:
        key = (entry["X"], entry["Y"], entry["Z"])
        for label, val in entry["coeff"].items():
            result[label][key] = Fraction(val)
    return result


def evaluate_gamma(gamma_sym: Dict[str, Dict], gb: Dict[str, int]) -> Dict[Tuple, Fraction]:
    """Evaluate γ(gb) = Σ_k gb_k * γ_k."""
    result = {}
    for label, gb_val in gb.items():
        if gb_val == 0:
            continue
        for key, coeff in gamma_sym.get(label, {}).items():
            v = Fraction(gb_val) * coeff
            result[key] = result.get(key, Fraction(0)) + v
    return {k: v for k, v in result.items() if v != 0}


# ---------------------------------------------------------------------------
# Rank test (fast, no solution extraction)
# ---------------------------------------------------------------------------

def rank_test_quick(row_dict, n_cols, gamma_vec):
    """Return (rank_M, rank_aug)."""
    RHS = n_cols
    all_keys = set(row_dict.keys()) | set(gamma_vec.keys())
    rows = []
    for key in all_keys:
        row = dict(row_dict.get(key, {}))
        rhs = gamma_vec.get(key, Fraction(0))
        if rhs != 0:
            row[RHS] = rhs
        if row:
            rows.append(row)
    if not rows:
        return 0, 0
    _, pivot_cols = gauss_rref(rows, n_cols)
    return (sum(1 for c in pivot_cols if c < n_cols), len(pivot_cols))


# ---------------------------------------------------------------------------
# Multi-column rank extension
# ---------------------------------------------------------------------------

def rank_test_multi_gamma(row_dict, n_cols, gamma_vecs: List[Dict[Tuple, Fraction]]):
    """
    Compute rank([M | γ_1 | γ_2 | ... | γ_K]).
    gamma_vecs: list of γ_k dicts (one per gb label).
    Returns (rank_M, rank_augmented_with_all_gammas).
    """
    K = len(gamma_vecs)
    # Columns: 0..n_cols-1 = M, n_cols..n_cols+K-1 = γ_k cols
    all_keys = set(row_dict.keys())
    for gv in gamma_vecs:
        all_keys |= set(gv.keys())

    rows = []
    for key in all_keys:
        row = dict(row_dict.get(key, {}))
        for k, gv in enumerate(gamma_vecs):
            v = gv.get(key, Fraction(0))
            if v != 0:
                row[n_cols + k] = v
        if row:
            rows.append(row)

    if not rows:
        return 0, 0

    # RREF treating all n_cols + K columns
    _, pivot_cols = gauss_rref(rows, n_cols + K)
    rank_M = sum(1 for c in pivot_cols if c < n_cols)
    rank_aug = len(pivot_cols)
    return rank_M, rank_aug


# ---------------------------------------------------------------------------
# Find obstruction witnesses: (X,Y,Z) rows causing inconsistency
# ---------------------------------------------------------------------------

def find_obstruction_witnesses(row_dict, n_cols, gamma_vec, max_witnesses=5):
    """
    Find (X,Y,Z) triples that witness the non-triviality.

    Strategy: after RREF of [M|γ], the "extra pivot" row (at col n_cols) gives
    a linear combination of original rows zeroing all M-columns. The original
    rows with non-zero coefficients in this combination are the witnesses.

    We approximate by finding rows (X,Y,Z) where:
    - γ[(X,Y,Z)] is large (highest contribution to obstruction)
    - M row [(X,Y,Z)] is NOT in the span of other M rows with γ entries
    """
    # Identify rows that participate in gamma but might reveal the obstruction:
    # these are kappa entries of γ that lie "outside" the column space of M.
    # Heuristic: try to solve the restricted system on γ-rows only and find residuals.
    RHS = n_cols
    gamma_keys = sorted(gamma_vec.keys(), key=lambda k: abs(gamma_vec[k]), reverse=True)

    # Take the top entries and check which combination forms the obstruction
    # For reporting: show the (X,Y) pairs with largest γ coefficient
    witnesses = []
    for key in gamma_keys[:max_witnesses]:
        X, Y, Z = key
        coeff = gamma_vec[key]
        m_row = row_dict.get(key, {})
        witnesses.append({
            "X": X, "Y": Y, "Z": Z,
            "gamma_coeff": str(coeff),
            "m_row_nonzero_count": len(m_row),
        })
    return witnesses


# ---------------------------------------------------------------------------
# Main analysis per n
# ---------------------------------------------------------------------------

def analyze_n(n: int) -> dict:
    print(f"\n{'='*65}")
    print(f"  C({n+1}) = osp(2|{2*n}),  n={n}")
    print(f"{'='*65}")

    row_dict, f_params, n_cols, _ = build_system(n)
    gamma_sym = load_gamma_symbolic(n)
    gb_labels = sorted(gamma_sym.keys())
    K = len(gb_labels)

    print(f"  M: {len(row_dict)} rows × {n_cols} cols")
    print(f"  gb parameters ({K}): {gb_labels}")

    # ------------------------------------------------------------------
    # 1. Baseline: gb0 (all zero) → trivially trivial
    # ------------------------------------------------------------------
    gamma_zero = evaluate_gamma(gamma_sym, {})
    rM0, rA0 = rank_test_quick(row_dict, n_cols, gamma_zero)
    print(f"\n  [1] gb=0 (trivially zero): rank_M={rM0}, rank_aug={rA0}  → "
          f"{'TRIVIAL ✓' if rM0==rA0 else 'NON-TRIVIAL ✗'}")

    # ------------------------------------------------------------------
    # 2. gb1 (all ones) → non-trivial (from I07-1)
    # ------------------------------------------------------------------
    gamma_gb1 = evaluate_gamma(gamma_sym, {k: 1 for k in gb_labels})
    rM1, rA1 = rank_test_quick(row_dict, n_cols, gamma_gb1)
    print(f"  [2] gb=1 (all ones): rank_M={rM1}, rank_aug={rA1}  → "
          f"{'TRIVIAL' if rM1==rA1 else f'NON-TRIVIAL (gap={rA1-rM1})'}")

    # ------------------------------------------------------------------
    # 3. Dimension D of cokernel projection
    # ------------------------------------------------------------------
    gamma_vecs = [gamma_sym[k] for k in gb_labels]
    rM_all, rA_all = rank_test_multi_gamma(row_dict, n_cols, gamma_vecs)
    D = rA_all - rM_all
    print(f"\n  [3] rank([M|γ_1|...|γ_{K}]) = {rA_all}  (rank_M={rM_all})")
    print(f"      → D = {D} independent non-trivial direction(s) in cokernel")
    print(f"      → Trivial subspace dimension = {K} - {D} = {K - D}")

    # ------------------------------------------------------------------
    # 4. Individual γ_k tests
    # ------------------------------------------------------------------
    print(f"\n  [4] Individual γ_k tests:")
    individual = {}
    for label in gb_labels:
        gamma_k = gamma_sym[label]
        rM_k, rA_k = rank_test_quick(row_dict, n_cols, gamma_k)
        trivial = (rM_k == rA_k)
        individual[label] = trivial
        status = "TRIVIAL ✓" if trivial else f"NON-TRIVIAL (gap={rA_k-rM_k})"
        print(f"    {label:30s}: {status}")

    # ------------------------------------------------------------------
    # 5. Pairwise cancellation tests (for n=1 fully, others summarized)
    # ------------------------------------------------------------------
    print(f"\n  [5] Pairwise cancellation tests (gb_i=1, gb_j=-1):")
    trivial_pairs = []
    nontrivial_count = 0
    for i, gi in enumerate(gb_labels):
        for j, gj in enumerate(gb_labels):
            if i >= j:
                continue
            gamma_diff = evaluate_gamma(gamma_sym, {gi: 1, gj: -1})
            if not gamma_diff:
                trivial_pairs.append((gi, gj, "zero γ"))
                print(f"    {gi} − {gj}: γ=0 → TRIVIAL ✓")
                continue
            rM_p, rA_p = rank_test_quick(row_dict, n_cols, gamma_diff)
            if rM_p == rA_p:
                trivial_pairs.append((gi, gj, "coboundary"))
                print(f"    {gi} − {gj}: TRIVIAL ✓  (γ ∈ col(M))")
            else:
                nontrivial_count += 1
                if n == 1 or nontrivial_count <= 4:
                    print(f"    {gi} − {gj}: NON-TRIVIAL (gap={rA_p-rM_p})")
    if nontrivial_count > 4 and n > 1:
        print(f"    ... ({nontrivial_count} total non-trivial pairs)")

    # ------------------------------------------------------------------
    # 6. Identify the constraint(s) on gb
    # ------------------------------------------------------------------
    print(f"\n  [6] Triviality constraint analysis:")
    if D == 0:
        print("    All γ_k ∈ col(M) → EVERY deformation is trivial!")
        constraint_summary = "all deformations trivial"
    elif D >= K:
        print("    All γ_k independently non-trivial, no non-zero gb is trivial.")
        print("    Only gb=0 gives a trivial deformation.")
        constraint_summary = "only gb=0 is trivial"
    else:
        # D < K: there are trivial combinations
        non_trivial_k = [k for k in gb_labels if not individual[k]]
        trivial_k = [k for k in gb_labels if individual[k]]
        print(f"    Trivial single-parameter directions: {trivial_k if trivial_k else 'none'}")
        print(f"    Non-trivial single-parameter directions: {non_trivial_k}")
        constraint_summary = f"D={D} constraints on {K} gb params"

    # ------------------------------------------------------------------
    # 7. Obstruction witnesses
    # ------------------------------------------------------------------
    print(f"\n  [7] Top obstruction witness entries (largest |γ| in gb1):")
    witnesses = find_obstruction_witnesses(row_dict, n_cols, gamma_gb1)
    for w in witnesses:
        print(f"    ({w['X']}, {w['Y']}) → {w['Z']}: γ={w['gamma_coeff']}  "
              f"(M row has {w['m_row_nonzero_count']} nonzero cols)")

    return {
        "n": n, "algebra": f"C({n+1}) = osp(2|{2*n})",
        "K": K, "rank_M": rM1, "D": D,
        "trivial_subspace_dim": K - D,
        "individual": individual,
        "trivial_pairs": trivial_pairs,
        "constraint_summary": constraint_summary,
        "witnesses": witnesses,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("C_triviality_analysis.py — Triviality condition analysis for C(n+1)")

    all_results = {}
    for n in (1, 2, 3):
        all_results[n] = analyze_n(n)

    print("\n\n" + "=" * 65)
    print("SUMMARY: Triviality analysis across C(n+1)")
    print("=" * 65)
    header = f"{'Algebra':28s} {'K':>4} {'D':>4} {'Trivial dim':>12} {'Constraint'}"
    print(header)
    print("-" * 65)
    for n, r in all_results.items():
        print(f"  {r['algebra']:28s} {r['K']:>4}   {r['D']:>2}   {r['trivial_subspace_dim']:>10}   {r['constraint_summary']}")
    print("=" * 65)

    print("\n\nCONJECTURE: General triviality condition for C(n+1)")
    print("-" * 65)
    # Look for pattern in D vs n
    Ds = [all_results[n]["D"] for n in [1,2,3]]
    Ks = [all_results[n]["K"] for n in [1,2,3]]
    print(f"  n=1: D={Ds[0]}/{Ks[0]},  n=2: D={Ds[1]}/{Ks[1]},  n=3: D={Ds[2]}/{Ks[2]}")
    if all(D == 1 for D in Ds):
        print("\n  FINDING: D=1 for all n. There is EXACTLY ONE independent non-trivial")
        print("  direction in the cokernel of δ for all C(n+1).")
        print("\n  CONJECTURE: The inhomogeneous deformation of C(n+1) is a coboundary")
        print("  if and only if the deformation vector γ(gb) lies in the (K-1)-dimensional")
        print("  hyperplane defined by: Σ_k c_k * gb_k = 0,  where c_k = v* · γ_k")
        print("  for the unique cokernel direction v* of the coboundary operator δ.")
        print("\n  For the gb1 profile (all gb_k=1): γ is NON-TRIVIAL for all n,")
        print("  demonstrating that the SPECIFIC constraint Σ_k c_k ≠ 0.")
    elif all(all_results[n]["D"] == all_results[n]["K"] for n in [1, 2, 3]):
        print("\n  FINDING: D=K for all n. NO non-zero gb profile gives trivial deformation.")
        print("  CONJECTURE: The ONLY trivial deformation is the undeformed algebra (gb=0).")


if __name__ == "__main__":
    main()
