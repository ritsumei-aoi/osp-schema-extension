"""Verify graded antisymmetry and the super Jacobi identity for C_{n}_structure.json.

Uses only the JSON data (no oscillator engine), so it is independent of the generator.
Usage:  python3 src/verify_C_structure.py [n ...]      (default n = 1 2 3)
"""
import json
import os
import sys
from fractions import Fraction

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_structure(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as f:
        d = json.load(f)
    sc = {}
    for e in d["structure_constants"]:
        sc.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return d["basis"]["global_order"], d["parity"], sc


def check_antisymmetry(basis, par, sc):
    """[Y,X] = -(-1)^{p(X)p(Y)} [X,Y] for all ordered pairs. Returns list of failures."""
    fails = []
    for X in basis:
        for Y in basis:
            s = -1 if (par[X] and par[Y]) else 1
            xy, yx = sc.get((X, Y), {}), sc.get((Y, X), {})
            for Z in set(xy) | set(yx):
                if yx.get(Z, 0) != -s * xy.get(Z, 0):
                    fails.append((X, Y, Z))
    return fails


def bracket_vec(sc, X, vec):
    """[X, sum_W v_W W] as a dict."""
    out = {}
    for W, c in vec.items():
        for Z, k in sc.get((X, W), {}).items():
            out[Z] = out.get(Z, 0) + c * k
    return {Z: c for Z, c in out.items() if c != 0}


def check_jacobi(basis, par, sc):
    """(-1)^{p(X)p(Z)}[X,[Y,Z]] + (-1)^{p(Y)p(X)}[Y,[Z,X]] + (-1)^{p(Z)p(Y)}[Z,[X,Y]] = 0."""
    fails, count = [], 0
    for X in basis:
        for Y in basis:
            for Z in basis:
                count += 1
                total = {}
                for A, B, C in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
                    sign = -1 if (par[A] and par[C]) else 1
                    for W, c in bracket_vec(sc, A, sc.get((B, C), {})).items():
                        total[W] = total.get(W, 0) + sign * c
                if any(v != 0 for v in total.values()):
                    fails.append((X, Y, Z, {k: str(v) for k, v in total.items() if v}))
    return count, fails


def verify(n):
    basis, par, sc = load_structure(n)
    anti = check_antisymmetry(basis, par, sc)
    count, jac = check_jacobi(basis, par, sc)
    return {"n": n, "dim": len(basis), "pairs": len(basis) ** 2, "antisymmetry_failures": anti,
            "triples": count, "jacobi_failures": jac}


def main(ns):
    ok = True
    for n in ns:
        r = verify(n)
        status = "PASS" if not (r["antisymmetry_failures"] or r["jacobi_failures"]) else "FAIL"
        ok &= status == "PASS"
        print(f"C({n+1}) n={n}: dim={r['dim']}  antisymmetry: {r['pairs']} pairs, "
              f"{len(r['antisymmetry_failures'])} failures  |  super Jacobi: {r['triples']} triples, "
              f"{len(r['jacobi_failures'])} failures  ->  {status}")
        for f in (r["antisymmetry_failures"] + r["jacobi_failures"])[:10]:
            print("   ", f)
    return ok


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    sys.exit(0 if main(ns) else 1)
