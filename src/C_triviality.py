"""Issue I08: triviality search for the inhomogeneous deformation of C(n+1).

Compares Layer 3 (evaluated gamma) with Layer 4 (coboundaries delta f) and solves the
linear systems  delta f = gamma  exactly, under three readings:

  R1 (strict)   : f : g -> g,        gamma : g x g -> g + C K   (as computed in I05)
  R2 (projected): f : g -> g,        gamma projected to g (K-components discarded)
  R3 (extended) : f : g -> g + C K,  gamma : g x g -> g + C K

For each n and gb profile the script reports whether delta f = gamma is solvable and
lists the inconsistent (X, Y, Z) components.  It also solves the joint symbolic system
in the unknowns (phi, gb) to obtain the exact subspace of gb values for which the
deformation is trivial, and checks that g is perfect ([g, g] = g).

Usage: python3 src/C_triviality.py [n ...]   -> docs/triviality_report.md (+ stdout)
"""
from __future__ import annotations

import os
import sys
from fractions import Fraction
from itertools import product
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_common import (ROOT_DIR, LieSuperalgebra, LinForm, SparseLinearSystem, frac_str,  # noqa: E402
                      lf_add, lf_str)
from C_coboundary import coboundary, evaluate_f, generic_f, load_coboundary, numeric, shift_map_symbolic  # noqa: E402
from C_evaluate import gb_profiles, load_evaluated  # noqa: E402
from C_gamma import load_gamma  # noqa: E402

PROFILES = ["all_plus", "fermion_sign", "boson_sign", "single_a1p_b1m", "row_a1p_only", "zero"]


def _pairs_upper(g: LieSuperalgebra):
    return [(X, Y) for i, X in enumerate(g.labels) for Y in g.labels[i:]]


def solve_delta_f_eq_gamma(g: LieSuperalgebra, gamma_num, allow_K: bool, project_K: bool):
    """Solve delta f = gamma for f generic (odd).  Returns (status, inconsistent components)."""
    f_gen, unknowns = generic_f(g, allow_K=allow_K)
    pairs = _pairs_upper(g)
    cob = coboundary(g, f_gen, pairs)
    sys_ = SparseLinearSystem()
    eq_index: List[Tuple[str, str, str]] = []
    rows: List[LinForm] = []
    targets = list(g.labels) + ([] if project_K else ["K"])
    for X, Y in pairs:
        lhs = cob.get((X, Y), {})
        rhs = gamma_num.get((X, Y), {})
        for Z in targets:
            lf = lf_add(lhs.get(Z, {}), {"": -rhs.get(Z, Fraction(0))})
            if lf:
                rows.append(lf)
                eq_index.append((X, Y, Z))
                sys_.add(lf)
    status, pivots, inconsistent = sys_.solve()
    # the solver only ever adds rows that are non-trivial, in order, so solver row index
    # == index into eq_index
    bad = [eq_index[i] + (row.get("", Fraction(0)),) for i, row in inconsistent]
    return status, bad, len(unknowns), len(rows), pivots


def trivial_gb_subspace(g: LieSuperalgebra, gamma_sym, allow_K: bool, project_K: bool, gb_names: List[str]):
    """Joint system delta f(phi) - gamma(gb) = 0; return the constraints on gb alone."""
    f_gen, unknowns = generic_f(g, allow_K=allow_K)
    pairs = _pairs_upper(g)
    cob = coboundary(g, f_gen, pairs)
    sys_ = SparseLinearSystem()
    targets = list(g.labels) + ([] if project_K else ["K"])
    for X, Y in pairs:
        lhs = cob.get((X, Y), {})
        rhs = gamma_sym.get((X, Y), {})
        for Z in targets:
            lf = lf_add(lhs.get(Z, {}), rhs.get(Z, {}), Fraction(-1))
            if lf:
                sys_.add(lf)
    # eliminate phi first (key 0), gb last (key 1)
    status, pivots, inconsistent = sys_.solve(pivot_key=lambda u: (0 if u.startswith("phi[") else 1, u))
    assert status == "consistent" and not inconsistent  # homogeneous system
    gb_constraints = {p: row for p, row in pivots.items() if not p.startswith("phi[")}
    return gb_constraints, len(unknowns)


def check_perfect(g: LieSuperalgebra) -> Tuple[int, int]:
    """dim [g,g] versus dim g (exact rank over Q)."""
    sys_ = SparseLinearSystem()
    # rank of the set of bracket vectors: treat each basis label as an unknown; each vector is a row
    rows = []
    for (X, Y), br in g.table.items():
        rows.append(dict(br))
    # rank via elimination
    pivots: Dict[str, LinForm] = {}
    for r in rows:
        r = dict(r)
        for p in [k for k in r if k in pivots]:
            if r.get(p, 0) != 0:
                r = lf_add(r, pivots[p], -r[p])
        r = {k: c for k, c in r.items() if c != 0}
        if not r:
            continue
        p = min(r)
        r = {k: c / r[p] for k, c in r.items()}
        for q, prow in list(pivots.items()):
            if prow.get(p, 0) != 0:
                pivots[q] = lf_add(prow, r, -prow[p])
        pivots[p] = r
    return len(pivots), len(g.labels)


def analyse(n: int, out: List[str]) -> None:
    g = LieSuperalgebra.load(n)
    gb_names = [f"gb_a1{s}_b{j}{t}" for s in ("p", "m") for j in range(1, n + 1) for t in ("p", "m")]
    _, gamma_sym = load_gamma(n)
    f_sym = shift_map_symbolic(n)
    cob_doc = load_coboundary(n)
    out.append(f"\n## C({n+1}) = osp(2|{2*n})  (n = {n}, dim g = {len(g.labels)})\n")
    r, d = check_perfect(g)
    out.append(f"* g is perfect: dim [g,g] = {r} = dim g = {d}  ({'yes' if r == d else 'NO'})")
    # ---- Layer 3 vs Layer 4 per profile --------------------------------------------
    out.append("\n### Layer 3 (gamma) vs Layer 4 (delta f_rep) and solvability of delta f = gamma\n")
    out.append("| profile | gamma pairs | K-entries | delta f_rep == gamma | R1 strict (f:g->g) | R2 projected | R3 extended |")
    out.append("|---|---|---|---|---|---|---|")
    details = []
    for prof in PROFILES:
        values = gb_profiles(n)[prof]
        _, gamma_num = load_evaluated(n, prof)
        if prof == "all_plus":
            stored = {}
            for e in cob_doc["coboundary_evaluated"]:
                stored.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
            cob_rep = stored
        else:
            cob_rep = numeric(coboundary(g, evaluate_f(f_sym, values)))
        match = cob_rep == gamma_num
        nK = sum(1 for e in gamma_num.values() for Z in e if Z == "K")
        s1, bad1, nu1, ne1, _ = solve_delta_f_eq_gamma(g, gamma_num, allow_K=False, project_K=False)
        s2, bad2, nu2, ne2, _ = solve_delta_f_eq_gamma(g, gamma_num, allow_K=False, project_K=True)
        s3, bad3, nu3, ne3, _ = solve_delta_f_eq_gamma(g, gamma_num, allow_K=True, project_K=False)
        fmt = lambda s, bad: ("trivial" if s == "consistent" else f"NON-trivial ({len(bad)} inconsistent eqs)")
        out.append(f"| {prof} | {len(gamma_num)} | {nK} | {'yes' if match else 'NO'} | {fmt(s1, bad1)} | {fmt(s2, bad2)} | {fmt(s3, bad3)} |")
        details.append((prof, bad1, nu1, ne1))
    # ---- details of the strict failures -----------------------------------------------
    out.append("\n### R1 (strict) inconsistent components, i.e. where Layer 3 and Layer 4 cannot be matched\n")
    for prof, bad, nu, ne in details:
        if not bad:
            out.append(f"* `{prof}`: system with {nu} unknowns, {ne} equations is consistent (trivial).")
            continue
        allK = all(Z == "K" for (_, _, Z, _) in bad)
        out.append(f"* `{prof}`: {nu} unknowns, {ne} equations; {len(bad)} inconsistent equations, "
                   f"all with Z = K: {'yes' if allK else 'NO'}. Pairs (index(X) <= index(Y)):")
        shown = bad if len(bad) <= 10 else bad[:10]
        for X, Y, Z, c in shown:
            out.append(f"    - gamma_K({X}, {Y}) = {frac_str(-c)}, but (delta f)_K = 0 for every f: g -> g")
        if len(bad) > 10:
            out.append(f"    - ... ({len(bad) - 10} more)")
        ys = sorted({Y for (_, Y, _, _) in bad} | {X for (X, _, _, _) in bad if g.parity[X] == 0})
        out.append(f"    even partners Y occurring in the failures: {', '.join(ys)}")
    # ---- symbolic: exact subspace of trivial gb ------------------------------------------
    out.append("\n### Exact gb-conditions from the joint symbolic system  delta f(phi) = gamma(gb)\n")
    for label, allow_K, project_K in (("R1 strict", False, False), ("R2 projected", False, True), ("R3 extended", True, False)):
        cons, nu = trivial_gb_subspace(g, gamma_sym, allow_K, project_K, gb_names)
        if not cons:
            out.append(f"* {label}: no constraint on gb — trivial for **all** {4*n} parameters "
                       f"(unknowns: {nu}).")
        else:
            out.append(f"* {label}: {len(cons)} independent linear constraints on the {4*n} parameters "
                       f"(unknowns: {nu}); trivial subspace has dimension {4*n - len(cons)}:")
            for p, row in sorted(cons.items()):
                out.append(f"    - {lf_str(row)} = 0")
    # ---- structure of the K-part -------------------------------------------------------
    out.append("\n### Structure of the K-components (evidence for the conjecture)\n")
    fK = {src: f_sym[src].get("K", {}) for src in g.labels if f_sym[src].get("K")}
    out.append("f_rep K-part (symbolic): " + "; ".join(f"f_K({s}) = {lf_str(lf)}" for s, lf in fK.items()))
    # verify gamma_K(X,Y) = -f_K([X,Y]) for all pairs
    ok = True
    for X, Y in product(g.labels, repeat=2):
        pred: LinForm = {}
        for W, c in g.bracket(X, Y).items():
            pred = lf_add(pred, fK.get(W, {}), -c)
        if pred != gamma_sym.get((X, Y), {}).get("K", {}):
            ok = False
            break
    out.append(f"\nIdentity gamma_K(X,Y) = -f_K([X,Y]) with f_K(E_eps1_del{{k}}_{{st}}) = ½·gb_a1{{s}}_b{{k}}{{t}} "
               f"checked on all {len(g.labels)**2} ordered pairs: {'PASS' if ok else 'FAIL'}")


def main(ns):
    out = ["# Triviality search report for the inhomogeneous deformation of C(n+1)", "",
           "Generated by `src/C_triviality.py` from Layers 1–4 in `data/`. Readings:",
           "R1 strict: f: g→g, γ: g×g→g⊕CK as computed; R2 projected: K-components of γ discarded, f: g→g;",
           "R3 extended: f: g→g⊕CK. See docs/issues/I08.md for the analysis."]
    for n in ns:
        analyse(n, out)
    text = "\n".join(out) + "\n"
    path = os.path.join(ROOT_DIR, "docs", "triviality_report.md")
    with open(path, "w") as fh:
        fh.write(text)
    print(text)
    print(f"[written to {path}]")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
