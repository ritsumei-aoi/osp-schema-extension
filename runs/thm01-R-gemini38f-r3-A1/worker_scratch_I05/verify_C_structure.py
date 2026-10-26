"""
Verification script for C(n+1) structure constants (Schema 1).
Validates graded skew-symmetry and Super-Jacobi identity for n=1, 2, 3.
"""

import json
import os
import sys
import time
from fractions import Fraction
from collections import defaultdict

def verify_structure(json_path: str):
    print(f"\n{'='*60}")
    print(f"Verifying: {json_path}")
    print(f"{'='*60}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    algebra = data["algebra"]
    n = algebra["n"]
    m = algebra["m"]
    cartan_type = algebra["cartan_type"]
    expected_even = 2 * n**2 + n + 1
    expected_odd = 4 * n
    expected_total = expected_even + expected_odd

    basis = data["basis"]
    even_basis = basis["even"]
    odd_basis = basis["odd"]
    all_basis = even_basis + odd_basis
    parity = data["parity"]

    print(f"Algebra: {cartan_type} (m={m}, n={n})")
    print(f"Dimension check: even={len(even_basis)} (expected {expected_even}), odd={len(odd_basis)} (expected {expected_odd}), total={len(all_basis)} (expected {expected_total})")
    assert len(even_basis) == expected_even, f"Even dimension mismatch: {len(even_basis)} != {expected_even}"
    assert len(odd_basis) == expected_odd, f"Odd dimension mismatch: {len(odd_basis)} != {expected_odd}"
    assert len(all_basis) == expected_total, f"Total dimension mismatch: {len(all_basis)} != {expected_total}"

    # Parity map verification
    for g in even_basis:
        assert parity[g] == 0, f"Generator {g} expected even parity (0), got {parity[g]}"
    for g in odd_basis:
        assert parity[g] == 1, f"Generator {g} expected odd parity (1), got {parity[g]}"

    brackets = data["structure_constants"]
    print(f"Non-zero structure constants: {len(brackets)}")

    # Build tensor map: (X, Y) -> {Z: Fraction(coeff)}
    tensor = defaultdict(dict)
    for entry in brackets:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        c = Fraction(entry["coeff"])
        tensor[(X, Y)][Z] = c

    # 1. Graded anti-symmetry / skew-symmetry:
    # [Y, X} = -(-1)^{p(X)p(Y)} [X, Y}
    skew_errors = []
    pairs_checked = 0
    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            pairs_checked += 1
            s = -Fraction(1, 1) if (pX * pY) % 2 == 1 else Fraction(1, 1)
            b_XY = tensor.get((X, Y), {})
            b_YX = tensor.get((Y, X), {})
            all_Z = set(b_XY.keys()) | set(b_YX.keys())
            for Z in all_Z:
                c_YX = b_YX.get(Z, Fraction(0, 1))
                c_XY = b_XY.get(Z, Fraction(0, 1))
                expected_YX = -s * c_XY
                if c_YX != expected_YX:
                    skew_errors.append((X, Y, Z, c_XY, c_YX, expected_YX))

    print(f"Graded anti-symmetry: checked {pairs_checked} pairs. Errors = {len(skew_errors)}")
    if skew_errors:
        for err in skew_errors[:5]:
            print(f"  Skew error: [{err[1]}, {err[0]}]_{{{err[2]}}} = {err[4]}, expected {err[5]}")

    # 2. Super-Jacobi identity:
    # (-1)^{pX pZ} [X, [Y, Z}} + (-1)^{pY pX} [Y, [Z, X}} + (-1)^{pZ pY} [Z, [X, Y}} = 0
    t0 = time.time()
    jacobi_errors = []
    triples_checked = 0

    for X in all_basis:
        pX = parity[X]
        for Y in all_basis:
            pY = parity[Y]
            for Z in all_basis:
                pZ = parity[Z]
                triples_checked += 1

                sum_decomp = defaultdict(Fraction)

                # Term 1: (-1)^{pX pZ} [X, [Y, Z}}
                s1 = -1 if (pX * pZ) % 2 == 1 else 1
                for W, c_YZ_W in tensor.get((Y, Z), {}).items():
                    for V, c_XW_V in tensor.get((X, W), {}).items():
                        sum_decomp[V] += s1 * c_YZ_W * c_XW_V

                # Term 2: (-1)^{pY pX} [Y, [Z, X}}
                s2 = -1 if (pY * pX) % 2 == 1 else 1
                for W, c_ZX_W in tensor.get((Z, X), {}).items():
                    for V, c_YW_V in tensor.get((Y, W), {}).items():
                        sum_decomp[V] += s2 * c_ZX_W * c_YW_V

                # Term 3: (-1)^{pZ pY} [Z, [X, Y}}
                s3 = -1 if (pZ * pY) % 2 == 1 else 1
                for W, c_XY_W in tensor.get((X, Y), {}).items():
                    for V, c_ZW_V in tensor.get((Z, W), {}).items():
                        sum_decomp[V] += s3 * c_XY_W * c_ZW_V

                for V, val in sum_decomp.items():
                    if val != 0:
                        jacobi_errors.append((X, Y, Z, V, val))
                        break

    t1 = time.time()
    print(f"Super-Jacobi identity: checked {triples_checked} triples in {t1 - t0:.2f}s. Errors = {len(jacobi_errors)}")
    if jacobi_errors:
        for err in jacobi_errors[:5]:
            print(f"  Jacobi error at ({err[0]}, {err[1]}, {err[2]}) along {err[3]}: residual = {err[4]}")

    passed = (len(skew_errors) == 0) and (len(jacobi_errors) == 0)
    print(f"Result for {cartan_type}: {'PASS' if passed else 'FAIL'}")
    return {
        "n": n,
        "cartan_type": cartan_type,
        "dim": len(all_basis),
        "even_dim": len(even_basis),
        "odd_dim": len(odd_basis),
        "brackets": len(brackets),
        "pairs_checked": pairs_checked,
        "skew_errors": len(skew_errors),
        "triples_checked": triples_checked,
        "jacobi_errors": len(jacobi_errors),
        "elapsed_sec": t1 - t0,
        "status": "PASS" if passed else "FAIL"
    }

def main():
    results = []
    base_dir = "<home>/notebook/git/thm01-R/thm01-R-gemini38f-r3-A1/data"
    for n in [1, 2, 3]:
        path = os.path.join(base_dir, f"C_{n}_structure.json")
        res = verify_structure(path)
        results.append(res)

    print("\n" + "="*70)
    print("VERIFICATION SUMMARY REPORT")
    print("="*70)
    print(f"{'Algebra':<10} | {'Dim (e|o)':<12} | {'Brackets':<10} | {'Pairs':<8} | {'Skew Err':<10} | {'Triples':<10} | {'Jacobi Err':<10} | {'Time (s)':<8} | {'Status'}")
    print("-" * 105)
    for r in results:
        dim_str = f"{r['dim']} ({r['even_dim']}|{r['odd_dim']})"
        print(f"{r['cartan_type']:<10} | {dim_str:<12} | {r['brackets']:<10} | {r['pairs_checked']:<8} | {r['skew_errors']:<10} | {r['triples_checked']:<10} | {r['jacobi_errors']:<10} | {r['elapsed_sec']:<8.2f} | {r['status']}")
    print("="*105)

if __name__ == "__main__":
    main()
