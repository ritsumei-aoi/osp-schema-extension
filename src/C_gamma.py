"""Schema 2 (gamma structure) for C(n+1): inhomogeneous deformation by [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa.

For basis elements X, Y the deformed bracket is
    [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y),        gamma(X,Y) in g (+ a scalar kappa*K residue).
gamma is *linear* in the 4n parameters gb, so every coefficient is stored as {gb_symbol: rational}.

Usage: python src/C_gamma.py      (writes data/C_{n}_gamma.json for n = 1, 2, 3)
Also provides check_cocycle(), the first-order (kappa-linear) super Jacobi identity, which is run
against the JSON files only.
"""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import C_generators as cg  # noqa: E402

ROOT = cg.ROOT
DATA = cg.DATA


def gb_matrix(n):
    rows = ["a_1_p", "a_1_m"]
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in "pm"]
    entries = [[cg.gb_name(r[-1], int(c.split("_")[1]), c[-1]) for c in cols] for r in rows]
    params = [
        {"name": entries[i][k], "row": rows[i], "col": cols[k], "parity": 1,
         "relation": f"[{cols[k]}, {rows[i]}] = -{entries[i][k]} * kappa"}
        for i in range(2) for k in range(2 * n)
    ]
    return {"shape": [2, 2 * n], "rows": rows, "cols": cols, "entries": entries, "parameters": params}


def schema2(n):
    alg = cg.CAlgebra(n)
    gamma, central = cg.gamma_table(alg)
    order = {b: i for i, b in enumerate(alg.basis)}
    syms = cg.gb_names(n)
    g_list = []
    for (X, Y) in sorted(gamma, key=lambda k: (order[k[0]], order[k[1]])):
        for Z in sorted(gamma[(X, Y)], key=lambda z: order[z]):
            coeff = gamma[(X, Y)][Z]
            g_list.append({"X": X, "Y": Y, "Z": Z,
                           "coeff": {s: cg.fstr(coeff[s]) for s in syms if s in coeff}})
    c_list = []
    for (X, Y) in sorted(central, key=lambda k: (order[k[0]], order[k[1]])):
        c = central[(X, Y)]
        c_list.append({"X": X, "Y": Y, "coeff": {s: cg.fstr(c[s]) for s in syms if s in c}})
    return {
        "schema_version": "5.0",
        "layer": 2,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})",
                    "dimension": {"even": len(alg.even), "odd": len(alg.odd), "total": len(alg.basis)}},
        "structure_file": f"C_{n}_structure.json",
        "gb_matrix": gb_matrix(n),
        "inhomogeneous_deformation": {
            "definition": "[b_j^s, a_1^σ] = -gb_{σ,j,s} κ ; [X,Y]_γ = [X,Y]_0 + κ γ(X,Y)",
            "parameter_count": 4 * n,
            "parameter_parity": 1,
            "parameter_convention": ("gb are ordinary commuting scalars; 'parity 1' labels the odd oscillator pair "
                                     "(b,a) they belong to, which is what makes [b,a] (odd) = gb * kappa (odd) parity-consistent."),
            "coefficient_format": "coeff maps gb symbol -> rational; gamma is linear in gb",
            "basis_order": alg.basis,
            "gamma": g_list,
            "central_component": {
                "description": ("Coefficient of kappa*K (= kappa) in [X,Y]_gamma: a scalar part that lies outside g "
                                "(K=1 is not a basis element). Always attached to pairs with [X,Y] odd."),
                "entries": c_list,
            },
        },
        "consistency": {
            "gamma_parity_rule": "p(Z) = p(X) + p(Y) + 1 for every gamma_{XYZ} entry",
            "undeformed_limit": "gb = 0 gives Schema 1 exactly",
            "cocycle": "kappa-linear super Jacobi identity checked by src/C_gamma.py::check_cocycle",
            "counts": {"gamma_entries": len(g_list), "central_entries": len(c_list)},
        },
        "metadata": {"generated_by": "src/C_gamma.py", "generation_date": "2026-10-06",
                     "references": ["docs/math/C_inhomogeneous_definition.md"]},
    }


# ---------------------------------------------------------------------------
# checks that use only the JSON files
# ---------------------------------------------------------------------------
def load_gamma(n):
    s1 = json.load(open(DATA / f"C_{n}_structure.json"))
    s2 = json.load(open(DATA / f"C_{n}_gamma.json"))
    return s1, s2


def tables(s1, s2):
    basis = s1["basis"]["even"] + s1["basis"]["odd"]
    parity = s1["parity"]
    table = {}
    for e in s1["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = F(e["coeff"])
    dfm = s2["inhomogeneous_deformation"]
    gam = {}  # sym -> {(X,Y): {Z: F}}
    for e in dfm["gamma"]:
        for sym, c in e["coeff"].items():
            gam.setdefault(sym, {}).setdefault((e["X"], e["Y"]), {})[e["Z"]] = F(c)
    cen = {}  # sym -> {(X,Y): F}
    for e in dfm["central_component"]["entries"]:
        for sym, c in e["coeff"].items():
            cen.setdefault(sym, {})[(e["X"], e["Y"])] = F(c)
    return basis, parity, table, gam, cen


def _lin(*terms):
    out = {}
    for coef, vec in terms:
        for k, v in vec.items():
            out[k] = out.get(k, F(0)) + coef * v
    return {k: v for k, v in out.items() if v}


def check_cocycle(s1, s2):
    """Returns list of failures of the kappa-linear Jacobi identity (g-valued and K-valued parts)."""
    basis, par, T, G, C = tables(s1, s2)

    def br(u, Y):  # [u, Y] for vector u
        return _lin(*[(c, T.get((x, Y), {})) for x, c in u.items()])

    def bl(X, u):  # [X, u]
        return _lin(*[(c, T.get((X, y), {})) for y, c in u.items()])

    fails = []
    for sym in set(G) | set(C):
        g = G.get(sym, {})
        c = C.get(sym, {})

        def gam(u, Y):
            return _lin(*[(cc, g.get((x, Y), {})) for x, cc in u.items()])

        def gam2(X, u):
            return _lin(*[(cc, g.get((X, y), {})) for y, cc in u.items()])

        def cen(u, Y):
            return sum((cc * c.get((x, Y), F(0)) for x, cc in u.items()), F(0))

        def cen2(X, u):
            return sum((cc * c.get((X, y), F(0)) for y, cc in u.items()), F(0))

        for X in basis:
            for Y in basis:
                s = -1 if (par[X] and par[Y]) else 1
                for Z in basis:
                    YZ, XY, XZ = T.get((Y, Z), {}), T.get((X, Y), {}), T.get((X, Z), {})
                    pX, pY = par[X], par[Y]
                    val = _lin(
                        ((-1) ** pX, bl(X, g.get((Y, Z), {}))), (1, gam2(X, YZ)),
                        (-1, br(g.get((X, Y), {}), Z)), (-1, gam(XY, Z)),
                        (-s * (-1) ** pY, bl(Y, g.get((X, Z), {}))), (-s, gam2(Y, XZ)),
                    )
                    kval = cen2(X, YZ) - cen(XY, Z) - s * cen2(Y, XZ)
                    if val or kval:
                        fails.append((sym, X, Y, Z))
                        if len(fails) > 20:
                            return fails
    return fails


def check_parity(s1, s2):
    basis, par, T, G, C = tables(s1, s2)
    bad = []
    for sym, g in G.items():
        for (X, Y), comps in g.items():
            for Z in comps:
                if par[Z] != (par[X] + par[Y] + 1) % 2:
                    bad.append((sym, X, Y, Z))
    for sym, c in C.items():
        for (X, Y) in c:
            if (par[X] + par[Y]) % 2 != 1:  # kappa is odd: [X,Y] must be odd
                bad.append((sym, X, Y, "K"))
    return bad


def check_schema1_consistency(s1, s2):
    errs = []
    basis = s1["basis"]["even"] + s1["basis"]["odd"]
    if s2["inhomogeneous_deformation"]["basis_order"] != basis:
        errs.append("basis order differs from Schema 1")
    n = s1["algebra"]["n"]
    if s2["algebra"] != {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})",
                         "dimension": {"even": len(s1["basis"]["even"]), "odd": len(s1["basis"]["odd"]), "total": len(basis)}}:
        errs.append("algebra block differs")
    gbm = s2["gb_matrix"]
    if gbm["shape"] != [2, 2 * n] or len(gbm["parameters"]) != 4 * n:
        errs.append("gb matrix shape")
    names = {p["name"] for p in gbm["parameters"]}
    used = {sym for e in s2["inhomogeneous_deformation"]["gamma"] for sym in e["coeff"]}
    if not used <= names:
        errs.append("gamma uses unknown gb symbols")
    return errs


def main(ns=(1, 2, 3)):
    ok = True
    for n in ns:
        cg.write_json(DATA / f"C_{n}_gamma.json", schema2(n))
        s1, s2 = load_gamma(n)
        errs = check_schema1_consistency(s1, s2)
        pbad = check_parity(s1, s2)
        cbad = check_cocycle(s1, s2)
        d = s2["consistency"]["counts"]
        print(f"n={n}: gamma entries={d['gamma_entries']} central entries={d['central_entries']} "
              f"consistency errors={len(errs)} parity failures={len(pbad)} cocycle failures={len(cbad)}")
        ok &= not (errs or pbad or cbad)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
