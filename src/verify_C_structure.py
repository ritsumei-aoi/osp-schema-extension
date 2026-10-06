"""Verify graded anti-symmetry and the super Jacobi identity for C_{n}_structure.json.

Works only from the JSON files (independent of the generator code).

  anti-symmetry:  [X,Y] = -(-1)^{p(X)p(Y)} [Y,X]
  super Jacobi:   (-1)^{p(X)p(Z)}[X,[Y,Z]] + (-1)^{p(Y)p(X)}[Y,[Z,X]]
                + (-1)^{p(Z)p(Y)}[Z,[X,Y]] = 0

Usage:  python3 src/verify_C_structure.py [n ...]   (default: 1 2 3)
"""
import json
import os
import sys
from fractions import Fraction

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_structure(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as f:
        d = json.load(f)
    basis = d["basis"]["odd"] + d["basis"]["even"]
    par = d["parity"]
    sc = {}
    for e in d["structure_constants"]:
        sc.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return basis, par, sc


def bracket_vec(sc, X, vec):
    """[X, sum_Y v_Y Y] using structure constants."""
    out = {}
    for Y, c in vec.items():
        for Z, d in sc.get((X, Y), {}).items():
            out[Z] = out.get(Z, 0) + c * d
    return {k: v for k, v in out.items() if v != 0}


def check_parity(basis, par, sc):
    return [(X, Y, Z) for (X, Y), r in sc.items() for Z in r if par[Z] != (par[X] + par[Y]) % 2]


def check_antisymmetry(basis, par, sc):
    fails = []
    for X in basis:
        for Y in basis:
            a = sc.get((X, Y), {})
            b = sc.get((Y, X), {})
            s = -(-1) ** (par[X] * par[Y])
            for Z in set(a) | set(b):
                if a.get(Z, 0) != s * b.get(Z, 0):
                    fails.append((X, Y, Z))
    return fails


def check_jacobi(basis, par, sc):
    fails, count = [], 0
    for X in basis:
        for Y in basis:
            for Z in basis:
                count += 1
                tot = {}
                for (A, B, C) in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
                    sign = (-1) ** (par[A] * par[C])
                    for W, c in bracket_vec(sc, A, sc.get((B, C), {})).items():
                        tot[W] = tot.get(W, 0) + sign * c
                tot = {k: v for k, v in tot.items() if v != 0}
                if tot:
                    fails.append((X, Y, Z, tot))
    return fails, count


def verify(n):
    basis, par, sc = load_structure(n)
    pf = check_parity(basis, par, sc)
    af = check_antisymmetry(basis, par, sc)
    jf, cnt = check_jacobi(basis, par, sc)
    return {"n": n, "dim": len(basis), "pairs": len(basis) ** 2, "triples": cnt,
            "parity_failures": len(pf), "antisymmetry_failures": len(af),
            "jacobi_failures": len(jf), "examples": (pf[:3], af[:3], jf[:3])}


def main(ns):
    ok = True
    for n in ns:
        r = verify(n)
        status = "PASS" if not (r["parity_failures"] or r["antisymmetry_failures"] or r["jacobi_failures"]) else "FAIL"
        ok &= status == "PASS"
        print(f"C({n+1}) n={n}: dim={r['dim']} pairs={r['pairs']} triples={r['triples']} "
              f"parity_fail={r['parity_failures']} antisym_fail={r['antisymmetry_failures']} "
              f"jacobi_fail={r['jacobi_failures']} -> {status}")
        if status == "FAIL":
            print("  examples:", r["examples"])
    return ok


if __name__ == "__main__":
    sys.exit(0 if main([int(a) for a in sys.argv[1:]] or [1, 2, 3]) else 1)
