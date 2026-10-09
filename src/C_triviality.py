"""Triviality search for the inhomogeneous deformation of C(n+1)  (Issue I08).

Part A  Layer 3 vs Layer 4: entry-wise comparison of gamma (C_{n}_evaluated*.json) with
        delta f_can (C_{n}_coboundary*.json); separate bookkeeping of g-components and
        K-components.
Part B  General linear solve: unknowns phi_<i>_<j> for ALL odd maps f: g -> g
        (optionally + phiK_<j> K), equations (delta f)(X,Y)_Z = gamma(X,Y)_Z over Q,
        exact sparse Gaussian elimination.  Reports solvability, rank, nullity and verifies
        a particular solution with delta_f.
        Run for: all_plus_one, alternating, every unit profile (one gb = 1), a seeded random
        rational profile, and gb = 0.
Part C  Where the structures do NOT coincide when f is restricted to g -> g: list of pairs
        (X,Y) with a K-component in gamma, and the closed form behind it.

Usage: python src/C_triviality.py [--n 1 2 3] [--datadir data] [--list-K-pairs N]
"""
from __future__ import annotations

import argparse
import os
import random
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_coboundary import FMap, canonical_f, delta_f  # noqa: E402
from C_evaluate import DATADIR, evaluate_gamma, gb_profile  # noqa: E402
from C_gamma import bracket_table_from_schema1, gamma_table_from_records, load_json, _padd, _pscale  # noqa: E402
from osc_algebra import OscillatorAlgebra, Poly, frac_str  # noqa: E402

NumTable = Dict[Tuple[str, str], Dict[str, Fraction]]


# --------------------------------------------------------------------------- Part A


def compare_tables(a: NumTable, b: NumTable) -> dict:
    keys = set(a) | set(b)
    mism_g, mism_K, equal = [], [], 0
    for k in keys:
        va, vb = a.get(k, {}), b.get(k, {})
        dg = {z: va.get(z, 0) - vb.get(z, 0) for z in (set(va) | set(vb)) if z != "K"}
        dg = {z: c for z, c in dg.items() if c != 0}
        dK = va.get("K", 0) - vb.get("K", 0)
        if dg:
            mism_g.append(k)
        if dK != 0:
            mism_K.append(k)
        if not dg and dK == 0:
            equal += 1
    return {"pairs": len(keys), "equal": equal, "mismatch_g": sorted(mism_g), "mismatch_K": sorted(mism_K)}


def numeric_table(records: List[dict]) -> NumTable:
    t = gamma_table_from_records(records, key="coeff")
    return {k: {z: p.const_value() for z, p in v.items()} for k, v in t.items()}


# --------------------------------------------------------------------------- Part B: linear system


class Unknowns:
    def __init__(self, labels: List[str], parity: Dict[str, int], allow_K: bool):
        self.names: List[str] = []
        self.pairs: List[Tuple[str, str]] = []       # (target, source)
        self.idx: Dict[Tuple[str, str], int] = {}
        for src in labels:
            for tgt in labels:
                if parity[tgt] != parity[src]:
                    self.idx[(tgt, src)] = len(self.names)
                    self.names.append(f"phi_{labels.index(tgt)}_{labels.index(src)}")
                    self.pairs.append((tgt, src))
            if allow_K and parity[src] == 1:
                self.idx[("K", src)] = len(self.names)
                self.names.append(f"phiK_{labels.index(src)}")
                self.pairs.append(("K", src))

    def __len__(self):
        return len(self.names)


def build_rows(labels: List[str], parity: Dict[str, int], br: NumTable, gamma: NumTable,
               U: Unknowns) -> List[Tuple[Dict[int, Fraction], Fraction, Tuple[str, str, str]]]:
    """Linear equations  sum_u A[u] phi_u = rhs  for (delta f)(X,Y)_Z = gamma(X,Y)_Z,
    one per (X <= Y, Z).  Derived from
       (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])."""
    idx = {l: i for i, l in enumerate(labels)}
    rows = []
    allow_K = any(t == "K" for t, _ in U.pairs)
    for x in labels:
        for y in labels:
            if idx[y] < idx[x]:
                continue
            sx = -1 if parity[x] else 1
            sxy = -1 if ((parity[x] + 1) % 2 and parity[y]) else 1
            coeffs: Dict[str, Dict[int, Fraction]] = {}      # Z -> {unknown: coeff}

            def add(z: str, u: int, c: Fraction):
                d = coeffs.setdefault(z, {})
                d[u] = d.get(u, Fraction(0)) + c

            # (-1)^{p(X)} [X, f(Y)]:  f(Y) = sum_t phi_{t,Y} t ;  [X, t] = sum_z br[(X,t)][z] z
            for t in labels:
                if (t, y) in U.idx:
                    for z, c in br.get((x, t), {}).items():
                        add(z, U.idx[(t, y)], sx * c)
            # - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
            for t in labels:
                if (t, x) in U.idx:
                    for z, c in br.get((y, t), {}).items():
                        add(z, U.idx[(t, x)], -sxy * c)
            # - f([X,Y]) = - sum_w br[(X,Y)][w] * sum_t phi_{t,w} t
            for w, c in br.get((x, y), {}).items():
                for t in labels + (["K"] if allow_K else []):
                    if (t, w) in U.idx:
                        add(t, U.idx[(t, w)], -c)
            targets = set(coeffs) | set(gamma.get((x, y), {}))
            for z in targets:
                row = {u: c for u, c in coeffs.get(z, {}).items() if c != 0}
                rhs = gamma.get((x, y), {}).get(z, Fraction(0))
                if row or rhs != 0:
                    rows.append((row, rhs, (x, y, z)))
    return rows


def solve_rows(rows, n_unknowns: int) -> dict:
    """Incremental exact elimination.  Returns rank, consistency, a particular solution."""
    pivots: Dict[int, Tuple[Dict[int, Fraction], Fraction]] = {}   # pivot col -> (row, rhs) with row[col]=1
    inconsistent_at = []
    for row, rhs, tag in rows:
        row = dict(row)
        # reduce by existing pivots (columns in increasing order)
        changed = True
        while changed:
            changed = False
            for col in sorted(row):
                if col in pivots and row.get(col, 0) != 0:
                    prow, prhs = pivots[col]
                    f = row[col]
                    for c2, v2 in prow.items():
                        nv = row.get(c2, Fraction(0)) - f * v2
                        if nv == 0:
                            row.pop(c2, None)
                        else:
                            row[c2] = nv
                    rhs -= f * prhs
                    changed = True
                    break
        if not row:
            if rhs != 0:
                inconsistent_at.append(tag)
            continue
        col = min(row)
        pv = row[col]
        row = {c: v / pv for c, v in row.items()}
        rhs = rhs / pv
        # back-substitute into existing pivot rows so that the pivot set stays reduced
        for pc, (prow, prhs) in list(pivots.items()):
            if col in prow:
                f = prow[col]
                for c2, v2 in row.items():
                    nv = prow.get(c2, Fraction(0)) - f * v2
                    if nv == 0:
                        prow.pop(c2, None)
                    else:
                        prow[c2] = nv
                pivots[pc] = (prow, prhs - f * rhs)
        pivots[col] = (row, rhs)
    rank = len(pivots)
    solution = None
    if not inconsistent_at:
        solution = [Fraction(0)] * n_unknowns          # free unknowns = 0
        for col, (prow, prhs) in pivots.items():
            solution[col] = prhs                       # other entries of prow are free columns (=0)
    return {"rank": rank, "nullity": n_unknowns - rank, "consistent": not inconsistent_at,
            "inconsistent_at": inconsistent_at, "solution": solution}


def solve_triviality(labels, parity, br: NumTable, gamma: NumTable, allow_K: bool) -> dict:
    U = Unknowns(labels, parity, allow_K)
    rows = build_rows(labels, parity, br, gamma, U)
    res = solve_rows(rows, len(U))
    res.update({"unknowns": len(U), "equations": len(rows), "allow_K": allow_K})
    if res["solution"] is not None:
        f: FMap = {}
        for (tgt, src), u in U.idx.items():
            if res["solution"][u] != 0:
                f.setdefault(src, {})[tgt] = Poly.const(res["solution"][u])
        df = delta_f(f, br, labels, parity)
        gam_p = {k: {z: Poly.const(c) for z, c in v.items()} for k, v in gamma.items()}
        bad = [k for k in set(df) | set(gam_p) if _padd(df.get(k, {}), _pscale(gam_p.get(k, {}), -1))]
        res["verified"] = not bad
        res["f"] = f
    else:
        res["verified"] = False
    return res


# --------------------------------------------------------------------------- report


def profile_list(n: int):
    labels = OscillatorAlgebra(n).gb_labels()
    rnd = random.Random(20261009 + n)
    out = [("zero", {l: Fraction(0) for l in labels}),
           ("all_plus_one", gb_profile(n, "all_plus_one")),
           ("alternating", gb_profile(n, "alternating")),
           ("random_rational", {l: Fraction(rnd.randint(-5, 5), rnd.randint(1, 4)) for l in labels})]
    out += [(f"unit:{l}", gb_profile(n, f"unit:{l}")) for l in labels]
    return out


def run(n: int, datadir: str, list_K_pairs: int) -> dict:
    doc1 = load_json(os.path.join(datadir, f"C_{n}_structure.json"))
    doc2 = load_json(os.path.join(datadir, f"C_{n}_gamma.json"))
    labels, parity = doc1["basis"]["pbw_order"], doc1["parity"]
    br = bracket_table_from_schema1(doc1)
    out = {"n": n, "dim": len(labels)}
    print(f"\n##### C({n+1}) = osp(2|{2*n}),  n = {n},  dim = {len(labels)}  ({len(doc1['basis']['even'])}|{len(doc1['basis']['odd'])})")

    # ---- Part A
    print("\n[A] Layer 3 (gamma) vs Layer 4 (delta f_can), entry-wise")
    out["A"] = {}
    for suffix in ["", "_alternating"]:
        p3 = os.path.join(datadir, f"C_{n}_evaluated{suffix}.json")
        p4 = os.path.join(datadir, f"C_{n}_coboundary{suffix}.json")
        if not (os.path.exists(p3) and os.path.exists(p4)):
            continue
        doc3, doc4 = load_json(p3), load_json(p4)
        g3, g4 = numeric_table(doc3["evaluated_gamma"]), numeric_table(doc4["coboundary"])
        cmp = compare_tables(g3, g4)
        # the same comparison after dropping the K-components of f_can (f restricted to g -> g)
        f_g: FMap = {}
        for r in doc4["odd_map_f"]["f_matrix"]:
            if r["target"] != "K":
                f_g.setdefault(r["source"], {})[r["target"]] = Poly.const(Fraction(r["coeff"]))
        df_g = {k: {z: p.const_value() for z, p in v.items()} for k, v in delta_f(f_g, br, labels, parity).items()}
        cmp_g = compare_tables(g3, df_g)
        prof = doc3["gb_assignment"]["profile"]
        out["A"][prof] = {"full": cmp, "f_restricted_to_g": cmp_g}
        print(f"  profile {prof:14s}: pairs {cmp['pairs']:4d}  equal {cmp['equal']:4d}  "
              f"g-mismatch {len(cmp['mismatch_g'])}  K-mismatch {len(cmp['mismatch_K'])}   "
              f"| f_can restricted to g->g: equal {cmp_g['equal']:4d}  g-mismatch {len(cmp_g['mismatch_g'])}  K-mismatch {len(cmp_g['mismatch_K'])}")

    # ---- Part C (listing)
    print("\n[C] Pairs whose gamma has a K-component (not reachable by delta f for f: g -> g); symbolic")
    gam_sym = gamma_table_from_records(doc2["gamma"])
    kpairs = [(k, v["K"]) for k, v in gam_sym.items() if "K" in v]
    idx = {l: i for i, l in enumerate(labels)}
    kpairs.sort(key=lambda kv: (idx[kv[0][0]], idx[kv[0][1]]))
    print(f"  {len(kpairs)} ordered pairs ({len(kpairs)//2} unordered) carry a K-component")
    # closed form check: gamma_K(X,Y) = -1/2 sum_{odd E} gb(E) [X,Y]_E
    gbl = {}
    for o in doc1["basis"]["odd"]:
        sig, k, s = o[len("E_eps1_del"):].split("_")[1][0], int(o[len("E_eps1_del"):].split("_")[0]), o[-1]
        gbl[o] = OscillatorAlgebra.gb_label(sig, k, s)
    closed_ok = True
    for (x, y), comps in gam_sym.items():
        pred = Poly()
        for w, c in br.get((x, y), {}).items():
            if parity[w] == 1:
                pred = pred + Poly.symbol(gbl[w], Fraction(-1, 2) * c)
        if not (pred - comps.get("K", Poly())).is_zero():
            closed_ok = False
    print(f"  closed form gamma_K(X,Y) = -1/2 * sum_{{odd E}} gb(E) [X,Y]_E  holds for all pairs: {closed_ok}")
    for (x, y), p in kpairs[:list_K_pairs]:
        print(f"    gamma({x}, {y})_K = {p}      ([{x},{y}]_0 = { {w: str(c) for w, c in br.get((x, y), {}).items()} })")
    out["C"] = {"K_pairs": len(kpairs), "closed_form_holds": closed_ok}

    # ---- Part B
    print("\n[B] General linear solve  delta f = gamma  over all odd maps f  (exact arithmetic)")
    print("     profile              | f: g->g            | f: g->g+K")
    print("                          | consistent rank nul | consistent rank nul  verified")
    out["B"] = {}
    for name, gb in profile_list(n):
        gam = evaluate_gamma(doc2, gb)
        r_g = solve_triviality(labels, parity, br, gam, allow_K=False)
        r_K = solve_triviality(labels, parity, br, gam, allow_K=True)
        # also: f: g->g against gamma projected to g (i.e. 'up to scalar')
        gam_mod = {k: {z: c for z, c in v.items() if z != "K"} for k, v in gam.items()}
        gam_mod = {k: v for k, v in gam_mod.items() if v}
        r_mod = solve_triviality(labels, parity, br, gam_mod, allow_K=False)
        out["B"][name] = {"g": r_g, "gK": r_K, "g_modK": r_mod}
        print(f"  {name:24s} | {str(r_g['consistent']):9s} {r_g['rank']:4d} {r_g['nullity']:3d} "
              f"| {str(r_K['consistent']):9s} {r_K['rank']:4d} {r_K['nullity']:3d}  {r_K['verified']}"
              f"   | g->g vs gamma mod K: {r_mod['consistent']} (verified {r_mod['verified']})")
    uk = Unknowns(labels, parity, False)
    print(f"  unknowns: {len(uk)} (g->g), {len(Unknowns(labels, parity, True))} (g->g+K); "
          f"nullity {out['B']['zero']['g']['nullity']} = 4n = {4*n}: {out['B']['zero']['g']['nullity'] == 4*n}"
          f"  (space of odd 1-cocycles; inner odd derivations ad_Z give 4n)")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--datadir", default=DATADIR)
    ap.add_argument("--list-K-pairs", type=int, default=6)
    args = ap.parse_args(argv)
    for n in args.n:
        run(n, args.datadir, args.list_K_pairs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
