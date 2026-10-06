"""Consistency of Schema 2 (gamma) with Schema 1 for C(n+1), using the JSON files only.

Checks, for every gb parameter (gamma is linear in gb):
  (1) labels/parity: X,Y,Z in Schema 1 basis (Z may be 'K'), p(Z) = p(X)+p(Y)+1;
  (2) skew-symmetry: gamma(X,Y) = -(-1)^{p(X)p(Y)} gamma(Y,X);
  (3) 2-cocycle identity (order kappa of the super Jacobi identity of [.,.]_gamma), using
      [X, kappa W] = (-1)^{p(X)} kappa [X,W]  and [kappa W, Z] = kappa [W,Z]  (kappa odd, central):
      gamma(X,[Y,Z]) + (-1)^x [X,gamma(Y,Z)] = gamma([X,Y],Z) + [gamma(X,Y),Z]
                                                + (-1)^{xy} ( gamma(Y,[X,Z]) + (-1)^y [Y,gamma(X,Z)] ).
K is central: [K,.] = 0 and gamma(K,.) = 0.
Usage: python src/verify_C_gamma.py [n ...]
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_C_structure import bracket_vec, load  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def load_gamma(n, data_dir=DATA_DIR):
    d = json.load(open(os.path.join(data_dir, f"C_{n}_gamma.json")))
    params = d["inhomogeneous_deformation"]["parameters"]
    gam = {p: {} for p in params}
    for e in d["inhomogeneous_deformation"]["gamma_structure"]:
        for p, c in e["coeff"].items():
            gam[p].setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(c)
    return d, params, gam


def apply_gamma(g, vx, vy):
    out = {}
    for x, cx in vx.items():
        for y, cy in vy.items():
            for z, c in g.get((x, y), {}).items():
                out[z] = out.get(z, 0) + cx * cy * c
    return {k: v for k, v in out.items() if v}


def comb(*terms):
    out = {}
    for s, v in terms:
        for k, c in v.items():
            out[k] = out.get(k, 0) + s * c
    return {k: c for k, c in out.items() if c}


def verify(n, data_dir=DATA_DIR, loaded=None):
    names, par, br = load(n, data_dir)
    d, params, gam = loaded or load_gamma(n, data_dir)
    par = dict(par)
    par["K"] = 0
    report = {"n": n, "params": len(params), "label_parity_failures": [], "skew_failures": [], "cocycle_failures": [],
              "triples": 0}
    allowed = set(names) | {"K"}
    for p in params:
        g = gam[p]
        for (X, Y), zs in g.items():
            for Z in zs:
                if X not in par or Y not in par or Z not in allowed or (par[Z] != (par[X] + par[Y] + 1) % 2):
                    report["label_parity_failures"].append((p, X, Y, Z))
        for X in names:
            for Y in names:
                a, b = g.get((X, Y), {}), g.get((Y, X), {})
                s = -((-1) ** (par[X] * par[Y]))
                for Z in set(a) | set(b):
                    if a.get(Z, 0) != s * b.get(Z, 0):
                        report["skew_failures"].append((p, X, Y, Z))
        for X in names:
            for Y in names:
                for Z in names:
                    x, y = par[X], par[Y]
                    gYZ = g.get((Y, Z), {})
                    # [X, W] with W possibly containing K (central -> drop K)
                    nok = lambda v: {k: c for k, c in v.items() if k != "K"}  # noqa: E731
                    brYZ = br.get((Y, Z), {})
                    brXY = br.get((X, Y), {})
                    brXZ = br.get((X, Z), {})
                    t1 = apply_gamma(g, {X: 1}, brYZ)
                    t2 = bracket_vec(br, {X: 1}, nok(gYZ))
                    r1 = apply_gamma(g, brXY, {Z: 1})
                    r2 = bracket_vec(br, nok(g.get((X, Y), {})), {Z: 1})
                    r3 = apply_gamma(g, {Y: 1}, brXZ)
                    r4 = bracket_vec(br, {Y: 1}, nok(g.get((X, Z), {})))
                    sxy = (-1) ** (x * y)
                    diff = comb((1, t1), ((-1) ** x, t2), (-1, r1), (-1, r2), (-sxy, r3), (-sxy * (-1) ** y, r4))
                    report["triples"] += 1
                    if diff:
                        report["cocycle_failures"].append((p, X, Y, Z, diff))
    return report


def main(argv):
    ok = True
    for n in [int(a) for a in argv] or [1, 2, 3]:
        r = verify(n)
        good = not (r["label_parity_failures"] or r["skew_failures"] or r["cocycle_failures"])
        ok &= good
        print(f"C_{n}: params={r['params']} triples/param={r['triples'] // r['params']} "
              f"label/parity_fail={len(r['label_parity_failures'])} skew_fail={len(r['skew_failures'])} "
              f"cocycle_fail={len(r['cocycle_failures'])} -> {'PASS' if good else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
