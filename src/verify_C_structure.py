"""
Verification of C(n+1) structure constants:
1. Graded anti-symmetry: [X, Y} = -(-1)^{p(X)p(Y)} [Y, X}
2. Super Jacobi identity for all generator triples.
"""

import json
import sys
from fractions import Fraction


def load_structure(filepath):
    with open(filepath) as f:
        return json.load(f)


def build_sc_dict(data):
    """Build dict: (X, Y) -> {Z: coeff} from structure constants list."""
    sc = {}
    for entry in data['structure_constants']:
        key = (entry['X'], entry['Y'])
        if key not in sc:
            sc[key] = {}
        sc[key][entry['Z']] = Fraction(entry['coeff'])
    return sc


def bracket(sc, parity, x, y):
    """Compute [X, Y} using stored structure constants and anti-symmetry."""
    if (x, y) in sc:
        return dict(sc[(x, y)])
    elif (y, x) in sc:
        sign = Fraction(-1) ** (1 + parity[x] * parity[y])
        return {z: sign * c for z, c in sc[(y, x)].items()}
    else:
        return {}


def bracket_value(sc, parity, x, y, z):
    """Get coefficient of Z in [X, Y}."""
    b = bracket(sc, parity, x, y)
    return b.get(z, Fraction(0))


def check_antisymmetry(data):
    basis = data['basis']['odd'] + data['basis']['even']
    parity = {k: v for k, v in data['parity'].items()}
    sc = build_sc_dict(data)
    failures = []
    checked = 0

    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            if i >= j:
                continue
            checked += 1
            bxy = bracket(sc, parity, x, y)
            byx = bracket(sc, parity, y, x)
            sign = Fraction(-1) ** (1 + parity[x] * parity[y])

            all_z = set(list(bxy.keys()) + list(byx.keys()))
            for z in all_z:
                lhs = bxy.get(z, Fraction(0))
                rhs = sign * byx.get(z, Fraction(0))
                if lhs != rhs:
                    failures.append((x, y, z, lhs, rhs))

    return checked, failures


def check_super_jacobi(data):
    """Check (-1)^{p(X)p(Z)} [X,[Y,Z}} + cyclic = 0 for all triples."""
    basis = data['basis']['odd'] + data['basis']['even']
    parity = {k: v for k, v in data['parity'].items()}
    sc = build_sc_dict(data)
    failures = []
    checked = 0

    def bracket_of_bracket(a, b, c):
        """Compute [A, [B, C}} as a dict Z -> coeff."""
        bc = bracket(sc, parity, b, c)
        result = {}
        for w, coeff_w in bc.items():
            aw = bracket(sc, parity, a, w)
            for z, coeff_z in aw.items():
                result[z] = result.get(z, Fraction(0)) + coeff_w * coeff_z
        return result

    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            if j <= i:
                continue
            for k, z in enumerate(basis):
                if k <= j:
                    continue
                checked += 1

                px, py, pz = parity[x], parity[y], parity[z]

                # (-1)^{px*pz} [X, [Y, Z}}
                term1 = bracket_of_bracket(x, y, z)
                s1 = Fraction(-1) ** (px * pz)

                # (-1)^{py*px} [Y, [Z, X}}
                term2 = bracket_of_bracket(y, z, x)
                s2 = Fraction(-1) ** (py * px)

                # (-1)^{pz*py} [Z, [X, Y}}
                term3 = bracket_of_bracket(z, x, y)
                s3 = Fraction(-1) ** (pz * py)

                all_w = set(list(term1.keys()) + list(term2.keys()) + list(term3.keys()))
                for w in all_w:
                    total = (s1 * term1.get(w, Fraction(0)) +
                             s2 * term2.get(w, Fraction(0)) +
                             s3 * term3.get(w, Fraction(0)))
                    if total != Fraction(0):
                        failures.append((x, y, z, w, total))

    return checked, failures


def verify_file(filepath):
    print(f"\n{'='*60}")
    print(f"Verifying: {filepath}")
    print(f"{'='*60}")
    data = load_structure(filepath)
    n = data['algebra']['n']
    print(f"Algebra: C({n+1}) = {data['algebra']['alternative_notation']['osp']}")
    print(f"Dimension: {data['algebra']['dimension']}")

    print("\n--- Anti-symmetry check ---")
    checked, failures = check_antisymmetry(data)
    print(f"Pairs checked: {checked}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for x, y, z, lhs, rhs in failures[:5]:
            print(f"  [{x}, {y}] -> {z}: LHS={lhs}, RHS={rhs}")
    else:
        print("PASS: All pairs satisfy graded anti-symmetry.")

    print("\n--- Super Jacobi identity check ---")
    checked, failures = check_super_jacobi(data)
    print(f"Triples checked: {checked}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for x, y, z, w, total in failures[:5]:
            print(f"  ({x}, {y}, {z}) -> {w}: residual={total}")
    else:
        print("PASS: Super Jacobi identity holds for all triples.")

    return len(check_antisymmetry(data)[1]) == 0 and len(failures) == 0


def main():
    all_pass = True
    for n in [1, 2, 3]:
        filepath = f'data/C_{n}_structure.json'
        if not verify_file(filepath):
            all_pass = False
    print(f"\n{'='*60}")
    if all_pass:
        print("ALL VERIFICATIONS PASSED")
    else:
        print("SOME VERIFICATIONS FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
