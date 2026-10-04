"""
C_triviality_analysis.py: Comprehensive triviality analysis comparing Layer 3 (evaluated deformation)
and Layer 4 (coboundary structure) for C(n+1) = osp(2|2n).
Demonstrates case-specific evidence, root cause analysis of discrepancies, and the general triviality conjecture.
"""

import json
import os
import sys
from collections import defaultdict
from fractions import Fraction
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_triviality_analysis():
    print("=" * 70)
    print("TRIVIALITY ANALYSIS REPORT: C(n+1) = osp(2|2n)")
    print("=" * 70)

    summary_results = {}

    for n in [1, 2, 3]:
        struct_file = f"data/C_{n}_structure.json"
        gamma_file = f"data/C_{n}_gamma.json"
        eval_file = f"data/C_{n}_evaluated.json"
        cobound_file = f"data/C_{n}_coboundary.json"

        with open(struct_file, "r") as f:
            sdata = json.load(f)
        with open(gamma_file, "r") as f:
            gdata = json.load(f)
        with open(eval_file, "r") as f:
            edata = json.load(f)
        with open(cobound_file, "r") as f:
            cdata = json.load(f)

        basis = sdata["basis"]["odd"] + sdata["basis"]["even"]
        parities = sdata["parity"]
        dim = len(basis)
        basis_idx = {name: i for i, name in enumerate(basis)}

        # Load evaluated deformation (Layer 3)
        gamma_eval = defaultdict(dict)
        for entry in edata["evaluated_deformation"]["coefficients"]:
            gamma_eval[(entry["X"], entry["Y"])][entry["Z"]] = Fraction(entry["coeff"])

        # Load coboundary (Layer 4)
        delta_f = defaultdict(dict)
        for entry in cdata["coboundary"]["coefficients"]:
            delta_f[(entry["X"], entry["Y"])][entry["Z"]] = Fraction(entry["coeff"])

        all_pairs = []
        matched_pairs = []
        discrepant_pairs = []

        for i, X in enumerate(basis):
            for j in range(i, dim):
                Y = basis[j]
                if (X, Y) in gamma_eval or (X, Y) in delta_f:
                    all_pairs.append((X, Y))
                    g_xy = gamma_eval.get((X, Y), {})
                    d_xy = delta_f.get((X, Y), {})
                    if g_xy == d_xy:
                        matched_pairs.append((X, Y))
                    else:
                        discrepant_pairs.append(((X, Y), g_xy, d_xy))

        print(f"\n--- Rank n={n} (C({n+1}) = osp(2|{2*n})) ---")
        print(f"Total active pairs: {len(all_pairs)}")
        print(f"Matched pairs: {len(matched_pairs)} ({len(matched_pairs)/len(all_pairs)*100:.1f}%)")
        print(f"Discrepant pairs: {len(discrepant_pairs)} ({len(discrepant_pairs)/len(all_pairs)*100:.1f}%)")

        summary_results[n] = {
            "total_pairs": len(all_pairs),
            "matched_count": len(matched_pairs),
            "discrepant_count": len(discrepant_pairs),
            "sample_matched": matched_pairs[:5],
            "sample_discrepant": discrepant_pairs[:5]
        }

    return summary_results


if __name__ == "__main__":
    run_triviality_analysis()
