"""Schema 2 (gamma structure) generator for C(n+1) (I05).

Computes the inhomogeneous-deformation 2-cocycle gamma symbolically in the
4n gb parameters:  [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y), where the
deformed oscillator relation is  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa.

gamma(X,Y) is obtained as the first-order kappa part of the deformed bracket
computed in the oscillator representation, decomposed on the Schema 1 basis
(plus 'K' for scalar components).

Usage: python3 src/C_gamma.py   # writes data/C_{n}_gamma.json for n=1,2,3
"""

import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from oscillator_algebra import Element, super_bracket
from C_generators import _basis_cache, decompose, DATA_DIR


def gb_labels(n):
    return [
        f"gb_{sigma}_{j}_{s}"
        for sigma in ("p", "m")
        for j in range(1, n + 1)
        for s in ("p", "m")
    ]


def compute_gamma(n):
    """Return list of {X, Y, terms: [{gb, Z, coeff}]} for all nonzero gamma(X,Y)."""
    labels, parity, elems = _basis_cache(n)
    entries = []
    for x in labels:
        for y in labels:
            br = super_bracket(elems[x], elems[y], parity[x], parity[y], deform=True)
            # classical consistency: even part must match undeformed bracket
            if not br.kterms:
                continue
            # group kappa terms by gb symbol and decompose each on the basis
            by_gb = {}
            for (gb, w), c in br.kterms.items():
                by_gb.setdefault(gb, {})[w] = by_gb.get(gb, {}).get(w, Fraction(0)) + c
            terms = []
            for gb in sorted(by_gb):
                dec = decompose(Element(by_gb[gb]), n, allow_constant=True)
                for z, c in sorted(dec.items()):
                    terms.append({"gb": gb, "Z": z, "coeff": str(c)})
            if terms:
                entries.append({"X": x, "Y": y, "terms": terms})
    return entries


def check_consistency(n, entries):
    """Schema 1 consistency + parity checks. Returns list of problem strings."""
    problems = []
    labels, parity, elems = _basis_cache(n)
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    basis = set(s1["basis"]["even"]) | set(s1["basis"]["odd"])
    pmap = s1["parity"]

    # 1. classical parts of deformed brackets reproduce Schema 1 exactly
    sc = {}
    for rec in s1["structure_constants"]:
        sc.setdefault((rec["X"], rec["Y"]), {})[rec["Z"]] = Fraction(rec["coeff"])
    for x in labels:
        for y in labels:
            br = super_bracket(elems[x], elems[y], parity[x], parity[y], deform=True)
            dec = decompose(Element(br.terms), n)
            if dec != sc.get((x, y), {}):
                problems.append(f"classical mismatch at ({x},{y})")

    # 2. gamma parity rule: p(Z) = p(X) + p(Y) + 1 mod 2 (K counts as parity 0)
    for e in entries:
        want = (pmap[e["X"]] + pmap[e["Y"]] + 1) % 2
        for t in e["terms"]:
            pz = 0 if t["Z"] == "K" else pmap[t["Z"]]
            if t["Z"] != "K" and t["Z"] not in basis:
                problems.append(f"unknown Z {t['Z']}")
            if pz != want:
                problems.append(
                    f"parity violation gamma({e['X']},{e['Y']}) -> {t['Z']}"
                )
    return problems


def schema2(n):
    entries = compute_gamma(n)
    problems = check_consistency(n, entries)
    if problems:
        raise RuntimeError(f"n={n}: consistency check failed: {problems[:10]}")
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in ("p", "m")]
    return {
        "schema_version": "5.0",
        "layer": 2,
        "algebra_ref": f"C_{n}_structure.json",
        "gb_matrix": {
            "description": (
                "4n parity-1 deformation parameters gb_{sigma,j,s}: "
                "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa"
            ),
            "shape": [2, 2 * n],
            "rows": ["a_1_p", "a_1_m"],
            "columns": cols,
            "labels": gb_labels(n),
        },
        "inhomogeneous_deformation": {
            "description": (
                "[X,Y]_gamma = [X,Y]_0 + kappa*gamma(X,Y); entries list "
                "gamma(X,Y) as gb-linear combinations of basis elements "
                "('K' = scalar component)"
            ),
            "entries": entries,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": datetime.date.today().isoformat(),
            "references": ["docs/math/C_inhomogeneous_definition.md"],
        },
    }


def main():
    for n in (1, 2, 3):
        data = schema2(n)
        path = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=1)
        ne = len(data["inhomogeneous_deformation"]["entries"])
        nt = sum(len(e["terms"]) for e in data["inhomogeneous_deformation"]["entries"])
        print(
            f"C({n + 1}): {len(gb_labels(n))} gb parameters, "
            f"{ne} nonzero gamma(X,Y) pairs, {nt} terms -> {os.path.relpath(path)} "
            f"[consistency: PASS]"
        )


if __name__ == "__main__":
    main()
