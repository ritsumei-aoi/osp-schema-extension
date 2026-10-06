"""Triviality analysis for the inhomogeneous deformation of C(n+1) (Issue I08).

Reads Layer 1 (structure), Layer 3 (evaluated gamma) and Layer 4 (coboundary) JSON and
  A. compares Layer 3 gamma with Layer 4 delta(f_gb) entry by entry for every profile;
  B. solves gamma = delta f for a *generic* odd f (least squares + rank) under three readings:
       strict-g   : f: g -> g,        all components compared (incl. K)
       mod-K      : f: g -> g,        K components ignored ("up to scalar")
       strict-gK  : f: g -> g + C K,  all components compared
     for every profile and for each single gb parameter (linearity => all gb);
  C. computes ker(delta) (odd derivations) and a negative control.

Usage:  python3 src/C_triviality.py [n ...]      (default: 1 2 3)
"""
import json
import os
import random
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import DATA_DIR  # noqa: E402
from verify_C_structure import load_structure  # noqa: E402

TOL = 1e-9


def load(n, layer):
    name = {3: "evaluated", 4: "coboundary"}[layer]
    with open(os.path.join(DATA_DIR, f"C_{n}_{name}.json")) as f:
        return json.load(f)


def entries_to_dict(lst):
    return {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in lst}


# ------------------------------------------------------------- part A ----
def compare_profiles(n, d3, d4):
    rows = []
    for name, p3 in d3["profiles"].items():
        p4 = d4["profiles"][name]
        g3, k3 = entries_to_dict(p3["gamma"]), entries_to_dict(p3["central_component"])
        g4, k4 = entries_to_dict(p4["delta_f"]), entries_to_dict(p4["delta_f_central"])
        mism_g = [k for k in set(g3) | set(g4) if g3.get(k, 0) != g4.get(k, 0)]
        mism_k = [k for k in set(k3) | set(k4) if k3.get(k, 0) != k4.get(k, 0)]
        f_K = [e for e in p4["f"] if e["Z"] == "K"]
        rows.append({"profile": name, "gamma_g": len(g3), "deltaf_g": len(g4), "mismatch_g": len(mism_g),
                     "gamma_K": len(k3), "deltaf_K": len(k4), "mismatch_K": len(mism_k),
                     "f_entries": len(p4["f"]), "f_central_entries": len(f_K)})
    return rows


# ------------------------------------------------------------- part B ----
class LinearSystem:
    """delta as a dense matrix: rows (X,Y,Z) with X <= Y in PBW order, cols phi unknowns."""

    def __init__(self, n, d4):
        basis, par, _ = load_structure(n)
        self.basis, self.par = basis, par
        order = {b: i for i, b in enumerate(basis)}
        gen = [e for e in d4["general_coboundary"] if order[e["X"]] <= order[e["Y"]]]
        self.cols_g = sorted({ph for e in gen for ph in e["coeff"] if not ph.startswith("phi[K|")})
        self.cols_K = sorted({ph for e in gen for ph in e["coeff"] if ph.startswith("phi[K|")})
        rowkeys = set()
        for e in gen:
            rowkeys.add((e["X"], e["Y"], e["Z"]))
        # also every (X,Y,Z) that could carry gamma: all X<=Y, Z in basis+K with right parity
        for X in basis:
            for Y in basis:
                if order[X] <= order[Y]:
                    for Z in basis + ["K"]:
                        pz = 0 if Z == "K" else par[Z]
                        if pz == (par[X] + par[Y] + 1) % 2:
                            rowkeys.add((X, Y, Z))
        self.rows = sorted(rowkeys)
        self.ridx = {r: i for i, r in enumerate(self.rows)}
        cols = self.cols_g + self.cols_K
        cidx = {c: i for i, c in enumerate(cols)}
        M = np.zeros((len(self.rows), len(cols)))
        for e in gen:
            for ph, c in e["coeff"].items():
                M[self.ridx[(e["X"], e["Y"], e["Z"])], cidx[ph]] = float(Fraction(c))
        self.M = M
        self.order = order
        self.isK = np.array([r[2] == "K" for r in self.rows])
        self.ng = len(self.cols_g)

    def rhs(self, entries):
        b = np.zeros(len(self.rows))
        for (X, Y, Z), c in entries.items():
            if self.order[X] <= self.order[Y]:
                b[self.ridx[(X, Y, Z)]] = float(c)
        return b

    def solve(self, b, mode):
        if mode == "strict-g":
            A, bb = self.M[:, :self.ng], b
        elif mode == "mod-K":
            A, bb = self.M[~self.isK, :self.ng], b[~self.isK]
        elif mode == "strict-gK":
            A, bb = self.M, b
        else:
            raise ValueError(mode)
        x, *_ = np.linalg.lstsq(A, bb, rcond=None)
        res = float(np.max(np.abs(A @ x - bb))) if len(bb) else 0.0
        rA = np.linalg.matrix_rank(A)
        rAb = np.linalg.matrix_rank(np.column_stack([A, bb]))
        return {"residual": res, "rank_A": int(rA), "rank_Ab": int(rAb), "solvable": bool(rA == rAb and res < 1e-8)}

    def kernel_dim(self, mode):
        A = self.M[:, :self.ng] if mode != "strict-gK" else self.M
        return A.shape[1] - int(np.linalg.matrix_rank(A))


def gamma_single(n, d3_like_gamma, g):
    """gamma restricted to one gb parameter, from Schema 2."""
    out = {}
    for e in d3_like_gamma:
        if g in e["coeff"]:
            out[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"][g])
    return out


def analyse(n, verbose=True):
    d3, d4 = load(n, 3), load(n, 4)
    with open(os.path.join(DATA_DIR, f"C_{n}_gamma.json")) as f:
        d2 = json.load(f)
    report = {"n": n}
    report["comparison"] = compare_profiles(n, d3, d4)
    L = LinearSystem(n, d4)
    report["system"] = {"rows": len(L.rows), "unknowns_g": L.ng, "unknowns_K": len(L.cols_K),
                        "kernel_dim_g": L.kernel_dim("strict-g"), "kernel_dim_gK": L.kernel_dim("strict-gK"),
                        "odd_dim": len([b for b in L.basis if L.par[b] == 1])}
    modes = ["strict-g", "mod-K", "strict-gK"]
    prof = {}
    for name, p3 in d3["profiles"].items():
        b = L.rhs({**entries_to_dict(p3["gamma"]), **entries_to_dict(p3["central_component"])})
        prof[name] = {m: L.solve(b, m) for m in modes}
    report["profiles"] = prof
    gam_all = d2["inhomogeneous_deformation"]["gamma"] + d2["inhomogeneous_deformation"]["central_component"]
    single = {}
    for g in [x for row in d2["gb_matrix"]["entries"] for x in row]:
        b = L.rhs(gamma_single(n, gam_all, g))
        single[g] = {m: L.solve(b, m)["solvable"] for m in modes}
    report["single_parameter"] = single
    # negative control: random odd cochain (not a cocycle) must be unsolvable
    rng = random.Random(7 + n)
    rnd = {}
    for r in L.rows:
        if rng.random() < 0.05:
            rnd[r] = Fraction(rng.choice([-1, 1]))
    report["negative_control"] = {m: L.solve(L.rhs(rnd), m)["solvable"] for m in modes}
    # central K-obstruction: pairs with gamma_K != 0 for all_plus, and per-gb support
    kpairs = [(e["X"], e["Y"], e["coeff"]) for e in d3["profiles"]["all_plus"]["central_component"]]
    report["K_pairs_all_plus"] = kpairs
    report["gb_with_K_component"] = sorted({g for e in d2["inhomogeneous_deformation"]["central_component"]
                                            for g in e["coeff"]})
    report["central_formula_failures"] = check_central_formula(n, d2)
    return report


def check_central_formula(n, d2):
    """Exact check (symbolic in gb) of gamma_K(X,Y) = -phi_K([X,Y]_0) with
    phi_K(E_eps1_del{k}_{sigma s}) = gb_{sigma,k,s} / 2  and phi_K = 0 on even generators."""
    basis, par, sc = load_structure(n)

    def phiK(W):
        if not W.startswith("E_eps1_del"):
            return {}
        k, ss = W[len("E_eps1_del"):].split("_")
        return {f"gb_{ss[0]}_{k}_{ss[1]}": Fraction(1, 2)}

    got = {}
    for e in d2["inhomogeneous_deformation"]["central_component"]:
        got[(e["X"], e["Y"])] = {g: Fraction(c) for g, c in e["coeff"].items()}
    fails = 0
    for X in basis:
        for Y in basis:
            exp = {}
            for W, c in sc.get((X, Y), {}).items():
                for g, v in phiK(W).items():
                    exp[g] = exp.get(g, 0) - c * v
            exp = {g: v for g, v in exp.items() if v != 0}
            fails += exp != got.get((X, Y), {})
    return fails


def main(ns):
    out = {}
    for n in ns:
        r = analyse(n)
        out[n] = r
        print(f"===== n={n} (C({n+1})) =====")
        print("A. Layer 3 vs Layer 4 (delta f_gb), per profile:")
        for row in r["comparison"]:
            print("   {profile:13s} gamma_g={gamma_g:5d} deltaf_g={deltaf_g:5d} mismatch_g={mismatch_g} | "
                  "gamma_K={gamma_K:4d} deltaf_K={deltaf_K:4d} mismatch_K={mismatch_K} | "
                  "f entries={f_entries} (K: {f_central_entries})".format(**row))
        s = r["system"]
        print(f"B. generic odd f: rows={s['rows']} unknowns g={s['unknowns_g']} K={s['unknowns_K']}; "
              f"dim ker(delta) on g-valued f = {s['kernel_dim_g']} (odd part dim {s['odd_dim']}), "
              f"on g+K-valued f = {s['kernel_dim_gK']}")
        for name, res in r["profiles"].items():
            print("   {:13s} ".format(name) + "  ".join(
                f"{m}: {'TRIVIAL' if v['solvable'] else 'non-trivial'} (rank {v['rank_A']}/{v['rank_Ab']}, res {v['residual']:.1e})"
                for m, v in res.items()))
        sp = r["single_parameter"]
        print("   single gb parameters:", {m: sum(v[m] for v in sp.values()) for m in ["strict-g", "mod-K", "strict-gK"]},
              f"solvable out of {len(sp)}")
        print("C. negative control (random odd cochain):", r["negative_control"])
        print(f"   gb labels with a K-component: {len(r['gb_with_K_component'])}/{4*n}; "
              f"all_plus K-pairs: {len(r['K_pairs_all_plus'])}, e.g. {r['K_pairs_all_plus'][:4]}")
        print(f"D. exact check gamma_K = -phi_K([X,Y]), phi_K(E_eps1_del{{k}}_{{sigma s}}) = gb/2: "
              f"failures = {r['central_formula_failures']}")
    summary = {n: {k: v for k, v in r.items() if k != "K_pairs_all_plus"} for n, r in out.items()}
    with open(os.path.join(DATA_DIR, "C_triviality_report.json"), "w") as f:
        json.dump(summary, f, indent=1)
    return out


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
