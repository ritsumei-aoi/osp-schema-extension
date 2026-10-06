"""Consistency checks for Schema 2 (C_{n}_gamma.json) against Schema 1.

1. kappa-free part of every deformed oscillator bracket == Schema 1 structure constants.
2. Parity rule p(Z) = p(X)+p(Y)+1 (K even) and graded antisymmetry of gamma.
3. Linearity: gamma recomputed at a generic numeric gb == symbolic gamma evaluated there.
4. Cocycle / Jacobi: the deformed bracket on L = g + kappa*g + C*kappa satisfies super Jacobi
   for every triple of g, for every unit gb vector (hence, by linearity, for all gb).

Usage: python3 src/verify_C_gamma.py [n ...]
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import gb_labels  # noqa: E402
from C_gamma import deformed_bracket_parts, evaluate_gamma  # noqa: E402
from verify_C_structure import load_structure, bracket_vec  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_gamma(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_gamma.json")) as f:
        d = json.load(f)
    gamma = {}
    for e in d["inhomogeneous_deformation"]["gamma"]:
        gamma.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {g: Fraction(c) for g, c in e["coeff"].items()}
    return d, gamma


def extended_structure(basis, par, sc, gam_num):
    """Structure constants of L = g + kappa*g + C*kappa for a numeric gamma.

    Labels: Z, 'k*Z' (kappa Z, parity p(Z)+1), 'kappa' (kappa K, parity 1).
    """
    Lsc = {}
    for X in basis:
        for Y in basis:
            v = dict(sc.get((X, Y), {}))
            for Z, c in gam_num.get((X, Y), {}).items():
                v["kappa" if Z == "K" else "k*" + Z] = c
            if v:
                Lsc[(X, Y)] = v
            sX = -1 if par[X] else 1
            if (X, Y) in sc:
                Lsc[(X, "k*" + Y)] = {"k*" + Z: sX * c for Z, c in sc[(X, Y)].items()}
                Lsc[("k*" + X, Y)] = {"k*" + Z: c for Z, c in sc[(X, Y)].items()}
    Lpar = dict(par)
    Lpar.update({"k*" + Z: 1 - par[Z] for Z in basis})
    Lpar["kappa"] = 1
    return Lpar, Lsc


def jacobi_on_g(basis, Lpar, Lsc):
    fails = 0
    for X in basis:
        for Y in basis:
            for Z in basis:
                total = {}
                for A, B, C in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
                    sign = -1 if (Lpar[A] and Lpar[C]) else 1
                    for W, c in bracket_vec(Lsc, A, Lsc.get((B, C), {})).items():
                        total[W] = total.get(W, 0) + sign * c
                fails += any(v != 0 for v in total.values())
    return fails


def verify(n):
    basis, par, sc = load_structure(n)
    d, gamma = load_gamma(n)
    res = {"n": n}
    # 1. kappa-free part vs Schema 1 (recomputed with all gb non-zero)
    generic = {g: Fraction(i + 2, 3) * (-1) ** i for i, g in enumerate(gb_labels(n))}
    parts = deformed_bracket_parts(n, generic)
    res["schema1_mismatch"] = sum(1 for p, (b0, _) in parts.items()
                                  if {k: v for k, v in b0.items()} != sc.get(p, {}))
    # 2. parity and antisymmetry
    bad_par = 0
    bad_anti = 0
    for (X, Y), zs in gamma.items():
        for Z in zs:
            pz = 0 if Z == "K" else par[Z]
            bad_par += pz != (par[X] + par[Y] + 1) % 2
        s = -1 if (par[X] and par[Y]) else 1
        rev = gamma.get((Y, X), {})
        for Z in set(zs) | set(rev):
            if rev.get(Z, {}) != {g: -s * c for g, c in zs.get(Z, {}).items()}:
                bad_anti += 1
    res["parity_violations"], res["antisymmetry_violations"] = bad_par, bad_anti
    # 3. linearity at the generic point
    sym_eval = evaluate_gamma(gamma, generic)
    direct = {p: g for p, (_, g) in parts.items() if g}
    res["linearity_mismatch"] = sum(1 for p in set(sym_eval) | set(direct)
                                    if sym_eval.get(p, {}) != direct.get(p, {}))
    # 4. Jacobi of the deformed bracket for each unit gb vector
    jf = 0
    for g in gb_labels(n):
        Lpar, Lsc = extended_structure(basis, par, sc, evaluate_gamma(gamma, {g: 1}))
        jf += jacobi_on_g(basis, Lpar, Lsc)
    res["deformed_jacobi_failures"] = jf
    res["triples_per_gb"] = len(basis) ** 3
    res["ok"] = not (res["schema1_mismatch"] or bad_par or bad_anti or res["linearity_mismatch"] or jf)
    return res


def main(ns):
    ok = True
    for n in ns:
        r = verify(n)
        ok &= r["ok"]
        print(f"n={n}: " + ", ".join(f"{k}={v}" for k, v in r.items() if k != "n")
              + ("  -> PASS" if r["ok"] else "  -> FAIL"))
    return ok


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    sys.exit(0 if main(ns) else 1)
