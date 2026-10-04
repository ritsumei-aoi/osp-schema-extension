"""
verify_C_structure.py: Verifies graded anti-symmetry and Super Jacobi identity
for all basis elements and all generator triples across C(2), C(3), C(4) structure files.
"""

from fractions import Fraction
import json
import os
import sys
import time
from typing import Dict, Tuple, List, Any


def load_structure(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as f:
        return json.load(f)


def verify_algebra(data: Dict[str, Any]) -> Dict[str, Any]:
    cartan_type = data["algebra"]["cartan_type"]
    n = data["algebra"]["n"]
    parity = data["parity"]
    even_basis = data["basis"]["even"]
    odd_basis = data["basis"]["odd"]
    all_basis = odd_basis + even_basis
    dim = len(all_basis)

    # Build bracket lookup table: (X, Y) -> Dict[Z, Fraction]
    # Represent non-zero brackets as { (x, y): {z: coeff} }
    sc_map: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in data["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        coeff = Fraction(entry["coeff"])
        if (x, y) not in sc_map:
            sc_map[(x, y)] = {}
        sc_map[(x, y)][z] = sc_map[(x, y)].get(z, Fraction(0)) + coeff

    def get_bracket(x: str, y: str) -> Dict[str, Fraction]:
        return sc_map.get((x, y), {})

    def bracket_eval(dict_a: Dict[str, Fraction], y: str) -> Dict[str, Fraction]:
        res: Dict[str, Fraction] = {}
        for a_gen, a_coeff in dict_a.items():
            b = get_bracket(a_gen, y)
            for z_gen, z_coeff in b.items():
                res[z_gen] = res.get(z_gen, Fraction(0)) + a_coeff * z_coeff
        # clean zeros
        return {k: v for k, v in res.items() if v != 0}

    def bracket_eval_right(x: str, dict_b: Dict[str, Fraction]) -> Dict[str, Fraction]:
        res: Dict[str, Fraction] = {}
        for b_gen, b_coeff in dict_b.items():
            b = get_bracket(x, b_gen)
            for z_gen, z_coeff in b.items():
                res[z_gen] = res.get(z_gen, Fraction(0)) + b_coeff * z_coeff
        return {k: v for k, v in res.items() if v != 0}

    # 1. Verify Graded Anti-symmetry for all pairs
    antisymmetry_failures = []
    pairs_checked = 0
    for x in all_basis:
        px = parity[x]
        for y in all_basis:
            py = parity[y]
            pairs_checked += 1
            sign = -1 if (px == 1 and py == 1) else 1
            b_xy = get_bracket(x, y)
            b_yx = get_bracket(y, x)

            # Check b_yx == - sign * b_xy
            all_z = set(b_xy.keys()) | set(b_yx.keys())
            for z in all_z:
                c_xy = b_xy.get(z, Fraction(0))
                c_yx = b_yx.get(z, Fraction(0))
                expected_yx = - Fraction(sign) * c_xy
                if c_yx != expected_yx:
                    antisymmetry_failures.append((x, y, z, c_xy, c_yx, expected_yx))

    # 2. Verify Super Jacobi Identity for all triples
    # (-1)^{p(X)p(Z)} [X, [Y, Z}] + (-1)^{p(Y)p(X)} [Y, [Z, X}] + (-1)^{p(Z)p(Y)} [Z, [X, Y}] = 0
    jacobi_failures = []
    triples_checked = 0
    t0 = time.time()

    for x in all_basis:
        px = parity[x]
        for y in all_basis:
            py = parity[y]
            # Precompute [X, Y]
            xy = get_bracket(x, y)
            for z in all_basis:
                pz = parity[z]
                triples_checked += 1

                # Term 1: (-1)^{px*pz} [X, [Y, Z}]
                yz = get_bracket(y, z)
                t1 = bracket_eval_right(x, yz)
                s1 = -1 if (px * pz) % 2 == 1 else 1

                # Term 2: (-1)^{py*px} [Y, [Z, X}]
                zx = get_bracket(z, x)
                t2 = bracket_eval_right(y, zx)
                s2 = -1 if (py * px) % 2 == 1 else 1

                # Term 3: (-1)^{pz*py} [Z, [X, Y}]
                t3 = bracket_eval_right(z, xy)
                s3 = -1 if (pz * py) % 2 == 1 else 1

                all_z_res = set(t1.keys()) | set(t2.keys()) | set(t3.keys())
                for target_gen in all_z_res:
                    val = (
                        s1 * t1.get(target_gen, Fraction(0)) +
                        s2 * t2.get(target_gen, Fraction(0)) +
                        s3 * t3.get(target_gen, Fraction(0))
                    )
                    if val != 0:
                        jacobi_failures.append((x, y, z, target_gen, val))

    elapsed = time.time() - t0

    return {
        "cartan_type": cartan_type,
        "n": n,
        "dimension": dim,
        "pairs_checked": pairs_checked,
        "antisymmetry_failures": len(antisymmetry_failures),
        "triples_checked": triples_checked,
        "jacobi_failures": len(jacobi_failures),
        "elapsed_sec": round(elapsed, 4),
        "status": "PASS" if len(antisymmetry_failures) == 0 and len(jacobi_failures) == 0 else "FAIL",
        "failure_details": {
            "antisymmetry": antisymmetry_failures[:5],
            "jacobi": jacobi_failures[:5]
        }
    }


def verify_all(data_dir: str = "data"):
    results = []
    for n in [1, 2, 3]:
        file_path = os.path.join(data_dir, f"C_{n}_structure.json")
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found.")
            continue
        data = load_structure(file_path)
        res = verify_algebra(data)
        results.append(res)
        print(f"[{res['status']}] {res['cartan_type']} (n={res['n']}, dim={res['dimension']}): "
              f"{res['pairs_checked']} pairs checked, {res['triples_checked']} triples checked in {res['elapsed_sec']}s")

    return results


if __name__ == "__main__":
    results = verify_all()
    all_passed = all(r["status"] == "PASS" for r in results)
    if not all_passed:
        sys.exit(1)
