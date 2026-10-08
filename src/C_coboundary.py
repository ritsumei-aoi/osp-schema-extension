"""
Schema 4 generator (Issue I07): coboundary structure for C(n+1).

Odd linear map f: g -> g, defined through the oscillator shift

    b_k^s  ->  b_k^s + kappa * c_k^s,    c_k^s = gb_{+,k,s} a_1^- + gb_{-,k,s} a_1^+ ,

which removes the deformation from the oscillator relations (see I07 Response).
For a basis element Z (a polynomial in the oscillators) the shifted element is
    phi(Z) = Z + kappa * F(Z)   (kappa written leftmost),
and we set  f := -F  so that gamma = delta f with the coboundary formula of
docs/math/C_coboundary_definition.md:

    (delta f)(X,Y) = (-1)^{|X|}[X,f(Y)] - (-1)^{(|X|+1)|Y|}[Y,f(X)] - f([X,Y]).

F(Z) lies in g + C K; the K-component of f (a linear functional lambda on g)
is stored separately as `f_K_component`.  `coboundary.entries` is delta f for
the strictly g-valued part of f (as the definition requires f: g -> g); the
K-terms  -lambda([X,Y]) K  that the K-component would add are stored under
`K_extension` for the analysis in I08.

Usage: python3 src/C_coboundary.py [n ...]   (default 1 2 3; all profiles)
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from fractions import Fraction

import sympy
from sympy import expand, Rational, Symbol

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osc_algebra import OscAlgebra, gb_symbols, ONE  # noqa: E402
import C_generators as G  # noqa: E402
import C_gamma as Gm  # noqa: E402
import C_evaluate as E  # noqa: E402

DATA_DIR = G.DATA_DIR


# ------------------------------------------------------------ the map f
def shift_map(n, syms):
    """b_k^s -> b_k^s + kappa * (gb_{+,k,s} a_1^- + gb_{-,k,s} a_1^+)."""
    m = {}
    for k in range(1, n + 1):
        for s in "pm":
            m[f"b_{k}_{s}"] = {(f"b_{k}_{s}",): ONE,
                               ("kappa", "a_1_m"): syms[("p", k, s)],
                               ("kappa", "a_1_p"): syms[("m", k, s)]}
    return m


def compute_f(n):
    """Return (f_g, lam, dec) with f_g[Z] = {Z_i: coeff} (g-valued part of f = -F)
    and lam[Z] = K-component of f(Z) (sympy expr, 0 if absent)."""
    syms = gb_symbols(n)
    alg = OscAlgebra(n, gb=syms)      # deformed engine (kappa^2 = 0 handles order)
    dec = G.Decomposer(n, alg)
    R = dec.R
    shift = shift_map(n, syms)
    f_g, lam = {}, {}
    for Z in G.basis(n):
        phi = alg.substitute(R[Z], shift)
        p0, p1 = alg.split_kappa(phi)
        assert {w: expand(c) for w, c in p0.items()} == R[Z], Z
        F = dec.decompose(p1) if p1 else {}
        f = {Zi: expand(-c) for Zi, c in F.items()}          # f = -F
        lam[Z] = f.pop("K", sympy.Integer(0))
        f_g[Z] = f
    return f_g, lam, dec


# --------------------------------------------------------- coboundary
def load_table(n):
    s1 = G.load_structure(n)
    table = {}
    for e in s1["structure_constants"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Rational(e["coeff"])
    return table


def _add(acc, vec, scale):
    for Z, c in vec.items():
        acc[Z] = acc.get(Z, 0) + scale * c


def bracket_with_vec(table, X, vec):
    """[X, sum_i c_i Z_i} as {Z: coeff}."""
    acc = {}
    for Zi, c in vec.items():
        _add(acc, table.get((X, Zi), {}), c)
    return acc


def coboundary(n, f_g, lam, table=None):
    """delta f for the g-valued f (strict) and the K-terms of the lambda part.
    Returns (delta_entries {(X,Y): {Z: expr}}, K_terms {(X,Y): expr})."""
    table = table or load_table(n)
    par = G.parity_map(n)
    B = G.basis(n)
    delta, kterms = {}, {}
    for X in B:
        for Y in B:
            acc = {}
            sX = -1 if par[X] else 1
            _add(acc, bracket_with_vec(table, X, f_g[Y]), sX)
            sY = -1 if ((par[X] + 1) * par[Y]) % 2 else 1
            _add(acc, bracket_with_vec(table, Y, f_g[X]), -sY)
            br = table.get((X, Y), {})
            kt = 0
            for Z, c in br.items():
                _add(acc, f_g[Z], -c)
                kt += -c * lam[Z]
            acc = {Z: expand(c) for Z, c in acc.items() if expand(c) != 0}
            if acc:
                delta[(X, Y)] = acc
            kt = expand(kt)
            if kt != 0:
                kterms[(X, Y)] = kt
    return delta, kterms


# ------------------------------------------------------------- output
def _entries(delta, kterms, values=None):
    """Flatten to JSON entries; if values given, substitute and drop zeros."""
    subs = ({Symbol(l): Rational(v) for l, v in values.items()} if values else None)

    def cs(c):
        c = c.subs(subs) if subs else c
        return expand(c)

    ent, kent = [], []
    for (X, Y), vec in delta.items():
        for Z, c in vec.items():
            v = cs(c)
            if v != 0:
                ent.append({"X": X, "Y": Y, "Z": Z, "coeff": str(v)})
    for (X, Y), c in kterms.items():
        v = cs(c)
        if v != 0:
            kent.append({"X": X, "Y": Y, "Z": "K", "coeff": str(v)})
    return ent, kent


def f_map_json(f_g, lam, values=None):
    subs = ({Symbol(l): Rational(v) for l, v in values.items()} if values else None)
    out = {}
    for Z, vec in f_g.items():
        d = {}
        for Zi, c in vec.items():
            v = expand(c.subs(subs)) if subs else c
            if v != 0:
                d[Zi] = str(v)
        out[Z] = d
    lam_out = {}
    for Z, c in lam.items():
        v = expand(c.subs(subs)) if subs else c
        if v != 0:
            lam_out[Z] = str(v)
    return out, lam_out


_CACHE = {}


def _compute(n):
    if n not in _CACHE:
        f_g, lam, dec = compute_f(n)
        delta, kterms = coboundary(n, f_g, lam)
        _CACHE[n] = (f_g, lam, delta, kterms)
    return _CACHE[n]


def build_schema4(n, profile=E.REPRESENTATIVE, date=None):
    date = date or datetime.date.today().isoformat()
    f_g, lam, delta, kterms = _compute(n)
    values = E.profile_values(profile, n)
    vals_str = {l: str(v) for l, v in values.items()}
    ent, kent = _entries(delta, kterms, vals_str)
    fmap, lam_json = f_map_json(f_g, lam, vals_str)
    par = G.parity_map(n)
    doc = {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
                    "dimension": G.dimensions(n)},
        "schema1_file": f"C_{n}_structure.json",
        "schema3_file": os.path.basename(E.evaluated_path(n, profile)),
        "profile": profile,
        "gb_assignment": vals_str,
        "f_definition": {
            "type": "odd linear map f: g -> g",
            "origin": "oscillator shift b_k^s -> b_k^s + kappa*(gb_{+,k,s} a_1^- + gb_{-,k,s} a_1^+); phi(Z) = Z + kappa F(Z); f = -F",
            "parity_rule": "|f(Z)| = |Z| + 1",
            "formula_even": "f(Z) = -(sum over boson letters of Z) of the letter replaced by its shift (normal-ordered, kappa leftmost)",
            "formula_odd": "f(E_{+eps,s delta_k}) = gb_{+,k,s} (a_1^+ a_1^-) = gb_{+,k,s} (N_a - 1/2) + gb_{+,k,s}/2 K ;  f(E_{-eps,s delta_k}) = gb_{-,k,s} (1 - a_1^+ a_1^-) = -gb_{-,k,s} (N_a - 1/2) + gb_{-,k,s}/2 K",
            "K_component": "f(Z) has a K-component lambda(Z) for odd Z; it is NOT part of the g-valued map and is stored in f_K_component",
        },
        "coboundary_formula": "(delta f)(X,Y) = (-1)^{|X|}[X,f(Y)] - (-1)^{(|X|+1)|Y|}[Y,f(X)] - f([X,Y])",
        "f_map": {
            "description": "f(Z_j) = sum_i phi_ij Z_i ; stored as {Z_j: {Z_i: phi_ij}} (g-valued part)",
            "entries": fmap,
        },
        "f_K_component": {
            "description": "lambda(Z) = K-coefficient of f(Z) (nonzero only for odd Z); not used in coboundary.entries",
            "entries": lam_json,
        },
        "coboundary": {
            "description": "(delta f)(X,Y) = sum_Z coeff * Z for the g-valued f; all ordered pairs with nonzero value",
            "entries": ent,
        },
        "K_extension": {
            "description": "extra terms -lambda([X,Y]) K that delta(f + lambda K) would add; compare with the Z=K entries of Layer 3",
            "entries": kent,
        },
        "summary": {
            "coboundary_entries": len(ent),
            "K_extension_entries": len(kent),
            "pairs_with_nonzero_coboundary": len({(e["X"], e["Y"]) for e in ent}),
            "f_even_to_odd_parity_ok": all(par[Zi] == 1 - par[Z] for Z, d in fmap.items() for Zi in d),
        },
        "metadata": {"generated_by": "src/C_coboundary.py", "generation_date": date,
                     "math": "docs/math/C_coboundary_definition.md"},
    }
    if profile == E.REPRESENTATIVE:
        ent_s, kent_s = _entries(delta, kterms)
        fmap_s, lam_s = f_map_json(f_g, lam)
        doc["symbolic"] = {
            "description": "same data with gb kept symbolic (linear in gb_*)",
            "f_map": fmap_s, "f_K_component": lam_s,
            "coboundary_entries": ent_s, "K_extension_entries": kent_s,
        }
    return doc


def coboundary_path(n, profile=E.REPRESENTATIVE):
    suffix = "" if profile == E.REPRESENTATIVE else f"_{profile}"
    return os.path.join(DATA_DIR, f"C_{n}_coboundary{suffix}.json")


def write_schema4(n, profile=E.REPRESENTATIVE):
    d = build_schema4(n, profile)
    with open(coboundary_path(n, profile), "w") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    return d


def load_coboundary(n, profile=E.REPRESENTATIVE):
    with open(coboundary_path(n, profile)) as f:
        return json.load(f)


def check_layer1_consistency(n):
    """f maps basis -> basis with flipped parity; delta f values lie in g (Z in basis)."""
    f_g, lam, delta, kterms = _compute(n)
    par = G.parity_map(n)
    B = set(G.basis(n))
    ok = True
    for Z, vec in f_g.items():
        for Zi in vec:
            ok &= Zi in B and par[Zi] == 1 - par[Z]
    for (X, Y), vec in delta.items():
        for Z in vec:
            ok &= Z in B and par[Z] == (par[X] + par[Y] + 1) % 2
    for Z, c in lam.items():
        ok &= (c == 0) or par[Z] == 1
    return ok


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        ok = check_layer1_consistency(n)
        for prof in E.PROFILES:
            d = write_schema4(n, prof)
            s = d["summary"]
            print(f"C({n+1}) n={n} profile={prof:12s}: {s['coboundary_entries']:4d} delta-f terms, "
                  f"{s['K_extension_entries']:3d} K-extension terms, layer1 consistency={ok} "
                  f"-> {os.path.relpath(coboundary_path(n, prof), G.ROOT)}")
