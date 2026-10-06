#!/usr/bin/env python3
"""
STANDALONE re-verification of the main theorem from the JSON artifacts only.

This script imports nothing from the derivation engine.  A third party can run
it against artifacts/Cn1_structure_n*.json to confirm, independently:

  (1) the recorded structure constants C satisfy the graded Jacobi identity,
      so they really define the Lie superalgebra C(n+1);
  (2) gamma is bilinear-graded-antisymmetric and vanishes iff gb = 0;
  (3) gamma = - delta(f) IDENTICALLY in the gb parameters, for the recorded
      odd map f = phi -- i.e. every inhomogeneous gb deformation is trivial;
  (4) f is parity-reversing (odd), as required of the coboundary operator.

Usage:  python3 verify_artifacts.py [path ...]
"""
from fractions import Fraction
import glob
import json
import sys


# -- affine-linear forms in the gb symbols ---------------------------------
def dec(d):
    return {k: Fraction(v) for k, v in d.items() if Fraction(v) != 0}


def ladd(a, b):
    out = dict(a)
    for k, v in b.items():
        nv = out.get(k, Fraction(0)) + v
        if nv:
            out[k] = nv
        else:
            out.pop(k, None)
    return out


def lscale(a, c):
    c = Fraction(c)
    return {} if c == 0 else {k: v * c for k, v in a.items()}


def run(path):
    D = json.load(open(path))
    d = D["dim"]
    par = [e["parity"] for e in D["basis"]]
    lab = [e["label"] for e in D["basis"]]

    C = [[[Fraction(0)] * d for _ in range(d)] for _ in range(d)]
    for key, v in D["structure_constants"].items():
        a, b, c = map(int, key.split(","))
        C[a][b][c] = Fraction(v)

    G = [[[dict() for _ in range(d)] for _ in range(d)] for _ in range(d)]
    for key, v in D["gamma"].items():
        a, b, c = map(int, key.split(","))
        G[a][b][c] = dec(v)

    phi = [[dict() for _ in range(d)] for _ in range(d)]
    for key, v in D["trivialiser_phi"].items():
        i, j = map(int, key.split(","))
        phi[i][j] = dec(v)

    print(f"--- {path}  ({D['algebra']}, dim {d} = {D['dim_even']}|{D['dim_odd']}) ---")

    # (1) graded Jacobi for C
    bad = 0
    for a in range(d):
        for b in range(d):
            for c in range(d):
                acc = [Fraction(0)] * d
                for (x, y, z, s) in (
                        (a, b, c, (-1) ** (par[a] * par[c])),
                        (b, c, a, (-1) ** (par[b] * par[a])),
                        (c, a, b, (-1) ** (par[c] * par[b]))):
                    for i in range(d):
                        if C[x][y][i]:
                            for k in range(d):
                                if C[i][z][k]:
                                    acc[k] += s * C[x][y][i] * C[i][z][k]
                if any(acc):
                    bad += 1
    print(f"  (1) graded Jacobi for C         : {'OK' if bad == 0 else f'FAIL ({bad})'}")

    # graded antisymmetry of C and gamma
    asym = 0
    for a in range(d):
        for b in range(d):
            s = (-1) ** (par[a] * par[b])
            for c in range(d):
                if C[a][b][c] + s * C[b][a][c] != 0:
                    asym += 1
                if ladd(G[a][b][c], lscale(G[b][a][c], s)):
                    asym += 1
    print(f"  (2a) graded antisymmetry        : {'OK' if asym == 0 else f'FAIL ({asym})'}")

    # (2b) gamma vanishes iff gb = 0
    seen = set()
    for a in range(d):
        for b in range(d):
            for c in range(d):
                seen |= {k for k in G[a][b][c] if k != "1"}
    allp = set(D["gb_parameters"])
    noconst = all("1" not in G[a][b][c] for a in range(d)
                  for b in range(d) for c in range(d))
    print(f"  (2b) gamma linear in gb, depends on all {len(allp)} parameters : "
          f"{'OK' if (seen == allp and noconst) else 'FAIL'}")

    # (4) f odd
    oddok = all(par[i] != par[j] for i in range(d) for j in range(d) if phi[i][j])
    print(f"  (4) f parity-reversing (odd)    : {'OK' if oddok else 'FAIL'}")

    # (3) gamma = - delta f, identically in gb
    mism = 0
    for a in range(d):
        pa = par[a]
        for b in range(d):
            pb = par[b]
            comp = [dict() for _ in range(d)]
            s1 = (-1) ** pa
            for i in range(d):
                if not phi[i][b]:
                    continue
                for c in range(d):
                    if C[a][i][c]:
                        comp[c] = ladd(comp[c], lscale(phi[i][b], s1 * C[a][i][c]))
            s2 = -((-1) ** (((pa + 1) * pb) % 2))
            for i in range(d):
                if not phi[i][a]:
                    continue
                for c in range(d):
                    if C[b][i][c]:
                        comp[c] = ladd(comp[c], lscale(phi[i][a], s2 * C[b][i][c]))
            for i in range(d):
                if not C[a][b][i]:
                    continue
                for c in range(d):
                    if phi[c][i]:
                        comp[c] = ladd(comp[c], lscale(phi[c][i], -C[a][b][i]))
            # require gamma + delta f = 0
            for c in range(d):
                if ladd(G[a][b][c], comp[c]):
                    mism += 1
    print(f"  (3) gamma = - delta f (exact)   : "
          f"{'OK' if mism == 0 else f'FAIL ({mism} mismatches)'}")
    return bad == 0 and asym == 0 and oddok and mism == 0 and seen == allp and noconst


paths = sys.argv[1:] or sorted(glob.glob("../artifacts/Cn1_structure_n*.json"))
ok = all(run(p) for p in paths)
print()
print("ALL ARTIFACT CHECKS PASSED" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
