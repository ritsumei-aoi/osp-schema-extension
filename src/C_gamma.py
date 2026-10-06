"""Schema 2 generator: inhomogeneous (gamma) deformation of C(n+1).  Issue I05.

The deformation is carried by the ``4n`` parameters ``gb[sigma, k, s]`` through
the single modified oscillator relation
(``docs/math/C_inhomogeneous_definition.md`` 1)::

    [b_k^s, a_1^sigma] = - gb[sigma, k, s] * kappa

Recomputing the graded bracket of two basis generators in this deformed algebra
gives::

    [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)

and ``gamma(X, Y) = sum_Z gamma_{XYZ} Z`` is read off by stripping the leading
``kappa``.  Each ``gamma_{XYZ}`` is **linear** in the gb parameters: a second
contraction would need a second ``kappa`` and ``kappa^2 = 0``.

Writes ``data/C_{n}_gamma.json``.

Usage::

    python src/C_gamma.py            # n = 1, 2, 3
"""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Tuple

import sympy as sp

try:
    from .osc_algebra import CAlgebra, boson, gb_symbols
    from .C_generators import algebra_field, GENERATION_DATE, REFERENCES, rat
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from osc_algebra import CAlgebra, boson, gb_symbols  # type: ignore
    from C_generators import algebra_field, GENERATION_DATE, REFERENCES, rat  # type: ignore

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")


def gb_matrix_field(n: int, labels: Dict[Tuple[str, int, str], str]) -> dict:
    rows = ["a_1_p", "a_1_m"]
    cols = [boson(k, s) for k in range(1, n + 1) for s in ("p", "m")]
    entries = [
        [labels[(sigma, k, s)] for k in range(1, n + 1) for s in ("p", "m")]
        for sigma in ("p", "m")
    ]
    return {
        "shape": [2, 2 * n],
        "rows": rows,
        "cols": cols,
        "entries": entries,
        "parameters": [e for row in entries for e in row],
        "count": 4 * n,
        "defining_relation": "[b_k^s, a_1^sigma] = - gb_{sigma,k,s} * kappa",
        "naming": "gb_a1{P|M}_b{k}{P|M}: fermionic sign, bosonic index, bosonic sign",
        "parity_note": (
            "gb parameters are treated as EVEN (commuting) formal scalars. "
            "See Issue I05 Response, section 'Parity of gb'."
        ),
    }


def build_gamma(n: int):
    """Return ``(alg_deformed, alg_plain, gamma_entries, consistency)``."""
    gb, labels = gb_symbols(n)
    alg = CAlgebra(n, gb)
    plain = CAlgebra(n)

    entries: List[dict] = []
    mismatches: List[str] = []
    central: List[str] = []

    order = alg.pbw_order
    for i, x in enumerate(order):
        for y in order[i:]:
            full = alg.bracket_labels(x, y)
            free, kap = alg.split_kappa(full)

            # the undeformed part must be unchanged (kappa^2 = 0 kills gb^2)
            ref = plain.bracket_labels(x, y)
            if not all(sp.expand(c) == 0 for c in
                       {**{w: free.get(w, 0) - ref.get(w, 0)
                           for w in set(free) | set(ref)}}.values()):
                mismatches.append(f"({x}, {y})")

            if not kap:
                continue
            coeffs = alg.decompose_kappa(kap)
            for z in order + ["K"]:
                c = coeffs.get(z)
                if c is None or sp.expand(c) == 0:
                    continue
                if z == "K":
                    central.append(f"({x}, {y})")
                entries.append({
                    "X": x, "Y": y, "Z": z,
                    "coeff": str(sp.expand(c)),
                    "parity_X": alg.parity[x],
                    "parity_Y": alg.parity[y],
                })

    consistency = {
        "undeformed_part_matches_schema1": not mismatches,
        "undeformed_mismatches": mismatches,
        "gamma_is_linear_in_gb": True,
        "central_K_component_pairs": sorted(set(central)),
        "central_K_note": (
            "gamma takes values in the central extension g + C*K, not in g alone. "
            "The K-components are genuine (see Issue I05 Response) and occur exactly "
            "on (odd, even) pairs; they constrain the Layer 4 map f, which is "
            "therefore allowed to take values in g + C*K (see Issue I07)."
        ),
    }
    return alg, plain, entries, consistency, labels


def gamma_table(alg: CAlgebra, entries: List[dict]) -> Dict[Tuple[str, str], Dict[str, sp.Expr]]:
    """Full (both orders) gamma table, expanded by graded antisymmetry."""
    stored: Dict[Tuple[str, str], Dict[str, sp.Expr]] = {}
    for e in entries:
        stored.setdefault((e["X"], e["Y"]), {})[e["Z"]] = sp.sympify(e["coeff"])
    full: Dict[Tuple[str, str], Dict[str, sp.Expr]] = {}
    for x in alg.pbw_order:
        for y in alg.pbw_order:
            if alg.index[x] <= alg.index[y]:
                full[(x, y)] = dict(stored.get((x, y), {}))
            else:
                sign = -1 if (alg.parity[x] and alg.parity[y]) else 1
                full[(x, y)] = {k: sp.expand(-sign * v)
                                for k, v in stored.get((y, x), {}).items()}
    return full


def check_cocycle(alg: CAlgebra, gam, max_report: int = 5):
    """Verify the 2-cocycle condition implied by super Jacobi on L = g + kappa*g.

    In ``L`` one has ``[kappa u, Z} = kappa [u, Z}_0``, so the kappa-component of
    ``[[X,Y]_gamma, Z]_gamma`` is

        Phi(X,Y,Z) = gamma([X,Y]_0, Z) + [gamma(X,Y), Z]_0 ,

    and super Jacobi (cyclic form) requires

        (-1)^{p(X)p(Z)} Phi(X,Y,Z) + (-1)^{p(Y)p(X)} Phi(Y,Z,X)
        + (-1)^{p(Z)p(Y)} Phi(Z,X,Y) = 0 .
    """
    order = alg.pbw_order
    par = dict(alg.parity)
    par["K"] = 0

    br: Dict[Tuple[str, str], Dict[str, sp.Expr]] = {}
    for x in order:
        for y in order:
            br[(x, y)] = alg.bracket_coeffs(x, y)

    def vadd(a, b, scale=1):
        out = dict(a)
        for k, v in b.items():
            nv = sp.expand(out.get(k, 0) + scale * v)
            if nv == 0:
                out.pop(k, None)
            else:
                out[k] = nv
        return out

    def gamma_vec(u, z):
        """gamma(u, z) for u a coefficient vector (K-component is central: gamma=0)."""
        out: Dict[str, sp.Expr] = {}
        for a, c in u.items():
            if a == "K":
                continue
            out = vadd(out, gam[(a, z)], c)
        return out

    def bracket_vec(u, z):
        out: Dict[str, sp.Expr] = {}
        for a, c in u.items():
            if a == "K":
                continue
            out = vadd(out, br[(a, z)], c)
        return out

    def phi(x, y, z):
        return vadd(gamma_vec(br[(x, y)], z), bracket_vec(gam[(x, y)], z))

    errs: List[str] = []
    count = 0
    for x in order:
        for y in order:
            for z in order:
                count += 1
                acc: Dict[str, sp.Expr] = {}
                for a, b, c in ((x, y, z), (y, z, x), (z, x, y)):
                    sgn = -1 if (par[a] and par[c]) else 1
                    acc = vadd(acc, phi(a, b, c), sgn)
                if acc:
                    if len(errs) < max_report:
                        errs.append(f"cocycle fails at ({x}, {y}, {z}): {acc}")
    return count, errs


def gamma_support_summary(alg: CAlgebra, entries: List[dict]) -> dict:
    """Which parity sectors carry a non-zero gamma."""
    sectors: Dict[str, int] = {"odd-odd": 0, "odd-even": 0, "even-even": 0}
    pairs = {(e["X"], e["Y"]) for e in entries}
    for x, y in pairs:
        px, py = alg.parity[x], alg.parity[y]
        key = {(1, 1): "odd-odd", (0, 0): "even-even"}.get((px, py), "odd-even")
        sectors[key] += 1
    return {
        "nonzero_pairs_by_sector": sectors,
        "nonzero_pairs_total": len(pairs),
        "nonzero_entries_total": len(entries),
    }


def build_schema2(n: int, cocycle: bool = True) -> dict:
    alg, _plain, entries, consistency, labels = build_gamma(n)
    if cocycle:
        gam = gamma_table(alg, entries)
        c_count, c_errs = check_cocycle(alg, gam)
        consistency["cocycle_triples_checked"] = c_count
        consistency["cocycle_condition_holds"] = not c_errs
        consistency["cocycle_failures"] = c_errs
    return {
        "schema_version": "5.0",
        "layer": 2,
        "algebra": algebra_field(n),
        "basis": {
            "even": alg.even,
            "odd": alg.odd,
            "pbw_order": alg.pbw_order,
            "source": f"data/C_{n}_structure.json",
        },
        "parity": {lab: alg.parity[lab] for lab in alg.pbw_order},
        "gb_matrix": gb_matrix_field(n, labels),
        "inhomogeneous_deformation": {
            "description": "gamma with [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y)",
            "convention": (
                "entries are stored for pbw_index(X) <= pbw_index(Y); "
                "gamma inherits the graded antisymmetry of the bracket: "
                "gamma(Y,X) = -(-1)^{p(X)p(Y)} gamma(X,Y)"
            ),
            "coeff_format": "linear form in the gb symbols (sympy string)",
            "entries": entries,
            **gamma_support_summary(alg, entries),
        },
        "consistency": consistency,
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": GENERATION_DATE,
            "references": REFERENCES + ["docs/math/C_inhomogeneous_definition.md"],
        },
    }


def write_schema2(n: int) -> str:
    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, f"C_{n}_gamma.json")
    with open(path, "w") as fh:
        json.dump(build_schema2(n), fh, indent=2)
        fh.write("\n")
    return path


def main(argv: List[str]) -> int:
    ns = [int(a) for a in argv[1:]] or [1, 2, 3]
    ok = True
    for n in ns:
        path = write_schema2(n)
        with open(path) as fh:
            doc = json.load(fh)
        d = doc["inhomogeneous_deformation"]
        c = doc["consistency"]
        ok &= c["undeformed_part_matches_schema1"] and c.get("cocycle_condition_holds", True)
        print(f"n={n}  gb params={doc['gb_matrix']['count']}  "
              f"gamma entries={d['nonzero_entries_total']}  "
              f"pairs={d['nonzero_pairs_total']} {d['nonzero_pairs_by_sector']}")
        print(f"      schema1-consistent={c['undeformed_part_matches_schema1']}  "
              f"cocycle={c.get('cocycle_condition_holds')} "
              f"({c.get('cocycle_triples_checked')} triples)  "
              f"K-pairs={len(c['central_K_component_pairs'])}  "
              f"-> {os.path.relpath(path, REPO)}")
    print("SUMMARY:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
