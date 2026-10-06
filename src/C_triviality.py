"""Triviality search for the inhomogeneous deformation of C(n+1) = osp(2|2n)  (Issue I08).

Solves  (δf)(X,Y) = γ(X,Y)  exactly (rational Gaussian elimination) using
  Layer 4 (data/C_{n}_coboundary.json)  : δf as linear forms in phi,
  Layer 3 (data/C_{n}_evaluated*.json)  : γ for concrete gb profiles,
  Layer 2 (data/C_{n}_gamma.json)       : γ symbolic in gb (to derive conditions on gb).
Three readings of "γ = δf":
  A  "mod scalars": f: g -> g ⊕ CK, all components (incl. K) compared
  B  "strict"     : f: g -> g (phi[K,*] = 0), all components (incl. K) compared
  C  "projected"  : f: g -> g, K-components dropped from both sides
Usage: python src/C_triviality.py [n ...]
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_coboundary import evaluate_forms, load_coboundary  # noqa: E402
from C_evaluate import PROFILES, evaluated_filename  # noqa: E402
from C_generators import DATA_DIR, CAlgebra, write_json  # noqa: E402
from oscillator_algebra import elem_add_into, gb_label, poly_const  # noqa: E402

MODES = {"A": "f: g -> g ⊕ CK, compare all components (triviality up to central scalars)",
         "B": "f: g -> g, compare all components incl. K (strict)",
         "C": "f: g -> g, drop K components on both sides (projection to g)"}


# ------------------------------------------------------------------- loaders


def load_json(name):
    with open(os.path.join(DATA_DIR, name)) as fh:
        return json.load(fh)


def gamma_from_layer3(n, profile):
    s3 = load_json(evaluated_filename(n, profile))
    g = {}
    for e in s3["evaluated_deformation"]["entries"]:
        g.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {"1": Fraction(e["coeff"])}
    return g, {k: Fraction(v) for k, v in s3["gb_values"].items()}


def gamma_from_layer2(n):
    s2 = load_json(f"C_{n}_gamma.json")
    g = {}
    for e in s2["inhomogeneous_deformation"]["entries"]:
        g.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {k: Fraction(v)
                                                      for k, v in e["coeff"].items()}
    return g


# -------------------------------------------------------------------- solver


def solve(basis, labels, forms, gamma, mode):
    """Exact incremental elimination of  δf(X,Y)_Z = γ(X,Y)_Z  (all ordered pairs).
    RHS entries are linear forms {param: Fraction} (param '1' for numeric data).
    Returns dict with rank, nullity, consistency conditions (linear forms in params that
    must vanish) and a particular solution (as linear forms) if consistent."""
    allowed = [k for k, lab in enumerate(labels) if mode == "A" or not lab.startswith("phi[K,")]
    allowed_set = set(allowed)
    pivots = {}          # var -> (lhs, rhs) with lhs[var] == 1
    order = []           # pivot creation order
    conditions = []      # rhs forms of rows reducing to 0 = rhs
    witnesses = []       # (X, Y, Z, rhs) for inconsistent rows
    n_eq = 0
    for X in basis:
        for Y in basis:
            fv, gv = forms.get((X, Y), {}), gamma.get((X, Y), {})
            for Z in set(fv) | set(gv):
                if mode == "C" and Z == "K":
                    continue
                lhs = {k: c for k, c in fv.get(Z, {}).items() if k in allowed_set}
                rhs = dict(gv.get(Z, {}))
                n_eq += 1
                for p in order:
                    c = lhs.get(p)
                    if c:
                        plhs, prhs = pivots[p]
                        for k, v in plhs.items():
                            w = lhs.get(k, 0) - c * v
                            if w:
                                lhs[k] = w
                            else:
                                lhs.pop(k, None)
                        for k, v in prhs.items():
                            w = rhs.get(k, 0) - c * v
                            if w:
                                rhs[k] = w
                            else:
                                rhs.pop(k, None)
                if lhs:
                    p = min(lhs)
                    c = lhs[p]
                    pivots[p] = ({k: v / c for k, v in lhs.items()},
                                 {k: v / c for k, v in rhs.items()})
                    order.append(p)
                elif rhs:
                    conditions.append(rhs)
                    witnesses.append((X, Y, Z, rhs))
    # particular solution (free variables = 0), as linear forms in params
    sol = {}
    for p in reversed(order):
        plhs, prhs = pivots[p]
        val = dict(prhs)
        for k, v in plhs.items():
            if k != p and k in sol:
                for q, w in sol[k].items():
                    val[q] = val.get(q, 0) - v * w
        sol[p] = {q: w for q, w in val.items() if w}
    return {"equations": n_eq, "unknowns": len(allowed), "rank": len(order),
            "nullity": len(allowed) - len(order), "conditions": conditions,
            "witnesses": witnesses, "solution": sol}


def condition_rank(conditions, params):
    """Rank of the set of linear conditions (forms in params)."""
    rows = [[Fraction(c.get(p, 0)) for p in params] for c in conditions]
    rank, col = 0, 0
    m = len(params)
    while rows and col < m:
        piv = next((r for r in range(rank, len(rows)) if rows[r][col] != 0), None)
        if piv is None:
            col += 1
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for r in range(len(rows)):
            if r != rank and rows[r][col] != 0:
                f = rows[r][col] / rows[rank][col]
                rows[r] = [a - f * b for a, b in zip(rows[r], rows[rank])]
        rank += 1
        col += 1
    return rank


def verify_solution(basis, labels, forms, gamma, sol_numeric, drop_K=False):
    """Independent check: evaluate δf at the solution and compare with γ entrywise.
    Returns list of mismatching (X, Y, Z, δf, γ)."""
    phi = {k: v for k, v in sol_numeric.items()}
    ev = evaluate_forms(forms, phi)
    bad = []
    for X in basis:
        for Y in basis:
            a, b = ev.get((X, Y), {}), gamma.get((X, Y), {})
            for Z in set(a) | set(b):
                if drop_K and Z == "K":
                    continue
                gv = b.get(Z, {}).get("1", Fraction(0))
                if a.get(Z, 0) != gv:
                    bad.append((X, Y, Z, a.get(Z, 0), gv))
    return bad


# -------------------------------------------- closed-form f from the oscillators


def canonical_f(n):
    """f from the oscillator change of variables  a^σ = a'^σ - κ c^σ,
    c^σ = sum_k ( gb_{σ,k,-} b_k^+ - gb_{σ,k,+} b_k^- ),  where a' obeys undeformed relations.
    Then X(a) = X(a') + κ f(X):
       f(a^σ b_j^s) = - c^σ b_j^s,   f(H_1) = a^+ c^- - a^- c^+,   f(other even) = 0.
    Returns {Z_j: {Z_i or 'K': {gb: Fraction}}} (decomposed in g ⊕ CK)."""
    calg = CAlgebra(n)
    alg = calg.alg

    def c_elem(sig):
        e = {}
        for k in range(1, n + 1):
            elem_add_into(e, {(f"b_{k}_p",): {(gb_label(sig, k, "m"),): Fraction(1)}})
            elem_add_into(e, {(f"b_{k}_m",): {(gb_label(sig, k, "p"),): Fraction(-1)}})
        return e

    c = {"p": c_elem("p"), "m": c_elem("m")}
    f = {}
    for X in calg.basis:
        if X.startswith("E_eps1_del"):
            k, ss = X[10:].split("_")
            sig, s = ss
            val = alg.mul(c[sig], {(f"b_{k}_{s}",): poly_const(1)})
            val = {w: {m: -v for m, v in p.items()} for w, p in val.items()}
        elif X == "H_1":
            val = alg.mul({("a_1_p",): poly_const(1)}, c["m"])
            elem_add_into(val, alg.mul({("a_1_m",): poly_const(1)}, c["p"]), poly_const(-1))
        else:
            continue
        dec = calg.decompose(val)
        f[X] = {Z: {m[0]: v for m, v in p.items()} for Z, p in dec.items()}
    return f


def canonical_phi(labels, fcan, gb_values):
    """Numeric phi vector (index -> value) from the closed form f for given gb values."""
    idx = {lab: k for k, lab in enumerate(labels)}
    phi = {}
    for Zj, comp in fcan.items():
        for Zi, lin in comp.items():
            v = sum((c * gb_values[g] for g, c in lin.items()), Fraction(0))
            if v:
                phi[idx[f"phi[{Zi},{Zj}]"]] = v
    return phi


# ----------------------------------------------------------- structural checks


def gamma_K_formula_mismatches(n):
    """Check  γ_K(X,Y) = -f_K([X,Y]),  f_K(E_eps1_del{j}_{σs}) = 1/2 gb_{σ,j,s}  (symbolic)."""
    from verify_C_structure import bracket_table, load_structure
    s1 = load_structure(n)
    tab, basis, par = bracket_table(s1["structure_constants"]), s1["basis"]["ordering"], s1["parity"]
    g = gamma_from_layer2(n)
    bad = 0
    for X in basis:
        for Y in basis:
            pred = {}
            for W, c in tab.get((X, Y), {}).items():
                if par[W] == 1:
                    k, ss = W[10:].split("_")
                    lab = gb_label(ss[0], int(k), ss[1])
                    pred[lab] = pred.get(lab, 0) - Fraction(1, 2) * c
            pred = {k: v for k, v in pred.items() if v}
            if pred != g.get((X, Y), {}).get("K", {}):
                bad += 1
    return bad


def inner_maps_in_kernel(n):
    """For odd Z, f_Z(X) = [Z, X} is an odd 1-cochain; return #Z with δf_Z != 0."""
    from verify_C_structure import bracket_table, load_structure
    s1 = load_structure(n)
    tab, par = bracket_table(s1["structure_constants"]), s1["parity"]
    basis, _, labels, forms = load_coboundary(n)
    idx = {lab: k for k, lab in enumerate(labels)}
    nonzero = 0
    for Z in basis:
        if par[Z] != 1:
            continue
        phi = {idx[f"phi[{W},{X}]"]: c for X in basis for W, c in tab.get((Z, X), {}).items()}
        nonzero += bool(evaluate_forms(forms, phi))
    return nonzero


# ---------------------------------------------------------------------- main


def fmt_form(form):
    return " + ".join(f"({v})*{k}" for k, v in sorted(form.items())) or "0"


def analyse(n, verbose=True):
    basis, parity, labels, forms = load_coboundary(n)
    s2 = load_json(f"C_{n}_gamma.json")
    params = [g for row in s2["gb_matrix"]["labels"] for g in row]
    out = {"n": n, "profiles": {}, "symbolic": {}}

    # (1) Layer 3 vs Layer 4: each evaluated profile, each mode
    for prof in PROFILES:
        gamma, vals = gamma_from_layer3(n, prof)
        rec = {"gb_values": {k: str(v) for k, v in vals.items()}}
        for mode in "ABC":
            r = solve(basis, labels, forms, gamma, mode)
            consistent = not r["conditions"]
            entry = {"trivial": consistent, "rank": r["rank"], "unknowns": r["unknowns"],
                     "nullity": r["nullity"], "equations": r["equations"],
                     "num_inconsistent_rows": len(r["conditions"])}
            if consistent:
                sol = {k: v.get("1", Fraction(0)) for k, v in r["solution"].items()}
                bad = verify_solution(basis, labels, forms, gamma, sol, drop_K=(mode == "C"))
                entry["independent_check_mismatches"] = len(bad)
                entry["solution_nonzero_phi"] = len([v for v in sol.values() if v])
            else:
                entry["witnesses"] = [{"X": X, "Y": Y, "Z": Z, "residual": str(rhs.get("1"))}
                                      for X, Y, Z, rhs in r["witnesses"][:12]]
            rec[mode] = entry
        # discrepancy of strict mode: K-components of γ (they are exactly the obstruction)
        rec["gamma_K_entries"] = sum(1 for v in gamma.values() for Z in v if Z == "K")
        out["profiles"][prof] = rec
        if verbose:
            print(f"n={n} {prof:8s} " + "  ".join(
                f"{m}:{'trivial' if rec[m]['trivial'] else 'NON-trivial'}"
                f"(rank {rec[m]['rank']}/{rec[m]['unknowns']}, null {rec[m]['nullity']}"
                + (f", chk {rec[m]['independent_check_mismatches']}" if rec[m]['trivial']
                   else f", bad rows {rec[m]['num_inconsistent_rows']}") + ")"
                for m in "ABC"))

    # (2) symbolic γ (Layer 2) vs Layer 4: necessary & sufficient linear conditions on gb
    gsym = gamma_from_layer2(n)
    for mode in "ABC":
        r = solve(basis, labels, forms, gsym, mode)
        rk = condition_rank(r["conditions"], params)
        out["symbolic"][mode] = {
            "num_condition_rows": len(r["conditions"]),
            "condition_rank": rk,
            "conclusion": ("trivial for ALL gb" if rk == 0 else
                           ("trivial iff gb = 0" if rk == len(params) else
                            f"trivial iff gb in a subspace of codim {rk}")),
            "sample_conditions": [fmt_form(c) for c in r["conditions"][:6]],
            "rank": r["rank"], "nullity": r["nullity"]}
        if verbose:
            print(f"n={n} symbolic mode {mode}: conditions rank {rk}/{len(params)} -> "
                  f"{out['symbolic'][mode]['conclusion']}")

    # (3) closed-form f: verify δf_can = γ for every unit gb vector (hence all gb)
    fcan = canonical_f(n)
    unit_bad = 0
    for g in params:
        vals = {h: Fraction(int(h == g)) for h in params}
        gam = {}
        for k, v in gsym.items():
            for Z, lin in v.items():
                c = lin.get(g, Fraction(0))
                if c:
                    gam.setdefault(k, {})[Z] = {"1": c}
        unit_bad += len(verify_solution(basis, labels, forms, gam,
                                        canonical_phi(labels, fcan, vals)))
    fK = {Zj: comp["K"] for Zj, comp in fcan.items() if "K" in comp}
    out["canonical_f"] = {
        "mismatches_over_unit_vectors": unit_bad,
        "f_K": {Zj: fmt_form(v) for Zj, v in fK.items()},
        "f": {Zj: {Zi: fmt_form(v) for Zi, v in comp.items()} for Zj, comp in fcan.items()},
    }
    out["gamma_K_formula_mismatches"] = gamma_K_formula_mismatches(n)
    out["inner_odd_maps_not_in_kernel"] = inner_maps_in_kernel(n)
    if verbose:
        print(f"n={n} closed-form f: δf_can - γ mismatches over all {len(params)} unit gb "
              f"vectors = {unit_bad}")
        print(f"n={n} γ_K = -f_K∘[,] formula mismatches = {out['gamma_K_formula_mismatches']}; "
              f"inner odd maps [Z,·] outside ker δ: {out['inner_odd_maps_not_in_kernel']}"
              f" of {4 * n}")
    return out


def main(ns):
    report = {"modes": MODES, "results": [analyse(n) for n in ns]}
    path = os.path.join(DATA_DIR, "C_triviality_report.json")
    write_json(report, path)
    print("->", path)


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
