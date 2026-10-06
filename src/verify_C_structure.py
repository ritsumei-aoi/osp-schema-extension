"""Verify graded antisymmetry and the super Jacobi identity for C_{n}_structure.json.

Works only from the JSON data (independent of the oscillator engine).
Usage:  python3 src/verify_C_structure.py [n ...]      (default: 1 2 3)
Exit status 1 if any check fails.
"""
import json
import os
import sys
from fractions import Fraction

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_structure(n):
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as fh:
        d = json.load(fh)
    basis = d["basis"]["odd"] + d["basis"]["even"]
    sc = {}
    for e in d["structure_constants"]:
        sc.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return d, basis, d["parity"], sc


def br_vec(sc, parity, u, v):
    """Bracket of two vectors (dict label -> Fraction), bilinear extension."""
    out = {}
    for x, cx in u.items():
        for y, cy in v.items():
            for z, c in sc.get((x, y), {}).items():
                out[z] = out.get(z, 0) + cx * cy * c
    return {k: c for k, c in out.items() if c}


def check_antisymmetry(basis, parity, sc):
    fails = []
    for x in basis:
        for y in basis:
            a = sc.get((x, y), {})
            b = sc.get((y, x), {})
            s = -(-1) ** (parity[x] * parity[y])
            for z in set(a) | set(b):
                if a.get(z, 0) != s * b.get(z, 0):
                    fails.append((x, y, z))
    return fails


def check_jacobi(basis, parity, sc):
    """(-1)^{p(X)p(Z)}[X,[Y,Z]] + (-1)^{p(Y)p(X)}[Y,[Z,X]] + (-1)^{p(Z)p(Y)}[Z,[X,Y]] = 0."""
    fails, count = [], 0
    for x in basis:
        for y in basis:
            for z in basis:
                count += 1
                px, py, pz = parity[x], parity[y], parity[z]
                tot = {}
                for sgn, a, (b, c) in (((-1) ** (px * pz), x, (y, z)),
                                       ((-1) ** (py * px), y, (z, x)),
                                       ((-1) ** (pz * py), z, (x, y))):
                    inner = sc.get((b, c), {})
                    for k, v in br_vec(sc, parity, {a: Fraction(1)}, inner).items():
                        tot[k] = tot.get(k, 0) + sgn * v
                tot = {k: v for k, v in tot.items() if v}
                if tot:
                    fails.append((x, y, z, tot))
    return fails, count


def check_parity(parity, sc):
    return [(x, y, z) for (x, y), r in sc.items() for z in r
            if parity[z] != (parity[x] + parity[y]) % 2]


def verify(n, verbose=True):
    d, basis, parity, sc = load_structure(n)
    anti = check_antisymmetry(basis, parity, sc)
    par = check_parity(parity, sc)
    jac, count = check_jacobi(basis, parity, sc)
    ok = not (anti or par or jac)
    if verbose:
        print(f"C({n+1}) n={n}: dim={len(basis)} pairs={len(basis)**2} triples={count} | "
              f"antisymmetry fails={len(anti)} parity fails={len(par)} Jacobi fails={len(jac)} "
              f"-> {'PASS' if ok else 'FAIL'}")
        for f in (anti + par)[:10]:
            print("   ", f)
        for f in jac[:10]:
            print("    Jacobi:", f)
    return ok


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    results = [verify(n) for n in ns]
    print("SUMMARY:", "ALL PASS" if all(results) else "FAILURES PRESENT")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
