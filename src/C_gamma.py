"""Schema 2 for C(n+1): inhomogeneous deformation gamma, linear in the gb parameters.

Deformed oscillator relation:  [b_j^s, a_1^sigma] = -gb[sigma,j,s] * kappa
(kappa odd, central, kappa^2 = 0).  The bracket of two basis elements is
    [X,Y}_gamma = [X,Y]_0 + kappa * gamma(X,Y),   gamma(X,Y) in g.
gamma is obtained by normal-ordering X*Y -+ Y*X in the deformed algebra and keeping the
words that start with kappa; since kappa^2 = 0, gamma is exactly linear in gb.
"""
import json
import os
from fractions import Fraction

import C_generators as G

SIGMAS = "pm"
SIGNS = "pm"


def gb_keys(n):
    """Ordered gb parameter keys (sigma, j, s): row sigma (a_1^sigma), column (j, s)."""
    return [(sg, j, s) for sg in SIGMAS for j in range(1, n + 1) for s in SIGNS]


def gb_name(key):
    sg, j, s = key
    return f"gb_a_1_{sg}_b_{j}_{s}"


def gamma_table(n, gb, expander=None):
    """gamma for a concrete gb dict {(sigma,j,s): number}. Returns
    (zero_part, gamma) as dicts {(X,Y): {Z: Fraction}}.  zero_part must equal Schema 1."""
    ex = expander or G.BasisExpander(n, with_K=True)
    osc = G.Oscillators({k: Fraction(v) for k, v in gb.items()})
    zero, gam = {}, {}
    names = G.basis_names(n)
    for X in names:
        for Y in names:
            br = osc.bracket(ex.real[X], G.parity_of(X), ex.real[Y], G.parity_of(Y))
            z = {w: c for w, c in br.items() if "K" not in w}
            g = {w[1:]: c for w, c in br.items() if w and w[0] == "K"}
            if any("K" in w[1:] for w in br if w and w[0] == "K"):
                raise ValueError("kappa^2 term survived")
            if z:
                zero[(X, Y)] = ex.expand(z)
            if g:
                gam[(X, Y)] = ex.expand(g)
    return zero, gam


def symbolic_gamma(n, expander=None):
    """{(X,Y,Z): {gb_key: Fraction}} by running one unit parameter at a time."""
    ex = expander or G.BasisExpander(n, with_K=True)
    out = {}
    for key in gb_keys(n):
        _, gam = gamma_table(n, {key: 1}, ex)
        for (X, Y), zs in gam.items():
            for Z, c in zs.items():
                out.setdefault((X, Y, Z), {})[key] = c
    return out


def gamma_parity_ok(sym):
    """gamma(X,Y) has parity p(X)+p(Y)+1 (kappa is odd)."""
    return all(G.parity_of(Z) == (G.parity_of(X) + G.parity_of(Y) + 1) % 2
               for (X, Y, Z) in sym)


def build_schema2(n, today="2026-10-06"):
    ex = G.BasisExpander(n, with_K=True)
    sym = symbolic_gamma(n, ex)
    keys = gb_keys(n)
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in SIGNS]
    matrix = [[gb_name((sg, j, s)) for j in range(1, n + 1) for s in SIGNS] for sg in SIGMAS]
    entries = []
    for X in G.basis_names(n):
        for Y in G.basis_names(n):
            for (x, y, Z), coeffs in sorted(((k, v) for k, v in sym.items()
                                             if k[0] == X and k[1] == Y)):
                entries.append({"X": X, "Y": Y, "Z": Z,
                                "coeff": {gb_name(k): G.frac_str(c)
                                          for k, c in sorted(coeffs.items())},
                                "sign_rule": "graded"})
    return {
        "schema_version": "5.0",
        "layer": "gamma",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})"},
        "source_structure": f"C_{n}_structure.json",
        "inhomogeneous_deformation": {
            "description": "[X,Y}_gamma = [X,Y]_0 + kappa * gamma(X,Y); gamma linear in gb.",
            "deformed_relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
            "bracket_rule": "XY - (-1)^{p(X)p(Y)} YX in U(A), kappa odd central, kappa^2 = 0",
            "gb_matrix": {
                "shape": [2, 2 * n], "parity": 1, "count": 4 * n,
                "rows": list(G.FERMIONS), "columns": cols,
                "entries": matrix,
                "parameters": [gb_name(k) for k in keys],
            },
            "gamma_parity_rule": "p(Z) = p(X) + p(Y) + 1 for every non-zero gamma_{XY}^Z",
            "gamma": entries,
        },
        "metadata": {"generated_by": "src/C_gamma.py", "generation_date": today,
                     "references": ["docs/math/C_inhomogeneous_definition.md"]},
    }


# ----------------------------------------------------------- consistency ----
def check_cocycle(n, sym):
    """First-order super Jacobi on g + kappa*g.  With [X,kappa Z] = (-1)^{p(X)} kappa [X,Z],
    the kappa-part of [X,[Y,Z]] = [[X,Y],Z] + (-1)^{xy}[Y,[X,Z]] reads, for each X,Y,Z:
      (-1)^x [X,g(Y,Z)] + g(X,[Y,Z]) = [g(X,Y),Z]' + g([X,Y],Z)
                                       + (-1)^{xy}( (-1)^y [Y,g(X,Z)] + g(Y,[X,Z]) )
    where [g(X,Y),Z]' = [kappa W, Z} part = (-1)^{...} handled via antisymmetry.
    Returns the list of failing triples (empty = cocycle)."""
    names = G.basis_names(n)
    par = {nm: G.parity_of(nm) for nm in names + ["K"]}
    zero = {}
    for e in _schema1(n):
        zero.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    gam = {}
    for (X, Y, Z), cs in sym.items():
        gam.setdefault((X, Y), {})[Z] = cs

    def lin(table, u, v):
        out = {}
        for x, cx in u.items():
            for y, cy in v.items():
                for z, c in table.get((x, y), {}).items():
                    out[z] = out.get(z, 0) + cx * cy * c
        return {k: c for k, c in out.items() if c != 0}

    def vec_add(a, b, s=1):
        out = dict(a)
        for k, c in b.items():
            out[k] = out.get(k, 0) + s * c
        return out

    # gamma is stored per gb key; check each gb key separately
    keys = sorted({k for cs in sym.values() for k in cs})
    bad = []
    for key in keys:
        g1 = {(X, Y): {Z: cs[key] for Z, cs in zs.items() if key in cs}
              for (X, Y), zs in gam.items()}
        g1 = {k: v for k, v in g1.items() if v}
        for X in names:
            for Y in names:
                for Z in names:
                    x, y, z = par[X], par[Y], par[Z]
                    # kappa-part of [X,[Y,Z]]
                    t1 = vec_add({k: (-1) ** x * c for k, c in
                                  lin(zero, {X: 1}, g1.get((Y, Z), {})).items()},
                                 lin(g1, {X: 1}, zero.get((Y, Z), {})))
                    # kappa-part of [[X,Y],Z]:  [kappa W, Z} = -(-1)^{(1+w)z}[Z, kappa W}
                    #   = -(-1)^{(1+w)z} (-1)^z kappa [Z,W] = -(-1)^{wz} kappa [Z,W]
                    gxy = g1.get((X, Y), {})
                    t2 = {}
                    for W, cw in gxy.items():
                        w = par[W]
                        t2 = vec_add(t2, {k: -((-1) ** (w * z)) * cw * c for k, c in
                                          lin(zero, {Z: 1}, {W: 1}).items()})
                    t2 = vec_add(t2, lin(g1, zero.get((X, Y), {}), {Z: 1}))
                    t3 = vec_add({k: (-1) ** y * c for k, c in
                                  lin(zero, {Y: 1}, g1.get((X, Z), {})).items()},
                                 lin(g1, {Y: 1}, zero.get((X, Z), {})))
                    rhs = vec_add(t2, t3, (-1) ** (x * y))
                    diff = vec_add(t1, rhs, -1)
                    if any(c != 0 for c in diff.values()):
                        bad.append((key, X, Y, Z))
    return bad


_S1 = {}


def _schema1(n):
    if n not in _S1:
        with open(os.path.join(G.DATA_DIR, f"C_{n}_structure.json")) as f:
            _S1[n] = json.load(f)["structure_constants"]
    return _S1[n]


def check_zero_part_matches_schema1(n, expander=None):
    """Undeformed part of the deformed bracket must reproduce Schema 1 exactly."""
    zero, _ = gamma_table(n, {k: 1 for k in gb_keys(n)}, expander)
    s1 = {}
    for e in _schema1(n):
        s1.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return zero == s1


def main(ns=(1, 2, 3)):
    for n in ns:
        d = build_schema2(n)
        path = os.path.join(G.DATA_DIR, f"C_{n}_gamma.json")
        with open(path, "w") as f:
            json.dump(d, f, indent=1)
        print(path, len(d["inhomogeneous_deformation"]["gamma"]), "gamma entries")


if __name__ == "__main__":
    main()
