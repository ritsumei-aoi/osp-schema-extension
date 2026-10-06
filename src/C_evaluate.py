"""Schema 3 generator: evaluated structure for C(n+1).  Issue I06.

Substitutes concrete numeric values into the ``4n`` gb parameters of Layer 2 and
emits ``data/C_{n}_evaluated_{profile}.json`` (plus ``data/C_{n}_evaluated.json``
for the primary profile).

Each gamma coefficient is linear in gb (proved in I05), so evaluation is exact
rational substitution.  The result is cross-checked two ways:

* substituting into the Layer 2 symbolic coefficients, and
* recomputing the deformed brackets from scratch with numeric gb,

which must agree entry-for-entry.

Usage::

    python src/C_evaluate.py          # n = 1, 2, 3, all profiles
"""

from __future__ import annotations

import json
import os
import sys
from typing import Callable, Dict, List, Tuple

import sympy as sp

try:
    from .osc_algebra import CAlgebra, gb_symbols
    from .C_gamma import build_gamma, gb_matrix_field, check_cocycle, gamma_table
    from .C_generators import algebra_field, GENERATION_DATE, REFERENCES
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from osc_algebra import CAlgebra, gb_symbols  # type: ignore
    from C_gamma import build_gamma, gb_matrix_field, check_cocycle, gamma_table  # type: ignore
    from C_generators import algebra_field, GENERATION_DATE, REFERENCES  # type: ignore

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")

Key = Tuple[str, int, str]

# --------------------------------------------------------------------------
# representative sign profiles for the 4n parameters gb[sigma, k, s]
# --------------------------------------------------------------------------
PROFILES: Dict[str, Tuple[str, Callable[[str, int, str], sp.Rational]]] = {
    "all_plus": (
        "All 4n parameters set to +1. The maximally symmetric deformation; "
        "the primary profile.",
        lambda sigma, k, s: sp.Integer(1),
    ),
    "fermionic_sign": (
        "gb = +1 for sigma = '+', -1 for sigma = '-'. Probes dependence on the "
        "fermionic (epsilon) sign only.",
        lambda sigma, k, s: sp.Integer(1 if sigma == "p" else -1),
    ),
    "bosonic_sign": (
        "gb = +1 for s = '+', -1 for s = '-'. Probes dependence on the bosonic "
        "(delta) sign only.",
        lambda sigma, k, s: sp.Integer(1 if s == "p" else -1),
    ),
    "creation_only": (
        "gb = 1 when s = '+', 0 when s = '-'. A degenerate (rank-deficient) "
        "profile: half the parameters vanish.",
        lambda sigma, k, s: sp.Integer(1 if s == "p" else 0),
    ),
    "single_mode": (
        "Only gb[+, 1, +] = 1; all other parameters 0. The sparsest non-zero "
        "deformation.",
        lambda sigma, k, s: sp.Integer(1 if (sigma, k, s) == ("p", 1, "p") else 0),
    ),
    "generic_rational": (
        "Pairwise distinct rationals with no accidental relations; the generic "
        "point of the 4n-dimensional parameter space.",
        lambda sigma, k, s: sp.Rational(
            (1 if sigma == "p" else -1) * (2 * k + (1 if s == "p" else 0)) + 1, 2 * k + 3
        ),
    ),
    "zero": (
        "All parameters 0: the undeformed control case. gamma must vanish identically.",
        lambda sigma, k, s: sp.Integer(0),
    ),
}

PRIMARY = "all_plus"


def gb_values(n: int, profile: str) -> Dict[Key, sp.Rational]:
    _desc, fn = PROFILES[profile]
    return {
        (sigma, k, s): fn(sigma, k, s)
        for sigma in ("p", "m")
        for k in range(1, n + 1)
        for s in ("p", "m")
    }


# --------------------------------------------------------------------------
def build_schema3(n: int, profile: str) -> dict:
    sym_gb, labels = gb_symbols(n)
    values = gb_values(n, profile)
    subs = {sym_gb[key]: values[key] for key in sym_gb}

    # (a) evaluate the Layer 2 symbolic table
    _alg_sym, _plain, sym_entries, _cons, _labels = build_gamma(n)
    evaluated: Dict[Tuple[str, str, str], sp.Expr] = {}
    for e in sym_entries:
        c = sp.expand(sp.sympify(e["coeff"]).subs(subs))
        if c != 0:
            evaluated[(e["X"], e["Y"], e["Z"])] = c

    # (b) recompute from scratch with numeric gb
    alg = CAlgebra(n, values)
    direct: Dict[Tuple[str, str, str], sp.Expr] = {}
    for i, x in enumerate(alg.pbw_order):
        for y in alg.pbw_order[i:]:
            _free, kap = alg.split_kappa(alg.bracket_labels(x, y))
            if not kap:
                continue
            for z, c in alg.decompose_kappa(kap).items():
                if sp.expand(c) != 0:
                    direct[(x, y, z)] = sp.expand(c)

    agree = evaluated == direct

    # (c) cocycle condition at this numeric point
    gam = gamma_table(alg, [
        {"X": x, "Y": y, "Z": z, "coeff": str(c)} for (x, y, z), c in direct.items()
    ])
    c_count, c_errs = check_cocycle(alg, gam)

    order = alg.pbw_order
    entries = [
        {"X": x, "Y": y, "Z": z, "coeff": str(direct[(x, y, z)]),
         "parity_X": alg.parity[x], "parity_Y": alg.parity[y]}
        for x in order for y in order for z in order + ["K"]
        if (x, y, z) in direct
    ]

    desc, _fn = PROFILES[profile]
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": algebra_field(n),
        "profile": {
            "name": profile,
            "description": desc,
            "is_primary": profile == PRIMARY,
        },
        "basis": {
            "even": alg.even,
            "odd": alg.odd,
            "pbw_order": order,
            "source": f"data/C_{n}_structure.json",
        },
        "parity": {lab: alg.parity[lab] for lab in order},
        "gb_matrix": gb_matrix_field(n, labels),
        "gb_values": {
            labels[key]: str(values[key]) for key in sorted(labels, key=lambda t: labels[t])
        },
        "evaluated_deformation": {
            "description": (
                "gamma with numeric gb: [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)"
            ),
            "convention": (
                "entries stored for pbw_index(X) <= pbw_index(Y); "
                "gamma(Y,X) = -(-1)^{p(X)p(Y)} gamma(X,Y)"
            ),
            "source_layer2": f"data/C_{n}_gamma.json",
            "entries": entries,
            "nonzero_entries_total": len(entries),
            "nonzero_pairs_total": len({(e["X"], e["Y"]) for e in entries}),
        },
        "consistency": {
            "substitution_matches_direct_recomputation": agree,
            "cocycle_condition_holds": not c_errs,
            "cocycle_triples_checked": c_count,
            "cocycle_failures": c_errs,
        },
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": GENERATION_DATE,
            "references": REFERENCES + ["docs/math/C_inhomogeneous_definition.md"],
        },
    }


def write_schema3(n: int, profile: str) -> str:
    os.makedirs(DATA, exist_ok=True)
    doc = build_schema3(n, profile)
    path = os.path.join(DATA, f"C_{n}_evaluated_{profile}.json")
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")
    if profile == PRIMARY:
        alias = os.path.join(DATA, f"C_{n}_evaluated.json")
        with open(alias, "w") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
    return path


def main(argv: List[str]) -> int:
    ns = [int(a) for a in argv[1:]] or [1, 2, 3]
    ok = True
    for n in ns:
        for profile in PROFILES:
            path = write_schema3(n, profile)
            with open(path) as fh:
                doc = json.load(fh)
            c = doc["consistency"]
            d = doc["evaluated_deformation"]
            good = c["substitution_matches_direct_recomputation"] and c["cocycle_condition_holds"]
            ok &= good
            print(f"n={n:<2} {profile:<17} entries={d['nonzero_entries_total']:<5} "
                  f"pairs={d['nonzero_pairs_total']:<4} "
                  f"subst==direct={c['substitution_matches_direct_recomputation']} "
                  f"cocycle={c['cocycle_condition_holds']} "
                  f"-> {os.path.relpath(path, REPO)}")
    print("SUMMARY:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
