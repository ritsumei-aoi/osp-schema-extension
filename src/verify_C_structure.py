"""Verify super-antisymmetry and the super-Jacobi identity of C(n+1) structure constants.

Works only from data/C_{n}_structure.json (independent of the generator code).
Usage: python src/verify_C_structure.py [n ...]
"""
import json
import os
import sys
from fractions import Fraction

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_structure(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as fh:
        return json.load(fh)


def bracket_table(entries):
    """{(X,Y): {Z: Fraction}}"""
    tab = {}
    for e in entries:
        tab.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return tab


def lin_bracket(tab, X, vec):
    """[X, sum_c c*W} for a vector {W: c}."""
    out = {}
    for W, c in vec.items():
        for Z, d in tab.get((X, W), {}).items():
            out[Z] = out.get(Z, 0) + c * d
    return out


def check_antisymmetry(basis, parity, tab):
    """[Y,X} = -(-1)^{p(X)p(Y)} [X,Y}. Returns list of failing pairs."""
    fails = []
    for X in basis:
        for Y in basis:
            s = -(-1) ** (parity[X] * parity[Y])
            a, b = tab.get((X, Y), {}), tab.get((Y, X), {})
            for Z in set(a) | set(b):
                if b.get(Z, 0) != s * a.get(Z, 0):
                    fails.append((X, Y, Z, a.get(Z, 0), b.get(Z, 0)))
    return fails


def check_grading(parity, tab):
    return [(X, Y, Z) for (X, Y), v in tab.items() for Z in v
            if parity[Z] != (parity[X] + parity[Y]) % 2]


def jacobiator(tab, parity, X, Y, Z):
    """(-1)^{pXpZ}[X,[Y,Z]] + (-1)^{pYpX}[Y,[Z,X]] + (-1)^{pZpY}[Z,[X,Y]]."""
    out = {}
    for (A, B, C) in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
        s = (-1) ** (parity[A] * parity[C])
        for W, c in lin_bracket(tab, A, tab.get((B, C), {})).items():
            out[W] = out.get(W, 0) + s * c
    return {W: c for W, c in out.items() if c != 0}


def check_jacobi(basis, parity, tab):
    fails, count = [], 0
    for X in basis:
        for Y in basis:
            for Z in basis:
                count += 1
                j = jacobiator(tab, parity, X, Y, Z)
                if j:
                    fails.append((X, Y, Z, j))
    return count, fails


def verify(n, verbose=True):
    s = load_structure(n)
    basis, parity = s["basis"]["ordering"], s["parity"]
    tab = bracket_table(s["structure_constants"])
    anti = check_antisymmetry(basis, parity, tab)
    grad = check_grading(parity, tab)
    ntrip, jac = check_jacobi(basis, parity, tab)
    report = {"n": n, "dim": len(basis), "pairs": len(basis) ** 2,
              "antisymmetry_failures": len(anti), "grading_failures": len(grad),
              "triples": ntrip, "jacobi_failures": len(jac)}
    report["status"] = "PASS" if not (anti or grad or jac) else "FAIL"
    if verbose:
        print(report)
        for f in (anti + grad + jac)[:10]:
            print("  failure:", f)
    return report


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    reports = [verify(n) for n in ns]
    sys.exit(0 if all(r["status"] == "PASS" for r in reports) else 1)
