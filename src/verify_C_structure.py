"""
Verification script for C(n+1) structure constants.
Checks anti-symmetry and the Super Jacobi identity.
"""

import json
import os
import sys
from fractions import Fraction


def load_structure(n, data_dir=None):
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def build_bracket_table(data):
    all_labels = data["basis"]["odd"] + data["basis"]["even"]
    parity = {k: v for k, v in data["parity"].items()}

    bracket = {}
    for sc in data["structure_constants"]:
        x, y = sc["X"], sc["Y"]
        result = {}
        for term in sc["result"]:
            z = term["Z"]
            c = Fraction(term["coeff"])
            result[z] = result.get(z, Fraction(0)) + c
        result = {k: v for k, v in result.items() if v != 0}
        bracket[(x, y)] = result

        px, py = parity[x], parity[y]
        sign = (-1) ** (px * py)
        reversed_result = {k: -sign * v for k, v in result.items()}
        reversed_result = {k: v for k, v in reversed_result.items() if v != 0}
        bracket[(y, x)] = reversed_result

    return bracket, all_labels, parity


def get_bracket(bracket_table, x, y):
    return bracket_table.get((x, y), {})


def compose_results(r1, r2, coeff=Fraction(1)):
    result = dict(r1)
    for k, v in r2.items():
        result[k] = result.get(k, Fraction(0)) + coeff * v
    return {k: v for k, v in result.items() if v != 0}


def bracket_with_result(bracket_table, result_dict, y, parity_map):
    """Compute [result, y] where result = sum c_z * Z."""
    total = {}
    for z, cz in result_dict.items():
        bzy = get_bracket(bracket_table, z, y)
        for w, cw in bzy.items():
            total[w] = total.get(w, Fraction(0)) + cz * cw
    return {k: v for k, v in total.items() if v != 0}


def check_antisymmetry(data):
    bracket, all_labels, parity = build_bracket_table(data)
    failures = []

    for i, x in enumerate(all_labels):
        for j, y in enumerate(all_labels):
            if j <= i:
                continue
            px, py = parity[x], parity[y]
            sign = (-1) ** (px * py)

            bxy = get_bracket(bracket, x, y)
            byx = get_bracket(bracket, y, x)

            for z in set(list(bxy.keys()) + list(byx.keys())):
                cxy = bxy.get(z, Fraction(0))
                cyx = byx.get(z, Fraction(0))
                expected = -sign * cxy
                if cyx != expected:
                    failures.append((x, y, z, cxy, cyx, expected))

    return failures


def check_super_jacobi(data):
    """Check: (-1)^{px*pz}[[x,y],z] + (-1)^{py*px}[[y,z],x] + (-1)^{pz*py}[[z,x],y] = 0"""
    bracket, all_labels, parity = build_bracket_table(data)
    failures = []
    checked = 0

    for i, x in enumerate(all_labels):
        for j, y in enumerate(all_labels):
            if j <= i:
                continue
            for k, z in enumerate(all_labels):
                if k <= j:
                    continue

                px, py, pz = parity[x], parity[y], parity[z]

                bxy = get_bracket(bracket, x, y)
                byz = get_bracket(bracket, y, z)
                bzx = get_bracket(bracket, z, x)

                term_a = bracket_with_result(bracket, bxy, z, parity)
                sign_a = Fraction((-1) ** (px * pz))

                term_b = bracket_with_result(bracket, byz, x, parity)
                sign_b = Fraction((-1) ** (py * px))

                term_c = bracket_with_result(bracket, bzx, y, parity)
                sign_c = Fraction((-1) ** (pz * py))

                jacobi = {}
                for w in set(list(term_a.keys()) + list(term_b.keys()) + list(term_c.keys())):
                    val = (sign_a * term_a.get(w, Fraction(0))
                           + sign_b * term_b.get(w, Fraction(0))
                           + sign_c * term_c.get(w, Fraction(0)))
                    if val != 0:
                        jacobi[w] = val

                checked += 1
                if jacobi:
                    failures.append((x, y, z, jacobi))

    return failures, checked


def verify_all(n, data_dir=None):
    data = load_structure(n, data_dir)
    algebra = data["algebra"]["cartan_type"]
    dim = data["algebra"]["dimension"]["total"]
    n_sc = len(data["structure_constants"])

    print(f"\n{'='*60}")
    print(f"Verifying {algebra} = osp(2|{2*n}), n={n}")
    print(f"Dimension: {dim}, Structure constants: {n_sc}")
    print(f"{'='*60}")

    print("\n1. Anti-symmetry check...")
    asym_failures = check_antisymmetry(data)
    if asym_failures:
        print(f"   FAIL: {len(asym_failures)} anti-symmetry violations")
        for x, y, z, cxy, cyx, expected in asym_failures[:5]:
            print(f"     [{x}, {y}]_z={z}: coeff={cxy}, [{y},{x}]_z={z}: got {cyx}, expected {expected}")
    else:
        print("   PASS: All pairs satisfy graded anti-symmetry")

    print("\n2. Super Jacobi identity check...")
    jacobi_failures, checked = check_super_jacobi(data)
    if jacobi_failures:
        print(f"   FAIL: {len(jacobi_failures)} / {checked} triples violate Jacobi")
        for x, y, z, residual in jacobi_failures[:5]:
            print(f"     ({x}, {y}, {z}): residual = {residual}")
    else:
        print(f"   PASS: All {checked} triples satisfy Super Jacobi identity")

    return len(asym_failures) == 0 and len(jacobi_failures) == 0


def main():
    all_pass = True
    for n in [1, 2, 3]:
        if not verify_all(n):
            all_pass = False

    print(f"\n{'='*60}")
    if all_pass:
        print("ALL VERIFICATIONS PASSED")
    else:
        print("SOME VERIFICATIONS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
