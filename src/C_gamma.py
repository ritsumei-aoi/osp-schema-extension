#!/usr/bin/env python3
"""
src/C_gamma.py

Compute Schema 2 (gamma / inhomogeneous deformation) for C(n+1) = osp(2|2n).
Outputs C_{n}_gamma.json for n = 1, 2, 3.

Sign convention (Option A, from C_inhomogeneous_definition.md):
    [b_j^s, a_1^sigma]_gamma = -gb_{sigma,j,s} * kappa

The 2-cocycle γ(X_a, X_b) is the coefficient of kappa in [X_a, X_b]_gamma,
expressed as a linear combination of generators with coefficients linear in gb.
"""

import json
import os
from fractions import Fraction
from datetime import date

# Import the core oscillator algebra from C_generators
import sys
sys.path.insert(0, os.path.dirname(__file__))
from C_generators import (
    build_generators, express, dim_even, dim_odd, dim_total,
    _is_fermionic, _sort_mono, _frac_str,
)


# ── gb parameter labels ───────────────────────────────────────────────────────

def _gb_label(fermion_idx: int, boson_idx: int) -> str:
    """
    Return the gb label for the deformation [b_j^s, a_1^sigma] = -gb * kappa.
    fermion_idx: 0 = a_1_p (sigma=+), 1 = a_1_m (sigma=-)
    boson_idx:   2k = b_k_p (s=+),   2k+1 = b_k_m (s=-)
    """
    sigma = "p" if fermion_idx == 0 else "m"
    k = boson_idx // 2
    s = "p" if boson_idx % 2 == 0 else "m"
    return f"gb_a1{sigma}_b{k}{s}"


def _gb_matrix_labels(n: int) -> list:
    """
    Return 2×2n gb label matrix as a list of two rows.
    Rows: [a_1_p, a_1_m];  Cols: [b_1_p, b_1_m, ..., b_n_p, b_n_m].
    """
    rows = []
    for fi in [0, 1]:
        row = [_gb_label(fi, 2 * k + s) for k in range(1, n + 1) for s in [0, 1]]
        rows.append(row)
    return rows


# ── Deformed normal-ordering ──────────────────────────────────────────────────
# Returns (regular_poly, kappa_parts) where:
#   regular_poly = {tuple: Fraction}          (undeformed part)
#   kappa_parts  = {gb_label: {tuple: Fraction}}  (first-order deformation)
#
# Second-order (and higher) gb terms are discarded because kappa^2 = 0.

def _sort_mono_def(mono: tuple):
    """Deformed normal-ordering of a monomial. See module docstring."""
    indices = list(mono)
    for i in range(len(indices) - 1):
        if indices[i] > indices[i + 1]:
            a, b = indices[i], indices[i + 1]
            pa = 1 if _is_fermionic(a) else 0
            pb = 1 if _is_fermionic(b) else 0
            swap_sign = Fraction((-1) ** (pa * pb))

            prefix = indices[:i]
            suffix = indices[i + 2:]

            # Standard (anti)commutator extra value
            std_extra = Fraction(0)
            if pa and pb:
                std_extra = Fraction(1)                      # {a_1_m, a_1_p} = 1
            elif (not pa) and (not pb):
                if a % 2 == 1 and b % 2 == 0 and a == b + 1:
                    std_extra = Fraction(1)                  # [b_k_m, b_k_p] = 1

            # Deformation extra: only for mixed (boson a, fermion b)
            # [b_j^s, a_1^sigma] = -gb * kappa  → extra = -gb
            gb_lbl = None
            if (not pa) and pb:
                gb_lbl = _gb_label(b, a)                     # b = fermion idx, a = boson idx

            # ── Recurse on the swapped main term ──
            m_reg, m_kap = _sort_mono_def(tuple(prefix + [b, a] + suffix))
            res_reg = {k: swap_sign * v for k, v in m_reg.items()}
            res_kap = {g: {k: swap_sign * v for k, v in p.items()}
                       for g, p in m_kap.items()}

            # ── Standard extra term (anticommutator / commutator = 1) ──
            if std_extra:
                e_reg, e_kap = _sort_mono_def(tuple(prefix + suffix))
                for k, v in e_reg.items():
                    res_reg[k] = res_reg.get(k, Fraction(0)) + std_extra * v
                for g, p in e_kap.items():
                    res_kap.setdefault(g, {})
                    for k, v in p.items():
                        res_kap[g][k] = res_kap[g].get(k, Fraction(0)) + std_extra * v

            # ── Deformation extra: contributes to kappa part only ──
            # [b_j^s, a_1^sigma]_gamma = -gb * kappa, so the "context" (prefix+suffix)
            # contributes -1 * sort_regular(prefix + suffix) to kappa_parts[gb_lbl].
            # (Second-order gb terms from further commutations in the context are
            #  discarded since kappa^2 = 0.)
            if gb_lbl is not None:
                ctx_reg = _sort_mono(tuple(prefix + suffix))  # undeformed sort only
                res_kap.setdefault(gb_lbl, {})
                for k, v in ctx_reg.items():
                    res_kap[gb_lbl][k] = res_kap[gb_lbl].get(k, Fraction(0)) + Fraction(-1) * v

            # Clean zeros
            res_reg = {k: v for k, v in res_reg.items() if v}
            res_kap = {g: {k: v for k, v in p.items() if v}
                       for g, p in res_kap.items()}
            res_kap = {g: p for g, p in res_kap.items() if p}
            return res_reg, res_kap

    # Already in PBW order; check fermionic self-product
    for i in range(len(indices) - 1):
        if indices[i] == indices[i + 1] and _is_fermionic(indices[i]):
            return {}, {}
    return {mono: Fraction(1)}, {}


# ── Deformed polynomial multiplication ───────────────────────────────────────

def _mul_def(p1_reg, p1_kap, p2_reg, p2_kap):
    """
    Multiply two deformed polynomials (reg, kap).
    kap × kap terms are O(kappa^2) and are discarded.
    """
    res_reg = {}
    res_kap = {}

    for m1, c1 in p1_reg.items():
        for m2, c2 in p2_reg.items():
            # regular × regular → regular
            sub_reg, sub_kap = _sort_mono_def(m1 + m2)
            for k, v in sub_reg.items():
                res_reg[k] = res_reg.get(k, Fraction(0)) + c1 * c2 * v
            # regular × kap from monomial product → kap
            for g, p in sub_kap.items():
                res_kap.setdefault(g, {})
                for k, v in p.items():
                    res_kap[g][k] = res_kap[g].get(k, Fraction(0)) + c1 * c2 * v

    # p1_reg × p2_kap
    for m1, c1 in p1_reg.items():
        for g2, p2 in p2_kap.items():
            for m2, c2 in p2.items():
                for k, v in _sort_mono(m1 + m2).items():
                    res_kap.setdefault(g2, {})
                    res_kap[g2][k] = res_kap[g2].get(k, Fraction(0)) + c1 * c2 * v

    # p1_kap × p2_reg
    for g1, p1 in p1_kap.items():
        for m1, c1 in p1.items():
            for m2, c2 in p2_reg.items():
                for k, v in _sort_mono(m1 + m2).items():
                    res_kap.setdefault(g1, {})
                    res_kap[g1][k] = res_kap[g1].get(k, Fraction(0)) + c1 * c2 * v

    res_reg = {k: v for k, v in res_reg.items() if v}
    res_kap = {g: {k: v for k, v in p.items() if v}
               for g, p in res_kap.items()}
    res_kap = {g: p for g, p in res_kap.items() if p}
    return res_reg, res_kap


def bracket_def(X_reg, X_kap, px, Y_reg, Y_kap, py):
    """Graded bracket [X, Y}_gamma = XY - (-1)^{px*py} YX, first order in gb."""
    sign = Fraction((-1) ** (px * py))
    xy_reg, xy_kap = _mul_def(X_reg, X_kap, Y_reg, Y_kap)
    yx_reg, yx_kap = _mul_def(Y_reg, Y_kap, X_reg, X_kap)

    res_reg = {}
    for k, v in xy_reg.items():
        res_reg[k] = res_reg.get(k, Fraction(0)) + v
    for k, v in yx_reg.items():
        res_reg[k] = res_reg.get(k, Fraction(0)) - sign * v

    res_kap = {}
    for g, p in xy_kap.items():
        res_kap.setdefault(g, {})
        for k, v in p.items():
            res_kap[g][k] = res_kap[g].get(k, Fraction(0)) + v
    for g, p in yx_kap.items():
        res_kap.setdefault(g, {})
        for k, v in p.items():
            res_kap[g][k] = res_kap[g].get(k, Fraction(0)) - sign * v

    res_reg = {k: v for k, v in res_reg.items() if v}
    res_kap = {g: {k: v for k, v in p.items() if v}
               for g, p in res_kap.items()}
    res_kap = {g: p for g, p in res_kap.items() if p}
    return res_reg, res_kap


# ── Gamma computation ─────────────────────────────────────────────────────────

def compute_gamma(n: int):
    """
    Compute all non-zero gamma entries for C(n+1) = osp(2|2n).
    Returns list of dicts:
      {"X": lbl, "Y": lbl, "Z": lbl, "gb_terms": [{"gb": gb_lbl, "scalar": str}]}
    """
    gens, par, basis = build_generators(n)

    # Represent each generator as (reg, kap={}) — no gb in the generators themselves
    gen_def = {lbl: (gp, {}) for lbl, gp in gens.items()}

    entries = []
    for i, xi in enumerate(basis):
        for j, xj in enumerate(basis):
            if j < i:
                continue
            xi_reg, xi_kap = gen_def[xi]
            xj_reg, xj_kap = gen_def[xj]
            _, kap = bracket_def(xi_reg, xi_kap, par[xi],
                                 xj_reg, xj_kap, par[xj])
            if not kap:
                continue

            # Express each gb component in the Lie algebra basis
            for gb_lbl, poly in sorted(kap.items()):
                coeffs = express(poly, n, gens)
                if not coeffs:
                    continue
                for z, c in sorted(coeffs.items()):
                    # Forward pair (xi, xj)
                    entries.append({
                        "X": xi, "Y": xj, "Z": z,
                        "gb_terms": [{"gb": gb_lbl, "scalar": _frac_str(c)}],
                    })
                    # Reverse pair (xj, xi): gamma is antisymmetric like the bracket
                    # [Y, X}_gamma = -(-1)^{px*py} [X, Y}_gamma
                    # => gamma(Y, X; Z) = -(-1)^{px*py} * gamma(X, Y; Z)
                    if i != j:
                        sign = (-1) ** (par[xi] * par[xj])
                        rev_c = -sign * c
                        if rev_c:
                            entries.append({
                                "X": xj, "Y": xi, "Z": z,
                                "gb_terms": [{"gb": gb_lbl, "scalar": _frac_str(rev_c)}],
                            })

    # Merge entries with same (X, Y, Z): combine gb_terms lists
    merged = {}
    for e in entries:
        key = (e["X"], e["Y"], e["Z"])
        if key not in merged:
            merged[key] = {"X": e["X"], "Y": e["Y"], "Z": e["Z"], "gb_terms": []}
        merged[key]["gb_terms"].extend(e["gb_terms"])

    return list(merged.values())


# ── Schema 2 builder ──────────────────────────────────────────────────────────

def build_gamma_schema(n: int) -> dict:
    gens, par, basis = build_generators(n)
    boson_cols = [f"b_{k}_{'p' if s==0 else 'm'}" for k in range(1, n+1) for s in [0,1]]
    gb_matrix_rows = _gb_matrix_labels(n)
    gamma_entries = compute_gamma(n)

    return {
        "schema_version": "5.0",
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n+1})",
            "alternative_notation": {
                "osp": f"osp(2|{2*n})",
                "dimension_formula": "osp(2m|2n) with m=1",
            },
            "dimension": {
                "total": dim_total(n),
                "even": dim_even(n),
                "odd": dim_odd(n),
            },
        },
        "schema1_ref": f"C_{n}_structure.json",
        "inhomogeneous_deformation": {
            "deformation_relation": "[b_j^s, a_1^sigma]_gamma = -gb_{sigma,j,s} * kappa",
            "sign_convention": "Option A: negative sign as in C_inhomogeneous_definition.md",
            "kappa_parity": 1,
            "gb_count": 4 * n,
            "gb_matrix": {
                "shape": [2, 2 * n],
                "rows": ["a_1_p", "a_1_m"],
                "cols": boson_cols,
                "labels": gb_matrix_rows,
            },
            "gamma_entries": gamma_entries,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date.today().isoformat(),
            "n": n,
            "gamma_entry_count": len(gamma_entries),
            "references": [
                "Frappat, Sciarrino, Sorba, Dictionary on Lie Algebras and Superalgebras (2000)",
                "arXiv:hep-th/9607161",
            ],
        },
    }


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    for n in [1, 2, 3]:
        print(f"Computing gamma for C({n+1}) = osp(2|{2*n}), n={n}...")
        schema = build_gamma_schema(n)
        out = os.path.join(data_dir, f"C_{n}_gamma.json")
        with open(out, "w") as f:
            json.dump(schema, f, indent=2)
        count = schema["metadata"]["gamma_entry_count"]
        print(f"  gamma entries: {count}")
        print(f"  gb parameters: {schema['inhomogeneous_deformation']['gb_count']}")
        print(f"  written: {out}")


if __name__ == "__main__":
    main()
