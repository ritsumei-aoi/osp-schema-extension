"""Triviality search for the inhomogeneous deformation of C(n+1) (Issue I08).

Compares Layer 3 (gamma at gb profiles) / Layer 2 (symbolic gamma) with Layer 4 (delta f linear
forms) by solving  gamma = delta f  exactly over Q, under three readings:
  mod_K   : components W in g only, unknowns phi                 ("up to scalar", the doc's reading)
  exact   : components W in g + C K, unknowns phi and psi        (f may have a scalar part)
  strict  : components W in g + C K, unknowns phi only (psi = 0) (f : g -> g, exact equality)
Also builds the analytic candidate f from the oscillator shift a = a' + kappa*lambda and checks it.

Usage: python3 src/C_triviality.py      -> data/C_{n}_triviality.json and a printed report
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import OscillatorAlgebra, gb_labels, KAPPA  # noqa: E402
from C_generators import Decomposer, realization_terms, write_json, frac_str, DATA_DIR  # noqa: E402
from C_coboundary import load_coboundary, load_sc, unknowns, phi_label, psi_label, evaluate_linear  # noqa: E402

READINGS = ("mod_K", "exact", "strict")


# ------------------------------------------------------------------ exact sparse solver
class SparseSolver:
    """Incremental exact row reduction for M x = B with several right-hand sides."""

    def __init__(self, n_rhs):
        self.n_rhs = n_rhs
        self.pivots = {}          # col -> (row dict, rhs list); row has min col == pivot col
        self.inconsistent = [[] for _ in range(n_rhs)]

    def add_row(self, row, rhs, tag=None):
        row = {c: Fraction(v) for c, v in row.items() if v}
        rhs = [Fraction(v) for v in rhs]
        while True:
            cols = [c for c in row if c in self.pivots]
            if not cols:
                break
            c = min(cols)
            prow, prhs = self.pivots[c]
            f = row[c]
            for k, v in prow.items():
                row[k] = row.get(k, 0) - f * v
                if row[k] == 0:
                    del row[k]
            rhs = [a - f * b for a, b in zip(rhs, prhs)]
        if row:
            c = min(row)
            p = row[c]
            self.pivots[c] = ({k: v / p for k, v in row.items()}, [a / p for a in rhs])
        else:
            for i, a in enumerate(rhs):
                if a != 0:
                    self.inconsistent[i].append(tag)

    def rank(self):
        return len(self.pivots)

    def particular_solution(self, i):
        x = {}
        for c in sorted(self.pivots, reverse=True):
            prow, prhs = self.pivots[c]
            v = prhs[i] - sum((a * x.get(k, 0) for k, a in prow.items() if k != c), Fraction(0))
            if v:
                x[c] = v
        return x


# ------------------------------------------------------------------ data loading
def load_gamma_symbolic(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_gamma.json")) as f:
        d = json.load(f)
    g = {}
    for e in d["inhomogeneous_deformation"]["gamma"]:
        g.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {k: Fraction(v) for k, v in e["coeff"].items()}
    return g


def load_profiles(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_evaluated.json")) as f:
        d = json.load(f)
    out = {}
    for p in d["evaluation"]["profiles"]:
        ev = {}
        for e in p["gamma_evaluated"]:
            ev.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
        out[p["name"]] = (p["gb"], ev)
    return out


def unit_targets(n, gamma_sym):
    """gamma for each unit gb vector, from Layer 2."""
    out = {}
    for g in gb_labels(n):
        ev = {}
        for pair, ws in gamma_sym.items():
            for W, lin in ws.items():
                if lin.get(g):
                    ev.setdefault(pair, {})[W] = lin[g]
        out[f"unit:{g}"] = ({h: int(h == g) for h in gb_labels(n)}, ev)
    return out


# ------------------------------------------------------------------ solving
def solve(n, targets, reading):
    """targets: name -> gamma dict. Returns solver, column labels, equation tags."""
    basis, par, _ = load_sc(n)
    _, sym = load_coboundary(n)
    idx = {x: i for i, x in enumerate(basis)}
    phis, psis = unknowns(basis, par)
    cols = [phi_label(i, j) for i, j in phis]
    if reading == "exact":
        cols += [psi_label(j) for j in psis]
    col_index = {c: k for k, c in enumerate(cols)}
    names = list(targets)
    solver = SparseSolver(len(names))
    keys = set()
    for pair, ws in sym.items():
        keys |= {(pair, W) for W in ws}
    for name in names:
        for pair, ws in targets[name].items():
            keys |= {(pair, W) for W in ws}
    for (X, Y), W in sorted(keys, key=lambda k: (idx[k[0][0]], idx[k[0][1]], k[1])):
        if idx[X] > idx[Y]:
            continue                         # symmetric partner carries the same equation
        if reading == "mod_K" and W == "K":
            continue
        lin = sym.get((X, Y), {}).get(W, {})
        row = {col_index[k]: v for k, v in lin.items() if k in col_index}
        rhs = [targets[nm].get((X, Y), {}).get(W, 0) for nm in names]
        solver.add_row(row, rhs, tag=(X, Y, W))
    return solver, cols, names


def residual(n, sol_values, target, reading):
    """gamma - delta f at the solution, all ordered pairs; returns {(X,Y): {W: value}}."""
    _, sym = load_coboundary(n)
    df = evaluate_linear(sym, sol_values)
    out = {}
    for pair in set(df) | set(target):
        for W in set(df.get(pair, {})) | set(target.get(pair, {})):
            if reading == "mod_K" and W == "K":
                continue
            r = target.get(pair, {}).get(W, 0) - df.get(pair, {}).get(W, 0)
            if r:
                out.setdefault(pair, {})[W] = r
    return out


# ------------------------------------------------------------------ analytic candidate
def lambda_shift(n, gb):
    """lambda^sigma = sum_j (gb_{sigma,j,+} b_j^- - gb_{sigma,j,-} b_j^+)."""
    lam = {}
    for sig in ("p", "m"):
        e = {}
        for j in range(1, n + 1):
            if gb.get(f"gb_{sig}_{j}_p"):
                e[(f"b_{j}_m",)] = Fraction(gb[f"gb_{sig}_{j}_p"])
            if gb.get(f"gb_{sig}_{j}_m"):
                e[(f"b_{j}_p",)] = -Fraction(gb[f"gb_{sig}_{j}_m"])
        lam[f"a_1_{sig}"] = e
    return lam


def analytic_f(n, gb):
    """f with X = X(a') + kappa f(X), a' = a - kappa*lambda; returns {Z_j: {Z_i or 'K': c}}."""
    alg = OscillatorAlgebra(n, gb=gb)
    lam = lambda_shift(n, gb)
    dec = Decomposer(n)
    f = {}
    for lab, (terms, _, _) in realization_terms(n).items():
        Xp = {}
        for w, c in terms:
            prod = {(): Fraction(c)}
            for x in w:
                factor = {(x,): Fraction(1)}
                if x in lam:                                   # a' = a - kappa*lambda
                    factor = alg.add(factor, {(KAPPA,) + k: v for k, v in lam[x].items()},
                                     coeffs=[1, -1])
                prod = alg.mul(prod, factor)
            Xp = alg.add(Xp, prod)
        X = alg.normalize({w: c for w, c in terms})
        e0, e1 = alg.split_kappa(alg.add(X, Xp, coeffs=[1, -1]))   # X - X(a') = kappa f(X)
        assert not e0
        coords = dec.decompose(e1)
        if coords:
            f[lab] = coords
    return f


def f_to_values(f):
    vals = {}
    for j, coords in f.items():
        for i, c in coords.items():
            vals[psi_label(j) if i == "K" else phi_label(i, j)] = c
    return vals


# ------------------------------------------------------------------ driver
def analyse(n):
    basis, par, sc = load_sc(n)
    gamma_sym = load_gamma_symbolic(n)
    targets = {name: ev for name, (_, ev) in load_profiles(n).items()}
    targets.update({name: ev for name, (_, ev) in unit_targets(n, gamma_sym).items()})
    report = {"n": n, "dim": len(basis), "readings": {}}
    for reading in READINGS:
        solver, cols, names = solve(n, targets, reading)
        rr = {"unknowns": len(cols), "rank": solver.rank(), "kernel_dim": len(cols) - solver.rank(),
              "targets": {}}
        for k, name in enumerate(names):
            bad = solver.inconsistent[k]
            entry = {"trivial": not bad}
            if not bad:
                x = solver.particular_solution(k)
                vals = {cols[c]: v for c, v in x.items()}
                res = residual(n, vals, targets[name], reading)
                entry["residual_entries"] = sum(len(v) for v in res.values())
                entry["particular_solution_nonzero"] = len(vals)
                if name in ("all_plus",) or name.startswith("unit:"):
                    entry["particular_solution"] = {c: frac_str(v) for c, v in sorted(vals.items())}
            else:
                entry["inconsistent_equations"] = len(bad)
                entry["inconsistent_examples"] = [
                    {"X": X, "Y": Y, "Z": W,
                     "gamma": frac_str(targets[name].get((X, Y), {}).get(W, 0))}
                    for X, Y, W in bad[:12]]
                entry["inconsistent_components"] = sorted({W for _, _, W in bad})
            rr["targets"][name] = entry
        report["readings"][reading] = rr
    # analytic candidate: check delta f_analytic == gamma (exact, incl. K) for unit gb and profiles
    an = {}
    for name, (gb, ev) in list(load_profiles(n).items()) + list(unit_targets(n, gamma_sym).items()):
        f = analytic_f(n, gb)
        res = residual(n, f_to_values(f), ev, "exact")
        an[name] = sum(len(v) for v in res.values())
    report["analytic_candidate_residual_entries"] = an
    # analytic f, symbolic in gb (linear): collect from unit vectors
    fsym = {}
    for g in gb_labels(n):
        for j, coords in analytic_f(n, {g: 1}).items():
            for i, c in coords.items():
                fsym.setdefault(j, {}).setdefault(i, {})[g] = c
    report["analytic_f_symbolic"] = {
        j: {i: " + ".join(f"{frac_str(c)}*{g}" for g, c in lin.items()) for i, lin in coords.items()}
        for j, coords in fsym.items()}
    # strict reading: the K-component of gamma as linear forms in gb
    kforms = {}
    for (X, Y), ws in gamma_sym.items():
        if "K" in ws:
            kforms[(X, Y)] = ws["K"]
    report["central_part_of_gamma"] = {
        "pairs_with_K": len(kforms),
        "gb_appearing": sorted({g for lin in kforms.values() for g in lin}),
    }
    return report


def main(ns=(1, 2, 3)):
    date = datetime.date.today().isoformat()
    for n in ns:
        r = analyse(n)
        r["metadata"] = {"generated_by": "src/C_triviality.py", "generation_date": date}
        write_json(r, f"C_{n}_triviality.json")
        print(f"=== n={n} (C({n+1}), dim {r['dim']})")
        for reading, rr in r["readings"].items():
            triv = [k for k, v in rr["targets"].items() if v["trivial"]]
            non = [k for k, v in rr["targets"].items() if not v["trivial"]]
            print(f"  [{reading}] unknowns={rr['unknowns']} rank={rr['rank']} kernel={rr['kernel_dim']}"
                  f"  trivial={len(triv)}/{len(rr['targets'])}  non-trivial={non}")
            for k in triv:
                assert rr["targets"][k]["residual_entries"] == 0
        print(f"  analytic candidate residuals: {set(r['analytic_candidate_residual_entries'].values())}")
        print(f"  central part of gamma: {r['central_part_of_gamma']}")


if __name__ == "__main__":
    main()
