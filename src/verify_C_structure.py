"""
Super Jacobi identity and anti-symmetry verification for C(n+1) structure constants.

Loads C_{n}_structure.json and verifies:
1. Anti-symmetry: [X, Y} = -(-1)^{p(X)p(Y)} [Y, X}
2. Super Jacobi identity for all triples:
   (-1)^{p(X)p(Z)} [X, [Y, Z}}} + cyclic = 0
"""

import json
import os
import sys
from fractions import Fraction


def load_structure(data_dir, n):
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def build_bracket_table(structure):
    """Build lookup: (X, Y) -> {Z: coeff, ...}"""
    table = {}
    parity = structure["parity"]

    for sc in structure["structure_constants"]:
        x, y = sc["X"], sc["Y"]
        result = {}
        for term in sc["result"]:
            result[term["Z"]] = Fraction(term["coeff"])
        table[(x, y)] = result

    return table


def get_bracket(table, parity, x, y):
    """Get [X, Y} from the table, using graded anti-symmetry if needed."""
    if (x, y) in table:
        return dict(table[(x, y)])
    if (y, x) in table:
        px = parity[x]
        py = parity[y]
        sign = -(-1) ** (px * py)
        return {z: Fraction(sign) * c for z, c in table[(y, x)].items()}
    if x == y:
        px = parity[x]
        if px == 0:
            return {}
        return {}
    return {}


def verify_antisymmetry(structure):
    """Check [X, Y} = -(-1)^{p(X)p(Y)} [Y, X} for all pairs."""
    table = build_bracket_table(structure)
    parity = structure["parity"]
    all_gens = structure["basis"]["odd"] + structure["basis"]["even"]
    failures = []

    for i, x in enumerate(all_gens):
        for j, y in enumerate(all_gens):
            if j <= i:
                continue

            xy = get_bracket(table, parity, x, y)
            yx = get_bracket(table, parity, y, x)

            px, py = parity[x], parity[y]
            sign = -(-1) ** (px * py)

            all_gens_set = set()
            all_gens_set.update(xy.keys())
            all_gens_set.update(yx.keys())

            for z in all_gens_set:
                lhs = xy.get(z, Fraction(0))
                rhs = Fraction(sign) * yx.get(z, Fraction(0))
                if lhs != rhs:
                    failures.append((x, y, z, lhs, rhs))

    return failures


def verify_super_jacobi(structure):
    """Check super Jacobi identity for all triples.

    (-1)^{p(X)p(Z)} [X, [Y, Z}}} + (-1)^{p(Y)p(X)} [Y, [Z, X}}} + (-1)^{p(Z)p(Y)} [Z, [X, Y}}} = 0
    """
    table = build_bracket_table(structure)
    parity = structure["parity"]
    all_gens = structure["basis"]["odd"] + structure["basis"]["even"]
    failures = []

    def bracket_result(a, b):
        return get_bracket(table, parity, a, b)

    def double_bracket(a, b, c):
        """Compute [A, [B, C}}} as dict Z -> coeff."""
        bc = bracket_result(b, c)
        result = {}
        for z, coeff_bc in bc.items():
            az = bracket_result(a, z)
            for w, coeff_az in az.items():
                result[w] = result.get(w, Fraction(0)) + coeff_bc * coeff_az
        return result

    total_triples = 0
    for i, x in enumerate(all_gens):
        for j, y in enumerate(all_gens):
            if j <= i:
                continue
            for k, z in enumerate(all_gens):
                if k <= j:
                    continue

                total_triples += 1
                px, py, pz = parity[x], parity[y], parity[z]

                s1 = (-1) ** (px * pz)
                s2 = (-1) ** (py * px)
                s3 = (-1) ** (pz * py)

                term1 = double_bracket(x, y, z)
                term2 = double_bracket(y, z, x)
                term3 = double_bracket(z, x, y)

                combined = {}
                for w, c in term1.items():
                    combined[w] = combined.get(w, Fraction(0)) + Fraction(s1) * c
                for w, c in term2.items():
                    combined[w] = combined.get(w, Fraction(0)) + Fraction(s2) * c
                for w, c in term3.items():
                    combined[w] = combined.get(w, Fraction(0)) + Fraction(s3) * c

                for w, c in combined.items():
                    if c != 0:
                        failures.append((x, y, z, w, c))
                        break

    return failures, total_triples


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), "data")

    all_pass = True

    for n in [1, 2, 3]:
        print(f"\n{'='*60}")
        print(f"Verifying C({n+1}) = osp(2|{2*n}), n={n}")
        print(f"{'='*60}")

        structure = load_structure(data_dir, n)
        n_even = len(structure["basis"]["even"])
        n_odd = len(structure["basis"]["odd"])
        n_total = n_even + n_odd
        print(f"Generators: {n_even} even + {n_odd} odd = {n_total} total")
        print(f"Structure constants: {len(structure['structure_constants'])} entries")

        print("\n--- Anti-symmetry check ---")
        asym_failures = verify_antisymmetry(structure)
        if asym_failures:
            print(f"FAIL: {len(asym_failures)} anti-symmetry violations")
            for x, y, z, lhs, rhs in asym_failures[:5]:
                print(f"  [{x}, {y}] -> {z}: got {lhs}, expected {rhs}")
            all_pass = False
        else:
            print("PASS: All anti-symmetry checks passed")

        print("\n--- Super Jacobi identity check ---")
        jacobi_failures, total_triples = verify_super_jacobi(structure)
        if jacobi_failures:
            print(f"FAIL: {len(jacobi_failures)} Jacobi violations out of {total_triples} triples")
            for x, y, z, w, c in jacobi_failures[:5]:
                print(f"  ({x}, {y}, {z}) -> {w}: residual {c}")
            all_pass = False
        else:
            print(f"PASS: All {total_triples} triples satisfy super Jacobi identity")

    print(f"\n{'='*60}")
    if all_pass:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED")
    print(f"{'='*60}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
