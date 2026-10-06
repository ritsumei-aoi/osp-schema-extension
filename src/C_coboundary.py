#!/usr/bin/env python3
"""
src/C_coboundary.py

Generate Schema 4 (Coboundary Structure) for C(n+1) = osp(2|2n).
Outputs C_{n}_coboundary.json for n = 1, 2, 3.

Coboundary operator (from C_coboundary_definition.md):
    (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)]
                    - (-1)^{(p(X)+1)*p(Y)} [Y, f(X)]
                    - f([X, Y])

where f: g -> g is the odd linear map parametrized by phi coefficients:
    f(E_j) = sum_i  phi_eo_{O_i}_{E_j} * O_i   (even -> odd)
    f(O_j) = sum_i  phi_oe_{E_i}_{O_j} * E_i   (odd -> even)

phi label format:
    phi_eo_{target_odd}_{source_even}
    phi_oe_{target_even}_{source_odd}

Output: (delta f)(X, Y; Z) stored as phi-polynomial entries analogous to
        Schema 2's gb-term format.
"""

import json
import os
from fractions import Fraction
from datetime import date


DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def _frac_str(f: Fraction) -> str:
    return str(f) if f.denominator != 1 else str(f.numerator)


def load_s1(n: int) -> dict:
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as fh:
        return json.load(fh)


# ── Symbolic phi-polynomial helpers ──────────────────────────────────────────
# A phi-polynomial is {phi_label: {gen_label: Fraction}}, representing:
#   sum_{phi} phi * (sum_Z coeff_Z * Z)

def _scale(phi_poly: dict, scalar: Fraction) -> dict:
    return {p: {W: scalar * v for W, v in gp.items()}
            for p, gp in phi_poly.items()}


def _add(*polys) -> dict:
    res = {}
    for pp in polys:
        for p, gp in pp.items():
            res.setdefault(p, {})
            for W, v in gp.items():
                res[p][W] = res[p].get(W, Fraction(0)) + v
    return {p: {W: v for W, v in gp.items() if v}
            for p, gp in res.items() if any(v for v in gp.values())}


def _f_sym(gen: str, par: dict, even_gens: list, odd_gens: list) -> dict:
    """Symbolic f(gen) as phi-polynomial."""
    if par[gen] == 0:                            # even -> odd
        return {f"phi_eo_{O}_{gen}": {O: Fraction(1)} for O in odd_gens}
    else:                                        # odd -> even
        return {f"phi_oe_{E}_{gen}": {E: Fraction(1)} for E in even_gens}


def _bracket_phi(X: str, phi_poly: dict, sc: dict) -> dict:
    """[X, phi_poly} = sum_{phi,Z} phi * coeff_Z * [X, Z}  (from SC table)."""
    res = {}
    for phi_lbl, gp in phi_poly.items():
        for Z, c in gp.items():
            for W, sc_c in sc.get((X, Z), {}).items():
                res.setdefault(phi_lbl, {})
                res[phi_lbl][W] = res[phi_lbl].get(W, Fraction(0)) + c * sc_c
    return {p: {W: v for W, v in gp.items() if v}
            for p, gp in res.items() if any(v for v in gp.values())}


def _f_of_poly(gen_coeffs: dict, par: dict, even_gens: list, odd_gens: list) -> dict:
    """f(sum_Z c_Z * Z) as phi-polynomial."""
    res = {}
    for Z, c in gen_coeffs.items():
        for phi_lbl, gp in _f_sym(Z, par, even_gens, odd_gens).items():
            res.setdefault(phi_lbl, {})
            for W, v in gp.items():
                res[phi_lbl][W] = res[phi_lbl].get(W, Fraction(0)) + c * v
    return {p: {W: v for W, v in gp.items() if v}
            for p, gp in res.items() if any(v for v in gp.values())}


# ── Coboundary computation ────────────────────────────────────────────────────

def compute_coboundary(n: int, s1: dict) -> list:
    """
    Compute (delta f)(X, Y) symbolically for all (X, Y) in basis × basis.
    Returns list of entries:
      {"X": x, "Y": y, "Z": z, "phi_terms": [{"phi": lbl, "scalar": str}]}
    Only non-zero (X, Y, Z) entries are stored.
    """
    even_gens = s1["basis"]["even"]
    odd_gens  = s1["basis"]["odd"]
    basis = even_gens + odd_gens
    par   = {k: int(v) for k, v in s1["parity"].items()}

    # Build SC lookup: (X, Y) -> {Z: Fraction}
    sc: dict = {}
    for e in s1["structure_constants"]:
        key = (e["X"], e["Y"])
        sc.setdefault(key, {})
        sc[key][e["Z"]] = sc[key].get(e["Z"], Fraction(0)) + Fraction(e["coeff"])

    entries = []

    for X in basis:
        fX = _f_sym(X, par, even_gens, odd_gens)
        px = par[X]
        for Y in basis:
            fY = _f_sym(Y, par, even_gens, odd_gens)
            py = par[Y]

            s1_ = Fraction((-1) ** px)
            s2_ = Fraction((-1) ** ((px + 1) * py))

            # Three terms of the coboundary
            t1  = _scale(_bracket_phi(X, fY, sc), s1_)          # (-1)^px [X,f(Y)]
            t2  = _scale(_bracket_phi(Y, fX, sc), -s2_)         # -(-1)^{(px+1)py} [Y,f(X)]
            t3  = _scale(_f_of_poly(sc.get((X, Y), {}),
                                    par, even_gens, odd_gens),
                         Fraction(-1))                            # -f([X,Y])

            total = _add(t1, t2, t3)
            if not total:
                continue

            # Collect by Z: accumulate phi contributions for each output generator
            by_Z: dict = {}
            for phi_lbl, gp in total.items():
                for W, c in gp.items():
                    if c:
                        if W not in by_Z:
                            by_Z[W] = {}
                        by_Z[W][phi_lbl] = by_Z[W].get(phi_lbl, Fraction(0)) + c

            for W in sorted(by_Z):
                phi_terms = [
                    {"phi": phi_lbl, "scalar": _frac_str(c)}
                    for phi_lbl, c in sorted(by_Z[W].items())
                    if c
                ]
                if phi_terms:
                    entries.append({"X": X, "Y": Y, "Z": W, "phi_terms": phi_terms})

    return entries


# ── Schema 4 builder ──────────────────────────────────────────────────────────

def build_coboundary_schema(n: int) -> dict:
    s1 = load_s1(n)
    even_gens = s1["basis"]["even"]
    odd_gens  = s1["basis"]["odd"]
    par       = {k: int(v) for k, v in s1["parity"].items()}

    # phi label catalogue
    phi_eo = [
        {"phi": f"phi_eo_{O}_{E}", "from": E, "to": O}
        for E in even_gens for O in odd_gens
    ]
    phi_oe = [
        {"phi": f"phi_oe_{E}_{O}", "from": O, "to": E}
        for O in odd_gens for E in even_gens
    ]

    coboundary_entries = compute_coboundary(n, s1)

    return {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": s1["algebra"],
        "schema1_ref": f"C_{n}_structure.json",
        "f_parametrization": {
            "description": (
                "Odd linear map f: g -> g. "
                "f(E_j) = sum_i phi_eo_{O_i}_{E_j} * O_i; "
                "f(O_j) = sum_i phi_oe_{E_i}_{O_j} * E_i."
            ),
            "phi_count": len(phi_eo) + len(phi_oe),
            "phi_eo_count": len(phi_eo),
            "phi_oe_count": len(phi_oe),
            "phi_eo_labels": phi_eo,
            "phi_oe_labels": phi_oe,
        },
        "coboundary_formula": (
            "(delta f)(X,Y) = (-1)^{p(X)} [X,f(Y)] "
            "- (-1)^{(p(X)+1)*p(Y)} [Y,f(X)] - f([X,Y])"
        ),
        "coboundary_entries": coboundary_entries,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": date.today().isoformat(),
            "n": n,
            "basis_pairs_total": (len(even_gens) + len(odd_gens)) ** 2,
            "coboundary_entry_count": len(coboundary_entries),
            "phi_eo_count": len(phi_eo),
            "phi_oe_count": len(phi_oe),
            "references": s1["metadata"].get("references", []),
        },
    }


def main():
    for n in [1, 2, 3]:
        print(f"Computing coboundary for C({n+1}) = osp(2|{2*n}), n={n}...")
        schema = build_coboundary_schema(n)
        out = os.path.join(DATA, f"C_{n}_coboundary.json")
        with open(out, "w") as fh:
            json.dump(schema, fh, indent=2)
        m = schema["metadata"]
        print(f"  basis pairs total         : {m['basis_pairs_total']}")
        print(f"  non-zero coboundary entries: {m['coboundary_entry_count']}")
        print(f"  phi_eo params             : {m['phi_eo_count']}")
        print(f"  phi_oe params             : {m['phi_oe_count']}")
        print(f"  written: {out}")


if __name__ == "__main__":
    main()
