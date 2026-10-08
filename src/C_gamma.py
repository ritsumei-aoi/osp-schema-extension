"""
Schema 2 generator (Issue I05): inhomogeneous deformation gamma for C(n+1).

Deformed oscillator relation (docs/math/C_inhomogeneous_definition.md):
    [b_k^s, a_1^sigma] = -gb_{sigma,k,s} * kappa,   kappa odd central, kappa^2 = 0.

For basis elements X, Y the deformed bracket computed in U(A) splits as
    [X, Y}_gamma = [X, Y}_0 + kappa * gamma(X, Y),
and gamma(X, Y) is decomposed in the basis of g together with the even central
element K (= 1).  The coefficients are linear forms in the 4n symbols gb_*.

Usage: python3 src/C_gamma.py [n ...]   (default 1 2 3)
"""
from __future__ import annotations

import datetime
import json
import os
import sys

import sympy
from sympy import Poly, expand

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from osc_algebra import OscAlgebra, gb_symbols, gb_label  # noqa: E402
import C_generators as G  # noqa: E402

DATA_DIR = G.DATA_DIR


def gb_matrix_labels(n):
    cols = [f"b_{k}_{s}" for k in range(1, n + 1) for s in "pm"]
    rows = ["a_1_p", "a_1_m"]
    labels = [[gb_label(sig, k, s) for k in range(1, n + 1) for s in "pm"] for sig in "pm"]
    return rows, cols, labels


def linear_form(expr, symbols):
    """Decompose a linear expression in the gb symbols into {label: rational str}."""
    expr = expand(expr)
    if expr == 0:
        return {}
    p = Poly(expr, *symbols)
    if p.total_degree() > 1 or p.coeff_monomial(1) != 0:
        raise ValueError(f"gamma coefficient not homogeneous linear in gb: {expr}")
    form = {}
    for s in symbols:
        c = p.coeff_monomial(s)
        if c != 0:
            form[str(s)] = G.coeff_str(c)
    return form


def compute_gamma(n):
    """Return (dec, entries, zeroth_order_table).

    entries: list of {X, Y, Z, coeff(str), linear_form} with Z in basis or 'K'.
    zeroth_order_table: {(X,Y): {Z: coeff}} of the kappa-free part, for the Schema 1 check.
    """
    syms = gb_symbols(n)
    alg = OscAlgebra(n, gb=syms)
    dec = G.Decomposer(n, alg)
    R = dec.R
    B = G.basis(n)
    symlist = list(syms.values())
    entries = []
    zeroth = {}
    gamma = {}
    for X in B:
        for Y in B:
            br = alg.bracket(R[X], R[Y])
            p0, p1 = alg.split_kappa(br)
            d0 = dec.decompose(p0) if p0 else {}
            if "K" in d0:
                raise ValueError("zeroth order has K component")
            zeroth[(X, Y)] = {Z: G.coeff_str(c) for Z, c in d0.items()}
            if not p1:
                continue
            d1 = dec.decompose(p1)
            gamma[(X, Y)] = d1
            for Z, c in d1.items():
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": str(c),
                                "linear_form": linear_form(c, symlist)})
    return dec, entries, zeroth, gamma


def check_consistency(n, zeroth, gamma, par):
    """Zeroth order equals Schema 1; gamma is graded antisymmetric."""
    s1 = G.load_structure(n)
    table1 = {}
    for e in s1["structure_constants"]:
        table1.setdefault((e["X"], e["Y"]), {})[e["Z"]] = e["coeff"]
    z = {k: v for k, v in zeroth.items() if v}
    ok_schema1 = (z == table1)
    ok_antisym = True
    for (X, Y), v in gamma.items():
        sign = -1 if (par[X] and par[Y]) else 1
        w = gamma.get((Y, X), {})
        if {Z: expand(-sign * c) for Z, c in v.items()} != {Z: expand(c) for Z, c in w.items()}:
            ok_antisym = False
    return ok_schema1, ok_antisym


def build_schema2(n, date=None):
    date = date or datetime.date.today().isoformat()
    dec, entries, zeroth, gamma = compute_gamma(n)
    par = G.parity_map(n)
    ok1, ok2 = check_consistency(n, zeroth, gamma, par)
    if not (ok1 and ok2):
        raise RuntimeError(f"consistency failed: schema1={ok1}, antisym={ok2}")
    rows, cols, labels = gb_matrix_labels(n)
    n_K = sum(1 for e in entries if e["Z"] == "K")
    return {
        "schema_version": "5.0",
        "layer": 2,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
                    "dimension": G.dimensions(n)},
        "schema1_file": f"C_{n}_structure.json",
        "deformation": {
            "type": "inhomogeneous",
            "oscillator_relation": "[b_k^s, a_1^sigma] = -gb_{sigma,k,s} * kappa   (sigma, s in {+,-})",
            "bracket": "[X, Y}_gamma = [X, Y}_0 + kappa * gamma(X, Y)",
            "kappa": {"parity": 1, "relation": "kappa^2 = 0", "central": True},
            "gb_parity": 1,
            "gb_treatment": ("gb parameters are treated as formal commuting scalars in all "
                             "computations; they always appear as the product gb*kappa, with kappa "
                             "written leftmost. See I05 Response for the parity discussion."),
            "gamma_target": "g + C K  (K = even central element, scalar 1)",
            "gamma_parity_rule": "|gamma(X,Y)| = |X| + |Y| + 1 mod 2 (kappa carries parity 1)",
        },
        "gb_matrix": {
            "shape": [2, 2 * n],
            "rows": rows,
            "columns": cols,
            "labels": labels,
            "count": 4 * n,
            "index_convention": "gb_a1{sigma}_b{k}{s} = gb_{sigma,k,s}, rows: a_1_p (sigma=+), a_1_m (sigma=-)",
        },
        "inhomogeneous_deformation": {
            "description": "gamma(X,Y) = sum_Z coeff * Z, coeff linear in gb; all ordered pairs with nonzero gamma",
            "coefficient_format": {"coeff": "sympy expression string",
                                   "linear_form": "{gb_label: rational string}"},
            "entries": entries,
        },
        "consistency": {
            "zeroth_order_equals_schema1": ok1,
            "gamma_graded_antisymmetric": ok2,
            "entries_total": len(entries),
            "entries_with_Z_K": n_K,
            "pairs_with_nonzero_gamma": len(gamma),
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date,
            "notation": "handover/notation.md",
            "math": "docs/math/C_inhomogeneous_definition.md",
        },
    }


def gamma_path(n):
    return os.path.join(DATA_DIR, f"C_{n}_gamma.json")


def write_schema2(n):
    d = build_schema2(n)
    with open(gamma_path(n), "w") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    return d


def load_gamma(n):
    with open(gamma_path(n)) as f:
        return json.load(f)


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        d = write_schema2(n)
        c = d["consistency"]
        print(f"C({n+1}) n={n}: {c['entries_total']} gamma terms over "
              f"{c['pairs_with_nonzero_gamma']} pairs ({c['entries_with_Z_K']} with Z=K); "
              f"schema1 match={c['zeroth_order_equals_schema1']}, "
              f"antisym={c['gamma_graded_antisymmetric']} -> {gamma_path(n)}")
