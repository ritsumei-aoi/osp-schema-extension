"""
C(n+1) triviality search.  Issue I08.

Compare Layer 3 (evaluated/symbolic gamma deformation) with Layer 4 (coboundary delta f) to decide
for which gb parameters the inhomogeneous deformation gamma is trivial, i.e. gamma = delta f for some
odd linear map f.

Method (exact rational linear algebra).
  * gamma(X,Y)_Z is linear in the 4n gb parameters.
  * delta f(X,Y)_Z is linear in the P phi parameters of the general odd map f (Schema 4).
  * Triviality for a given gb means: exists phi with  M phi = B gb, where
        M = matrix of phi-coefficients of delta f   (E x P),
        B = matrix of gb-coefficients of gamma      (E x 4n),
        rows E = basis pairs/targets (X<=Y, Z).
  * The set of trivializable gb is the projection onto gb-coordinates of null([M | -B]):
        dim(trivial locus) = dim null([M|-B]) - dim null(M).
    If dim = 4n the deformation is trivial for ALL gb; otherwise the missing directions give explicit
    linear conditions on gb (null space of the trivial-locus spanning matrix).

Run:  python3 src/C_triviality.py
"""

from __future__ import annotations
import json
import os
import sys
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osc_algebra as oa
import C_generators as cg
import C_gamma as cgm
import C_coboundary as ccb

DATA_DIR = cg.DATA_DIR


def gamma_map(n):
    """{(X,Y,Z): sympy expr in gb} for X<=Y."""
    R = cg.realizations(n)
    P = cg.parity_map(n)
    order = cg.pbw_order(n)
    out = {}
    for a in range(len(order)):
        for b in range(a, len(order)):
            X, Y = order[a], order[b]
            _, gam = cgm.split_kappa(cgm.deformed_bracket(X, Y, R, P))
            for Z, c in cg.decompose(gam, n).items():
                out[(X, Y, Z)] = sp.expand(c)
    return out


def deltaf_map(n):
    """{(X,Y,Z): sympy expr in phi} for X<=Y."""
    base = ccb.Base(n)
    order = base.basis
    out = {}
    for a in range(len(order)):
        for b in range(a, len(order)):
            X, Y = order[a], order[b]
            for Z, c in ccb.delta_f(base, X, Y).items():
                out[(X, Y, Z)] = c
    return out


def analyze(n):
    gb_syms = [sp.Symbol(s) for s in cgm.gb_list(n)]
    phi_syms = [sp.Symbol(s) for s in ccb.phi_symbols(ccb.Base(n))]
    gmap = gamma_map(n)
    dmap = deltaf_map(n)

    keys = sorted(set(gmap) | set(dmap))
    E = len(keys)
    P = len(phi_syms)
    G = len(gb_syms)

    M = sp.zeros(E, P)
    B = sp.zeros(E, G)
    phi_index = {s: j for j, s in enumerate(phi_syms)}
    gb_index = {s: j for j, s in enumerate(gb_syms)}

    for i, key in enumerate(keys):
        dexpr = dmap.get(key, sp.Integer(0))
        gexpr = gmap.get(key, sp.Integer(0))
        if dexpr != 0:
            for s in phi_syms:
                M[i, phi_index[s]] = dexpr.coeff(s)
        if gexpr != 0:
            for s in gb_syms:
                B[i, gb_index[s]] = gexpr.coeff(s)

    # Rank-based analysis (exact, fast):
    #   dim(trivial locus) = G - ( rank([M|B]) - rank(M) )
    rankM = M.rank()
    rankB = B.rank()
    MB = M.row_join(B)
    rankMB = MB.rank()
    added = rankMB - rankM                      # independent gamma directions NOT in col(M)
    dimL = G - added

    # Explicit conditions on gb (only needed when the trivial locus is a proper subspace).
    # When dimL == 0 the condition is simply: every gb = 0.
    if dimL == 0:
        conditions = [sp.eye(G)[:, k] for k in range(G)]
        L_rows = []
    else:
        null_MB = M.row_join(-B).nullspace()
        null_M_dim = P - rankM
        L_rows = []
        for v in null_MB:
            g_part = [v[P + k] for k in range(G)]
            if any(x != 0 for x in g_part):
                L_rows.append(g_part)
        Lmat = sp.Matrix(L_rows) if L_rows else sp.zeros(0, G)
        conditions = Lmat.nullspace() if Lmat.rows else []

    return {
        "n": n,
        "num_equations": E,
        "num_phi": P,
        "num_gb": G,
        "rank_M": rankM,
        "rank_B": rankB,
        "rank_MB": rankMB,
        "dim_trivial_locus": dimL,
        "always_trivial": (dimL == G),
        "nontrivial_classes": added,
        "num_conditions": G - dimL,
        "gb_order": [str(s) for s in gb_syms],
        "conditions": [[sp.nsimplify(c[k]) for k in range(G)] for c in conditions],
        "L_basis": [[sp.nsimplify(r[k]) for k in range(G)] for r in L_rows],
    }


def condition_str(coeffs, gb_order):
    terms = []
    for c, name in zip(coeffs, gb_order):
        if c == 0:
            continue
        terms.append(f"({c})*{name}")
    return " + ".join(terms) + " = 0" if terms else "0 = 0"


def main():
    results = {}
    for n in (1, 2, 3):
        print("=" * 70)
        print(f"C({n+1}) triviality analysis (n={n})")
        res = analyze(n)
        results[str(n)] = res
        print(f"  equations={res['num_equations']}, phi={res['num_phi']}, gb={res['num_gb']}")
        print(f"  rank(M)={res['rank_M']} (coboundary space), rank(B)={res['rank_B']}, "
              f"rank([M|B])={res['rank_MB']}")
        print(f"  nontrivial deformation classes = {res['nontrivial_classes']}")
        print(f"  dim(trivial locus in gb-space) = {res['dim_trivial_locus']} / {res['num_gb']}")
        print(f"  ALWAYS TRIVIAL: {res['always_trivial']}  "
              f"(independent conditions on gb: {res['num_conditions']})")
        for c in res["conditions"]:
            print("    condition:", condition_str(c, res["gb_order"]))
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "C_triviality_summary.json"), "w") as f:
        json.dump({k: {kk: (vv if kk not in ("conditions", "L_basis")
                            else [[str(x) for x in row] for row in vv])
                       for kk, vv in v.items()} for k, v in results.items()},
                  f, indent=2)
    print("\nwrote data/C_triviality_summary.json")
    return results


if __name__ == "__main__":
    main()
