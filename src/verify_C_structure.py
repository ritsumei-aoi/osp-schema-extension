"""Verify anti-symmetry and the super Jacobi identity for data/C_{n}_structure.json.

Works only from the JSON (independent of the oscillator code).
Usage: python src/verify_C_structure.py [n ...]
"""
import json
import os
import sys
from fractions import Fraction

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def load(n, data_dir=DATA_DIR):
    d = json.load(open(os.path.join(data_dir, f"C_{n}_structure.json")))
    names = d["basis"]["odd"] + d["basis"]["even"]
    par = d["parity"]
    br = {}
    for e in d["structure_constants"]:
        br.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return names, par, br


def bracket_vec(br, vec_x, vec_y):
    """Bilinear extension of the bracket to dict vectors over basis elements."""
    out = {}
    for x, cx in vec_x.items():
        for y, cy in vec_y.items():
            for z, c in br.get((x, y), {}).items():
                out[z] = out.get(z, 0) + cx * cy * c
    return {k: v for k, v in out.items() if v}


def check_antisymmetry(names, par, br):
    """[X,Y} = -(-1)^{p(X)p(Y)} [Y,X}  for all ordered pairs and all Z."""
    bad = []
    for X in names:
        for Y in names:
            sign = -((-1) ** (par[X] * par[Y]))
            a = br.get((X, Y), {})
            b = br.get((Y, X), {})
            for Z in set(a) | set(b):
                if a.get(Z, 0) != sign * b.get(Z, 0):
                    bad.append((X, Y, Z))
    return bad


def check_jacobi(names, par, br):
    """[X,[Y,Z]] = [[X,Y],Z] + (-1)^{p(X)p(Y)} [Y,[X,Z]]  for all basis triples."""
    bad = []
    count = 0
    for X in names:
        for Y in names:
            xy = (-1) ** (par[X] * par[Y])
            BXY = br.get((X, Y), {})
            for Z in names:
                lhs = bracket_vec(br, {X: 1}, br.get((Y, Z), {}))
                r1 = bracket_vec(br, BXY, {Z: 1})
                r2 = bracket_vec(br, {Y: 1}, br.get((X, Z), {}))
                tot = dict(r1)
                for k, v in r2.items():
                    tot[k] = tot.get(k, 0) + xy * v
                diff = {k: lhs.get(k, 0) - tot.get(k, 0) for k in set(lhs) | set(tot)}
                diff = {k: v for k, v in diff.items() if v}
                count += 1
                if diff:
                    bad.append((X, Y, Z, diff))
    return count, bad


def verify(n, data_dir=DATA_DIR):
    names, par, br = load(n, data_dir)
    anti = check_antisymmetry(names, par, br)
    count, jac = check_jacobi(names, par, br)
    return {"n": n, "dim": len(names), "pairs": len(names) ** 2, "triples": count,
            "antisym_failures": anti, "jacobi_failures": jac}


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    ok = True
    for n in ns:
        r = verify(n)
        status = "PASS" if not r["antisym_failures"] and not r["jacobi_failures"] else "FAIL"
        ok &= status == "PASS"
        print(f"C_{n}: dim={r['dim']} pairs={r['pairs']} triples={r['triples']} "
              f"antisym_failures={len(r['antisym_failures'])} jacobi_failures={len(r['jacobi_failures'])} -> {status}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
