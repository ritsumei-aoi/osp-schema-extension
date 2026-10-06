"""
C(n+1) Schema-2: inhomogeneous deformation (gamma structure).  Issue I05.

The deformation is carried by the odd central element kappa (kappa^2 = 0) through the deformed
boson-fermion relation (docs/math/C_inhomogeneous_definition.md):

    [b_j^s, a_1^sigma] = - gb_{sigma, j, s} * kappa ,   sigma,s in {+,-},  j=1..n   (4n parameters).

The deformed graded bracket is  [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y),  so gamma(X,Y) is the
coefficient of kappa in the deformed graded commutator, re-expressed on the C(n+1) basis. Each
gamma coefficient is linear in the gb parameters.

Run:  python3 src/C_gamma.py        # writes data/C_{1,2,3}_gamma.json
"""

from __future__ import annotations
import json
import os
import sys
from datetime import date
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osc_algebra as oa
import C_generators as cg

DATA_DIR = cg.DATA_DIR

# --- gb parameters --------------------------------------------------------
# name:  gb_{F}_{j}_{B}  with F in {p,m} (fermion a_1 sign), B in {p,m} (boson sign), j=1..n


def gb_name(sigma, j, s):
    F = "p" if sigma == +1 else "m"
    B = "p" if s == +1 else "m"
    return f"gb_{F}_{j}_{B}"


def gb_symbol(sigma, j, s):
    return sp.Symbol(gb_name(sigma, j, s))


def gb_list(n):
    """The 4n gb parameter names in a stable order."""
    names = []
    for sigma in (+1, -1):
        for j in range(1, n + 1):
            for s in (+1, -1):
                names.append(gb_name(sigma, j, s))
    return names


def _gb_hook():
    return lambda sigma, j, s: gb_symbol(sigma, j, s)


# --- gamma computation ----------------------------------------------------

def deformed_bracket(X, Y, R, P):
    """Full deformed graded commutator (kappa_flag 0 and 1 parts)."""
    return oa.graded_commutator(R[X], P[X], R[Y], P[Y], gb=_gb_hook())


def split_kappa(poly):
    """Return (base_part, gamma_part_stripped): base = kappa_flag 0 terms,
    gamma = kappa_flag 1 terms with the kappa flag removed (an osc poly)."""
    base, gam = oa.poly_zero(), oa.poly_zero()
    for (kf, word), c in poly.items():
        if kf == 0:
            oa.poly_add_term(base, 0, word, c)
        else:
            oa.poly_add_term(gam, 0, word, c)
    return base, gam


def gamma_records(n):
    R = cg.realizations(n)
    P = cg.parity_map(n)
    order = cg.pbw_order(n)
    pos = {lab: i for i, lab in enumerate(order)}
    records = []
    for a in range(len(order)):
        for b in range(a, len(order)):
            X, Y = order[a], order[b]
            defbr = deformed_bracket(X, Y, R, P)
            _, gam = split_kappa(defbr)
            if not gam:
                continue
            comps = cg.decompose(gam, n)  # gb-linear coefficients onto basis (+K)
            for Z, coeff in sorted(comps.items(), key=lambda kv: pos.get(kv[0], 10 ** 9)):
                records.append({
                    "X": X, "Y": Y, "Z": Z,
                    "coeff": str(sp.expand(coeff)),
                    "carrier": "kappa",
                })
    return records


def consistency_with_schema1(n):
    """Verify the kappa^0 part of every deformed bracket equals the Schema-1 structure constant."""
    R = cg.realizations(n)
    P = cg.parity_map(n)
    order = cg.pbw_order(n)
    mismatches = []
    for a in range(len(order)):
        for b in range(a, len(order)):
            X, Y = order[a], order[b]
            defbr = deformed_bracket(X, Y, R, P)
            base, _ = split_kappa(defbr)
            undef = oa.graded_commutator(R[X], P[X], R[Y], P[Y])  # no gb
            base_c = cg.decompose(base, n)
            undef_c = cg.decompose(undef, n)
            keys = set(base_c) | set(undef_c)
            for k in keys:
                if sp.simplify(base_c.get(k, 0) - undef_c.get(k, 0)) != 0:
                    mismatches.append((X, Y, k))
    return mismatches


def build_schema2(n):
    recs = gamma_records(n)
    gbs = gb_list(n)
    mism = consistency_with_schema1(n)
    return {
        "schema_version": "5.0",
        "layer": 2,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})"},
        "inhomogeneous_deformation": {
            "type": "inhomogeneous",
            "carrier": {"symbol": "kappa", "parity": 1, "nilpotency": "kappa^2 = 0"},
            "relation": "[b_j^s, a_1^sigma] = - gb_{sigma,j,s} * kappa",
            "bracket": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
        },
        "gb_matrix": {
            "shape": [2, 2 * n],
            "rows": "fermion sign sigma in {+,-}",
            "cols": "(boson index j = 1..n) x (boson sign s in {+,-})",
            "count": 4 * n,
            "parameters": gbs,
            "parity": 1,
        },
        "gamma": recs,
        "consistency": {
            "kappa0_equals_schema1": (len(mism) == 0),
            "mismatches": mism,
            "note": "The kappa^0 part of every deformed bracket reproduces the Schema-1 structure "
                    "constants; gamma is purely the kappa^1 part.",
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date.today().isoformat(),
            "references": ["docs/math/C_inhomogeneous_definition.md"],
        },
    }


def generate_all():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in (1, 2, 3):
        data = build_schema2(n)
        path = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        nz = len(data["gamma"])
        ok = data["consistency"]["kappa0_equals_schema1"]
        print(f"wrote {path}  (#gamma_records={nz}, consistency_with_schema1={ok})")


if __name__ == "__main__":
    generate_all()
