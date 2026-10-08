"""Verify graded antisymmetry and the super Jacobi identity for C(n+1) Schema 1 data.

Usage:  python src/verify_C_structure.py [N ...]   (default N = 1 2 3)

Checks, with exact Fraction arithmetic:
  antisymmetry:  [X,Y] = -(-1)^{p(X)p(Y)} [Y,X]
  super Jacobi:  (-1)^{p(X)p(Z)} [X,[Y,Z]] + cyclic(X,Y,Z) = 0
"""
from fractions import Fraction
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def load(n):
    with open(os.path.join(ROOT, "data", f"C_{n}_structure.json")) as fh:
        return json.load(fh)


def bracket_table(data):
    table = {}
    for e in data["structure_constants"]["brackets"]:
        assert e["kappa_coeff"] == "0", "kappa part not expected in Schema 1"
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return table


def br(table, x, y):
    """[x,y] for basis labels x,y, as a dict {label: Fraction}."""
    return table.get((x, y), {})


def br_vec(table, u, v):
    """[u,v] for linear combinations u, v (dicts label -> coefficient)."""
    out = {}
    for x, cx in u.items():
        for y, cy in v.items():
            for z, c in br(table, x, y).items():
                out[z] = out.get(z, Fraction(0)) + cx * cy * c
    return {k: c for k, c in out.items() if c != 0}


def add(a, b, s=1):
    out = dict(a)
    for k, c in b.items():
        out[k] = out.get(k, Fraction(0)) + s * c
    return {k: c for k, c in out.items() if c != 0}


def check(n):
    data = load(n)
    labels = data["basis"]["odd"] + data["basis"]["even"]
    parity = data["parity"]
    table = bracket_table(data)

    antisym_fail = []
    for x in labels:
        for y in labels:
            sgn = -1 if (parity[x] and parity[y]) else 1
            lhs = br(table, x, y)
            rhs = {k: -sgn * c for k, c in br(table, y, x).items()}
            if lhs != rhs:
                antisym_fail.append((x, y))

    jacobi_fail = []
    for x in labels:
        for y in labels:
            for z in labels:
                # (-1)^{xz}[x,[y,z]] + (-1)^{yx}[y,[z,x]] + (-1)^{zy}[z,[x,y]] = 0
                s1 = -1 if (parity[x] and parity[z]) else 1
                s2 = -1 if (parity[y] and parity[x]) else 1
                s3 = -1 if (parity[z] and parity[y]) else 1
                term1 = br_vec(table, {x: Fraction(1)}, br_vec(table, {y: Fraction(1)}, {z: Fraction(1)}))
                term2 = br_vec(table, {y: Fraction(1)}, br_vec(table, {z: Fraction(1)}, {x: Fraction(1)}))
                term3 = br_vec(table, {z: Fraction(1)}, br_vec(table, {x: Fraction(1)}, {y: Fraction(1)}))
                total = add(add({k: s1 * c for k, c in term1.items()},
                                {k: s2 * c for k, c in term2.items()}),
                            {k: s3 * c for k, c in term3.items()})
                if total:
                    jacobi_fail.append((x, y, z))

    return {
        "n": n,
        "generators": len(labels),
        "ordered_pairs": len(labels) ** 2,
        "triples": len(labels) ** 3,
        "antisymmetry_failures": len(antisym_fail),
        "jacobi_failures": len(jacobi_fail),
        "pass": not antisym_fail and not jacobi_fail,
        "first_failures": (antisym_fail[:3], jacobi_fail[:3]),
    }


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    all_pass = True
    for n in ns:
        r = check(n)
        all_pass &= r["pass"]
        status = "PASS" if r["pass"] else "FAIL"
        print(f"n={n} C({n + 1}): {r['generators']} generators, "
              f"{r['triples']} triples | antisymmetry failures={r['antisymmetry_failures']} "
              f"| Jacobi failures={r['jacobi_failures']} | {status}")
        if not r["pass"]:
            print("  first failures:", r["first_failures"])
    print("OVERALL:", "PASS" if all_pass else "FAIL")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
