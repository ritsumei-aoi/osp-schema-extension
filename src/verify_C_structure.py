"""
verify_C_structure.py: Verifies graded anti-symmetry and Super Jacobi identity
for C(n+1) = osp(2|2n) structure constants (n=1, 2, 3) loaded directly from Schema 1 JSONs.
"""

import json
import os
import sys
import time
from collections import defaultdict
from fractions import Fraction
from typing import Dict, Tuple, Any


def load_structure_data(filepath: str) -> Tuple[Dict[str, int], Dict[Tuple[str, str], Dict[str, Fraction]], list]:
    with open(filepath, "r") as f:
        data = json.load(f)

    basis = data["basis"]["odd"] + data["basis"]["even"]
    parities = data["parity"]

    brackets = defaultdict(lambda: defaultdict(Fraction))
    for entry in data["structure_constants"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        c_str = entry["coeff"]
        c = Fraction(c_str)
        brackets[(X, Y)][Z] = c

    return parities, brackets, basis


def verify_algebra(n: int, filepath: str) -> Dict[str, Any]:
    start_time = time.time()
    parities, brackets, basis = load_structure_data(filepath)
    dim = len(basis)

    # 1. Graded anti-symmetry
    pairs_checked = 0
    antisymmetry_failures = []

    for X in basis:
        for Y in basis:
            pairs_checked += 1
            pX, pY = parities[X], parities[Y]
            expected_sign = - ((-1)**(pX * pY))

            xy_terms = brackets.get((X, Y), {})
            yx_terms = brackets.get((Y, X), {})

            all_Z = set(xy_terms.keys()) | set(yx_terms.keys())
            for Z in all_Z:
                c_xy = xy_terms.get(Z, Fraction(0))
                c_yx = yx_terms.get(Z, Fraction(0))
                if c_yx != expected_sign * c_xy:
                    antisymmetry_failures.append({
                        "X": X, "Y": Y, "Z": Z,
                        "c_xy": str(c_xy), "c_yx": str(c_yx),
                        "expected_sign": expected_sign
                    })

    # 2. Super Jacobi identity
    # (-1)^{p(X)p(Z)} [X, [Y, Z}] + (-1)^{p(Y)p(X)} [Y, [Z, X}] + (-1)^{p(Z)p(Y)} [Z, [X, Y}] = 0
    triples_checked = 0
    jacobi_failures = []

    for X in basis:
        pX = parities[X]
        for Y in basis:
            pY = parities[Y]
            for Z in basis:
                pZ = parities[Z]
                triples_checked += 1

                # Term 1: (-1)^{pX pZ} [X, [Y, Z}]
                s1 = (-1)**(pX * pZ)
                t1 = defaultdict(Fraction)
                for W, c_yz in brackets.get((Y, Z), {}).items():
                    for U, c_xw in brackets.get((X, W), {}).items():
                        t1[U] += c_yz * c_xw

                # Term 2: (-1)^{pY pX} [Y, [Z, X}]
                s2 = (-1)**(pY * pX)
                t2 = defaultdict(Fraction)
                for W, c_zx in brackets.get((Z, X), {}).items():
                    for U, c_yw in brackets.get((Y, W), {}).items():
                        t2[U] += c_zx * c_yw

                # Term 3: (-1)^{pZ pY} [Z, [X, Y}]
                s3 = (-1)**(pZ * pY)
                t3 = defaultdict(Fraction)
                for W, c_xy in brackets.get((X, Y), {}).items():
                    for U, c_zw in brackets.get((Z, W), {}).items():
                        t3[U] += c_xy * c_zw

                all_U = set(t1.keys()) | set(t2.keys()) | set(t3.keys())
                for U in all_U:
                    tot = s1 * t1[U] + s2 * t2[U] + s3 * t3[U]
                    if tot != 0:
                        jacobi_failures.append({
                            "triple": (X, Y, Z),
                            "target": U,
                            "residual": str(tot)
                        })

    elapsed = time.time() - start_time
    passed = (len(antisymmetry_failures) == 0 and len(jacobi_failures) == 0)

    report = {
        "n": n,
        "dimension": dim,
        "pairs_checked": pairs_checked,
        "antisymmetry_failures_count": len(antisymmetry_failures),
        "triples_checked": triples_checked,
        "jacobi_failures_count": len(jacobi_failures),
        "passed": passed,
        "elapsed_seconds": round(elapsed, 3),
        "sample_antisymmetry_failures": antisymmetry_failures[:5],
        "sample_jacobi_failures": jacobi_failures[:5]
    }
    return report


def main():
    print("=" * 60)
    print("Verification of C(n+1) Structure Constants (n=1, 2, 3)")
    print("=" * 60)

    all_passed = True
    for n in [1, 2, 3]:
        filepath = f"data/C_{n}_structure.json"
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            sys.exit(1)

        report = verify_algebra(n, filepath)
        status = "PASSED" if report["passed"] else "FAILED"
        print(f"\n[n={n} | C({n+1}) = osp(2|{2*n})] Dimension = {report['dimension']}")
        print(f"  Anti-symmetry: {report['pairs_checked']} pairs checked -> {report['antisymmetry_failures_count']} failures")
        print(f"  Super Jacobi:  {report['triples_checked']} triples checked -> {report['jacobi_failures_count']} failures")
        print(f"  Result: {status} (time: {report['elapsed_seconds']}s)")

        if not report["passed"]:
            all_passed = False
            if report["sample_antisymmetry_failures"]:
                print(f"  Sample anti-symmetry failures: {report['sample_antisymmetry_failures']}")
            if report["sample_jacobi_failures"]:
                print(f"  Sample Jacobi failures: {report['sample_jacobi_failures']}")

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL CHECKS PASSED: Structure constants satisfy anti-symmetry and Super Jacobi.")
    else:
        print("VERIFICATION FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
