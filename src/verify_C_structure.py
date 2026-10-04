"""Verification script for C(n+1) structure constants.

Verifies:
1. Graded anti-symmetry: [Y, X} = -(-1)^(p(X)p(Y)) [X, Y} for all generator pairs.
2. Super Jacobi identity:
   (-1)^(p(X)p(Z)) [X, [Y, Z}} + (-1)^(p(Y)p(X)) [Y, [Z, X}} + (-1)^(p(Z)p(Y)) [Z, [X, Y}} = 0
   for all generator triples.
"""

import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import sys
import time


def verify_c_structure(n, json_path=None):
    if json_path is None:
        json_path = f"data/C_{n}_structure.json"

    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Structure JSON not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_gens = data["basis"]["odd"] + data["basis"]["even"]
    parities = data["parity"]
    num_gens = len(all_gens)

    # Build bracket table
    c_table = defaultdict(dict)
    for entry in data["structure_constants"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        c_table[(X, Y)][Z] = Fraction(entry["coeff"])

    # 1. Check anti-symmetry
    antisymmetry_failures = []
    total_pairs = 0
    for x in all_gens:
        for y in all_gens:
            total_pairs += 1
            px, py = parities[x], parities[y]
            sign = -1 if (px * py == 1) else 1
            d_xy = c_table.get((x, y), {})
            d_yx = c_table.get((y, x), {})

            all_targets = set(d_xy.keys()) | set(d_yx.keys())
            for z in all_targets:
                c_xy = d_xy.get(z, Fraction(0))
                c_yx = d_yx.get(z, Fraction(0))
                if c_yx != -sign * c_xy:
                    antisymmetry_failures.append({
                        "pair": (x, y),
                        "target": z,
                        "c_yx": str(c_yx),
                        "expected": str(-sign * c_xy),
                    })

    # 2. Check Super Jacobi identity
    # Helper to evaluate bracket of generator X with a linear combination
    def br_lin(x, comb):
        res = defaultdict(Fraction)
        for m, cm in comb.items():
            b = c_table.get((x, m), {})
            for w, cw in b.items():
                res[w] += cm * cw
        return {k: v for k, v in res.items() if v != 0}

    jacobi_failures = []
    total_triples = 0
    t0 = time.time()

    for x in all_gens:
        px = parities[x]
        for y in all_gens:
            py = parities[y]
            for z in all_gens:
                pz = parities[z]
                total_triples += 1

                # Koszul signs
                s1 = -1 if (px * pz % 2 == 1) else 1
                s2 = -1 if (py * px % 2 == 1) else 1
                s3 = -1 if (pz * py % 2 == 1) else 1

                # T1 = [X, [Y, Z}}
                t1 = br_lin(x, c_table.get((y, z), {}))
                # T2 = [Y, [Z, X}}
                t2 = br_lin(y, c_table.get((z, x), {}))
                # T3 = [Z, [X, Y}}
                t3 = br_lin(z, c_table.get((x, y), {}))

                tot = defaultdict(Fraction)
                for w, c in t1.items():
                    tot[w] += s1 * c
                for w, c in t2.items():
                    tot[w] += s2 * c
                for w, c in t3.items():
                    tot[w] += s3 * c

                bad = {w: c for w, c in tot.items() if c != 0}
                if bad:
                    jacobi_failures.append({
                        "triple": (x, y, z),
                        "residual": {w: str(c) for w, c in bad.items()},
                    })

    elapsed = time.time() - t0

    result = {
        "n": n,
        "algebra": data["algebra"]["cartan_type"],
        "num_generators": num_gens,
        "total_pairs_checked": total_pairs,
        "antisymmetry_failures": len(antisymmetry_failures),
        "total_triples_checked": total_triples,
        "jacobi_failures": len(jacobi_failures),
        "jacobi_time_seconds": elapsed,
        "status": "PASS" if (len(antisymmetry_failures) == 0 and len(jacobi_failures) == 0) else "FAIL",
    }
    return result, antisymmetry_failures, jacobi_failures


def main():
    all_passed = True
    print("=" * 70)
    print("Super Jacobi Identity & Anti-Symmetry Verification for C(n+1)")
    print("=" * 70)

    for n in [1, 2, 3]:
        res, asym_fails, jac_fails = verify_c_structure(n)
        print(f"\n--- Algebra: {res['algebra']} (n={n}, dim={res['num_generators']}) ---")
        print(f"  Pairs checked (anti-symmetry): {res['total_pairs_checked']} -> {res['antisymmetry_failures']} failures")
        print(f"  Triples checked (Super Jacobi): {res['total_triples_checked']} -> {res['jacobi_failures']} failures")
        print(f"  Execution time: {res['jacobi_time_seconds']:.3f} s")
        print(f"  Result: {res['status']}")

        if res["status"] != "PASS":
            all_passed = False
            if asym_fails:
                print(f"  First anti-symmetry failure: {asym_fails[0]}")
            if jac_fails:
                print(f"  First Jacobi failure: {jac_fails[0]}")

    print("\n" + "=" * 70)
    if all_passed:
        print("OVERALL RESULT: ALL CHECKS PASSED SUCCESSFULLY (3/3)")
        print("=" * 70)
        sys.exit(0)
    else:
        print("OVERALL RESULT: VERIFICATION FAILED")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
