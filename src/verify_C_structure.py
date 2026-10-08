"""
verify_C_structure.py
Verify anti-symmetry and Super Jacobi identity for C(n+1) structure constants.

Super Jacobi identity:
  (-1)^{p(X)p(Z)} [X,[Y,Z]] + (-1)^{p(Y)p(X)} [Y,[Z,X]] + (-1)^{p(Z)p(Y)} [Z,[X,Y]] = 0

Anti-symmetry (graded):
  [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]
"""

import json
import os
import sys
from fractions import Fraction
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_structure(n):
    path = os.path.join(DATA_DIR, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def build_bracket_table(data):
    """
    Build a dictionary: (X, Y) -> {Z: Fraction(coeff), ...}
    covering all pairs. Includes anti-symmetry expansion.
    K is treated as a special generator with parity 0.
    """
    parity = data["parity"]
    parity["K"] = 0  # central element, even

    table = defaultdict(lambda: defaultdict(Fraction))

    for entry in data["structure_constants"]:
        X, Y = entry["X"], entry["Y"]
        for term in entry["result"]:
            Z = term["Z"]
            c = Fraction(term["coeff"])
            table[(X, Y)][Z] += c

    # Expand anti-symmetry: [X,Y] = -(-1)^{p(X)p(Y)} [Y,X]
    all_pairs = list(table.keys())
    for (X, Y) in all_pairs:
        px = parity.get(X, 0)
        py = parity.get(Y, 0)
        sign = Fraction(-1) * Fraction((-1) ** (px * py))
        for Z, c in table[(X, Y)].items():
            table[(Y, X)][Z] += sign * c

    return table, parity


def bracket(table, X, Y):
    """Return {Z: coeff} for [X, Y]."""
    return dict(table[(X, Y)])


def linear_combo_bracket(table, parity, combo, gen):
    """
    Compute [combo, gen] where combo = {Z: coeff} (linear combination).
    Result: {Z: coeff}
    """
    result = defaultdict(Fraction)
    for (G, c) in combo.items():
        if G == "K":
            continue  # K is central
        sub = table[(G, gen)]
        # We need graded bracket: [c*G, gen] = c * [G, gen]
        # The graded sign is built into table already
        for Z, coeff in sub.items():
            result[Z] += c * coeff
    return dict(result)


def add_combos(a, b):
    result = defaultdict(Fraction)
    for Z, c in a.items():
        result[Z] += c
    for Z, c in b.items():
        result[Z] += c
    return {Z: c for Z, c in result.items() if c != 0}


def scale_combo(combo, factor):
    return {Z: c * factor for Z, c in combo.items() if c * factor != 0}


def verify_n(n, verbose=False):
    data = load_structure(n)
    table, parity = build_bracket_table(data)

    basis_all = data["basis"]["even"] + data["basis"]["odd"]

    # --- Anti-symmetry check ---
    antisym_failures = []
    for X in basis_all:
        for Y in basis_all:
            px = parity[X]
            py = parity[Y]
            xy = table[(X, Y)]
            yx = table[(Y, X)]
            # [X,Y] should = -(-1)^{px*py} [Y,X]
            sign = Fraction((-1) ** (px * py + 1))
            for Z in set(list(xy.keys()) + list(yx.keys())):
                lhs = xy.get(Z, Fraction(0))
                rhs = sign * yx.get(Z, Fraction(0))
                if lhs != rhs:
                    antisym_failures.append(
                        f"Antisym fail: [{X},{Y}]_Z={Z}: {lhs} != {rhs}")

    # --- Super Jacobi identity ---
    jacobi_failures = []
    for X in basis_all:
        for Y in basis_all:
            for Z in basis_all:
                px = parity[X]
                py = parity[Y]
                pz = parity[Z]

                # Term 1: (-1)^{px*pz} [X, [Y,Z]]
                yz = table[(Y, Z)]
                x_yz = linear_combo_bracket(table, parity, yz, X)
                # Wait: [X, [Y,Z]] but we need [X, linear combo of basis]
                # Actually: compute [X, Σ c_W W] = Σ c_W [X, W]
                x_yz = defaultdict(Fraction)
                for W, c in table[(Y, Z)].items():
                    if W == "K":
                        continue
                    for V, cv in table[(X, W)].items():
                        x_yz[V] += c * cv
                term1 = scale_combo(dict(x_yz), Fraction((-1) ** (px * pz)))

                # Term 2: (-1)^{py*px} [Y, [Z,X]]
                zx = table[(Z, X)]
                y_zx = defaultdict(Fraction)
                for W, c in zx.items():
                    if W == "K":
                        continue
                    for V, cv in table[(Y, W)].items():
                        y_zx[V] += c * cv
                term2 = scale_combo(dict(y_zx), Fraction((-1) ** (py * px)))

                # Term 3: (-1)^{pz*py} [Z, [X,Y]]
                xy = table[(X, Y)]
                z_xy = defaultdict(Fraction)
                for W, c in xy.items():
                    if W == "K":
                        continue
                    for V, cv in table[(Z, W)].items():
                        z_xy[V] += c * cv
                term3 = scale_combo(dict(z_xy), Fraction((-1) ** (pz * py)))

                total = add_combos(add_combos(term1, term2), term3)
                if any(c != 0 for c in total.values()):
                    jacobi_failures.append(
                        f"Jacobi fail: ({X},{Y},{Z}) -> {dict(total)}")

    return antisym_failures, jacobi_failures


def main():
    total_antisym = 0
    total_jacobi = 0
    for n in [1, 2, 3]:
        print(f"\n=== C({n+1}) = osp(2|{2*n}), n={n} ===")
        af, jf = verify_n(n)
        if af:
            print(f"  ANTISYM FAILURES ({len(af)}):")
            for msg in af[:5]:
                print(f"    {msg}")
        else:
            print(f"  Anti-symmetry: PASS")
        if jf:
            print(f"  JACOBI FAILURES ({len(jf)}):")
            for msg in jf[:5]:
                print(f"    {msg}")
        else:
            print(f"  Super Jacobi: PASS")
        total_antisym += len(af)
        total_jacobi += len(jf)

    print(f"\nSummary: {total_antisym} anti-symmetry failures, {total_jacobi} Jacobi failures")
    return total_antisym + total_jacobi


if __name__ == "__main__":
    code = main()
    sys.exit(0 if code == 0 else 1)
