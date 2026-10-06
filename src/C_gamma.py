"""Schema 2 (gamma structure) for C(n+1): inhomogeneous deformation, symbolic in gb.

Deformation (docs/math/C_inhomogeneous_definition.md):  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa.
In U(A) every graded commutator of two generators splits as
    [X, Y] = [X, Y]_0 + kappa * gamma(X, Y),   gamma(X, Y) in g + C K,
and gamma is linear in gb (kappa^2 = 0). We compute gamma for each unit gb vector exactly.

Usage:  python3 src/C_gamma.py        -> data/C_{n}_gamma.json, n = 1, 2, 3
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import OscillatorAlgebra, gb_labels  # noqa: E402
from C_generators import (Decomposer, global_order, parity_map, realization_terms,  # noqa: E402
                          write_json, frac_str, DATA_DIR)


def lin_expr(coeff):
    """{'gb_p_1_m': Fraction(2), ...} -> '2*gb_p_1_m - gb_m_1_p'."""
    parts = []
    for k, v in coeff.items():
        mag = abs(v)
        term = k if mag == 1 else f"{frac_str(mag)}*{k}"
        parts.append(("- " if v < 0 else "+ ") + term)
    s = " ".join(parts)
    return s[2:] if s.startswith("+ ") else "-" + s[2:]


def deformed_bracket_parts(n, gb):
    """{(X, Y): (bracket0 coords, gamma coords)} for numeric gb dict; coords include 'K'."""
    alg = OscillatorAlgebra(n, gb=gb)
    terms = realization_terms(n)
    reals = {lab: alg.normalize({w: c for w, c in t}) for lab, (t, _, _) in terms.items()}
    dec = Decomposer(n)
    basis = global_order(n)
    out = {}
    for X in basis:
        for Y in basis:
            e0, e1 = alg.split_kappa(alg.bracket(reals[X], reals[Y]))
            out[(X, Y)] = (dec.decompose(e0), dec.decompose(e1))
    return out


def gamma_symbolic(n):
    """{(X, Y): {Z: {gb_label: Fraction}}} (Z may be 'K'), plus the gb-independent bracket0."""
    gamma, bracket0 = {}, None
    for g in gb_labels(n):
        parts = deformed_bracket_parts(n, {g: 1})
        b0 = {k: v[0] for k, v in parts.items()}
        if bracket0 is None:
            bracket0 = b0
        elif b0 != bracket0:
            raise RuntimeError("kappa-free part depends on gb")
        for pair, (_, gam) in parts.items():
            for Z, c in gam.items():
                gamma.setdefault(pair, {}).setdefault(Z, {})[g] = c
    return gamma, bracket0


def evaluate_gamma(gamma, gb):
    """Substitute numeric gb into the symbolic gamma: {(X,Y): {Z: Fraction}}."""
    out = {}
    for pair, zs in gamma.items():
        for Z, lin in zs.items():
            v = sum((Fraction(gb.get(g, 0)) * c for g, c in lin.items()), Fraction(0))
            if v:
                out.setdefault(pair, {})[Z] = v
    return out


def gb_matrix(n):
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in ("p", "m")]
    return {
        "rows": ["a_1_p", "a_1_m"],
        "columns": cols,
        "symbols": [[f"gb_{sig}_{c[2:]}" for c in cols] for sig in ("p", "m")],
        "count": 4 * n,
        "shape": [2, 2 * n],
        "defining_relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} κ   (σ = row, (j,s) = column)",
        "parameter_parity": 1,
        "parity_note": ("Formal parity label from C_inhomogeneous_definition.md (gb multiplies the odd "
                        "κ in an odd-even mixed bracket). For computation gb are commuting scalars: "
                        "the odd degree is carried by κ alone, otherwise [b,a] (odd) = -gb κ would be even."),
    }


def build_schema2(n, date=None):
    date = date or datetime.date.today().isoformat()
    basis = global_order(n)
    idx = {x: i for i, x in enumerate(basis + ["K"])}
    par = parity_map(n)
    gamma, _ = gamma_symbolic(n)
    entries = []
    for (X, Y) in sorted(gamma, key=lambda p: (idx[p[0]], idx[p[1]])):
        for Z in sorted(gamma[(X, Y)], key=idx.get):
            lin = gamma[(X, Y)][Z]
            entries.append({"X": X, "Y": Y, "Z": Z,
                            "coeff": {g: frac_str(c) for g, c in lin.items()},
                            "expr": lin_expr(lin)})
    n_central = sum(1 for e in entries if e["Z"] == "K")
    pairs = {(e["X"], e["Y"]) for e in entries}
    return {
        "schema_version": "5.0",
        "layer": 2,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})", "osp": f"osp(2|{2*n})"},
        "structure_ref": f"C_{n}_structure.json",
        "basis_order": basis,
        "parity": {x: par[x] for x in basis},
        "inhomogeneous_deformation": {
            "description": ("Inhomogeneous deformation of C(n+1) induced by the mixed pre-oscillator form "
                            "(b_j^s | a_1^σ) = -gb_{σ,j,s}; brackets computed in U(A) and split by κ."),
            "bracket_convention": "[X,Y]_γ = [X,Y]_0 + κ γ(X,Y), κ written on the left; [X,Y] graded commutator",
            "gb_matrix": gb_matrix(n),
            "gamma_target_space": "g ⊕ C K; an entry with Z = 'K' is the central part (coefficient of κK = κ)",
            "gamma_parity_rule": "p(Z) = p(X) + p(Y) + 1 mod 2 (κ is odd); K counts as even",
            "symmetry": "γ(Y,X) = -(-1)^{p(X)p(Y)} γ(X,Y); all ordered pairs are stored",
            "linearity": "γ is exactly linear in gb (κ^2 = 0); coeff maps gb symbol -> rational",
            "gamma": entries,
            "statistics": {"entries": len(entries), "central_entries": n_central,
                           "nonzero_pairs": len(pairs), "parameters": 4 * n},
        },
        "metadata": {"generated_by": "src/C_gamma.py", "generation_date": date,
                     "conventions": "handover/notation.md",
                     "math_reference": "docs/math/C_inhomogeneous_definition.md"},
    }


def main(ns=(1, 2, 3)):
    for n in ns:
        s = build_schema2(n)
        p = write_json(s, f"C_{n}_gamma.json")
        st = s["inhomogeneous_deformation"]["statistics"]
        print(f"n={n}: {st} -> {os.path.relpath(p)}")


if __name__ == "__main__":
    main()
