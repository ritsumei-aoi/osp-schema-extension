"""
verify_C_structure.py - Verifies super-antisymmetry and Super Jacobi identity
for C(n+1) structure constants (n=1, 2, 3).
"""

import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple, Any


def load_structure_json(filepath: str) -> Tuple[List[str], Dict[str, int], Dict[Tuple[str, str], Dict[str, Fraction]]]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    basis = data["basis"]["odd"] + data["basis"]["even"]
    parity = data["parity"]

    bracket_dict: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in data["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        if (x, y) not in bracket_dict:
            bracket_dict[(x, y)] = {}
        bracket_dict[(x, y)][z] = c

    return basis, parity, bracket_dict


def compute_bracket(
    bracket_dict: Dict[Tuple[str, str], Dict[str, Fraction]],
    x: str,
    y: str
) -> Dict[str, Fraction]:
    return bracket_dict.get((x, y), {})


def compute_bracket_linear(
    bracket_dict: Dict[Tuple[str, str], Dict[str, Fraction]],
    v: Dict[str, Fraction],
    w: Dict[str, Fraction]
) -> Dict[str, Fraction]:
    res: Dict[str, Fraction] = {}
    for x, cx in v.items():
        if cx == 0:
            continue
        for y, cy in w.items():
            if cy == 0:
                continue
            br = compute_bracket(bracket_dict, x, y)
            for z, cz in br.items():
                res[z] = res.get(z, Fraction(0)) + cx * cy * cz
                if res[z] == 0:
                    del res[z]
    return res


def verify_algebra(n: int, filepath: str) -> Dict[str, Any]:
    basis, parity, bracket_dict = load_structure_json(filepath)
    dim = len(basis)

    # 1. Verify Super-Antisymmetry
    antisymmetry_failures = []
    pairs_checked = 0
    for x in basis:
        for y in basis:
            pairs_checked += 1
            px, py = parity[x], parity[y]
            sign = -1 if (px == 1 and py == 1) else 1
            expected_factor = -sign

            br_xy = compute_bracket(bracket_dict, x, y)
            br_yx = compute_bracket(bracket_dict, y, x)

            all_z = set(br_xy.keys()) | set(br_yx.keys())
            for z in all_z:
                c_xy = br_xy.get(z, Fraction(0))
                c_yx = br_yx.get(z, Fraction(0))
                if c_yx != expected_factor * c_xy:
                    antisymmetry_failures.append((x, y, z, c_xy, c_yx))

    # 2. Verify Super Jacobi Identity:
    # (-1)^{p(X)p(Z)} [X, [Y, Z]] + (-1)^{p(Y)p(X)} [Y, [Z, X]] + (-1)^{p(Z)p(Y)} [Z, [X, Y]] = 0
    jacobi_failures = []
    triples_checked = 0
    for x in basis:
        px = parity[x]
        for y in basis:
            py = parity[y]
            for z in basis:
                pz = parity[z]
                triples_checked += 1

                sign1 = -1 if (px == 1 and pz == 1) else 1
                sign2 = -1 if (py == 1 and px == 1) else 1
                sign3 = -1 if (pz == 1 and py == 1) else 1

                # [Y, Z]
                br_yz = compute_bracket(bracket_dict, y, z)
                # [X, [Y, Z]]
                term1 = compute_bracket_linear(bracket_dict, {x: Fraction(1)}, br_yz)

                # [Z, X]
                br_zx = compute_bracket(bracket_dict, z, x)
                # [Y, [Z, X]]
                term2 = compute_bracket_linear(bracket_dict, {y: Fraction(1)}, br_zx)

                # [X, Y]
                br_xy = compute_bracket(bracket_dict, x, y)
                # [Z, [X, Y]]
                term3 = compute_bracket_linear(bracket_dict, {z: Fraction(1)}, br_xy)

                # Total sum
                all_w = set(term1.keys()) | set(term2.keys()) | set(term3.keys())
                for w in all_w:
                    tot = (
                        sign1 * term1.get(w, Fraction(0)) +
                        sign2 * term2.get(w, Fraction(0)) +
                        sign3 * term3.get(w, Fraction(0))
                    )
                    if tot != 0:
                        jacobi_failures.append((x, y, z, w, tot))

    return {
        "n": n,
        "dim": dim,
        "pairs_checked": pairs_checked,
        "antisymmetry_failures": len(antisymmetry_failures),
        "triples_checked": triples_checked,
        "jacobi_failures": len(jacobi_failures),
        "passed": (len(antisymmetry_failures) == 0 and len(jacobi_failures) == 0)
    }


def main():
    print("=== Super Jacobi & Antisymmetry Verification for C(n+1) ===")
    all_passed = True
    results = []

    for n in [1, 2, 3]:
        filepath = f"data/C_{n}_structure.json"
        if not os.path.exists(filepath):
            print(f"File {filepath} does not exist. Run C_generators.py first.")
            sys.exit(1)

        res = verify_algebra(n, filepath)
        results.append(res)
        status = "PASSED" if res["passed"] else "FAILED"
        print(f"C({n+1}) [n={n}, dim={res['dim']}]:")
        print(f"  - Pairs checked for Super-Antisymmetry: {res['pairs_checked']:,} (Failures: {res['antisymmetry_failures']})")
        print(f"  - Triples checked for Super Jacobi:      {res['triples_checked']:,} (Failures: {res['jacobi_failures']})")
        print(f"  - Status: {status}\n")
        if not res["passed"]:
            all_passed = False

    if all_passed:
        print("All structure constants for C(2), C(3), and C(4) satisfy the Super Jacobi identity and Antisymmetry perfectly!")
        sys.exit(0)
    else:
        print("Verification FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
