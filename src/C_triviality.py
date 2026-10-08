"""
Issue I08: triviality search for the inhomogeneous deformation of C(n+1).

Part A — data comparison: Layer 3 (evaluated gamma) vs Layer 4 (delta f of the
canonical odd map), entry by entry, for every n and sign profile.

Part B — independent linear-algebra search: for a *general* odd linear map
f: g -> g with unknown coefficients phi_ij, solve  delta f = gamma  (least squares,
numpy) in two settings:
    strict   : f is g-valued (as in C_coboundary_definition.md)
    extended : f may have a K-component lambda (f: g -> g + C K)
and report residuals, ranks and null-space dimensions.

Part C — the symbolic obstruction: the K-component gamma_K(X,Y) as a linear
form in gb, and the proof-style statement that gamma_K = 0  <=>  gb = 0.

Usage: python3 src/C_triviality.py [n ...]   (default 1 2 3)
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

import numpy as np
import sympy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import C_generators as G  # noqa: E402
import C_gamma as Gm  # noqa: E402
import C_evaluate as E  # noqa: E402
import C_coboundary as C  # noqa: E402


def _dict(entries, key="coeff"):
    return {(e["X"], e["Y"], e["Z"]): Fraction(e[key]) for e in entries}


# ------------------------------------------------------------------ Part A
def compare_layers(n, profile):
    L3 = E.load_evaluated(n, profile)
    L4 = C.load_coboundary(n, profile)
    gam = _dict(L3["evaluated_gamma"]["entries"])
    cob = _dict(L4["coboundary"]["entries"])
    kext = _dict(L4["K_extension"]["entries"])
    gam_g = {k: v for k, v in gam.items() if k[2] != "K"}
    gam_K = {k: v for k, v in gam.items() if k[2] == "K"}
    mism_g = {k: (gam_g.get(k), cob.get(k)) for k in set(gam_g) | set(cob)
              if gam_g.get(k) != cob.get(k)}
    return {
        "n": n, "profile": profile,
        "gamma_terms": len(gam), "gamma_g_terms": len(gam_g), "gamma_K_terms": len(gam_K),
        "deltaf_terms": len(cob),
        "g_part_identical": not mism_g,
        "g_part_mismatches": mism_g,
        "K_part_unmatched_by_strict_f": len(gam_K),       # strict delta f has no K terms
        "K_part_equals_K_extension": gam_K == kext,
        "trivial_strict": len(gam_K) == 0 and not mism_g,
        "trivial_extended": (not mism_g) and gam_K == kext,
        "K_examples": sorted(gam_K.items())[:4],
    }


# ------------------------------------------------------------------ Part B
def general_search(n, profile, extended):
    """Least-squares solve of delta f = gamma over all odd maps f."""
    B = G.basis(n)
    par = G.parity_map(n)
    table = {}
    for e in G.load_structure(n)["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    gam = _dict(E.load_evaluated(n, profile)["evaluated_gamma"]["entries"])

    unknowns = {}
    for Zj in B:
        for Zi in B:
            if par[Zi] == 1 - par[Zj]:
                unknowns[("phi", Zi, Zj)] = len(unknowns)
    if extended:
        for Zj in B:
            unknowns[("lam", Zj)] = len(unknowns)
    nu = len(unknowns)

    rows = {}   # (X,Y,Z) -> {col: coeff}

    def add(X, Y, Z, col, c):
        if c == 0:
            return
        r = rows.setdefault((X, Y, Z), {})
        r[col] = r.get(col, Fraction(0)) + c

    for X in B:
        for Y in B:
            sX = -1 if par[X] else 1
            sY = -1 if ((par[X] + 1) * par[Y]) % 2 else 1
            # (-1)^{|X|} [X, f(Y)]
            for Zi in B:
                if par[Zi] != 1 - par[Y]:
                    continue
                for Z, c in table.get((X, Zi), {}).items():
                    add(X, Y, Z, unknowns[("phi", Zi, Y)], sX * c)
            # -(-1)^{(|X|+1)|Y|} [Y, f(X)]
            for Zi in B:
                if par[Zi] != 1 - par[X]:
                    continue
                for Z, c in table.get((Y, Zi), {}).items():
                    add(X, Y, Z, unknowns[("phi", Zi, X)], -sY * c)
            # - f([X,Y])
            for W, c in table.get((X, Y), {}).items():
                for Zi in B:
                    if par[Zi] == 1 - par[W]:
                        add(X, Y, Zi, unknowns[("phi", Zi, W)], -c)
                if extended:
                    add(X, Y, "K", unknowns[("lam", W)], -c)

    keys = sorted(set(rows) | set(gam))
    # rows with no unknown but nonzero rhs are directly infeasible
    infeasible = [k for k in keys if k not in rows and gam.get(k, 0) != 0]
    active = [k for k in keys if k in rows]
    A = np.zeros((len(active), nu))
    b = np.zeros(len(active))
    for i, k in enumerate(active):
        for col, c in rows[k].items():
            A[i, col] = float(c)
        b[i] = float(gam.get(k, 0))
    sol, _, rank, _ = np.linalg.lstsq(A, b, rcond=None)
    res = float(np.linalg.norm(A @ sol - b))
    res_inf = float(np.sqrt(sum(float(gam[k]) ** 2 for k in infeasible)))
    total_res = float(np.sqrt(res ** 2 + res_inf ** 2))
    return {
        "n": n, "profile": profile, "extended": extended,
        "unknowns": nu, "equations": len(active) + len(infeasible),
        "rank": int(rank), "nullity": nu - int(rank),
        "rows_without_unknowns_but_nonzero_rhs": len(infeasible),
        "residual_active_rows": res, "residual_infeasible_rows": res_inf,
        "residual": total_res,
        "solvable": total_res < 1e-9,
    }


# ------------------------------------------------------------------ Part C
def K_obstruction(n):
    """gamma_K as linear forms in gb; the Cartan-vs-odd pairs that pin down each gb."""
    g2 = Gm.load_gamma(n)
    ent = [e for e in g2["inhomogeneous_deformation"]["entries"] if e["Z"] == "K"]
    forms = {}
    for e in ent:
        forms[(e["X"], e["Y"])] = e["linear_form"]
    # for each gb label find a (H_j, E) pair whose K-term is exactly a multiple of that gb
    cartan = G.cartan_labels(n)
    witnesses = {}
    for lab in [x for row in g2["gb_matrix"]["labels"] for x in row]:
        for (X, Y), lf in forms.items():
            if X in cartan and Y in G.odd_basis(n) and set(lf) == {lab}:
                witnesses[lab] = (X, Y, lf[lab])
                break
    # all gb symbols appear in some K-term?
    appearing = set()
    for lf in forms.values():
        appearing |= set(lf)
    return {"n": n, "K_terms": len(ent), "gb_appearing_in_K_terms": sorted(appearing),
            "all_gb_obstructed": len(appearing) == 4 * n, "witnesses": witnesses}


def main(ns):
    print("=" * 78)
    print("PART A: Layer 3 (evaluated gamma) vs Layer 4 (delta f, canonical odd map)")
    print("=" * 78)
    for n in ns:
        for prof in E.PROFILES:
            r = compare_layers(n, prof)
            print(f"n={n} {prof:12s} gamma terms={r['gamma_terms']:4d} "
                  f"(g: {r['gamma_g_terms']:4d}, K: {r['gamma_K_terms']:3d}) | delta f terms={r['deltaf_terms']:4d} | "
                  f"g-part identical={r['g_part_identical']} | K-part == K_extension={r['K_part_equals_K_extension']} | "
                  f"trivial strict={r['trivial_strict']} extended={r['trivial_extended']}")
            if r["g_part_mismatches"]:
                print("   g-part mismatches:", list(r["g_part_mismatches"].items())[:5])
            if prof in ("all_plus", "single") and r["K_examples"]:
                for (X, Y, Z), v in r["K_examples"]:
                    print(f"   unmatched K-term: gamma({X}, {Y}) ∋ {v} K")
    print()
    print("=" * 78)
    print("PART B: least-squares search over ALL odd maps f (numpy)")
    print("=" * 78)
    for n in ns:
        for prof in E.PROFILES:
            for ext in (False, True):
                r = general_search(n, prof, ext)
                print(f"n={n} {prof:12s} {'extended' if ext else 'strict  '}: unknowns={r['unknowns']:4d} "
                      f"eqs={r['equations']:5d} rank={r['rank']:4d} nullity={r['nullity']:3d} "
                      f"K-rows w/o unknowns={r['rows_without_unknowns_but_nonzero_rhs']:3d} "
                      f"residual(g-rows)={r['residual_active_rows']:.1e} "
                      f"residual(K-rows)={r['residual_infeasible_rows']:.3e} solvable={r['solvable']}")
    print()
    print("=" * 78)
    print("PART C: the K-obstruction as a function of gb")
    print("=" * 78)
    for n in ns:
        r = K_obstruction(n)
        print(f"n={n}: {r['K_terms']} K-terms; gb symbols appearing: {len(r['gb_appearing_in_K_terms'])}/{4*n}; "
              f"all obstructed={r['all_gb_obstructed']}")
        for lab, (X, Y, c) in sorted(r["witnesses"].items()):
            print(f"   gamma_K({X}, {Y}) = {c} * {lab}")


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    main(ns)
