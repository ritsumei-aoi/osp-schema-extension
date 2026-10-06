"""Verify anti-symmetry and the super Jacobi identity for data/C_{n}_structure.json.

    [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}
    [X,[Y,Z}} = [[X,Y},Z} + (-1)^{p(X)p(Y)} [Y,[X,Z}}     (all triples)
"""
import json
import os
import sys
from fractions import Fraction

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_structure(path):
    with open(path) as fh:
        d = json.load(fh)
    labels = d["basis"]["odd"] + d["basis"]["even"]
    sc = {}
    for e in d["structure_constants"]:
        sc.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return labels, d["parity"], sc


def br(sc, X, Y):
    return sc.get((X, Y), {})


def br_vec(sc, vec, Y):
    """[vec, Y} for vec = {label: coeff}."""
    out = {}
    for x, cx in vec.items():
        for z, c in br(sc, x, Y).items():
            out[z] = out.get(z, 0) + cx * c
    return out


def br_left(sc, X, vec):
    out = {}
    for y, cy in vec.items():
        for z, c in br(sc, X, y).items():
            out[z] = out.get(z, 0) + cy * c
    return out


def check_antisymmetry(labels, par, sc):
    bad = []
    for X in labels:
        for Y in labels:
            s = -1 if (par[X] and par[Y]) else 1
            a = br(sc, X, Y)
            b = br(sc, Y, X)
            for z in set(a) | set(b):
                if a.get(z, 0) != -s * b.get(z, 0):
                    bad.append((X, Y, z))
    return bad


def check_jacobi(labels, par, sc):
    bad, count = [], 0
    for X in labels:
        for Y in labels:
            sXY = -1 if (par[X] and par[Y]) else 1
            XY = br(sc, X, Y)
            for Z in labels:
                count += 1
                lhs = br_left(sc, X, br(sc, Y, Z))
                rhs = dict(br_vec(sc, XY, Z))
                for z, c in br_left(sc, Y, br(sc, X, Z)).items():
                    rhs[z] = rhs.get(z, 0) + sXY * c
                if any(lhs.get(z, 0) != rhs.get(z, 0) for z in set(lhs) | set(rhs)):
                    bad.append((X, Y, Z))
    return bad, count


def verify(n, data_dir=DATA_DIR):
    labels, par, sc = load_structure(os.path.join(data_dir, f"C_{n}_structure.json"))
    anti = check_antisymmetry(labels, par, sc)
    jac, count = check_jacobi(labels, par, sc)
    return {"n": n, "dim": len(labels), "pairs": len(labels) ** 2, "triples": count,
            "antisymmetry_failures": anti, "jacobi_failures": jac}


def main():
    ok = True
    for n in (1, 2, 3):
        r = verify(n)
        passed = not r["antisymmetry_failures"] and not r["jacobi_failures"]
        ok &= passed
        print(f"C_{n} (dim {r['dim']}): pairs={r['pairs']} triples={r['triples']} "
              f"antisym_fail={len(r['antisymmetry_failures'])} jacobi_fail={len(r['jacobi_failures'])} "
              f"-> {'PASS' if passed else 'FAIL'}")
    print("OVERALL:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
