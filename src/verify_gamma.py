"""Consistency checks of Schema 2 (gamma) against Schema 1, using only the JSON files.

Checks, for generic integer gb:
  (a) gamma(X,Y) has parity p(X)+p(Y)+1 and graded antisymmetry gamma(Y,X) = -(-1)^{p(X)p(Y)} gamma(X,Y)
  (b) the bracket [X,Y} = [X,Y]_0 + kappa*gamma(X,Y) on L = g + kappa g satisfies the super Jacobi identity
      (all triples with at most one kappa-factor; more kappa-factors give zero)
usage: python src/verify_gamma.py
"""
import itertools
import json
import os
import random
from fractions import Fraction

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load(n):
    s1 = json.load(open(os.path.join(DATA, f"C_{n}_structure.json")))
    s2 = json.load(open(os.path.join(DATA, f"C_{n}_gamma.json")))
    return s1, s2


def evaluate_gamma(s2, gb):
    g = {}
    for e in s2["inhomogeneous_deformation"]["gamma_structure"]:
        v = sum(Fraction(t["coeff"]) * gb[t["param"]] for t in e["gamma"])
        if v:
            g.setdefault((e["X"], e["Y"]), {})[e["Z"]] = v
    return g


def _add(acc, other, c):
    for k, v in other.items():
        nv = acc.get(k, 0) + c * v
        if nv:
            acc[k] = nv
        elif k in acc:
            del acc[k]


def check(n, gb=None, seed=0):
    s1, s2 = load(n)
    par = s1["parity"]
    labels = s1["basis"]["odd"] + s1["basis"]["even"]
    g0 = {}
    for t in s1["structure_constants"]:
        g0.setdefault((t["X"], t["Y"]), {})[t["Z"]] = Fraction(t["coeff"])
    if gb is None:
        rnd = random.Random(seed)
        gb = {p: Fraction(rnd.randint(-5, 5)) for p in s2["inhomogeneous_deformation"]["gb_matrix"]["parameters"]}
    gam = evaluate_gamma(s2, gb)
    errors = []
    for X, Y in itertools.product(labels, labels):
        gxy = gam.get((X, Y), {})
        for Z in gxy:
            if par[Z] != (par[X] + par[Y] + 1) % 2:
                errors.append(("parity", X, Y, Z))
        rhs = {}
        _add(rhs, gam.get((Y, X), {}), -(-1) ** (par[X] * par[Y]))
        if gxy != rhs:
            errors.append(("antisym", X, Y))

    # bracket on L: elements are dicts {(Z, e): c}, parity of (Z,e) = p(Z)+e
    def p(el):
        return (par[el[0]] + el[1]) % 2

    def br_basis(x, y):
        (X, ex), (Y, ey) = x, y
        out = {}
        if ex == 0 and ey == 0:
            for Z, c in g0.get((X, Y), {}).items():
                out[(Z, 0)] = c
            for Z, c in gam.get((X, Y), {}).items():
                out[(Z, 1)] = out.get((Z, 1), 0) + c
        elif ex == 0 and ey == 1:  # [X, kappa Y] = (-1)^{p(X)} kappa [X,Y]_0
            for Z, c in g0.get((X, Y), {}).items():
                out[(Z, 1)] = (-1) ** par[X] * c
        elif ex == 1 and ey == 0:  # [kappa X, Y] = kappa [X,Y]_0
            for Z, c in g0.get((X, Y), {}).items():
                out[(Z, 1)] = c
        return {k: v for k, v in out.items() if v}

    def br(A, B):
        out = {}
        for x, cx in A.items():
            for y, cy in B.items():
                _add(out, br_basis(x, y), cx * cy)
        return out

    elems = [(Z, 0) for Z in labels]
    ntrip = 0
    for pos in range(3):
        for X, Y, Z in itertools.product(labels, repeat=3):
            x, y, z = [(W, 0) for W in (X, Y, Z)]
            tr = [x, y, z]
            tr[pos] = (tr[pos][0], 1)
            x, y, z = tr
            lhs = br({x: 1}, br({y: 1}, {z: 1}))
            rhs = br(br({x: 1}, {y: 1}), {z: 1})
            _add(rhs, br({y: 1}, br({x: 1}, {z: 1})), (-1) ** (p(x) * p(y)))
            ntrip += 1
            if lhs != rhs:
                errors.append(("jacobi", x, y, z))
    return {"n": n, "errors": errors, "triples": ntrip, "gamma_nonzero": sum(len(v) for v in gam.values())}


def main():
    ok = True
    for n in (1, 2, 3):
        r = check(n)
        ok &= not r["errors"]
        print(f"n={n} gamma_nonzero={r['gamma_nonzero']} triples_checked={r['triples']} errors={len(r['errors'])}"
              f" -> {'PASS' if not r['errors'] else 'FAIL ' + str(r['errors'][:3])}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
