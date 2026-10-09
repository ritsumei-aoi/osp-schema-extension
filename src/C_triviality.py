"""Triviality search for the inhomogeneous deformation of C(n+1)  (Issue I08).

Compares Layer 3 (evaluated gamma) with Layer 4 (coboundary structure) and decides, for each
gb profile and for each gb parameter separately (gamma is linear in gb), whether gamma is a
coboundary delta f of an odd linear map f.  Three readings of "odd map f" are tested:

  S1  f: g -> g,        gamma compared modulo the centre C K  ("up to scalar")
  S2  f: g -> g,        gamma compared exactly (K components must be matched by delta f, impossible
                        since delta f has no K component unless f has)
  S3  f: g -> g ⊕ C K,  gamma compared exactly

Method: exact sparse Gaussian elimination over Q of the linear system
      sum_ij phi_ij (delta f_ij)(X,Y)_Z = gamma(X,Y)_Z
built from Schema 4's elementary table, with the right-hand sides of every profile and of
every unit gb vector attached as extra columns.  Independently, the explicit candidate map
f_shift of Schema 4 is evaluated at each profile and compared with Layer 3 entry by entry.

Usage: python3 src/C_triviality.py [--datadir data] [n ...]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from C_coboundary import coboundary_table, load_structure, restrict_f  # noqa: E402
from C_evaluate import PROFILES  # noqa: E402
from C_gamma import gb_labels  # noqa: E402


# ---------------------------------------------------------------------- exact sparse solver

class SparseEliminator:
    """Incremental exact row reduction.  Unknown columns are ints; RHS columns are strings."""

    def __init__(self):
        self.pivots: dict = {}      # pivot column -> row (dict col -> Fraction)
        self.inconsistent: dict = {}  # rhs name -> list of equation ids whose reduced row is 0 = nonzero
        self.zero_rows = 0

    def add_row(self, row: dict, eq_id):
        row = {c: v for c, v in row.items() if v != 0}
        while True:
            cols = [c for c in row if isinstance(c, int) and c in self.pivots]
            if not cols:
                break
            c = min(cols)
            p = self.pivots[c]
            factor = row[c] / p[c]
            for cc, vv in p.items():
                nv = row.get(cc, Fraction(0)) - factor * vv
                if nv == 0:
                    row.pop(cc, None)
                else:
                    row[cc] = nv
        unknown_cols = [c for c in row if isinstance(c, int)]
        if unknown_cols:
            self.pivots[min(unknown_cols)] = row
        else:
            self.zero_rows += 1
            for c in row:  # remaining entries are RHS columns -> inconsistency
                self.inconsistent.setdefault(c, []).append(eq_id)

    @property
    def rank(self):
        return len(self.pivots)


# ---------------------------------------------------------------------- data loading

def load_json(datadir, name):
    with open(os.path.join(datadir, name)) as fh:
        return json.load(fh)


def gamma_linear(s2):
    g = {}
    for e in s2["inhomogeneous_deformation"]["gamma"]:
        g.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {l: Fraction(c) for l, c in e["coeff"].items()}
    return g


def gamma_evaluated(s3):
    g = {}
    for e in s3["evaluated_gamma"]:
        g.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return g


def f_linear(s4):
    f = {}
    for e in s4["candidate_map"]["f"]:
        f.setdefault(e["source"], {})[e["target"]] = {l: Fraction(c) for l, c in e["coeff"].items()}
    return f


def evaluate_f(f_lin, values):
    out = {}
    for src, tg in f_lin.items():
        for tgt, fl in tg.items():
            c = sum(Fraction(v) * values[l] for l, v in fl.items())
            if c != 0:
                out.setdefault(src, {})[tgt] = c
    return out


def drop_K(table):
    out = {}
    for k, d in table.items():
        dd = {Z: c for Z, c in d.items() if Z != "K"}
        if dd:
            out[k] = dd
    return out


# ---------------------------------------------------------------------- analysis per n

def analyse(n: int, datadir: str, verbose=True) -> dict:
    s1, order, par, sc = load_structure(os.path.join(datadir, f"C_{n}_structure.json"))
    s2 = load_json(datadir, f"C_{n}_gamma.json")
    s4 = load_json(datadir, f"C_{n}_coboundary.json")
    labels = [l for l, _ in gb_labels(n)]
    idx = {l: i for i, l in enumerate(order)}
    odd = [l for l in order if par[l] == 1]
    gam_lin = gamma_linear(s2)
    f_lin = f_linear(s4)
    profiles = {}
    for prof in PROFILES:
        name = f"C_{n}_evaluated.json" if prof == "ones" else f"C_{n}_evaluated_{prof}.json"
        s3 = load_json(datadir, name)
        profiles[prof] = ({l: Fraction(v) for l, v in s3["gb_assignment"].items()}, gamma_evaluated(s3))
    report = {"n": n, "algebra": f"C({n+1}) = osp(2|{2*n})", "dim": len(order), "gb_count": len(labels)}

    # ---- (A) closed form of the scalar obstruction:  gamma(X,Y)_K = -(1/2) sum_{Z odd} [X,Y]^Z gb_Z
    def gb_of(Z):
        sig_s = Z.split("_")[-1]
        k = Z.split("_del")[1].split("_")[0]
        return f"gb_a1{sig_s[0]}_b{k}{sig_s[1]}"
    closed_form_ok = True
    for X in order:
        for Y in order:
            pred = {}
            for Z, c in sc[(X, Y)].items():
                if par[Z] == 1:
                    pred[gb_of(Z)] = pred.get(gb_of(Z), Fraction(0)) - c / 2
            pred = {l: v for l, v in pred.items() if v != 0}
            if pred != gam_lin.get((X, Y), {}).get("K", {}):
                closed_form_ok = False
    report["K_part_closed_form_verified"] = closed_form_ok

    # ---- (B) candidate map f_shift evaluated per profile, compared with Layer 3
    cand = {}
    for prof, (values, gam_ev) in profiles.items():
        f = evaluate_f(f_lin, values)
        df = coboundary_table(sc, par, order, f, all_pairs=True)
        f_noK = {s: {t: c for t, c in tg.items() if t != "K"} for s, tg in f.items()}
        f_noK = {s: tg for s, tg in f_noK.items() if tg}
        df_noK = coboundary_table(sc, par, order, f_noK, all_pairs=True)
        diff_noK = {}
        for key in set(gam_ev) | set(df_noK):
            a, b = gam_ev.get(key, {}), df_noK.get(key, {})
            d = {Z: a.get(Z, Fraction(0)) - b.get(Z, Fraction(0)) for Z in set(a) | set(b)}
            d = {Z: v for Z, v in d.items() if v != 0}
            if d:
                diff_noK[key] = d
        cand[prof] = {
            "exact_match_with_K_targets": df == gam_ev,
            "match_modulo_K": drop_K(df) == drop_K(gam_ev),
            "f_without_K_targets_mismatching_pairs": len(diff_noK),
            "f_without_K_targets_mismatch_only_in_K": all(set(d) == {"K"} for d in diff_noK.values()),
            "sample_mismatches": [
                {"X": X, "Y": Y, "gamma_K": str(gam_ev.get((X, Y), {}).get("K", 0)), "delta_f_K": "0"}
                for (X, Y) in sorted(diff_noK, key=lambda k: (idx[k[0]], idx[k[1]]))[:4]
            ],
            "K_entries_in_gamma": sum(1 for d in gam_ev.values() if "K" in d),
        }
    report["candidate_map"] = cand

    # ---- (C) general linear solve with the elementary coboundary table
    phis = s4["odd_map_parameterization"]["phi_labels"]
    phi_idx = {p: i for i, p in enumerate(phis)}
    phi_noK = [p for p in phis if not p.startswith("phi[K]")]
    eqs: dict = {}   # (X,Y,Z) -> {phi_index: coeff}
    for e in s4["elementary_coboundaries"]["table"]:
        eqs.setdefault((e["X"], e["Y"], e["Z"]), {})[phi_idx[e["phi"]]] = Fraction(e["coeff"])
    # right-hand sides: unit gb vectors (symbolic columns) and profiles; pairs with index(X) <= index(Y)
    rhs_cols: dict = {}
    for (X, Y), d in gam_lin.items():
        if idx[X] > idx[Y]:
            continue
        for Z, fl in d.items():
            for l, c in fl.items():
                rhs_cols.setdefault((X, Y, Z), {})[f"unit:{l}"] = c
    for prof, (values, gam_ev) in profiles.items():
        for (X, Y), d in gam_ev.items():
            if idx[X] > idx[Y]:
                continue
            for Z, c in d.items():
                rhs_cols.setdefault((X, Y, Z), {})[f"profile:{prof}"] = c
    settings = {
        "S1_f_to_g_modulo_K": (set(phi_noK), False),
        "S2_f_to_g_exact": (set(phi_noK), True),
        "S3_f_to_g_plus_K_exact": (set(phis), True),
    }
    solve = {}
    for sname, (allowed, include_K_eqs) in settings.items():
        allowed_idx = {phi_idx[p] for p in allowed}
        el = SparseEliminator()
        keys = set(eqs) | set(rhs_cols)
        for key in sorted(keys, key=lambda k: (idx[k[0]], idx[k[1]], -1 if k[2] == "K" else idx[k[2]])):
            X, Y, Z = key
            if Z == "K" and not include_K_eqs:
                continue
            row = {i: c for i, c in eqs.get(key, {}).items() if i in allowed_idx}
            row.update(rhs_cols.get(key, {}))
            el.add_row(row, key)
        unknowns = len(allowed_idx)
        res = {"unknowns": unknowns, "rank_of_delta": el.rank, "kernel_dim": unknowns - el.rank,
               "equations": len([k for k in keys if include_K_eqs or k[2] != "K"]),
               "solvable": {}, "inconsistent_equations": {}}
        names = [f"unit:{l}" for l in labels] + [f"profile:{p}" for p in PROFILES]
        for nm in names:
            bad = el.inconsistent.get(nm, [])
            res["solvable"][nm] = not bad
            if bad:
                res["inconsistent_equations"][nm] = {"count": len(bad), "all_in_K": all(k[2] == "K" for k in bad),
                                                     "sample": [list(k) for k in bad[:3]]}
        solve[sname] = res
    report["linear_solve"] = solve
    report["inner_odd_derivations"] = len(odd)  # ad(W), W odd, always lie in ker(delta)

    if verbose:
        print(f"=== {report['algebra']}: dim {len(order)}, {len(labels)} gb parameters ===")
        print(f"  K-part closed form gamma_K(X,Y) = -(1/2) sum_{{Z odd}} [X,Y]^Z gb_Z verified: {closed_form_ok}")
        for prof, c in cand.items():
            print(f"  profile {prof:12s}: delta f_shift == gamma exactly: {c['exact_match_with_K_targets']}, "
                  f"modulo K: {c['match_modulo_K']}; with f restricted to g->g: "
                  f"{c['f_without_K_targets_mismatching_pairs']} mismatching pairs, all only in K: "
                  f"{c['f_without_K_targets_mismatch_only_in_K']}")
        for sname, res in solve.items():
            sol = res["solvable"]
            units = [l for l in labels if sol[f'unit:{l}']]
            profs = [p for p in PROFILES if sol[f'profile:{p}']]
            print(f"  {sname}: unknowns {res['unknowns']}, equations {res['equations']}, rank {res['rank_of_delta']}, "
                  f"kernel dim {res['kernel_dim']} (inner odd derivations: {len(odd)})")
            print(f"     solvable for unit gb vectors: {len(units)}/{len(labels)}; for profiles: {profs}")
            if res["inconsistent_equations"]:
                nm = next(iter(res["inconsistent_equations"]))
                print(f"     e.g. {nm}: {res['inconsistent_equations'][nm]}")
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ns", nargs="*", type=int, default=[1, 2, 3])
    ap.add_argument("--datadir", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    args = ap.parse_args(argv)
    reports = [analyse(n, args.datadir) for n in args.ns]
    out = os.path.join(args.datadir, "C_triviality_report.json")
    with open(out, "w") as fh:
        json.dump(reports, fh, indent=1, ensure_ascii=False)
    print(f"-> {os.path.relpath(out)}")


if __name__ == "__main__":
    main()
