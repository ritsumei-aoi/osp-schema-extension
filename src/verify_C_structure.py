"""Verify antisymmetry and the super Jacobi identity from the Schema 1 JSON files only.

usage: python src/verify_C_structure.py
"""
import json
import os
from fractions import Fraction

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load(n):
    d = json.load(open(os.path.join(DATA, f"C_{n}_structure.json")))
    labels = d["basis"]["odd"] + d["basis"]["even"]
    par = d["parity"]
    br = {}
    for t in d["structure_constants"]:
        br.setdefault((t["X"], t["Y"]), {})[t["Z"]] = Fraction(t["coeff"])
    return labels, par, br


def add(acc, other, c):
    for k, v in other.items():
        nv = acc.get(k, 0) + c * v
        if nv:
            acc[k] = nv
        elif k in acc:
            del acc[k]


def bracket_lin(br, A, B):
    out = {}
    for x, cx in A.items():
        for y, cy in B.items():
            add(out, br.get((x, y), {}), cx * cy)
    return out


def verify(n):
    labels, par, br = load(n)
    anti_fail, jac_fail = [], []
    for X in labels:
        for Y in labels:
            lhs = br.get((X, Y), {})
            rhs = {}
            add(rhs, br.get((Y, X), {}), -(-1) ** (par[X] * par[Y]))
            if lhs != rhs:
                anti_fail.append((X, Y))
    for X in labels:
        for Y in labels:
            XY = br.get((X, Y), {})
            for Z in labels:
                # [X,[Y,Z]] = [[X,Y],Z] + (-1)^{p(X)p(Y)} [Y,[X,Z]]
                lhs = bracket_lin(br, {X: 1}, br.get((Y, Z), {}))
                r1 = bracket_lin(br, XY, {Z: 1})
                r2 = bracket_lin(br, {Y: 1}, br.get((X, Z), {}))
                rhs = dict(r1)
                add(rhs, r2, (-1) ** (par[X] * par[Y]))
                if lhs != rhs:
                    jac_fail.append((X, Y, Z))
    N = len(labels)
    return {"n": n, "dim": N, "pairs": N * N, "triples": N ** 3,
            "antisym_failures": anti_fail, "jacobi_failures": jac_fail}


def main():
    ok = True
    for n in (1, 2, 3):
        r = verify(n)
        passed = not r["antisym_failures"] and not r["jacobi_failures"]
        ok &= passed
        print(f"n={n} dim={r['dim']} pairs={r['pairs']} triples={r['triples']} "
              f"antisym_fail={len(r['antisym_failures'])} jacobi_fail={len(r['jacobi_failures'])} "
              f"-> {'PASS' if passed else 'FAIL'}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
