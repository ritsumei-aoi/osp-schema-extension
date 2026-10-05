"""
Verification script for C(n+1) structure constants.
Verifies graded anti-symmetry and super Jacobi identity from generated JSON files.
"""

from fractions import Fraction
import json
import os
import sys
from typing import Dict, Tuple, List, Any


def load_structure_data(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r") as f:
        return json.load(f)


def verify_algebra(filepath: str) -> Dict[str, Any]:
    data = load_structure_data(filepath)
    algebra_info = data["algebra"]
    n = algebra_info["n"]
    cartan_type = algebra_info["cartan_type"]
    
    basis = data["basis"]
    all_gens = basis["even"] + basis["odd"]
    dim = len(all_gens)
    parity = data["parity"]
    
    # Parse structure constants into sparse map: (X, Y) -> {Z: Fraction}
    bracket_map: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in data["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        coeff = Fraction(entry["coeff"])
        if (x, y) not in bracket_map:
            bracket_map[(x, y)] = {}
        bracket_map[(x, y)][z] = coeff

    def br(u: str, v: str) -> Dict[str, Fraction]:
        return bracket_map.get((u, v), {})

    def br_lin_left(lin_u: Dict[str, Fraction], v: str) -> Dict[str, Fraction]:
        res: Dict[str, Fraction] = {}
        for u_i, c_i in lin_u.items():
            for w, coeff in br(u_i, v).items():
                res[w] = res.get(w, Fraction(0)) + c_i * coeff
        return {k: v_c for k, v_c in res.items() if v_c != 0}

    def br_lin_right(u: str, lin_v: Dict[str, Fraction]) -> Dict[str, Fraction]:
        res: Dict[str, Fraction] = {}
        for v_j, c_j in lin_v.items():
            for w, coeff in br(u, v_j).items():
                res[w] = res.get(w, Fraction(0)) + c_j * coeff
        return {k: v_c for k, v_c in res.items() if v_c != 0}

    # 1. Anti-symmetry check
    antisymmetry_failures = []
    pairs_checked = 0
    for x in all_gens:
        px = parity[x]
        for y in all_gens:
            py = parity[y]
            pairs_checked += 1
            sign = -1 if (px * py) % 2 == 1 else 1
            
            # [X, Y}
            xy_map = br(x, y)
            yx_map = br(y, x)
            
            # Check: [Y, X} == -sign * [X, Y}
            all_z = set(xy_map.keys()).union(set(yx_map.keys()))
            for z in all_z:
                c_xy = xy_map.get(z, Fraction(0))
                c_yx = yx_map.get(z, Fraction(0))
                if c_yx != -sign * c_xy:
                    antisymmetry_failures.append({
                        "pair": (x, y),
                        "Z": z,
                        "c_xy": str(c_xy),
                        "c_yx": str(c_yx),
                        "expected_yx": str(-sign * c_xy)
                    })

    # 2. Super Jacobi identity check
    # [X, [Y, Z}} = [[X, Y}, Z} + (-1)^(px py) [Y, [X, Z}}
    jacobi_failures = []
    triples_checked = 0
    for x in all_gens:
        px = parity[x]
        for y in all_gens:
            py = parity[y]
            sign_xy = -1 if (px * py) % 2 == 1 else 1
            for z in all_gens:
                triples_checked += 1
                
                # Term 1: [X, [Y, Z}}
                term1 = br_lin_right(x, br(y, z))
                # Term 2: [[X, Y}, Z}
                term2 = br_lin_left(br(x, y), z)
                # Term 3: (-1)^(px py) [Y, [X, Z}}
                term3_raw = br_lin_right(y, br(x, z))
                term3 = {k: sign_xy * v for k, v in term3_raw.items()}
                
                # RHS = term2 + term3
                rhs = dict(term2)
                for k, v in term3.items():
                    rhs[k] = rhs.get(k, Fraction(0)) + v
                rhs = {k: v for k, v in rhs.items() if v != 0}
                
                if term1 != rhs:
                    jacobi_failures.append({
                        "triple": (x, y, z),
                        "lhs": {k: str(v) for k, v in term1.items()},
                        "rhs": {k: str(v) for k, v in rhs.items()}
                    })

    return {
        "cartan_type": cartan_type,
        "n": n,
        "dim": dim,
        "pairs_checked": pairs_checked,
        "antisymmetry_failures": len(antisymmetry_failures),
        "triples_checked": triples_checked,
        "jacobi_failures": len(jacobi_failures),
        "pass": len(antisymmetry_failures) == 0 and len(jacobi_failures) == 0
    }


def main():
    data_dir = "data"
    all_passed = True
    results = []
    for n in [1, 2, 3]:
        filepath = os.path.join(data_dir, f"C_{n}_structure.json")
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            sys.exit(1)
        res = verify_algebra(filepath)
        results.append(res)
        print(f"--- Verification for {res['cartan_type']} (n={res['n']}) ---")
        print(f"Dimension: {res['dim']}")
        print(f"Pairs checked: {res['pairs_checked']}, Anti-symmetry failures: {res['antisymmetry_failures']}")
        print(f"Triples checked: {res['triples_checked']}, Jacobi failures: {res['jacobi_failures']}")
        print(f"Status: {'PASS' if res['pass'] else 'FAIL'}\n")
        if not res['pass']:
            all_passed = False

    if all_passed:
        print("All algebras successfully passed anti-symmetry and Super Jacobi identity verification.")
    else:
        print("Some verifications failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
