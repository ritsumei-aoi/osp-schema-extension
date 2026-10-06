"""Triviality search for the inhomogeneous deformation of C(n+1) = osp(2|2n).

(1) Layer 3 vs Layer 4 comparison for every (n, profile), pair by pair.
(2) Explicit identity  gamma_K(X,Y) = -f_K([X,Y])  for the central (κK) residue.
(3) Independent linear-algebra search over *all* odd linear maps f (not just the reference f):
    which gb give gamma_gb in the image of δ ?  Three target spaces:
      strict   : f : g -> g,         γ must be the full κ-part (g-valued part AND κK residue)
      g-part   : f : g -> g,         γ = g-valued part only (K residue ignored)
      extended : f : g -> g ⊕ CK,    γ = full κ-part
Usage: python src/triviality_search.py
"""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import C_coboundary as cb  # noqa: E402
import C_evaluate as ev  # noqa: E402
import C_generators as cg  # noqa: E402

DATA = cg.DATA


# ---------------------------------------------------------------------------
# (1) + (2): data comparison
# ---------------------------------------------------------------------------
def compare_layers(n, name):
    d3 = json.load(open(ev.output_path(n, name)))["evaluated_deformation"]
    d4 = json.load(open(cb.output_path(n, name)))
    g3 = {(e["X"], e["Y"], e["Z"]): F(e["coeff"]) for e in d3["gamma"]}
    g4 = {(e["X"], e["Y"], e["Z"]): F(e["coeff"]) for e in d4["coboundary"]["delta_f"]}
    k3 = {(e["X"], e["Y"]): F(e["coeff"]) for e in d3["central_component"]}
    mism = sorted(k for k in set(g3) | set(g4) if g3.get(k, 0) != g4.get(k, 0))
    # K-identity: gamma_K(X,Y) == -f_K([X,Y])
    s1 = json.load(open(DATA / f"C_{n}_structure.json"))
    T = {}
    for e in s1["structure_constants"]:
        T.setdefault((e["X"], e["Y"]), {})[e["Z"]] = F(e["coeff"])
    fK = {e["X"]: F(e["coeff"]) for e in d4["odd_map"]["central_component"]}
    pred = {}
    for (X, Y), comps in T.items():
        v = -sum((c * fK.get(Z, F(0)) for Z, c in comps.items()), F(0))
        if v:
            pred[(X, Y)] = v
    return {"g_mismatches": mism, "n_gamma": len(g3), "n_central": len(k3), "central": k3,
            "k_identity_ok": pred == k3, "fK": fK}


# ---------------------------------------------------------------------------
# (3): linear algebra over all odd maps
# ---------------------------------------------------------------------------
def build_system(alg, table):
    """Columns of δ over all odd f (g-valued) and optional K-valued f, rows = (X,Y,Z or 'K')."""
    even, odd = alg.even, alg.odd
    unknowns = [(s, d) for s in even for d in odd] + [(s, d) for s in odd for d in even]
    rows = {}

    def row(key):
        if key not in rows:
            rows[key] = len(rows)
        return rows[key]

    data, ri, ci = [], [], []
    for c, (src, dst) in enumerate(unknowns):
        for (X, Y), comps in cb.coboundary(alg, table, {src: {dst: F(1)}}).items():
            for Z, v in comps.items():
                data.append(float(v)); ri.append(row((X, Y, Z))); ci.append(c)
    nA = len(unknowns)
    # K-valued part of f (odd source only): (δf)_K(X,Y) = -f_K([X,Y])
    for k, src in enumerate(odd):
        for (X, Y), comps in table.items():
            if src in comps:
                data.append(-float(comps[src])); ri.append(row((X, Y, "K"))); ci.append(nA + k)
    return unknowns, rows, data, ri, ci, nA, len(odd)


def search(n):
    alg = cg.CAlgebra(n)
    table = cg.structure_table(alg)
    gamma, central = cg.gamma_table(alg)
    syms = cg.gb_names(n)
    unknowns, rows, data, ri, ci, nA, nK = build_system(alg, table)

    def row(key):
        if key not in rows:
            rows[key] = len(rows)
        return rows[key]

    # right-hand sides (columns = gb symbols); g-valued and K parts separately flagged
    gd, gr, gc = [], [], []
    for (X, Y), comps in gamma.items():
        for Z, cm in comps.items():
            for s, v in cm.items():
                gd.append(float(v)); gr.append(row((X, Y, Z))); gc.append(syms.index(s))
    for (X, Y), cm in central.items():
        for s, v in cm.items():
            gd.append(float(v)); gr.append(row((X, Y, "K"))); gc.append(syms.index(s))
    nrows = len(rows)
    A_full = np.zeros((nrows, nA + nK))
    np.add.at(A_full, (ri, ci), data)  # only rows with a non-zero entry exist, so this stays small
    G_full = np.zeros((nrows, len(syms)))
    np.add.at(G_full, (gr, gc), gd)
    isK = np.array([k[2] == "K" for k in sorted(rows, key=rows.get)])
    A_g = A_full[:, :nA]

    def trivial_dim(A, G):
        x = np.linalg.lstsq(A.T @ A, A.T @ G, rcond=None)[0]
        R = G - A @ x
        sv = np.linalg.svd(R, compute_uv=False)
        tol = 1e-9 * max(1.0, sv.max() if sv.size else 1.0)
        rank_R = int((sv > tol).sum())
        _, _, vt = np.linalg.svd(R)
        null = vt[rank_R:]  # gb-vectors v with R v = 0
        return len(syms) - rank_R, null, R

    out = {"n": n, "num_gb": len(syms), "num_f_unknowns": nA, "rank_delta_strict": int(np.linalg.matrix_rank(A_g.T @ A_g)),
           "rank_delta_extended": int(np.linalg.matrix_rank(A_full.T @ A_full))}
    # strict: f g-valued, full gamma (g part + K residue)
    out["strict"] = trivial_dim(A_g, G_full)[0]
    # g-part: drop K rows from both sides
    keep = ~isK
    out["g_part"] = trivial_dim(A_g[keep], G_full[keep])[0]
    # extended
    out["extended"] = trivial_dim(A_full, G_full)[0]
    # rank of the K-residue map gb -> gamma_K
    out["rank_K_residue_map"] = int(np.linalg.matrix_rank(G_full[isK]))
    return out


def witnesses(n):
    """For each gb symbol, a pair (X,Y) whose central residue involves only that symbol."""
    alg = cg.CAlgebra(n)
    _, central = cg.gamma_table(alg)
    res = {}
    for (X, Y), cm in central.items():
        if len(cm) == 1:
            (s, v), = cm.items()
            res.setdefault(s, (X, Y, str(v)))
    return res


def main():
    for n in (1, 2, 3):
        print(f"=== n={n} (C({n + 1})) ===")
        for name in ev.PROFILE_NAMES:
            r = compare_layers(n, name)
            print(f"  profile={name:7s} gamma entries={r['n_gamma']:5d}  g-part mismatches Layer3 vs Layer4={len(r['g_mismatches'])}  "
                  f"central(κK) entries={r['n_central']:4d}  γ_K = -f_K∘[,]: {r['k_identity_ok']}")
        r = search(n)
        print(f"  all odd maps f: unknowns={r['num_f_unknowns']} rank(δ strict)={r['rank_delta_strict']}  rank(δ ext)={r['rank_delta_extended']}")
        print(f"  trivial gb-subspace dimension (of {r['num_gb']}):  g-part only={r['g_part']}   strict(full γ)={r['strict']}   extended(f into g⊕K)={r['extended']}")
        print(f"  rank of gb -> κK-residue map = {r['rank_K_residue_map']}")
        w = witnesses(n)
        print("  residue witnesses:", {s: w[s] for s in sorted(w)[:4]}, "...")


if __name__ == "__main__":
    main()
