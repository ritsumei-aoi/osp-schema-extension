"""
verify_C_structure.py
Verifies anti-symmetry and Super Jacobi identity for C(n+1) structure constants.

Super Jacobi identity (graded):
  (-1)^{p(X)p(Z)} [X,[Y,Z}] + (-1)^{p(Y)p(X)} [Y,[Z,X}] + (-1)^{p(Z)p(Y)} [Z,[X,Y}] = 0

Anti-symmetry (graded):
  [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}
"""

import json
import os
import sys
from fractions import Fraction


def load_structure(n, data_dir="data"):
    path = os.path.join(data_dir, f"C_{n}_structure.json")
    with open(path) as f:
        return json.load(f)


def build_sc_table(data):
    """Build structure constant lookup: sc[(X,Y)][Z] = Fraction(coeff)."""
    parity = {k: v for k, v in data["parity"].items()}
    sc = {}
    for entry in data["structure_constants"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        if (X, Y) not in sc:
            sc[(X, Y)] = {}
        sc[(X, Y)][Z] = sc[(X, Y)].get(Z, Fraction(0)) + c
    return sc, parity


def bracket(X, Y, sc, parity):
    """Compute [X,Y} returning dict {Z: coeff}. Returns empty if zero."""
    result = {}
    # Direct lookup
    direct = sc.get((X, Y), {})
    for Z, c in direct.items():
        result[Z] = result.get(Z, Fraction(0)) + c
    return {Z: c for Z, c in result.items() if c != 0}


def apply_bracket(v, Y, sc, parity):
    """Apply bracket [v, Y} where v is a linear combination dict."""
    result = {}
    for X, cx in v.items():
        for Z, c in bracket(X, Y, sc, parity).items():
            result[Z] = result.get(Z, Fraction(0)) + cx * c
    return {Z: c for Z, c in result.items() if c != 0}


def check_antisymmetry(data, sc, parity):
    """Check [X,Y} = -(-1)^{p(X)p(Y)} [Y,X} for all pairs."""
    basis = list(data["parity"].keys())
    errors = []
    for X in basis:
        for Y in basis:
            px, py = parity[X], parity[Y]
            xy = bracket(X, Y, sc, parity)
            yx = bracket(Y, X, sc, parity)
            # Expected: [X,Y} + (-1)^{px*py} [Y,X} = 0
            sign = (-1) ** (px * py)
            # Check: for each Z in union of keys
            all_Z = set(xy.keys()) | set(yx.keys())
            for Z in all_Z:
                val = xy.get(Z, Fraction(0)) + sign * yx.get(Z, Fraction(0))
                if val != 0:
                    errors.append(f"Anti-sym fail: [{X},{Y}]_Z={Z}: {val}")
    return errors


def check_jacobi(data, sc, parity):
    """Check graded Jacobi identity for all triples."""
    basis = list(data["parity"].keys())
    errors = []
    for X in basis:
        for Y in basis:
            for Z in basis:
                px, py, pz = parity[X], parity[Y], parity[Z]
                # Term 1: (-1)^{px*pz} [X,[Y,Z}]
                YZ = bracket(Y, Z, sc, parity)
                t1 = apply_bracket({X: Fraction((-1) ** (px * pz))}, "dummy", sc, parity)
                # Recompute properly
                t1 = {}
                for W, c in YZ.items():
                    for V, d in bracket(X, W, sc, parity).items():
                        t1[V] = t1.get(V, Fraction(0)) + ((-1) ** (px * pz)) * c * d

                # Term 2: (-1)^{py*px} [Y,[Z,X}]
                ZX = bracket(Z, X, sc, parity)
                t2 = {}
                for W, c in ZX.items():
                    for V, d in bracket(Y, W, sc, parity).items():
                        t2[V] = t2.get(V, Fraction(0)) + ((-1) ** (py * px)) * c * d

                # Term 3: (-1)^{pz*py} [Z,[X,Y}]
                XY = bracket(X, Y, sc, parity)
                t3 = {}
                for W, c in XY.items():
                    for V, d in bracket(Z, W, sc, parity).items():
                        t3[V] = t3.get(V, Fraction(0)) + ((-1) ** (pz * py)) * c * d

                # Sum all three terms
                all_V = set(t1.keys()) | set(t2.keys()) | set(t3.keys())
                for V in all_V:
                    total = (t1.get(V, Fraction(0)) + t2.get(V, Fraction(0))
                             + t3.get(V, Fraction(0)))
                    if total != 0:
                        errors.append(
                            f"Jacobi fail n={data['algebra']['n']}: "
                            f"[{X},{Y},{Z}]_V={V}: {total}"
                        )
    return errors


def verify_n(n, data_dir="data"):
    data = load_structure(n, data_dir)
    sc, parity = build_sc_table(data)

    print(f"\n=== C_{n}_structure.json (C({n+1}) = osp(2|{2*n})) ===")
    print(f"  Basis size: {len(parity)} generators")
    print(f"  Structure constants: {len(data['structure_constants'])}")

    asym_errors = check_antisymmetry(data, sc, parity)
    if asym_errors:
        print(f"  Anti-symmetry: FAIL ({len(asym_errors)} errors)")
        for e in asym_errors[:5]:
            print(f"    {e}")
    else:
        print("  Anti-symmetry: PASS")

    jac_errors = check_jacobi(data, sc, parity)
    if jac_errors:
        print(f"  Super Jacobi: FAIL ({len(jac_errors)} errors)")
        for e in jac_errors[:5]:
            print(f"    {e}")
    else:
        print("  Super Jacobi: PASS")

    return len(asym_errors) == 0 and len(jac_errors) == 0


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    results = {}
    for n in [1, 2, 3]:
        results[n] = verify_n(n, data_dir)

    print("\n=== Summary ===")
    all_pass = True
    for n, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  n={n} (C({n+1})): {status}")
        if not ok:
            all_pass = False
    print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")
