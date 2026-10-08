"""I05: Schema 2 (inhomogeneous deformation / gamma structure) for C(n+1).

The deformed oscillator relations  [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa  (kappa odd, kappa^2 = 0)
induce on g = C(n+1) the deformed bracket
        [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y),        gamma(X, Y) in g (+) C K .
gamma is computed exactly (symbolically in the 4n parameters gb) by evaluating the super-commutator
of the oscillator realizations in the deformed algebra and reading off the kappa-component.

Usage:  python src/C_gamma.py [n ...]   -> data/C_{n}_gamma.json  (+ consistency checks)
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import Poly  # noqa: E402
from C_generators import CBasis, DATA_DIR  # noqa: E402


# ---------------------------------------------------------------------------
# computation
# ---------------------------------------------------------------------------
def compute_gamma(n: int):
    """Return (basis, undeformed table, gamma) with gamma[(X,Y)] = {Z: Poly} (Z may be 'K')."""
    B = CBasis(n, deformed=True)
    table, gamma = B.structure_constants()
    return B, table, gamma


def gb_matrix(n: int) -> dict:
    rows = ["a_1_p", "a_1_m"]
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in "pm"]
    entries = [[f"gb_a1{sigma}_b{j}{s}" for j in range(1, n + 1) for s in "pm"] for sigma in "pm"]
    return {
        "description": "Deformation parameters gb_{sigma,j,s}: rows = fermionic oscillator a_1^sigma, columns = bosonic oscillator b_j^s",
        "shape": [2, 2 * n],
        "rows": rows,
        "columns": cols,
        "entries": entries,
        "parameter_count": 4 * n,
        "parameters": [g for row in entries for g in row],
        "parity_note": "gb are scalar coefficients of the odd (boson-fermion) block of the pre-oscillator form; "
                       "the 'parity 1' of C_inhomogeneous_definition.md refers to that block. "
                       "[b, a] is odd and kappa is odd, so gb itself is an even scalar.",
    }


# ---------------------------------------------------------------------------
# consistency checks
# ---------------------------------------------------------------------------
def deformed_bracket(B: CBasis, table, gamma, u: dict, v: dict, pu: int, pv: int):
    """Bracket on L = g (+) kappa(g (+) K) for u = (u0, u1), v = (v0, v1) meaning u0 + kappa u1.

    Vectors are dicts label -> Poly.  Returns (w0, w1).
    [u0, v0]_gamma = [u0,v0]_0 + kappa gamma(u0,v0);  [u0, kappa v1] = (-1)^{p(u0)} kappa [u0, v1]_0;
    [kappa u1, v0] = kappa [u1, v0]_0;  [kappa u1, kappa v1] = 0;  [., K] = 0.
    """
    u0, u1 = u
    v0, v1 = v
    w0: dict = {}
    w1: dict = {}

    def acc(target, comps, scale):
        for z, c in comps.items():
            s = target.get(z, Poly()) + c * scale
            if s:
                target[z] = s
            elif z in target:
                del target[z]

    for x, cx in u0.items():
        for y, cy in v0.items():
            acc(w0, table.get((x, y), {}), cx * cy)
            acc(w1, gamma.get((x, y), {}), cx * cy)
    sgn = -1 if pu else 1
    for x, cx in u0.items():
        for y, cy in v1.items():
            if y != "K":
                acc(w1, table.get((x, y), {}), cx * cy * sgn)
    for x, cx in u1.items():
        if x == "K":
            continue
        for y, cy in v0.items():
            acc(w1, table.get((x, y), {}), cx * cy)
    return w0, w1


def check_cocycle(B: CBasis, table, gamma) -> int:
    """Super Jacobi of the deformed bracket at order kappa for all basis triples. Returns #failures."""
    labs, p = B.labels, B.parity
    one = Poly.const(1)
    fails = 0
    for x in labs:
        for y in labs:
            for z in labs:
                tot: dict = {}
                for (a, b, c) in ((x, y, z), (y, z, x), (z, x, y)):
                    sgn = -1 if (p[a] and p[c]) else 1
                    inner = deformed_bracket(B, table, gamma, ({b: one}, {}), ({c: one}, {}), p[b], p[c])
                    _, w1 = deformed_bracket(B, table, gamma, ({a: one}, {}), inner, p[a], (p[b] + p[c]) % 2)
                    for w, cc in w1.items():
                        s = tot.get(w, Poly()) + cc * sgn
                        if s:
                            tot[w] = s
                        elif w in tot:
                            del tot[w]
                if tot:
                    fails += 1
    return fails


def check_consistency(n: int, B: CBasis, table, gamma, schema1: dict) -> dict:
    """Checks: (1) gb-independent part == Schema 1; (2) gamma homogeneous linear in gb;
    (3) parity rule p(Z) = p(X)+p(Y)+1; (4) cocycle condition."""
    rep = {}
    # (1)
    s1 = {}
    for e in schema1["structure_constants"]:
        s1.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    mine = {k: {z: c.constant() for z, c in v.items()} for k, v in table.items()}
    rep["undeformed_part_matches_schema1"] = (s1 == mine)
    # (2)
    lin = all(c.degree() == 1 and c.constant() == 0 for v in gamma.values() for c in v.values())
    rep["gamma_linear_homogeneous_in_gb"] = lin
    # (3)
    par = all(((0 if z == "K" else B.parity[z]) == (B.parity[x] + B.parity[y] + 1) % 2)
              for (x, y), v in gamma.items() for z in v)
    rep["parity_rule"] = par
    # (4)
    rep["cocycle_failures"] = check_cocycle(B, table, gamma)
    rep["passed"] = rep["undeformed_part_matches_schema1"] and lin and par and rep["cocycle_failures"] == 0
    return rep


# ---------------------------------------------------------------------------
# Schema 2 JSON
# ---------------------------------------------------------------------------
def gamma_entries(B: CBasis, gamma) -> list:
    out = []
    zorder = B.labels + ["K"]
    for x in B.labels:
        for y in B.labels:
            comps = gamma.get((x, y))
            if not comps:
                continue
            for z in zorder:
                if z in comps:
                    out.append({"X": x, "Y": y, "Z": z, "coeff": str(comps[z]),
                                "coeff_terms": comps[z].to_terms_dict()})
    return out


def build_schema2(n: int, date: str | None = None) -> dict:
    B, table, gamma = compute_gamma(n)
    date = date or datetime.date.today().isoformat()
    entries = gamma_entries(B, gamma)
    return {
        "schema_version": "5.0",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
                    "structure_file": f"C_{n}_structure.json",
                    "dimension": {"even": len(B.even), "odd": len(B.odd), "total": len(B.labels)}},
        "gb_matrix": gb_matrix(n),
        "deformed_oscillator_relations": {
            "description": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa ; all other oscillator relations unchanged",
            "relations": [{"boson": f"b_{j}_{s}", "fermion": f"a_1_{sigma}",
                           "bracket": f"[b_{j}_{s}, a_1_{sigma}] = -{B.alg.gb_label(sigma, j, s)} * kappa"}
                          for sigma in "pm" for j in range(1, n + 1) for s in "pm"],
        },
        "central_elements": {
            "kappa": {"label": "kappa", "parity": 1, "relation": "kappa^2 = 0", "super_central": True},
            "K": {"label": "K", "parity": 0, "relation": "K = 1"},
        },
        "inhomogeneous_deformation": {
            "description": "[X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y); gamma(X,Y) = sum_Z coeff * Z",
            "codomain": "g (+) C K : entries with Z = 'K' are the constant (central) components",
            "parity_rule": "p(Z) = p(X) + p(Y) + 1 (mod 2), with p(K) = 0",
            "coefficient_format": "coeff: polynomial in gb as a string; coeff_terms: {monomial: rational}",
            "pairs_stored": "all ordered pairs (X, Y) with gamma(X, Y) != 0",
            "gamma": entries,
            "statistics": {
                "nonzero_pairs": len(gamma),
                "entries": len(entries),
                "entries_with_K": sum(1 for e in entries if e["Z"] == "K"),
            },
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date,
            "conventions": "handover/notation.md",
            "references": ["docs/math/C_inhomogeneous_definition.md"],
        },
    }


def write_schema2(n: int, out_dir: str = DATA_DIR) -> str:
    path = os.path.join(out_dir, f"C_{n}_gamma.json")
    with open(path, "w") as fh:
        json.dump(build_schema2(n), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


def load_json(name: str, data_dir: str = DATA_DIR) -> dict:
    with open(os.path.join(data_dir, name)) as fh:
        return json.load(fh)


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    ok = True
    for n in ns:
        p = write_schema2(n)
        B, table, gamma = compute_gamma(n)
        rep = check_consistency(n, B, table, gamma, load_json(f"C_{n}_structure.json"))
        d = build_schema2(n)
        st = d["inhomogeneous_deformation"]["statistics"]
        print(f"{p}: {st} consistency={rep}")
        ok &= rep["passed"]
    print("SUMMARY:", "all consistency checks passed" if ok else "FAILURES PRESENT")
    sys.exit(0 if ok else 1)
