"""
Verify Super Jacobi identity and anti-symmetry for C(n+1) structure constants.
Loads C_{n}_structure.json and checks all generator pairs/triples.
"""

import json
import os
import sys
from fractions import Fraction


def load_structure(n):
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    filename = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(filename) as f:
        return json.load(f)


def build_bracket_map(data):
    """Build a dictionary: (X, Y) -> {Z: coeff}"""
    parity = data["parity"]
    bracket = {}
    for sc in data["structure_constants"]:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        c = Fraction(sc["coeff"])
        if (X, Y) not in bracket:
            bracket[(X, Y)] = {}
        bracket[(X, Y)][Z] = bracket[(X, Y)].get(Z, Fraction(0)) + c

        px, py = parity[X], parity[Y]
        sign = (-1) ** (px * py)
        if (Y, X) not in bracket:
            bracket[(Y, X)] = {}
        bracket[(Y, X)][Z] = bracket[(Y, X)].get(Z, Fraction(0)) - sign * c

    return bracket


def get_bracket(bracket_map, X, Y):
    """Return {Z: coeff} for [X, Y]."""
    return bracket_map.get((X, Y), {})


def verify_antisymmetry(data):
    """Check [X, Y] = -(-1)^{p(X)p(Y)} [Y, X] for all pairs."""
    parity = data["parity"]
    all_basis = data["basis"]["odd"] + data["basis"]["even"]
    bracket = build_bracket_map(data)
    failures = []

    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            if j <= i:
                continue
            px, py = parity[X], parity[Y]
            sign = (-1) ** (px * py)

            lhs = get_bracket(bracket, X, Y)
            rhs_raw = get_bracket(bracket, Y, X)

            all_Z = set(lhs.keys()) | set(rhs_raw.keys())
            for Z in all_Z:
                lhs_val = lhs.get(Z, Fraction(0))
                rhs_val = rhs_raw.get(Z, Fraction(0))
                expected = -sign * rhs_val
                if lhs_val != expected:
                    failures.append((X, Y, Z, lhs_val, expected))

    return failures


def verify_super_jacobi(data):
    """Check Super Jacobi identity for all triples:
    (-1)^{p(X)p(Z)} [X,[Y,Z]] + (-1)^{p(Y)p(X)} [Y,[Z,X]] + (-1)^{p(Z)p(Y)} [Z,[X,Y]] = 0
    """
    parity = data["parity"]
    all_basis = data["basis"]["odd"] + data["basis"]["even"]
    bracket = build_bracket_map(data)
    failures = []

    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            if j <= i:
                continue
            for k, Z in enumerate(all_basis):
                if k <= j:
                    continue

                px, py, pz = parity[X], parity[Y], parity[Z]

                term1 = double_bracket(bracket, X, Y, Z, parity)
                sign1 = (-1) ** (px * pz)

                term2 = double_bracket(bracket, Y, Z, X, parity)
                sign2 = (-1) ** (py * px)

                term3 = double_bracket(bracket, Z, X, Y, parity)
                sign3 = (-1) ** (pz * py)

                total = {}
                for W in set(list(term1.keys()) + list(term2.keys()) + list(term3.keys())):
                    val = (sign1 * term1.get(W, Fraction(0)) +
                           sign2 * term2.get(W, Fraction(0)) +
                           sign3 * term3.get(W, Fraction(0)))
                    if val != 0:
                        total[W] = val

                if total:
                    failures.append((X, Y, Z, total))

    return failures


def double_bracket(bracket_map, A, B, C, parity):
    """Compute [A, [B, C]] expressed in the basis."""
    inner = get_bracket(bracket_map, B, C)
    result = {}
    for W, cw in inner.items():
        outer = get_bracket(bracket_map, A, W)
        for V, cv in outer.items():
            result[V] = result.get(V, Fraction(0)) + cw * cv
    return {k: v for k, v in result.items() if v != 0}


def main():
    for n in [1, 2, 3]:
        print(f"\n=== Verifying C({n+1}) = osp(2|{2*n}), n={n} ===")
        data = load_structure(n)

        all_basis = data["basis"]["odd"] + data["basis"]["even"]
        n_gens = len(all_basis)
        n_pairs = n_gens * (n_gens - 1) // 2
        n_triples = n_gens * (n_gens - 1) * (n_gens - 2) // 6

        print(f"  Generators: {n_gens}")
        print(f"  Pairs to check: {n_pairs}")
        print(f"  Triples to check: {n_triples}")

        anti_failures = verify_antisymmetry(data)
        if anti_failures:
            print(f"  ANTI-SYMMETRY FAILURES: {len(anti_failures)}")
            for f in anti_failures[:5]:
                print(f"    [{f[0]}, {f[1]}] -> {f[2]}: got {f[3]}, expected {f[4]}")
        else:
            print(f"  Anti-symmetry: PASS ({n_pairs} pairs checked)")

        jacobi_failures = verify_super_jacobi(data)
        if jacobi_failures:
            print(f"  SUPER JACOBI FAILURES: {len(jacobi_failures)}")
            for f in jacobi_failures[:5]:
                print(f"    ({f[0]}, {f[1]}, {f[2]}): residual = {f[3]}")
        else:
            print(f"  Super Jacobi: PASS ({n_triples} triples checked)")

    print("\n=== Verification complete ===")


if __name__ == "__main__":
    main()
