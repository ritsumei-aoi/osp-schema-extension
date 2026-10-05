"""
Verification script for C(n+1) structure constants: Graded Anti-symmetry and Super Jacobi Identity
"""
import json
import os
import sys
from fractions import Fraction
from typing import Dict, Tuple

def verify_structure_file(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r") as f:
        data = json.load(f)

    algebra_name = data["algebra"]["cartan_type"]
    basis = data["basis"]["odd"] + data["basis"]["even"]
    parity = data["parity"]

    # Build bracket dictionary: (X, Y) -> {Z: Fraction}
    brackets: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in data["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        if (x, y) not in brackets:
            brackets[(x, y)] = {}
        brackets[(x, y)][z] = c

    # Helper function to get bracket [X, Y] as a dict
    def get_bracket(x: str, y: str) -> Dict[str, Fraction]:
        return brackets.get((x, y), {})

    # 1. Graded anti-symmetry check
    antisymmetry_failures = []
    for x in basis:
        for y in basis:
            px = parity[x]
            py = parity[y]
            sign = -1 if (px == 1 and py == 1) else 1

            xy = get_bracket(x, y)
            yx = get_bracket(y, x)

            all_targets = set(xy.keys()).union(yx.keys())
            for z in all_targets:
                c_xy = xy.get(z, Fraction(0))
                c_yx = yx.get(z, Fraction(0))
                if c_xy != -sign * c_yx:
                    antisymmetry_failures.append((x, y, z, c_xy, c_yx))

    # 2. Super Jacobi identity check
    # (-1)^{p(X) p(Z)} [X, [Y, Z]] + (-1)^{p(Y) p(X)} [Y, [Z, X]] + (-1)^{p(Z) p(Y)} [Z, [X, Y]] = 0
    jacobi_failures = []
    triples_count = 0

    for x in basis:
        px = parity[x]
        for y in basis:
            py = parity[y]
            for z in basis:
                pz = parity[z]
                triples_count += 1

                # Term 1: (-1)^{px * pz} [X, [Y, Z]]
                # [Y, Z] = sum_U c(Y,Z,U) U => [X, [Y,Z]] = sum_U c(Y,Z,U) [X, U]
                res_vector: Dict[str, Fraction] = {}
                sign1 = -1 if (px * pz) % 2 == 1 else 1
                for u, c_yz_u in get_bracket(y, z).items():
                    for w, c_xu_w in get_bracket(x, u).items():
                        res_vector[w] = res_vector.get(w, Fraction(0)) + sign1 * c_yz_u * c_xu_w

                # Term 2: (-1)^{py * px} [Y, [Z, X]]
                sign2 = -1 if (py * px) % 2 == 1 else 1
                for u, c_zx_u in get_bracket(z, x).items():
                    for w, c_yu_w in get_bracket(y, u).items():
                        res_vector[w] = res_vector.get(w, Fraction(0)) + sign2 * c_zx_u * c_yu_w

                # Term 3: (-1)^{pz * py} [Z, [X, Y]]
                sign3 = -1 if (pz * py) % 2 == 1 else 1
                for u, c_xy_u in get_bracket(x, y).items():
                    for w, c_zu_w in get_bracket(z, u).items():
                        res_vector[w] = res_vector.get(w, Fraction(0)) + sign3 * c_xy_u * c_zu_w

                # Check if res_vector is zero for all w
                non_zero = {w: c for w, c in res_vector.items() if c != 0}
                if non_zero:
                    jacobi_failures.append((x, y, z, non_zero))

    return {
        "algebra": algebra_name,
        "total_basis": len(basis),
        "triples_checked": triples_count,
        "antisymmetry_failures": len(antisymmetry_failures),
        "jacobi_failures": len(jacobi_failures),
        "status": "PASS" if (len(antisymmetry_failures) == 0 and len(jacobi_failures) == 0) else "FAIL"
    }

def main():
    data_dir = "data"
    all_passed = True
    print("=" * 60)
    print("C(n+1) STRUCTURE CONSTANTS VERIFICATION REPORT")
    print("=" * 60)

    for n in (1, 2, 3):
        filepath = os.path.join(data_dir, f"C_{n}_structure.json")
        res = verify_structure_file(filepath)
        print(f"Algebra: {res['algebra']} (n={n})")
        print(f"  Basis elements count: {res['total_basis']}")
        print(f"  Triples checked: {res['triples_checked']}")
        print(f"  Anti-symmetry failures: {res['antisymmetry_failures']}")
        print(f"  Super Jacobi failures: {res['jacobi_failures']}")
        print(f"  Status: {res['status']}")
        print("-" * 60)
        if res["status"] != "PASS":
            all_passed = False

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
