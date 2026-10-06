"""Schema 2 (gamma structure) for C(n+1): inhomogeneous deformation [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa.

For every ordered pair of basis elements the bracket is computed in the deformed oscillator
algebra and normal ordered with kappa on the left:
    [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y),
gamma(X, Y) is decomposed in basis + K ("K" entries = the central kappa*1 part).

Usage:  python3 src/C_gamma.py        # writes data/C_{1,2,3}_gamma.json and checks them
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import (DATA_DIR, K_LABEL, SCHEMA_VERSION, CAlgebra, algebra_block,  # noqa: E402
                          central_elements_block, write_json)
from C_osc import Lin, gb_name, split_kappa  # noqa: E402
from verify_C_structure import verify  # noqa: E402


def gb_symbols(n: int) -> list[str]:
    return [gb_name(sig, j, s) for sig in ("p", "m") for j in range(1, n + 1) for s in ("p", "m")]


def gamma_table(n: int) -> dict:
    """{(X, Y): {Z or 'K': Lin}} for all ordered pairs with non-zero gamma."""
    alg = CAlgebra(n, deformed=True)
    und = CAlgebra(n)
    out = {}
    for x in alg.basis:
        for y in alg.basis:
            p0, p1 = split_kappa(alg.raw_bracket(x, y))
            assert alg.decompose(p0) == und.bracket0(x, y), "kappa-free part differs from Schema 1"
            dec = alg.decompose(p1)
            if dec:
                out[(x, y)] = dec
    return out


def build_gamma(n: int) -> dict:
    tab = gamma_table(n)
    alg_basis = CAlgebra(n).basis
    syms = gb_symbols(n)
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in ("p", "m")]
    gamma = []
    for x in alg_basis:
        for y in alg_basis:
            dec = tab.get((x, y), {})
            for z in alg_basis + [K_LABEL]:
                if z in dec:
                    gamma.append({"X": x, "Y": y, "Z": z, "coeff": dec[z].to_str()})
    return {
        "schema_version": SCHEMA_VERSION,
        "algebra": algebra_block(n),
        "basis_ref": {"file": f"C_{n}_structure.json", "ordered": alg_basis},
        "central_elements": central_elements_block(),
        "inhomogeneous_deformation": {
            "relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} kappa",
            "bracket": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)   (kappa normal-ordered to the left)",
            "gb_matrix": {
                "rows": ["a_1_p", "a_1_m"],
                "cols": cols,
                "symbols": [[gb_name(sig, int(c.split('_')[1]), c.split('_')[2]) for c in cols]
                            for sig in ("p", "m")],
                "count": len(syms),
                "parity": 1,
                "parity_note": "gb multiplies the odd central kappa in a mixed-parity bracket; numerically the gb are "
                               "ordinary (commuting) scalars",
            },
            "gamma_target": "basis + K; Z = 'K' is the central part kappa*1 of the bracket",
            "gamma": gamma,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": ["docs/math/C_inhomogeneous_definition.md"],
            "notation": "handover/notation.md",
        },
    }


# --------------------------------------------------------------------------- consistency checks
def extended_structure(struct: dict, gamma_entries: list, values: dict) -> dict:
    """Schema-1-like table of L = g + kappa*g + C kappa*K with gamma evaluated at `values`.

    [X, Y]      = [X,Y]_0 + kappa gamma(X,Y)
    [X, kA]     = (-1)^{p(X)} kappa [X, A]_0
    [kA, Y]     = kappa [A, Y]_0
    [kA, kB]    = 0,   kappa*K central.
    Its super Jacobi identity is equivalent to the 2-cocycle condition for gamma.
    """
    basis = struct["basis"]["ordered"]
    par = struct["parity"]
    kl = {b: "kappa*" + b for b in basis}
    ext_basis = basis + [kl[b] for b in basis] + ["kappa*K"]
    ext_par = dict(par)
    ext_par.update({kl[b]: 1 - par[b] for b in basis})
    ext_par["kappa*K"] = 1
    sc = []
    for e in struct["structure_constants"]:
        x, y, z, c = e["X"], e["Y"], e["Z"], Fraction(e["coeff"])
        sc.append({"X": x, "Y": y, "Z": z, "coeff": str(c)})
        sc.append({"X": x, "Y": kl[y], "Z": kl[z], "coeff": str((-1) ** par[x] * c)})
        sc.append({"X": kl[x], "Y": y, "Z": kl[z], "coeff": str(c)})
    for e in gamma_entries:
        v = _parse_lin(e["coeff"]).evaluate(values)
        if v:
            sc.append({"X": e["X"], "Y": e["Y"], "Z": "kappa*" + e["Z"], "coeff": str(v)})
    # merge duplicates
    merged: dict = {}
    for e in sc:
        k = (e["X"], e["Y"], e["Z"])
        merged[k] = merged.get(k, 0) + Fraction(e["coeff"])
    return {"algebra": struct["algebra"], "basis": {"ordered": ext_basis}, "parity": ext_par,
            "structure_constants": [{"X": x, "Y": y, "Z": z, "coeff": str(c)} for (x, y, z), c in merged.items() if c]}


def _parse_lin(s: str) -> Lin:
    """Parse the Lin.to_str() format (sum of [coeff*]symbol and rational constants)."""
    import sympy
    expr = sympy.sympify(s)
    out = Lin()
    for term in sympy.Add.make_args(expr):
        if term == 0:
            continue
        c, rest = term.as_coeff_Mul()
        key = "1" if rest == 1 else str(rest)
        out = out + Lin({key: Fraction(int(sympy.Rational(c).p), int(sympy.Rational(c).q))})
    return out


def check_consistency(n: int, gam: dict, struct: dict) -> dict:
    basis = struct["basis"]["ordered"]
    par = struct["parity"]
    entries = gam["inhomogeneous_deformation"]["gamma"]
    syms = gb_symbols(n)
    res = {"basis_match": gam["basis_ref"]["ordered"] == basis, "labels_known": True, "parity_ok": True,
           "linear_in_gb": True, "antisymmetry_ok": True, "cocycle_ok": True}
    table: dict = {}
    for e in entries:
        if e["Z"] != K_LABEL and e["Z"] not in par or e["X"] not in par or e["Y"] not in par:
            res["labels_known"] = False
        pz = 0 if e["Z"] == K_LABEL else par[e["Z"]]
        if pz != (par[e["X"]] + par[e["Y"]] + 1) % 2:
            res["parity_ok"] = False
        lin = _parse_lin(e["coeff"])
        if "1" in lin or not set(lin) <= set(syms):
            res["linear_in_gb"] = False
        table[(e["X"], e["Y"], e["Z"])] = lin
    # antisymmetry of gamma: gamma(X,Y) = -(-1)^{p(X)p(Y)} gamma(Y,X)
    for (x, y, z), v in table.items():
        w = table.get((y, x, z), Lin())
        if v + w.scale((-1) ** (par[x] * par[y])):
            res["antisymmetry_ok"] = False
    # cocycle condition via Jacobi of the extended algebra, for each unit gb (complete by linearity)
    for s in syms:
        vals = {t: (1 if t == s else 0) for t in syms}
        r = verify(extended_structure(struct, entries, vals))
        if not r["passed"]:
            res["cocycle_ok"] = False
    res["passed"] = all(res.values())
    return res


def main(ns=(1, 2, 3)) -> int:
    ok = True
    for n in ns:
        gam = build_gamma(n)
        write_json(gam, f"C_{n}_gamma.json")
        with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as fh:
            struct = json.load(fh)
        res = check_consistency(n, gam, struct)
        ent = gam["inhomogeneous_deformation"]["gamma"]
        nk = sum(1 for e in ent if e["Z"] == K_LABEL)
        pairs = len({(e["X"], e["Y"]) for e in ent})
        print(f"n={n}: {len(gb_symbols(n))} gb params, {len(ent)} gamma entries ({nk} central K) over {pairs} pairs; "
              f"checks {res}")
        ok &= res["passed"]
    print("OVERALL:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
