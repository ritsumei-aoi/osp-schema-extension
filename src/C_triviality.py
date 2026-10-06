"""Triviality search for the inhomogeneous deformation of C(n+1) (Issue I08).

Compares Layer 3 (evaluated gamma) / Layer 2 (symbolic gamma) with Layer 4 (delta f) by solving
gamma = delta f exactly over Q, in three modes:

  mod_K       : equations with Z = K dropped, f: g -> g        ("up to scalar" = modulo the central part)
  strict      : all equations incl. Z = K,   f: g -> g (phi_K = 0)
  strict_cent : all equations incl. Z = K,   f: g -> g + C K   (phi_K free)

Symbolic elimination (rhs = linear forms in gb) gives the exact linear conditions on gb for
solvability; each Layer 3 profile is then solved explicitly and the solution is verified by
substitution into the Layer 4 JSON entries.

It also builds the closed-form trivializing map from the oscillator substitution
    a_1^sigma -> a_1^sigma + kappa * sum_j (gb_{sigma,j,-} b_j^+ - gb_{sigma,j,+} b_j^-)
and checks gamma = delta(f_closed) symbolically.

Usage:  python3 src/C_triviality.py      # prints the report, writes data/C_triviality_report.json
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import _parse_lin, gb_symbols  # noqa: E402
from C_generators import DATA_DIR, K_LABEL, CAlgebra, write_json  # noqa: E402
from C_osc import Lin, gb_name, split_kappa  # noqa: E402
from verify_C_structure import load_table  # noqa: E402

MODES = ("mod_K", "strict", "strict_cent")


def load(name):
    with open(os.path.join(DATA_DIR, name)) as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- exact sparse elimination
class Eliminator:
    """Row echelon form over Q; rows {col: Fraction}, rhs Lin (symbolic in gb)."""

    def __init__(self, col_order: dict):
        self.co = col_order
        self.piv: dict = {}          # col -> (row, rhs)
        self.conditions: list = []   # (key, rhs Lin) from rows reducing to 0 = rhs
        self.n_rows = 0

    def add(self, key, row: dict, rhs: Lin):
        self.n_rows += 1
        row = dict(row)
        while True:
            cand = [c for c in row if c in self.piv]
            if not cand:
                break
            c = min(cand, key=self.co.__getitem__)
            prow, prhs = self.piv[c]
            a = row[c]
            for cc, v in prow.items():
                w = row.get(cc, 0) - a * v
                if w:
                    row[cc] = w
                else:
                    row.pop(cc, None)
            rhs = rhs + prhs.scale(-a)
        if not row:
            if rhs:
                self.conditions.append((key, rhs))
            return
        c = min(row, key=self.co.__getitem__)
        a = row[c]
        self.piv[c] = ({cc: v / a for cc, v in row.items()}, rhs.scale(Fraction(1) / a))

    def rank(self) -> int:
        return len(self.piv)

    def solve(self, values: dict) -> dict:
        """Particular solution (free variables = 0) with gb substituted by `values`."""
        sol: dict = {}
        for c in sorted(self.piv, key=self.co.__getitem__, reverse=True):
            row, rhs = self.piv[c]
            v = rhs.evaluate(values)
            for cc, a in row.items():
                if cc != c:
                    v -= a * sol.get(cc, 0)
            sol[c] = v
        return sol


def condition_rank(conds: list, syms: list) -> tuple[int, list]:
    """Rank of the gb-linear conditions and a reduced basis of them (as strings)."""
    el = Eliminator({s: i for i, s in enumerate(syms)})
    for key, lin in conds:
        row = {s: v for s, v in lin.items() if s != "1"}
        el.add(key, row, Lin())
    basis = []
    for c in sorted(el.piv, key=syms.index):
        basis.append(Lin(el.piv[c][0]).to_str() + " = 0")
    return el.rank(), basis


# --------------------------------------------------------------------------- equations
def equations(struct, gam_entries, cob_entries, mode):
    idx = {b: i for i, b in enumerate(struct["basis"]["ordered"])}
    lhs, rhs = {}, {}
    for e in cob_entries:
        if idx[e["X"]] > idx[e["Y"]]:
            continue  # super-antisymmetry verified in I05/I07; keep X <= Y
        if mode == "mod_K" and e["Z"] == K_LABEL:
            continue
        lin = _parse_lin(e["coeff"])
        if mode != "strict_cent":
            lin = Lin({k: v for k, v in lin.items() if not k.startswith("phi_K_")})
        lhs[(e["X"], e["Y"], e["Z"])] = lin
    for e in gam_entries:
        if idx[e["X"]] > idx[e["Y"]]:
            continue
        if mode == "mod_K" and e["Z"] == K_LABEL:
            continue
        rhs[(e["X"], e["Y"], e["Z"])] = _parse_lin(e["coeff"])
    keys = sorted(set(lhs) | set(rhs))
    return keys, lhs, rhs


def symbolic_elimination(struct, gam_entries, cob_entries, mode):
    keys, lhs, rhs = equations(struct, gam_entries, cob_entries, mode)
    cols = sorted({c for v in lhs.values() for c in v})
    el = Eliminator({c: i for i, c in enumerate(cols)})
    for k in keys:
        el.add(k, dict(lhs.get(k, {})), rhs.get(k, Lin()))
    return el, keys, lhs, rhs, cols


def verify_solution(sol, keys, lhs, values_gamma):
    """Max |delta f - gamma| over all equations (exact)."""
    bad = []
    for k in keys:
        d = sum((a * sol.get(c, 0) for c, a in lhs.get(k, {}).items()), Fraction(0))
        g = values_gamma.get(k, Fraction(0))
        if d != g:
            bad.append((k, str(d), str(g)))
    return bad


# --------------------------------------------------------------------------- closed form
def closed_form_f(n: int) -> dict:
    """F(X) := kappa-part of X(a', b) in the deformed algebra; f_closed = -F.  Returns {X: {Z: Lin}}."""
    alg = CAlgebra(n, deformed=True)
    osc = alg.osc

    def a_prime(sig):
        el = {(f"a_1_{sig}",): Lin.const(1)}
        for j in range(1, n + 1):
            el[("kappa", f"b_{j}_p")] = Lin.sym(gb_name(sig, j, "m"))
            el[("kappa", f"b_{j}_m")] = Lin.sym(gb_name(sig, j, "p"), -1)
        return el

    subst = {"a_1_p": a_prime("p"), "a_1_m": a_prime("m")}
    out = {}
    for x in alg.basis:
        tot: dict = {}
        for w, c in alg.elem[x].items():
            term = {(): c}
            for letter in w:
                term = osc.mul(term, subst.get(letter, {(letter,): Lin.const(1)}))
            for ww, cc in term.items():
                tot[ww] = tot.get(ww, Lin()) + cc
        tot = {w: c for w, c in tot.items() if c}
        p0, p1 = split_kappa(osc.normal(tot))
        assert alg.decompose(p0) == alg.decompose(alg.elem[x])
        dec = alg.decompose(p1)
        out[x] = {z: -c for z, c in dec.items()}
    return out


def check_oscillator_substitution(n: int) -> bool:
    """[b_j^s, a'^sigma] = 0, {a'^-, a'^+} = 1, (a'^±)^2 = 0 in the deformed algebra."""
    alg = CAlgebra(n, deformed=True)
    osc = alg.osc
    ap = {}
    for sig in ("p", "m"):
        el = {(f"a_1_{sig}",): Lin.const(1)}
        for j in range(1, n + 1):
            el[("kappa", f"b_{j}_p")] = Lin.sym(gb_name(sig, j, "m"))
            el[("kappa", f"b_{j}_m")] = Lin.sym(gb_name(sig, j, "p"), -1)
        ap[sig] = el
    ok = osc.bracket(ap["m"], ap["p"], 1, 1) == {(): Lin.const(1)}
    ok &= osc.bracket(ap["p"], ap["p"], 1, 1) == {} and osc.bracket(ap["m"], ap["m"], 1, 1) == {}
    for j in range(1, n + 1):
        for s in ("p", "m"):
            for sig in ("p", "m"):
                ok &= osc.bracket({(f"b_{j}_{s}",): Lin.const(1)}, ap[sig], 0, 1) == {}
    return ok


def delta_symbolic(struct, f: dict) -> dict:
    """delta f for f = {X: {Z or K: Lin}} with symbolic (gb) coefficients."""
    basis, par, table = load_table(struct)
    out = {}
    for x in basis:
        for y in basis:
            px, py = par[x], par[y]
            acc: dict = {}

            def add(z, c):
                acc[z] = acc.get(z, Lin()) + c
            for z0, c in f[y].items():
                if z0 != K_LABEL:
                    for z, a in table.get((x, z0), {}).items():
                        add(z, c.scale(a * (-1) ** px))
            for z0, c in f[x].items():
                if z0 != K_LABEL:
                    for z, a in table.get((y, z0), {}).items():
                        add(z, c.scale(-a * (-1) ** ((px + 1) * py)))
            for w, a in table.get((x, y), {}).items():
                for z, c in f[w].items():
                    add(z, c.scale(-a))
            acc = {z: c for z, c in acc.items() if c}
            if acc:
                out[(x, y)] = acc
    return out


# --------------------------------------------------------------------------- main
def analyse(n: int) -> dict:
    struct = load(f"C_{n}_structure.json")
    gam = load(f"C_{n}_gamma.json")["inhomogeneous_deformation"]["gamma"]
    ev = load(f"C_{n}_evaluated.json")["profiles"]
    cob = load(f"C_{n}_coboundary.json")["coboundary"]
    syms = gb_symbols(n)
    rep = {"n": n, "modes": {}}
    for mode in MODES:
        el, keys, lhs, rhs, cols = symbolic_elimination(struct, gam, cob, mode)
        crank, cbasis = condition_rank(el.conditions, syms)
        m = {"equations": len(keys), "unknowns": len(cols), "rank_delta": el.rank(),
             "gb_condition_rank": crank, "gb_conditions": cbasis,
             "trivial_gb_subspace_dim": len(syms) - crank,
             "obstruction_examples": [{"X": k[0], "Y": k[1], "Z": k[2], "residual": r.to_str()}
                                      for k, r in el.conditions[:6]],
             "profiles": {}}
        idx = {b: i for i, b in enumerate(struct["basis"]["ordered"])}
        for p in ev:
            vals = p["gb_values"]
            gvals = {}
            for e in p["gamma"]:
                if idx[e["X"]] <= idx[e["Y"]] and not (mode == "mod_K" and e["Z"] == K_LABEL):
                    gvals[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])
            # consistency: some condition violated <=> non-trivial
            violated = [(k, r.evaluate(vals)) for k, r in el.conditions if r.evaluate(vals) != 0]
            sol = el.solve(vals)
            bad = verify_solution(sol, keys, lhs, gvals)
            m["profiles"][p["name"]] = {
                "trivial": not bad,
                "violated_conditions": len(violated),
                "mismatched_equations": len(bad),
                "mismatch_examples": [{"X": k[0], "Y": k[1], "Z": k[2], "delta_f": d, "gamma": g}
                                      for k, d, g in bad[:4]],
                "solution_nonzero_phi": sum(1 for v in sol.values() if v) if not bad else None,
            }
            assert (not bad) == (not violated), "solver inconsistency"
        rep["modes"][mode] = m
    # closed form
    fc = closed_form_f(n)
    dfc = delta_symbolic(struct, fc)
    gam_tab: dict = {}
    for e in gam:
        gam_tab.setdefault((e["X"], e["Y"]), {})[e["Z"]] = _parse_lin(e["coeff"])
    mism_full, mism_modK = 0, 0
    for k in set(gam_tab) | set(dfc):
        a, b = gam_tab.get(k, {}), dfc.get(k, {})
        for z in set(a) | set(b):
            if a.get(z, Lin()) + -(b.get(z, Lin())):
                mism_full += 1
                if z != K_LABEL:
                    mism_modK += 1
    rep["closed_form"] = {
        "oscillator_substitution_ok": check_oscillator_substitution(n),
        "f_closed_nonzero_entries": sum(len(v) for v in fc.values()),
        "f_closed_has_K_component": any(K_LABEL in v for v in fc.values()),
        "mismatches_including_K": mism_full,
        "mismatches_mod_K": mism_modK,
        "f_closed_sample": {x: {z: c.to_str() for z, c in fc[x].items()}
                            for x in list(fc)[: 2 * n] + [f"H_{k}" for k in range(1, n + 2)]},
    }
    return rep


def main(ns=(1, 2, 3)):
    reports = []
    for n in ns:
        r = analyse(n)
        reports.append(r)
        print(f"===== n={n} (C({n + 1}) = osp(2|{2 * n})) =====")
        for mode, m in r["modes"].items():
            triv = [k for k, v in m["profiles"].items() if v["trivial"]]
            non = [k for k, v in m["profiles"].items() if not v["trivial"]]
            print(f"[{mode}] eqs={m['equations']} unknowns={m['unknowns']} rank(delta)={m['rank_delta']} "
                  f"gb-condition rank={m['gb_condition_rank']} -> trivial gb subspace dim "
                  f"{m['trivial_gb_subspace_dim']}/{4 * n}")
            print(f"    trivial profiles: {triv}")
            print(f"    non-trivial profiles: {non}")
            if m["gb_conditions"]:
                print(f"    conditions: {m['gb_conditions']}")
                for ex in m["obstruction_examples"][:3]:
                    print(f"    obstruction example: {ex}")
                for name in non[:1]:
                    print(f"    {name} mismatches: {m['profiles'][name]['mismatch_examples'][:3]}")
        print(f"[closed form] {r['closed_form']['oscillator_substitution_ok']=}, "
              f"mismatches incl. K = {r['closed_form']['mismatches_including_K']}, "
              f"mod K = {r['closed_form']['mismatches_mod_K']}, "
              f"f_closed has K component = {r['closed_form']['f_closed_has_K_component']}")
    write_json({"reports": reports}, "C_triviality_report.json")


if __name__ == "__main__":
    main()
