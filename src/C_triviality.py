"""Triviality search for the inhomogeneous deformation of C(n+1) = osp(2|2n)  (Issue I08).

Compares Layer 3 (evaluated gamma) / Layer 2 (symbolic gamma) with Layer 4 (symbolic delta f).

Three notions (gamma_K = kappa K component of the deformed bracket, see I05):
  (T1) g-valued:   gamma = delta f              for some odd f: g -> g        (L = g + kappa g)
  (T2) extended:   gamma + gamma_K K = delta f + delta h,  h: g_odd -> C K
  (T3) strict:     gamma + gamma_K K = delta f  with f g-valued (forces gamma_K = 0)
The sign "gamma = -delta f" vs "+delta f" is irrelevant (f -> -f); we solve gamma = delta f.

Usage:  python3 src/C_triviality.py [n ...]     (default 1 2 3; writes data/C_triviality_report.json)
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_coboundary import evaluate, load_schema4  # noqa: E402
from C_generators import DATA, make_algebra, write_json  # noqa: E402
from C_oscillator import ONE, elem_add, elem_mul, lin, lin_add, lin_from_json, lin_scale, lin_str  # noqa: E402


# ------------------------------------------------------------------ exact sparse elimination
class Eliminator:
    """Incremental Gaussian elimination: rows {var: Fraction} = rhs (Lin over gb or constants).
    Rows whose LHS reduces to 0 give consistency conditions rhs = 0."""

    def __init__(self, order):
        self.rank_of = {v: i for i, v in enumerate(order)}
        self.piv = {}  # var -> (row, rhs), row normalised with row[var] = 1
        self.conditions = []

    def reduce(self, row, rhs):
        row = dict(row)
        while True:
            cand = [v for v in row if v in self.piv]
            if not cand:
                return row, rhs
            v = cand[0]
            c = row[v]
            prow, prhs = self.piv[v]
            for k, a in prow.items():
                w = row.get(k, 0) - c * a
                if w:
                    row[k] = w
                else:
                    row.pop(k, None)
            rhs = lin_add(rhs, lin_scale(prhs, c), -1)

    def add(self, row, rhs, tag=None):
        row, rhs = self.reduce({k: v for k, v in row.items() if v}, rhs)
        if not row:
            if rhs:
                self.conditions.append((tag, rhs))
            return
        v = min(row, key=self.rank_of.__getitem__)
        c = row[v]
        row = {k: a / c for k, a in row.items()}
        rhs = lin_scale(rhs, 1 / c)
        self.piv[v] = (row, rhs)

    def solve(self):
        """Particular solution with free variables = 0 (back substitution)."""
        sol = {}
        for v in sorted(self.piv, key=self.rank_of.__getitem__, reverse=True):
            row, rhs = self.piv[v]
            val = dict(rhs)
            for k, a in row.items():
                if k != v and k in sol:
                    val = lin_add(val, lin_scale(sol[k], a), -1)
            sol[v] = val
        return sol

    @property
    def rank(self):
        return len(self.piv)


# ------------------------------------------------------------------ data loading
def load_gamma(n):
    with open(os.path.join(DATA, f"C_{n}_gamma.json")) as fh:
        d = json.load(fh)
    idf = d["inhomogeneous_deformation"]
    gam, cen = {}, {}
    for e in idf["gamma_coefficients"]:
        gam.setdefault((e["X"], e["Y"]), {})[e["Z"]] = lin_from_json(e["coeff"])
    for e in idf["gamma_central"]:
        cen[(e["X"], e["Y"])] = lin_from_json(e["coeff"])
    return idf["parameters"], gam, cen


def load_evaluated(n):
    with open(os.path.join(DATA, f"C_{n}_evaluated.json")) as fh:
        d = json.load(fh)
    out = []
    for p in d["profiles"]:
        gam, cen = {}, {}
        for e in p["gamma_evaluated"]:
            gam.setdefault((e["X"], e["Y"]), {})[e["Z"]] = lin(Fraction(e["coeff"]))
        for e in p["gamma_central_evaluated"]:
            cen[(e["X"], e["Y"])] = lin(Fraction(e["coeff"]))
        out.append((p["name"], {k: Fraction(v) for k, v in p["gb_values"].items()}, gam, cen))
    return out


# ------------------------------------------------------------------ the linear system
def build_system(basis, parity, df, dh, gam, cen, use_f=True, use_h=False, include_central=True):
    """Equations (delta f + delta h)(X,Y)_Z = gamma(X,Y)_Z over unordered pairs index(X) <= index(Y)."""
    phis = sorted({k for r in df.values() for c in r.values() for k in c},
                  key=lambda s: tuple(map(int, s.split("_")[1:])))
    psis = sorted({k for c in dh.values() for k in c}, key=lambda s: int(s.split("_")[1]))
    order = (phis if use_f else []) + (psis if use_h else [])
    el = Eliminator(order)
    for i, x in enumerate(basis):
        for y in basis[i:]:
            lhs = df.get((x, y), {}) if use_f else {}
            rhs = gam.get((x, y), {})
            for z in basis:
                if z in lhs or z in rhs:
                    el.add(lhs.get(z, {}), rhs.get(z, {}), tag=(x, y, z))
            if include_central:
                row = dh.get((x, y), {}) if use_h else {}
                r = cen.get((x, y), {})
                if row or r:
                    el.add(row, r, tag=(x, y, "K"))
    return el, order


def residual(basis, df, dh, gam, cen, sol, use_h, include_central=True):
    """Exact comparison of Layer 4 evaluated at the solution with Layer 2/3 data, all ordered pairs.
    Returns list of mismatching (X, Y, Z)."""
    bad = []
    for x in basis:
        for y in basis:
            lhs = {}
            for z, c in df.get((x, y), {}).items():
                v = {}
                for p, a in c.items():
                    v = lin_add(v, lin_scale(sol.get(p, {}), a))
                if v:
                    lhs[z] = v
            rhs = gam.get((x, y), {})
            for z in set(lhs) | set(rhs):
                if lin_add(lhs.get(z, {}), rhs.get(z, {}), -1):
                    bad.append((x, y, z))
            if include_central:
                v = {}
                if use_h:
                    for p, a in dh.get((x, y), {}).items():
                        v = lin_add(v, lin_scale(sol.get(p, {}), a))
                if lin_add(v, cen.get((x, y), {}), -1):
                    bad.append((x, y, "K"))
    return bad


# ------------------------------------------------------------------ closed form (oscillator shift)
def closed_form_F(n):
    """F from a^sigma -> a^sigma + kappa L^sigma,  L^sigma = sum_j (gb_{sigma,j,-} b_j^+ - gb_{sigma,j,+} b_j^-).
    X(a', b) = X + kappa F(X); returns {X: {Z|'K': Lin}}."""
    alg = make_algebra(n, deformed=True)
    osc = alg.osc
    shifted = {}
    for sg in "pm":
        a = osc.index[f"a_1_{sg}"]
        el = {(0, (a,)): lin(1)}
        for j in range(1, n + 1):
            el = elem_add(el, {(1, (osc.index[f"b_{j}_p"],)): lin(1, osc.gb_name(sg, j, "m"))})
            el = elem_add(el, {(1, (osc.index[f"b_{j}_m"],)): lin(-1, osc.gb_name(sg, j, "p"))})
        shifted[a] = el
    F = {}
    for x, terms in alg.real_terms.items():
        tot = {}
        for words, c in terms:
            prod = {(0, ()): lin(c)}
            for l in words:
                i = osc.index[l]
                fac = shifted.get(i, {(0, (i,)): lin(1)})
                prod = elem_mul(osc, prod, fac)
            tot = elem_add(tot, prod)
        dec = alg.decompose(tot)
        assert {z: v for z, v in dec.get(0, {}).items()} == alg.decompose(alg.gen[x]).get(0, {})
        F[x] = dec.get(1, {})
    return alg, F


def check_closed_form(n, basis, parity, df, dh, gam, cen):
    """Verify gamma = -(delta F) and gamma_K = -(delta h_F) exactly (symbolic in gb)."""
    _, F = closed_form_F(n)
    idx = {x: i for i, x in enumerate(basis)}
    sol = {}
    for y, img in F.items():
        for z, c in img.items():
            if z == "K":
                sol[f"psi_{idx[y]}"] = lin_scale(c, -1)
            else:
                sol[f"phi_{idx[z]}_{idx[y]}"] = lin_scale(c, -1)
    bad = residual(basis, df, dh, gam, cen, sol, use_h=True)
    return F, bad


# ------------------------------------------------------------------ analysis
def analyse(n, verbose=True):
    params, gam, cen = load_gamma(n)
    d4, basis, parity, df, dh = load_schema4(n)
    rep = {"n": n, "algebra": f"C({n+1}) = osp(2|{2*n})", "gb_parameters": params}

    # dimension data: rank of delta on odd 1-cochains
    el0, order = build_system(basis, parity, df, dh, {}, {}, use_f=True, include_central=False)
    nphi = len(order)
    rep["odd_1_cochains"] = nphi
    rep["rank_delta"] = el0.rank
    rep["dim_ker_delta_odd"] = nphi - el0.rank
    rep["dim_odd_part_of_g"] = len(d4["basis"]["odd"])

    # symbolic solves (gb kept as symbols): consistency conditions are linear forms in gb
    for name, kw in (("T1_g_valued", dict(use_f=True, use_h=False, include_central=False)),
                     ("T2_with_central_h", dict(use_f=True, use_h=True, include_central=True)),
                     ("T3_strict_no_h", dict(use_f=True, use_h=False, include_central=True))):
        el, _ = build_system(basis, parity, df, dh, gam, cen, **kw)
        conds = el.conditions
        res = {"rank": el.rank, "n_consistency_conditions": len(conds)}
        # span of the conditions (as linear forms in gb)
        span = Eliminator(params)
        for tag, c in conds:
            span.add(c, {}, tag)
        res["independent_conditions_on_gb"] = [lin_str(r) for r, _ in span.piv.values()]
        res["example_obstructions"] = [{"pair": list(t), "required_zero": lin_str(c)} for t, c in conds[:8]]
        if not conds:
            sol = el.solve()
            bad = residual(basis, df, dh, gam, cen, sol, use_h=kw["use_h"], include_central=kw["include_central"])
            res["particular_solution_residual_mismatches"] = len(bad)
            res["trivial_for_all_gb"] = not bad
        else:
            res["trivial_for_all_gb"] = False
        rep[name] = res

    # closed-form f from the oscillator shift
    F, bad = check_closed_form(n, basis, parity, df, dh, gam, cen)
    rep["closed_form_check_mismatches"] = len(bad)
    rep["closed_form_examples"] = {x: {z: lin_str(v) for z, v in F[x].items()}
                                   for x in (basis[0], f"H_1", f"H_{n+1}", "E_2del1_p") if x in F}

    # Layer 3 vs Layer 4: per-profile numeric comparison
    profiles = []
    for pname, values, g3, c3 in load_evaluated(n):
        pr = {"profile": pname,
              "gb_nonzero": sum(1 for v in values.values() if v)}
        # naive comparison with f = 0
        pr["mismatches_with_f_equal_0"] = sum(len(r) for r in g3.values()) + len(c3)
        for name, kw in (("T1", dict(use_f=True, use_h=False, include_central=False)),
                         ("T2", dict(use_f=True, use_h=True, include_central=True)),
                         ("T3", dict(use_f=True, use_h=False, include_central=True))):
            el, _ = build_system(basis, parity, df, dh, g3, c3, **kw)
            if el.conditions:
                pr[name] = {"trivial": False, "n_inconsistent_equations": len(el.conditions),
                            "first_inconsistencies": [
                                {"X": t[0], "Y": t[1], "Z": t[2], "gamma_value_not_matched": str(c.get(ONE))}
                                for t, c in el.conditions[:5]]}
            else:
                sol = el.solve()
                bad = residual(basis, df, dh, g3, c3, sol, use_h=kw["use_h"],
                               include_central=kw["include_central"])
                nz = sum(1 for v in sol.values() if v)
                pr[name] = {"trivial": not bad, "residual_mismatches": len(bad),
                            "nonzero_f_coefficients_in_solution": nz}
        profiles.append(pr)
    rep["profiles"] = profiles

    if verbose:
        print(f"== n={n} {rep['algebra']}: odd 1-cochains={nphi}, rank δ={el0.rank}, "
              f"dim ker δ={nphi - el0.rank} (dim g_odd={rep['dim_odd_part_of_g']})")
        for name in ("T1_g_valued", "T2_with_central_h", "T3_strict_no_h"):
            r = rep[name]
            print(f"   {name:18s}: conditions on gb = {r['independent_conditions_on_gb'] or 'none'}"
                  f"; trivial for all gb = {r['trivial_for_all_gb']}"
                  + (f"; residual = {r.get('particular_solution_residual_mismatches')}" if not r[
                      'n_consistency_conditions'] else ""))
        print(f"   closed-form f (a -> a + κL): mismatches = {rep['closed_form_check_mismatches']}")
        for pr in profiles:
            print(f"   profile {pr['profile']:>15}: f=0 mismatches={pr['mismatches_with_f_equal_0']:5d} | "
                  f"T1 trivial={pr['T1']['trivial']} | T2 trivial={pr['T2']['trivial']} | "
                  f"T3 trivial={pr['T3']['trivial']}"
                  + (f" ({pr['T3']['n_inconsistent_equations']} inconsistent eqs, e.g. "
                     f"{pr['T3']['first_inconsistencies'][0]})" if not pr['T3']['trivial'] else ""))
    return rep


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    reports = [analyse(n) for n in ns]
    if not argv:
        write_json({"generated_by": "src/C_triviality.py", "reports": reports}, "C_triviality_report.json")


if __name__ == "__main__":
    main(sys.argv[1:])
