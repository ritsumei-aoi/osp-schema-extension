"""I08: Triviality condition search for the inhomogeneous deformation of C(n+1).

Compares Layer 3 (evaluated gamma) with Layer 4 (coboundary of the canonical
odd map f) and determines for which gb assignments the deformation is trivial.

Strategy: gamma and delta-f are both linear in the 4n gb parameters, so exact
agreement on every unit assignment (one gb = 1, the rest 0) proves
gamma = delta f identically in gb. Random rational assignments are added as
an independent cross-check. The K-component question (f: g -> g strictly,
vs f: g -> g + C·K) is analyzed separately.

Usage: python3 src/compare_triviality.py
"""

import itertools
import json
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_generators import DATA_DIR
from C_gamma import gb_labels
from C_evaluate import evaluate_gamma
from C_coboundary import compute_coboundary


def as_table(records):
    out = {}
    for r in records:
        out[(r["X"], r["Y"], r["Z"])] = Fraction(r["coeff"])
    return out


def compare(n, assignment, drop_K=False):
    """Return dict of mismatches {(X,Y,Z): (gamma, delta_f)}."""
    g = as_table(evaluate_gamma(n, assignment))
    _, cb = compute_coboundary(n, assignment)
    d = as_table(cb)
    if drop_K:
        g = {k: v for k, v in g.items() if k[2] != "K"}
        d = {k: v for k, v in d.items() if k[2] != "K"}
    keys = set(g) | set(d)
    return {k: (g.get(k, Fraction(0)), d.get(k, Fraction(0)))
            for k in keys if g.get(k, Fraction(0)) != d.get(k, Fraction(0))}


def main():
    rng = random.Random(20261010)
    all_ok = True
    for n in (1, 2, 3):
        labels = gb_labels(n)
        print(f"=== C({n + 1})  [n={n}, {len(labels)} gb parameters] ===")

        # 1. stored all-ones files (Layer 3 vs Layer 4 as committed)
        with open(os.path.join(DATA_DIR, f"C_{n}_evaluated.json")) as f:
            ev = as_table(json.load(f)["evaluated_gamma"])
        with open(os.path.join(DATA_DIR, f"C_{n}_coboundary.json")) as f:
            cb = as_table(json.load(f)["coboundary"])
        mism = {k for k in set(ev) | set(cb) if ev.get(k) != cb.get(k)}
        print(f"  stored files (gb=all+1): {len(ev)} gamma vs {len(cb)} "
              f"coboundary records, {len(mism)} mismatches")
        all_ok &= not mism

        # 2. unit assignments: linearity => identity in gb if all pass
        unit_fail = 0
        for lbl in labels:
            assignment = {l: Fraction(1 if l == lbl else 0) for l in labels}
            mm = compare(n, assignment)
            if mm:
                unit_fail += 1
                print(f"  UNIT FAIL {lbl}: {list(mm.items())[:3]}")
        print(f"  unit assignments: {len(labels)} tested, {unit_fail} failures")
        all_ok &= unit_fail == 0

        # 3. random rational assignments
        rand_fail = 0
        for _ in range(3):
            assignment = {
                l: Fraction(rng.randint(-9, 9), rng.randint(1, 5)) for l in labels
            }
            if compare(n, assignment):
                rand_fail += 1
        print(f"  random assignments: 3 tested, {rand_fail} failures")
        all_ok &= rand_fail == 0

        # 4. K-component analysis: gamma modulo center vs strict f: g -> g
        assignment = {l: Fraction(1) for l in labels}
        g = as_table(evaluate_gamma(n, assignment))
        k_terms = {k: v for k, v in g.items() if k[2] == "K"}
        mm_modK = compare(n, assignment, drop_K=True)
        print(f"  gamma K-components (gb=all+1): {len(k_terms)} "
              f"(pairs with scalar part)")
        print(f"  comparison modulo center K: {len(mm_modK)} mismatches")
        all_ok &= not mm_modK
    print("CONCLUSION:",
          "gamma == delta f identically in gb for n=1,2,3 -> deformation "
          "TRIVIAL for ALL gb" if all_ok else "DISCREPANCIES FOUND")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
