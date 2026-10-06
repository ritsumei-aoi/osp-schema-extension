"""Checks for Schema 4 (C_{n}_coboundary.json).

1. Basis consistency with Schema 1: every X, Y, Z label is in basis (or Z = 'K'), unknown labels
   only couple opposite parities, parity rule p(Z) = p(X)+p(Y)+1.
2. Independent recomputation: for random rational phi/psi, delta f is recomputed with oscillator
   realizations in U(A) (no use of Schema 1 constants) and compared with the stored linear forms.
3. Sign-convention check: f = ad_Z (Z odd) gives delta f = 0 (kappa-conjugation by exp(kappa Z)).
4. delta f is a 2-cocycle: the bracket [,]_0 + kappa*delta f satisfies super Jacobi.

Usage: python3 src/verify_C_coboundary.py [n ...]
"""
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import OscillatorAlgebra  # noqa: E402
from C_generators import Decomposer, realizations  # noqa: E402
from C_coboundary import load_coboundary, load_sc, unknowns, phi_label, psi_label, evaluate_linear  # noqa: E402
from verify_C_gamma import extended_structure, jacobi_on_g  # noqa: E402


def direct_delta_f(n, basis, par, phi, psi):
    """delta f computed from oscillator realizations; phi[(i,j)], psi[j] numeric."""
    alg = OscillatorAlgebra(n)
    R = realizations(n, alg)
    dec = Decomposer(n)
    fR = {}
    for j in basis:
        terms = [R[i] for i in basis if (i, j) in phi]
        coeffs = [phi[(i, j)] for i in basis if (i, j) in phi]
        e = alg.add(*terms, coeffs=coeffs) if terms else {}
        if psi.get(j):
            e = alg.add(e, {(): Fraction(1)}, coeffs=[1, psi[j]])
        fR[j] = e

    def f_of(elem_coords):
        return alg.add(*[fR[V] for V in elem_coords], coeffs=list(elem_coords.values())) \
            if elem_coords else {}

    out = {}
    for X in basis:
        for Y in basis:
            pX, pY = par[X], par[Y]
            br = dec.decompose(alg.bracket(R[X], R[Y]))
            assert "K" not in br
            t1 = alg.bracket(R[X], fR[Y]) if fR[Y] else {}
            t2 = alg.bracket(R[Y], fR[X]) if fR[X] else {}
            res = alg.add(t1, t2, f_of(br),
                          coeffs=[(-1) ** pX, -((-1) ** (((pX + 1) * pY) % 2)), -1])
            coords = dec.decompose(res)
            if coords:
                out[(X, Y)] = coords
    return out


def verify(n, seed=0):
    rng = random.Random(seed)
    basis, par, sc = load_sc(n)
    d, sym = load_coboundary(n)
    res = {"n": n}
    labels = set(basis) | {"K"}
    phis, psis = unknowns(basis, par)
    allowed = {phi_label(i, j) for i, j in phis} | {psi_label(j) for j in psis}
    bad = 0
    for (X, Y), ws in sym.items():
        for W, lin in ws.items():
            bad += X not in labels or Y not in labels or W not in labels
            bad += (0 if W == "K" else par[W]) != (par[X] + par[Y] + 1) % 2
            bad += any(k not in allowed for k in lin)
    res["basis_or_parity_violations"] = bad
    # 2. random phi / psi, independent recomputation
    phi = {(i, j): Fraction(rng.randint(-5, 5), rng.randint(1, 4)) for i, j in phis}
    psi = {j: Fraction(rng.randint(-5, 5), rng.randint(1, 4)) for j in psis}
    values = {phi_label(i, j): v for (i, j), v in phi.items()}
    values.update({psi_label(j): v for j, v in psi.items()})
    stored = evaluate_linear(sym, values)
    direct = direct_delta_f(n, basis, par, phi, psi)
    res["random_phi_mismatch_pairs"] = sum(1 for p in set(stored) | set(direct)
                                           if stored.get(p, {}) != direct.get(p, {}))
    # 3. f = ad_Z for odd Z must be a cocycle-free coboundary: delta(ad_Z) = 0
    nonzero = 0
    for Z in basis:
        if par[Z] != 1:
            continue
        vals = {phi_label(W, j): c for j in basis for W, c in sc.get((Z, j), {}).items()}
        nonzero += bool(evaluate_linear(sym, vals))
    res["delta_adZ_nonzero"] = nonzero
    # 4. cocycle condition for the random delta f
    Lpar, Lsc = extended_structure(basis, par, sc, stored)
    res["cocycle_jacobi_failures"] = jacobi_on_g(basis, Lpar, Lsc)
    res["ok"] = not (bad or res["random_phi_mismatch_pairs"] or nonzero or res["cocycle_jacobi_failures"])
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
