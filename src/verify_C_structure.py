"""
Super Jacobi identity and anti-symmetry verification for C(n+1) structure constants.
"""

import json
import sys
from fractions import Fraction


def load_structure(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


def build_bracket_table(structure_constants, all_generators):
    """Build a lookup: (X, Y) -> {Z: coeff} for the graded bracket."""
    table = {}
    for sc in structure_constants:
        X, Y, Z = sc["X"], sc["Y"], sc["Z"]
        coeff = Fraction(sc["coeff"])
        key = (X, Y)
        if key not in table:
            table[key] = {}
        table[key][Z] = table[key].get(Z, Fraction(0)) + coeff
    return table


def bracket(table, parity, X, Y):
    """Return {Z: coeff} for [X, Y}."""
    if (X, Y) in table:
        return dict(table[(X, Y)])
    elif (Y, X) in table:
        sign = Fraction(-1) ** (parity[X] * parity[Y])
        result = {}
        for Z, c in table[(Y, X)].items():
            result[Z] = -sign * c
        return result
    return {}


def verify_antisymmetry(data):
    """Check [X, Y} = -(-1)^{p(X)p(Y)} [Y, X} for all pairs."""
    parity = data["parity"]
    all_gens = data["basis"]["odd"] + data["basis"]["even"]
    table = build_bracket_table(data["structure_constants"], all_gens)
    failures = []

    for i, X in enumerate(all_gens):
        for j, Y in enumerate(all_gens):
            if j <= i:
                continue
            lhs = bracket(table, parity, X, Y)
            rhs_raw = bracket(table, parity, Y, X)
            sign = Fraction(-1) ** (parity[X] * parity[Y])
            rhs = {Z: -sign * c for Z, c in rhs_raw.items()}

            all_Z = set(list(lhs.keys()) + list(rhs.keys()))
            for Z in all_Z:
                l = lhs.get(Z, Fraction(0))
                r = rhs.get(Z, Fraction(0))
                if l != r:
                    failures.append((X, Y, Z, str(l), str(r)))

    return failures


def verify_super_jacobi(data):
    """Check the super Jacobi identity for all triples:
    (-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0
    """
    parity = data["parity"]
    all_gens = data["basis"]["odd"] + data["basis"]["even"]
    table = build_bracket_table(data["structure_constants"], all_gens)
    failures = []

    def bracket_vec(A, B):
        return bracket(table, parity, A, B)

    def double_bracket(A, B, C):
        """Compute [A, [B, C}} as a vector."""
        inner = bracket_vec(B, C)
        result = {}
        for W, c1 in inner.items():
            if W == "scalar":
                continue
            outer = bracket_vec(A, W)
            for Z, c2 in outer.items():
                result[Z] = result.get(Z, Fraction(0)) + c1 * c2
        return result

    n_triples = 0
    for i, X in enumerate(all_gens):
        for j, Y in enumerate(all_gens):
            if j <= i:
                continue
            for k, Z in enumerate(all_gens):
                if k <= j:
                    continue
                n_triples += 1

                pX, pY, pZ = parity[X], parity[Y], parity[Z]

                s1 = Fraction(-1) ** (pX * pZ)
                s2 = Fraction(-1) ** (pY * pX)
                s3 = Fraction(-1) ** (pZ * pY)

                term1 = double_bracket(X, Y, Z)
                term2 = double_bracket(Y, Z, X)
                term3 = double_bracket(Z, X, Y)

                total = {}
                for d, s in [(term1, s1), (term2, s2), (term3, s3)]:
                    for W, c in d.items():
                        total[W] = total.get(W, Fraction(0)) + s * c

                for W, c in total.items():
                    if c != 0:
                        failures.append((X, Y, Z, W, str(c)))

    return failures, n_triples


def main():
    for n in [1, 2, 3]:
        filename = f"data/C_{n}_structure.json"
        print(f"\n=== Verifying C({n+1}) = osp(2|{2*n}) [n={n}] ===")
        data = load_structure(filename)

        anti_failures = verify_antisymmetry(data)
        if anti_failures:
            print(f"  Anti-symmetry: FAIL ({len(anti_failures)} violations)")
            for f in anti_failures[:5]:
                print(f"    [{f[0]}, {f[1]}] -> {f[2]}: LHS={f[3]}, RHS={f[4]}")
        else:
            print("  Anti-symmetry: PASS")

        jacobi_failures, n_triples = verify_super_jacobi(data)
        if jacobi_failures:
            print(f"  Super Jacobi: FAIL ({len(jacobi_failures)} violations in {n_triples} triples)")
            for f in jacobi_failures[:5]:
                print(f"    ({f[0]}, {f[1]}, {f[2]}) -> {f[3]}: residual={f[4]}")
        else:
            print(f"  Super Jacobi: PASS ({n_triples} triples checked)")

    print("\nDone.")


if __name__ == "__main__":
    main()
