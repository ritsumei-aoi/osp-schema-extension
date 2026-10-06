"""Verify anti-symmetry and the super Jacobi identity for data/C_{n}_structure.json.

Works from the JSON alone (independent of the oscillator code in C_generators.py).
Super Jacobi: [X,[Y,Z]] = [[X,Y],Z] + (-1)^{xy} [Y,[X,Z]]  for all ordered triples.
Anti-symmetry: [Y,X] = -(-1)^{xy} [X,Y].
"""
import json
import os
import sys
from fractions import Fraction

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def load_structure(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as f:
        d = json.load(f)
    names = d["basis"]["odd"] + d["basis"]["even"]
    par = d["parity"]
    br = {}
    for e in d["structure_constants"]:
        br.setdefault((e["X"], e["Y"]), {})
        br[(e["X"], e["Y"])][e["Z"]] = br[(e["X"], e["Y"])].get(e["Z"], 0) + Fraction(e["coeff"])
    return names, par, br


def bracket_vec(br, par, u, v):
    """Bilinear extension of the bracket to vectors u, v ({name: coeff})."""
    out = {}
    for x, cx in u.items():
        for y, cy in v.items():
            for z, c in br.get((x, y), {}).items():
                out[z] = out.get(z, 0) + cx * cy * c
    return {k: c for k, c in out.items() if c != 0}


def check_antisymmetry(names, par, br):
    bad = []
    for X in names:
        for Y in names:
            s = -1 if par[X] * par[Y] == 0 else 1
            a = br.get((X, Y), {})
            b = br.get((Y, X), {})
            for z in set(a) | set(b):
                if b.get(z, 0) != s * a.get(z, 0):
                    bad.append((X, Y, z))
    return bad


def check_jacobi(names, par, br):
    bad = []
    count = 0
    for X in names:
        for Y in names:
            xy = (par[X] * par[Y]) % 2
            bxy = br.get((X, Y), {})
            for Z in names:
                count += 1
                lhs = bracket_vec(br, par, {X: 1}, bracket_vec(br, par, {Y: 1}, {Z: 1}))
                r1 = bracket_vec(br, par, bxy, {Z: 1})
                r2 = bracket_vec(br, par, {Y: 1}, bracket_vec(br, par, {X: 1}, {Z: 1}))
                sgn = -1 if xy else 1
                diff = dict(lhs)
                for k, c in r1.items():
                    diff[k] = diff.get(k, 0) - c
                for k, c in r2.items():
                    diff[k] = diff.get(k, 0) - sgn * c
                if any(c != 0 for c in diff.values()):
                    bad.append((X, Y, Z))
    return bad, count


def verify(n):
    names, par, br = load_structure(n)
    anti = check_antisymmetry(names, par, br)
    jac, count = check_jacobi(names, par, br)
    return {"n": n, "dim": len(names), "pairs": len(names) ** 2, "triples": count,
            "antisymmetry_failures": anti, "jacobi_failures": jac,
            "pass": not anti and not jac}


def main(ns=(1, 2, 3)):
    ok = True
    for n in ns:
        r = verify(n)
        ok &= r["pass"]
        print(f"C({n+1}) n={n}: dim={r['dim']} pairs={r['pairs']} triples={r['triples']} "
              f"antisym_fail={len(r['antisymmetry_failures'])} "
              f"jacobi_fail={len(r['jacobi_failures'])} -> {'PASS' if r['pass'] else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
