"""
Verification script for C(n+1) structure constants.

Verifies:
1. Graded anti-symmetry (skew-supersymmetry):
   [Y, X} = -(-1)^{p(X)p(Y)} [X, Y} for all generator pairs (X, Y).
2. Parity grading preservation:
   If [X, Y} contains Z, then p(Z) = (p(X) + p(Y)) mod 2.
3. Super Jacobi identity:
   (-1)^{p(X)p(Z)} [X, [Y, Z}} + (-1)^{p(Y)p(X)} [Y, [Z, X}} + (-1)^{p(Z)p(Y)} [Z, [X, Y}} = 0
   for all generator triples (X, Y, Z).
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys
import time
from typing import Dict, List, Tuple, Any


def load_schema(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_c_structure(n: int, filepath: str) -> Dict[str, Any]:
    data = load_schema(filepath)
    even_basis = data["basis"]["even"]
    odd_basis = data["basis"]["odd"]
    full_basis = even_basis + odd_basis
    parity = data["parity"]
    sc_list = data["structure_constants"]

    dim = len(full_basis)
    expected_dim = 2 * n**2 + 5 * n + 1
    assert dim == expected_dim, f"Dimension mismatch: got {dim}, expected {expected_dim}"

    # Build bracket table: (X, Y) -> {Z: Fraction}
    bracket_table = defaultdict(dict)
    for sc in sc_list:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        bracket_table[(X, Y)][Z] = coeff

    # 1. Parity grading check
    parity_errors = []
    for (X, Y), res in bracket_table.items():
        pX, pY = parity[X], parity[Y]
        expected_pZ = (pX + pY) % 2
        for Z, coeff in res.items():
            pZ = parity[Z]
            if pZ != expected_pZ:
                parity_errors.append((X, Y, Z, coeff, pX, pY, pZ))

    # 2. Skew-supersymmetry check for all pairs
    skew_errors = []
    pair_count = 0
    for i, X in enumerate(full_basis):
        pX = parity[X]
        for j, Y in enumerate(full_basis):
            pair_count += 1
            pY = parity[Y]
            sign = -1 if (pX * pY) % 2 == 1 else 1

            # [X, Y}
            xy = bracket_table.get((X, Y), {})
            # [Y, X}
            yx = bracket_table.get((Y, X), {})

            # Must satisfy yx == -sign * xy
            all_Z = set(xy.keys()) | set(yx.keys())
            for Z in all_Z:
                c_xy = xy.get(Z, Fraction(0))
                c_yx = yx.get(Z, Fraction(0))
                expected_c_yx = -sign * c_xy
                if c_yx != expected_c_yx:
                    skew_errors.append((X, Y, Z, c_xy, c_yx, expected_c_yx))

    # 3. Super Jacobi identity check for all triples
    # (-1)^{p(X)p(Z)} [X, [Y, Z}} + (-1)^{p(Y)p(X)} [Y, [Z, X}} + (-1)^{p(Z)p(Y)} [Z, [X, Y}} = 0
    jacobi_errors = []
    triple_count = 0
    t0 = time.time()

    for i, X in enumerate(full_basis):
        pX = parity[X]
        for j, Y in enumerate(full_basis):
            pY = parity[Y]
            s_XY = -1 if (pX * pY) % 2 == 1 else 1
            xy_res = bracket_table.get((X, Y), {})

            for k, Z in enumerate(full_basis):
                pZ = parity[Z]
                triple_count += 1

                s_XZ = -1 if (pX * pZ) % 2 == 1 else 1
                s_YX = s_XY
                s_ZY = -1 if (pZ * pY) % 2 == 1 else 1

                # Term 1: (-1)^{pX pZ} [X, [Y, Z}}
                term1 = defaultdict(Fraction)
                yz_res = bracket_table.get((Y, Z), {})
                for mid, c_yz in yz_res.items():
                    for fin, c_xmid in bracket_table.get((X, mid), {}).items():
                        term1[fin] += c_yz * c_xmid

                # Term 2: (-1)^{pY pX} [Y, [Z, X}}
                term2 = defaultdict(Fraction)
                zx_res = bracket_table.get((Z, X), {})
                for mid, c_zx in zx_res.items():
                    for fin, c_ymid in bracket_table.get((Y, mid), {}).items():
                        term2[fin] += c_zx * c_ymid

                # Term 3: (-1)^{pZ pY} [Z, [X, Y}}
                term3 = defaultdict(Fraction)
                for mid, c_xy in xy_res.items():
                    for fin, c_zmid in bracket_table.get((Z, mid), {}).items():
                        term3[fin] += c_xy * c_zmid

                all_fin = set(term1.keys()) | set(term2.keys()) | set(term3.keys())
                for fin in all_fin:
                    val = s_XZ * term1[fin] + s_YX * term2[fin] + s_ZY * term3[fin]
                    if val != 0:
                        jacobi_errors.append((X, Y, Z, fin, val))
                        if len(jacobi_errors) > 20:
                            break
                if len(jacobi_errors) > 20:
                    break
            if len(jacobi_errors) > 20:
                break
        if len(jacobi_errors) > 20:
            break

    elapsed = time.time() - t0

    return {
        "n": n,
        "dim": dim,
        "pair_count": pair_count,
        "triple_count": triple_count,
        "non_zero_brackets": len(sc_list),
        "parity_ok": len(parity_errors) == 0,
        "parity_errors": parity_errors,
        "skew_ok": len(skew_errors) == 0,
        "skew_errors": skew_errors,
        "jacobi_ok": len(jacobi_errors) == 0,
        "jacobi_errors": jacobi_errors,
        "elapsed_sec": elapsed,
    }


def main():
    results = []
    all_ok = True
    for n in (1, 2, 3):
        filepath = f"data/C_{n}_structure.json"
        print(f"Verifying {filepath} (n={n})...")
        res = verify_c_structure(n, filepath)
        results.append(res)
        status = "PASSED" if (res["parity_ok"] and res["skew_ok"] and res["jacobi_ok"]) else "FAILED"
        print(f"  Result: {status} (Triples: {res['triple_count']}, Time: {res['elapsed_sec']:.2f}s)")
        if status == "FAILED":
            all_ok = False
            print(f"  Parity errors: {len(res['parity_errors'])}")
            print(f"  Skew errors: {len(res['skew_errors'])}")
            print(f"  Jacobi errors: {len(res['jacobi_errors'])}")

    print(f"\nOverall Verification: {'ALL PASSED' if all_ok else 'FAILED'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
