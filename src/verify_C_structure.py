"""
Verification script for C(n+1) structure constants.
Checks graded anti-symmetry and Super Jacobi identity.
"""

import json
from fractions import Fraction
from typing import Dict, Tuple, List, Any

def verify_structure(json_filepath: str) -> Dict[str, Any]:
    with open(json_filepath) as f:
        data = json.load(f)

    n = data["algebra"]["n"]
    even_basis = data["basis"]["even"]
    odd_basis = data["basis"]["odd"]
    all_basis = odd_basis + even_basis
    parity_map = data["parity"]
    dim_total = data["algebra"]["dimension"]["total"]

    # Build structure constant lookup table C[ (X, Y) ][ Z ] = Fraction
    C: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in data["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        coeff = Fraction(entry["coeff"])
        if (x, y) not in C:
            C[(x, y)] = {}
        C[(x, y)][z] = coeff

    def get_bracket(x: str, y: str) -> Dict[str, Fraction]:
        return C.get((x, y), {})

    # 1. Check Anti-symmetry
    antisymmetry_failures = []
    for x in all_basis:
        for y in all_basis:
            px, py = parity_map[x], parity_map[y]
            sign = (-1) ** (px * py)
            b1 = get_bracket(x, y)
            b2 = get_bracket(y, x)

            # Check b1[z] + sign * b2[z] == 0 for all z
            all_z = set(b1.keys()).union(set(b2.keys()))
            for z in all_z:
                v1 = b1.get(z, Fraction(0))
                v2 = b2.get(z, Fraction(0))
                if v1 + Fraction(sign) * v2 != 0:
                    antisymmetry_failures.append({
                        "X": x, "Y": y, "Z": z,
                        "coeff(X,Y)": str(v1), "coeff(Y,X)": str(v2), "parity_sign": sign
                    })

    # 2. Check Super Jacobi identity
    # (-1)^(p_x p_z) [x, [y, z]] + (-1)^(p_y p_x) [y, [z, x]] + (-1)^(p_z p_y) [z, [x, y]] = 0
    jacobi_failures = []
    total_triples = len(all_basis) ** 3
    checked_triples = 0

    for x in all_basis:
        px = parity_map[x]
        for y in all_basis:
            py = parity_map[y]
            for z in all_basis:
                pz = parity_map[z]
                checked_triples += 1

                s1 = (-1) ** (px * pz)
                s2 = (-1) ** (py * px)
                s3 = (-1) ** (pz * py)

                # Term 1: s1 * [x, [y, z]]
                # Term 2: s2 * [y, [z, x]]
                # Term 3: s3 * [z, [x, y]]
                jacobi_sum: Dict[str, Fraction] = {}

                # Term 1
                for m, c_yz in get_bracket(y, z).items():
                    for r, c_xm in get_bracket(x, m).items():
                        jacobi_sum[r] = jacobi_sum.get(r, Fraction(0)) + Fraction(s1) * c_yz * c_xm

                # Term 2
                for m, c_zx in get_bracket(z, x).items():
                    for r, c_ym in get_bracket(y, m).items():
                        jacobi_sum[r] = jacobi_sum.get(r, Fraction(0)) + Fraction(s2) * c_zx * c_ym

                # Term 3
                for m, c_xy in get_bracket(x, y).items():
                    for r, c_zm in get_bracket(z, m).items():
                        jacobi_sum[r] = jacobi_sum.get(r, Fraction(0)) + Fraction(s3) * c_xy * c_zm

                for r, val in jacobi_sum.items():
                    if val != 0:
                        jacobi_failures.append({
                            "X": x, "Y": y, "Z": z, "R": r, "sum": str(val)
                        })

    return {
        "n": n,
        "dim_total": dim_total,
        "total_triples": total_triples,
        "antisymmetry_pass": len(antisymmetry_failures) == 0,
        "antisymmetry_failure_count": len(antisymmetry_failures),
        "antisymmetry_failures": antisymmetry_failures[:5],
        "jacobi_pass": len(jacobi_failures) == 0,
        "jacobi_failure_count": len(jacobi_failures),
        "jacobi_failures": jacobi_failures[:5],
    }


def verify_all():
    results = []
    all_passed = True
    for n in [1, 2, 3]:
        filepath = f"data/C_{n}_structure.json"
        res = verify_structure(filepath)
        results.append(res)
        print(f"C({n+1}) Verification [n={n}]: Anti-symmetry {'PASS' if res['antisymmetry_pass'] else 'FAIL'}, Super Jacobi {'PASS' if res['jacobi_pass'] else 'FAIL'} ({res['total_triples']} triples checked)")
        if not (res['antisymmetry_pass'] and res['jacobi_pass']):
            all_passed = False
    return all_passed, results


if __name__ == "__main__":
    passed, results = verify_all()
    if not passed:
        exit(1)
