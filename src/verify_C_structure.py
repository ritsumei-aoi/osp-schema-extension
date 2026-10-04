"""
verify_C_structure.py: Verifies graded skew-symmetry and Super Jacobi identity
for C(n+1) structure constants across n=1, 2, 3.
"""

import json
from fractions import Fraction
from typing import Dict, Tuple, List, Any


def load_structure(path: str):
    with open(path, "r") as f:
        data = json.load(f)
    
    basis = data["basis"]["odd"] + data["basis"]["even"]
    parity = data["parity"]
    
    # Store brackets as (X, Y) -> Dict[Z, Fraction]
    brackets: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for entry in data["structure_constants"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        brackets.setdefault((X, Y), {})[Z] = c

    return basis, parity, brackets, data


def bracket_eval(brackets: Dict[Tuple[str, str], Dict[str, Fraction]], 
                 v1: Dict[str, Fraction], p1_func, 
                 v2: Dict[str, Fraction], p2_func) -> Dict[str, Fraction]:
    """
    Compute bilinear bracket of two formal linear combinations.
    """
    res: Dict[str, Fraction] = {}
    for x, cx in v1.items():
        if cx == 0:
            continue
        for y, cy in v2.items():
            if cy == 0:
                continue
            pair_dict = brackets.get((x, y), {})
            for z, cz in pair_dict.items():
                val = cx * cy * cz
                if val != 0:
                    res[z] = res.get(z, Fraction(0)) + val
                    if res[z] == Fraction(0):
                        del res[z]
    return res


def verify_skew_symmetry(basis: List[str], parity: Dict[str, int], 
                         brackets: Dict[Tuple[str, str], Dict[str, Fraction]]) -> Tuple[bool, List[str]]:
    errors = []
    for x in basis:
        px = parity[x]
        for y in basis:
            py = parity[y]
            expected_sign = -1 if (px * py == 0) else 1  # -(-1)^(px*py)
            xy = brackets.get((x, y), {})
            yx = brackets.get((y, x), {})

            # All Z in xy must have -(-1)^(px py) in yx
            all_z = set(xy.keys()).union(set(yx.keys()))
            for z in all_z:
                c_xy = xy.get(z, Fraction(0))
                c_yx = yx.get(z, Fraction(0))
                if c_yx != expected_sign * c_xy:
                    errors.append(f"Skew error: [{x}, {y}]^{z} = {c_xy}, but [{y}, {x}]^{z} = {c_yx} (expected {expected_sign * c_xy})")
    return len(errors) == 0, errors


def verify_super_jacobi(basis: List[str], parity: Dict[str, int], 
                        brackets: Dict[Tuple[str, str], Dict[str, Fraction]]) -> Tuple[bool, int, List[str]]:
    """
    Check Super Jacobi identity:
    (-1)^(pX*pZ) [X, [Y, Z}} + (-1)^(pY*pX) [Y, [Z, X}} + (-1)^(pZ*pY) [Z, [X, Y}} = 0
    """
    checked = 0
    errors = []
    
    for X in basis:
        pX = parity[X]
        vX = {X: Fraction(1)}
        for Y in basis:
            pY = parity[Y]
            vY = {Y: Fraction(1)}
            for Z in basis:
                pZ = parity[Z]
                vZ = {Z: Fraction(1)}
                checked += 1

                # Term 1: (-1)^(pX * pZ) [X, [Y, Z}}
                yz = brackets.get((Y, Z), {})
                term1 = bracket_eval(brackets, vX, lambda x: pX, yz, lambda z: (pY + pZ) % 2)
                s1 = -1 if ((pX * pZ) % 2 == 1) else 1

                # Term 2: (-1)^(pY * pX) [Y, [Z, X}}
                zx = brackets.get((Z, X), {})
                term2 = bracket_eval(brackets, vY, lambda y: pY, zx, lambda x: (pZ + pX) % 2)
                s2 = -1 if ((pY * pX) % 2 == 1) else 1

                # Term 3: (-1)^(pZ * pY) [Z, [X, Y}}
                xy = brackets.get((X, Y), {})
                term3 = bracket_eval(brackets, vZ, lambda z: pZ, xy, lambda y: (pX + pY) % 2)
                s3 = -1 if ((pZ * pY) % 2 == 1) else 1

                # Sum all three terms
                jacobi_sum: Dict[str, Fraction] = {}
                for w, c in term1.items():
                    jacobi_sum[w] = jacobi_sum.get(w, Fraction(0)) + s1 * c
                for w, c in term2.items():
                    jacobi_sum[w] = jacobi_sum.get(w, Fraction(0)) + s2 * c
                for w, c in term3.items():
                    jacobi_sum[w] = jacobi_sum.get(w, Fraction(0)) + s3 * c

                # Clean zeros
                jacobi_sum = {w: c for w, c in jacobi_sum.items() if c != 0}

                if jacobi_sum:
                    errors.append(f"Super Jacobi failed for ({X}, {Y}, {Z}): residual = {jacobi_sum}")
                    if len(errors) > 20:
                        return False, checked, errors

    return len(errors) == 0, checked, errors


def run_verification():
    summary = {}
    all_ok = True
    for n in [1, 2, 3]:
        path = f"data/C_{n}_structure.json"
        basis, parity, brackets, data = load_structure(path)
        dim = len(basis)
        print(f"\n--- Verifying C({n+1}) [n={n}] (Dim={dim}) from {path} ---")

        skew_ok, skew_errs = verify_skew_symmetry(basis, parity, brackets)
        print(f"  Graded Skew-Symmetry: {'PASS' if skew_ok else 'FAIL'} ({len(skew_errs)} errors)")

        jacobi_ok, checked_count, jacobi_errs = verify_super_jacobi(basis, parity, brackets)
        print(f"  Super Jacobi Identity: {'PASS' if jacobi_ok else 'FAIL'} ({checked_count} triples checked, {len(jacobi_errs)} errors)")

        status = skew_ok and jacobi_ok
        if not status:
            all_ok = False
        summary[n] = {
            "dim": dim,
            "triples_checked": checked_count,
            "skew_symmetry": "PASS" if skew_ok else "FAIL",
            "super_jacobi": "PASS" if jacobi_ok else "FAIL",
            "status": "PASS" if status else "FAIL"
        }

    print("\n================ SUMMARY ================")
    for n, res in summary.items():
        print(f"C({n+1}) [n={n}]: Status={res['status']} | Skew={res['skew_symmetry']} | Jacobi={res['super_jacobi']} ({res['triples_checked']} triples)")
    return all_ok


if __name__ == "__main__":
    success = run_verification()
    if not success:
        exit(1)
