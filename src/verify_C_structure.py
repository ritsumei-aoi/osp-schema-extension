"""
verify_C_structure.py: Independent verification script for C(n+1) structure constants.
Verifies graded anti-symmetry and the Super Jacobi identity from data/C_{n}_structure.json.
"""

import json
import os
import sys
import time
from fractions import Fraction
from collections import defaultdict


def load_structure_data(n, data_dir="data"):
    filepath = os.path.join(data_dir, f"C_{n}_structure.json")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Structure file {filepath} not found.")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_c_structure(n, data_dir="data"):
    data = load_structure_data(n, data_dir)
    algebra_info = data["algebra"]
    even_basis = data["basis"]["even"]
    odd_basis = data["basis"]["odd"]
    full_basis = odd_basis + even_basis
    parity = data["parity"]
    struct_consts_list = data["structure_constants"]

    dim = len(full_basis)
    print(f"\n=======================================================")
    print(f"Verifying {algebra_info['cartan_type']} = {algebra_info['alternative_notation']['osp']} (n={n})")
    print(f"Dimension: {dim} ({len(even_basis)} even, {len(odd_basis)} odd)")
    print(f"Total non-zero structure constant triples: {len(struct_consts_list)}")
    print(f"=======================================================")

    # Build bracket table: (X, Y) -> dict of {Z: Fraction}
    bracket_map = defaultdict(dict)
    for entry in struct_consts_list:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        val = Fraction(entry["coeff"])
        bracket_map[(X, Y)][Z] = val

    # 1. Verify Graded Anti-Symmetry:
    # [Y, X} = -(-1)^{p(X) p(Y)} [X, Y}
    start_time = time.time()
    antisymm_failures = []
    total_pairs = dim * dim

    for X in full_basis:
        for Y in full_basis:
            pX = parity[X]
            pY = parity[Y]
            sign = -1 if (pX * pY) % 2 == 1 else 1

            br_XY = bracket_map.get((X, Y), {})
            br_YX = bracket_map.get((Y, X), {})

            # All targets in br_XY must be in br_YX with opposite/proper sign
            all_targets = set(br_XY.keys()) | set(br_YX.keys())
            for Z in all_targets:
                c_xy = br_XY.get(Z, Fraction(0))
                c_yx = br_YX.get(Z, Fraction(0))
                expected_yx = -sign * c_xy
                if c_yx != expected_yx:
                    antisymm_failures.append({
                        "pair": (X, Y),
                        "Z": Z,
                        "c_YX": str(c_yx),
                        "expected": str(expected_yx)
                    })

    antisymm_time = time.time() - start_time
    antisymm_pass = len(antisymm_failures) == 0

    print(f"[1] Graded Anti-symmetry check:")
    print(f"    Pairs checked: {total_pairs}")
    print(f"    Passed: {antisymm_pass} (Failures: {len(antisymm_failures)})")
    print(f"    Elapsed: {antisymm_time:.3f}s")

    # 2. Verify Super Jacobi Identity for ALL triples (X, Y, Z):
    # (-1)^{p(X) p(Z)} [X, [Y, Z}} + (-1)^{p(Y) p(X)} [Y, [Z, X}} + (-1)^{p(Z) p(Y)} [Z, [X, Y}} = 0
    start_time = time.time()
    total_triples = dim ** 3
    jacobi_failures = []
    non_trivial_triples = 0

    for X in full_basis:
        pX = parity[X]
        for Y in full_basis:
            pY = parity[Y]
            br_XY = bracket_map.get((X, Y), {})
            for Z in full_basis:
                pZ = parity[Z]
                br_YZ = bracket_map.get((Y, Z), {})
                br_ZX = bracket_map.get((Z, X), {})

                if not br_YZ and not br_ZX and not br_XY:
                    continue  # All double brackets are trivially 0

                non_trivial_triples += 1

                # Sum accumulator for J(X, Y, Z) in the basis: dict of {U: Fraction}
                jac_sum = defaultdict(Fraction)

                # Term 1: (-1)^{pX pZ} [X, [Y, Z}}
                sign1 = -1 if (pX * pZ) % 2 == 1 else 1
                for W, c_yz_w in br_YZ.items():
                    br_XW = bracket_map.get((X, W), {})
                    for U, c_xw_u in br_XW.items():
                        jac_sum[U] += sign1 * c_yz_w * c_xw_u

                # Term 2: (-1)^{pY pX} [Y, [Z, X}}
                sign2 = -1 if (pY * pX) % 2 == 1 else 1
                for W, c_zx_w in br_ZX.items():
                    br_YW = bracket_map.get((Y, W), {})
                    for U, c_yw_u in br_YW.items():
                        jac_sum[U] += sign2 * c_zx_w * c_yw_u

                # Term 3: (-1)^{pZ pY} [Z, [X, Y}}
                sign3 = -1 if (pZ * pY) % 2 == 1 else 1
                for W, c_xy_w in br_XY.items():
                    br_ZW = bracket_map.get((Z, W), {})
                    for U, c_zw_u in br_ZW.items():
                        jac_sum[U] += sign3 * c_xy_w * c_zw_u

                # Check if any component U is non-zero
                non_zeros = {U: val for U, val in jac_sum.items() if val != 0}
                if non_zeros:
                    jacobi_failures.append({
                        "triple": (X, Y, Z),
                        "residuals": {U: str(val) for U, val in non_zeros.items()}
                    })

    jacobi_time = time.time() - start_time
    jacobi_pass = len(jacobi_failures) == 0

    print(f"[2] Super Jacobi identity check:")
    print(f"    Total triples checked: {total_triples}")
    print(f"    Non-trivial triples: {non_trivial_triples}")
    print(f"    Passed: {jacobi_pass} (Failures: {len(jacobi_failures)})")
    print(f"    Elapsed: {jacobi_time:.3f}s")

    return {
        "n": n,
        "cartan_type": algebra_info["cartan_type"],
        "dimension": dim,
        "total_pairs": total_pairs,
        "antisymm_pass": antisymm_pass,
        "antisymm_failures": antisymm_failures,
        "total_triples": total_triples,
        "non_trivial_triples": non_trivial_triples,
        "jacobi_pass": jacobi_pass,
        "jacobi_failures": jacobi_failures
    }


def main():
    all_results = []
    overall_pass = True

    for n in [1, 2, 3]:
        res = verify_c_structure(n)
        all_results.append(res)
        if not (res["antisymm_pass"] and res["jacobi_pass"]):
            overall_pass = False

    print("\n" + "=" * 55)
    print("FINAL SUMMARY REPORT:")
    for res in all_results:
        status = "PASSED" if (res["antisymm_pass"] and res["jacobi_pass"]) else "FAILED"
        print(f"  {res['cartan_type']} (n={res['n']}): {status} "
              f"(Pairs: {res['total_pairs']}, Triples: {res['total_triples']})")
    print(f"OVERALL STATUS: {'ALL CHECKS PASSED' if overall_pass else 'FAILURES DETECTED'}")
    print("=" * 55)

    if not overall_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
