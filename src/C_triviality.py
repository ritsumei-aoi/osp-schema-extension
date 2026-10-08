"""I08: triviality search for the inhomogeneous deformation of C(n+1).

Part A  Layer 3 vs Layer 4 comparison (entry by entry, per gb profile).
Part B  Independent linear-algebra search: solve gamma = delta(phi) for an *arbitrary* odd linear map
        phi (unknown coefficients), exactly over Q, under three readings of the triviality condition:
          full     f : g -> g (+) C K,   gamma compared including its K components
          adjoint  f : g -> g,           K components of gamma dropped (K acts trivially in ad)
          strict   f : g -> g,           gamma compared including its K components
        For each: consistent?, rank, nullity, failing equations (X, Y, Z).
Part C  Symbolic facts used for the general conjecture (which gb appear in K components, etc.).

Usage: python src/C_triviality.py [n ...]      (writes docs/C_triviality_report.md as well)
"""
from __future__ import annotations

import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import DATA_DIR  # noqa: E402
from C_gamma import load_json  # noqa: E402
from C_evaluate import profiles  # noqa: E402
from C_coboundary import canonical_f  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "docs", "C_triviality_report.md")


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------
def load_layer3(n, profile):
    d = load_json(f"C_{n}_evaluated_{profile}.json")
    out = {}
    for e in d["evaluated_structure"]["gamma_evaluated"]:
        out[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])
    return out


def load_layer4(n, profile):
    d = load_json(f"C_{n}_coboundary_{profile}.json")
    out = {}
    for e in d["coboundary"]["entries"]:
        out[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])
    return out


def load_structure(n):
    d = load_json(f"C_{n}_structure.json")
    labels = d["basis"]["pbw_order"]
    parity = d["parity"]
    table = {}
    for e in d["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return labels, parity, table


# ---------------------------------------------------------------------------
# Part A
# ---------------------------------------------------------------------------
def compare_layers(n, profile):
    g3, g4 = load_layer3(n, profile), load_layer4(n, profile)
    keys = set(g3) | set(g4)
    mism = {k: (g3.get(k, Fraction(0)), g4.get(k, Fraction(0))) for k in keys
            if g3.get(k, Fraction(0)) != g4.get(k, Fraction(0))}
    return {"layer3_entries": len(g3), "layer4_entries": len(g4), "common": len(set(g3) & set(g4)),
            "mismatches": mism, "K_entries": sum(1 for k in g3 if k[2] == "K")}


# ---------------------------------------------------------------------------
# Part B: exact sparse linear solve  delta(phi) = gamma
# ---------------------------------------------------------------------------
def unknowns_for(labels, parity, allow_K):
    """Unknown phi_{Z,X} (f(X) contains Z) with p(Z) = p(X) + 1; K allowed only for odd X."""
    unk = []
    for x in labels:
        for z in labels:
            if parity[z] == (parity[x] + 1) % 2:
                unk.append((z, x))
        if allow_K and parity[x] == 1:
            unk.append(("K", x))
    return unk


def delta_columns(labels, parity, table, unknowns):
    """For each unknown (Z0, X0) the sparse column {(X, Y, Z): coeff} of delta(E_{Z0 <- X0})."""
    # c^{X0}_{XY}: pairs (X, Y) whose bracket contains X0
    contains = {}
    for (x, y), comps in table.items():
        for z, c in comps.items():
            contains.setdefault(z, []).append((x, y, c))
    cols = {}
    for (z0, x0) in unknowns:
        col = {}

        def acc(key, val):
            v = col.get(key, Fraction(0)) + val
            if v:
                col[key] = v
            elif key in col:
                del col[key]

        if z0 != "K":
            for x in labels:                      # (-1)^{p(X)} [X, Z0]   at pair (X, X0)
                s = -1 if parity[x] else 1
                for z, c in table.get((x, z0), {}).items():
                    acc((x, x0, z), s * c)
            for y in labels:                      # -(-1)^{(p(X0)+1)p(Y)} [Y, Z0]   at pair (X0, Y)
                s = -((-1) ** ((parity[x0] + 1) * parity[y]))
                for z, c in table.get((y, z0), {}).items():
                    acc((x0, y, z), s * c)
        for (x, y, c) in contains.get(x0, []):    # -c^{X0}_{XY} Z0   at pair (X, Y)
            acc((x, y, z0), -c)
        cols[(z0, x0)] = col
    return cols


def solve(unknowns, cols, rhs):
    """Exact Gaussian elimination on the sparse system  sum_u col_u[eq] * phi_u = rhs[eq].

    Returns dict(consistent, rank, nullity, failing_equations, solution or None)."""
    uidx = {u: i for i, u in enumerate(unknowns)}
    rows = {}
    for u, col in cols.items():
        for eq, c in col.items():
            rows.setdefault(eq, {})[uidx[u]] = c
    for eq in rhs:
        rows.setdefault(eq, {})
    pivots = {}          # pivot column -> (row dict normalised, rhs)
    failing = []
    for eq in sorted(rows):
        row = dict(rows[eq])
        b = rhs.get(eq, Fraction(0))
        # reduce
        changed = True
        while changed:
            changed = False
            for col in sorted(row):
                if col in pivots:
                    prow, pb = pivots[col]
                    f = row[col]
                    for c2, v in prow.items():
                        nv = row.get(c2, Fraction(0)) - f * v
                        if nv:
                            row[c2] = nv
                        elif c2 in row:
                            del row[c2]
                    b -= f * pb
                    changed = True
                    break
        if not row:
            if b != 0:
                failing.append((eq, b))
            continue
        pc = min(row)
        pv = row[pc]
        row = {c: v / pv for c, v in row.items()}
        b = b / pv
        # keep existing pivot rows reduced w.r.t. the new pivot
        for col, (prow, pb) in list(pivots.items()):
            if pc in prow:
                f = prow[pc]
                for c2, v in row.items():
                    nv = prow.get(c2, Fraction(0)) - f * v
                    if nv:
                        prow[c2] = nv
                    elif c2 in prow:
                        del prow[c2]
                pivots[col] = (prow, pb - f * b)
        pivots[pc] = (row, b)
    rank = len(pivots)
    res = {"consistent": not failing, "rank": rank, "nullity": len(unknowns) - rank,
           "failing_equations": failing, "unknowns": len(unknowns), "equations": len(rows)}
    if not failing:
        sol = {}
        for col, (prow, pb) in pivots.items():   # free variables = 0
            sol[unknowns[col]] = pb
        res["solution"] = {u: v for u, v in sol.items() if v != 0}
    return res


def triviality_search(n, profile, variant, cache):
    labels, parity, table, cols_full, cols_noK, unk_full, unk_noK = cache
    g3 = load_layer3(n, profile)
    if variant == "full":
        unk, cols, rhs = unk_full, cols_full, g3
    elif variant == "adjoint":
        unk, cols = unk_noK, cols_noK
        rhs = {k: v for k, v in g3.items() if k[2] != "K"}
    elif variant == "strict":
        unk, cols, rhs = unk_noK, cols_noK, g3
    else:
        raise ValueError(variant)
    return solve(unk, cols, rhs)


def build_cache(n):
    labels, parity, table = load_structure(n)
    unk_full = unknowns_for(labels, parity, True)
    unk_noK = unknowns_for(labels, parity, False)
    cols_full = delta_columns(labels, parity, table, unk_full)
    cols_noK = {u: cols_full[u] for u in unk_noK}
    return labels, parity, table, cols_full, cols_noK, unk_full, unk_noK


# ---------------------------------------------------------------------------
# Part C: symbolic facts
# ---------------------------------------------------------------------------
def symbolic_facts(n):
    B, table, gamma, f, sign = canonical_f(n)
    kvars, kpairs = set(), []
    for (x, y), comps in gamma.items():
        if "K" in comps:
            kvars |= comps["K"].variables()
            kpairs.append((x, y, str(comps["K"])))
    allvars = set(B.alg.gb_labels())
    # which generator pairs carry K components, by type
    types = {}
    for x, y, c in kpairs:
        t = (("cartan" if x.startswith("H_") else "sp-root" if B.parity[x] == 0 else "odd"),
             ("cartan" if y.startswith("H_") else "sp-root" if B.parity[y] == 0 else "odd"))
        types[t] = types.get(t, 0) + 1
    return {"gb_in_K_components": sorted(kvars), "all_gb": sorted(allvars),
            "all_gb_appear_in_K": kvars == allvars, "K_pairs": len(kpairs), "K_pair_types": types,
            "f_linear_in_gb": all(c.degree() == 1 for comps in f.values() for c in comps.values()),
            "example_K_pairs": kpairs[:4]}


# ---------------------------------------------------------------------------
def main(ns):
    lines = []
    P = lines.append
    P("# Triviality search report for C(n+1) (generated by src/C_triviality.py)\n")
    for n in ns:
        P(f"## n = {n}  (C({n+1}) = osp(2|{2*n}))\n")
        cache = build_cache(n)
        labels = cache[0]
        P(f"dim g = {len(labels)}; unknowns phi: full {len(cache[5])}, without K {len(cache[6])}\n")
        P("### Part A: Layer 3 (evaluated gamma) vs Layer 4 (delta f of the shift map)\n")
        P("| profile | L3 entries | L4 entries | K entries | mismatches |")
        P("|---|---|---|---|---|")
        for prof in profiles(n):
            r = compare_layers(n, prof)
            P(f"| {prof} | {r['layer3_entries']} | {r['layer4_entries']} | {r['K_entries']} | {len(r['mismatches'])} |")
        P("")
        P("### Part B: search for ANY odd f with delta f = gamma (exact linear algebra)\n")
        P("| profile | variant | consistent | rank | nullity | failing eqs | example failing (X, Y, Z) = rhs |")
        P("|---|---|---|---|---|---|---|")
        for prof in profiles(n):
            for variant in ("full", "adjoint", "strict"):
                r = triviality_search(n, prof, variant, cache)
                ex = ""
                if r["failing_equations"]:
                    (x, y, z), b = r["failing_equations"][0]
                    ex = f"({x}, {y}, {z}) = {b}"
                P(f"| {prof} | {variant} | {'yes' if r['consistent'] else 'NO'} | {r['rank']} | {r['nullity']} | "
                  f"{len(r['failing_equations'])} | {ex} |")
        P("")
        facts = symbolic_facts(n)
        P("### Part C: symbolic facts\n")
        P(f"- gb parameters occurring in K components of gamma: {len(facts['gb_in_K_components'])} of "
          f"{len(facts['all_gb'])} (all: {facts['all_gb_appear_in_K']})")
        P(f"- pairs (X, Y) with a K component: {facts['K_pairs']}, by type {facts['K_pair_types']}")
        P(f"- shift map f linear in gb: {facts['f_linear_in_gb']}")
        P(f"- examples of K components: {facts['example_K_pairs']}")
        P("")
    text = "\n".join(lines)
    print(text)
    with open(REPORT, "w") as fh:
        fh.write(text + "\n")
    print(f"(report written to {REPORT})")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
