"""Schema 2 (gamma structure) for the inhomogeneous deformation of C(n+1).

Deformed oscillator relation (docs/math/C_inhomogeneous_definition.md):
    [b_j^s, a_1^sigma] = -gb_{sigma}_{j}_{s} kappa,     kappa odd central, kappa^2 = 0.
Deformed bracket:
    [X, Y]_gamma = [X, Y]_0 + kappa * gamma(X, Y)       (kappa on the left)

gamma(X, Y) is linear in the 4n gb parameters and takes values in g + C K
(K = 1 is the central element; the K-part is stored separately as the
"central_component").

Usage:  python3 src/C_gamma.py [n ...]      (default: 1 2 3)
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import DATA_DIR, SIGNS, CAlgebra, frac_str, write_json  # noqa: E402
from oscillator import gb_label  # noqa: E402


def gb_matrix(n):
    rows = ["a_1_p", "a_1_m"]
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in SIGNS]
    entries = [[gb_label(sg, j, s) for j in range(1, n + 1) for s in SIGNS] for sg in SIGNS]
    return rows, cols, entries


def compute_gamma(n):
    """Returns (gamma, undeformed) where gamma[(X, Y)] = {Z or 'K': {gb: coeff}}."""
    C = CAlgebra(n, deformed=True)
    gamma, und = {}, {}
    for X in C.basis:
        for Y in C.basis:
            r0, rk = C.split(C.raw_bracket(X, Y))
            if r0:
                und[(X, Y)] = r0
            g = {}
            for gb, vec in rk.items():
                for Z, c in vec.items():
                    g.setdefault(Z, {})[gb] = c
            if g:
                gamma[(X, Y)] = g
    return C, gamma, und


def gb_sort_key(n):
    _, _, ent = gb_matrix(n)
    order = {g: i for i, g in enumerate(ent[0] + ent[1])}
    return lambda g: order[g]


def build_schema2(n):
    C, gamma, und = compute_gamma(n)
    rows, cols, entries = gb_matrix(n)
    order = {lab: i for i, lab in enumerate(C.basis)}
    gk = gb_sort_key(n)
    glist, klist = [], []
    for (X, Y), res in gamma.items():
        for Z in sorted(res, key=lambda z: order.get(z, 10 ** 6)):
            coeff = {g: frac_str(c) for g, c in sorted(res[Z].items(), key=lambda t: gk(t[0]))}
            entry = {"X": X, "Y": Y, "Z": Z, "coeff": coeff}
            (klist if Z == "K" else glist).append(entry)
    return {
        "schema_version": "5.0",
        "layer": 2,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
                    "structure_file": f"C_{n}_structure.json"},
        "gb_matrix": {
            "shape": [2, 2 * n],
            "rows": rows, "cols": cols, "entries": entries,
            "parameter_count": 4 * n,
            "parameter_parity": 1,
            "parity_note": ("Labelled parity 1 as in the spec (they enter only through the odd kappa). "
                            "Computationally gb are commuting scalar coefficients: [b,a] is odd and "
                            "kappa is odd, so the scalar gb must commute with everything."),
            "relation": "[b_j^s, a_1^sigma] = - gb_{sigma}_{j}_{s} * kappa",
        },
        "inhomogeneous_deformation": {
            "convention": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y), kappa written on the left",
            "gamma_parity": "odd: p(Z) = p(X) + p(Y) + 1 mod 2",
            "coefficient_format": "coeff is a linear form {gb_label: rational}; gamma_XY^Z = sum gb * c",
            "gamma": glist,
            "central_component": klist,
            "central_note": "Z = 'K': component along the central element K = 1 (scalar part of gamma)",
        },
        "metadata": {"generated_by": "src/C_gamma.py",
                     "generation_date": datetime.date.today().isoformat(),
                     "n_gamma_entries": len(glist), "n_central_entries": len(klist),
                     "notation": "handover/notation.md"},
    }


# ----------------------------------------------------------- consistency ----
def load_gamma(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_gamma.json")) as f:
        d = json.load(f)
    gam = {}
    for e in d["inhomogeneous_deformation"]["gamma"] + d["inhomogeneous_deformation"]["central_component"]:
        gam.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {g: Fraction(c) for g, c in e["coeff"].items()}
    return d, gam


def check_consistency(n):
    """Checks Schema 2 against Schema 1 (both read from JSON):
    1. labels/parities: gamma is odd, all labels in the Schema 1 basis;
    2. undeformed part of the deformed bracket reproduces Schema 1;
    3. 2-cocycle condition (Jacobi of [,]_gamma at order kappa), per gb parameter."""
    from verify_C_structure import load_structure
    basis, par, sc = load_structure(n)
    d, gam = load_gamma(n)
    par_ext = dict(par, K=0)
    res = {}
    res["parity_failures"] = sum(1 for (X, Y), r in gam.items() for Z in r
                                 if par_ext[Z] != (par[X] + par[Y] + 1) % 2)
    res["label_failures"] = sum(1 for (X, Y), r in gam.items()
                                if not ({X, Y} | (set(r) - {"K"})) <= set(basis))
    _, _, und = compute_gamma(n)
    res["undeformed_mismatch"] = sum(1 for X in basis for Y in basis
                                     if und.get((X, Y), {}) != sc.get((X, Y), {}))
    gbs = [g for row in d["gb_matrix"]["entries"] for g in row]
    res["cocycle_failures"] = cocycle_failures(basis, par, sc, gam, gbs)
    res["cocycle_triples_checked"] = len(gbs) * len(basis) ** 3
    return res


def cocycle_failures(basis, par, sc, gam, gbs):
    """Number of (gb, X, Y, Z) violating the order-kappa Jacobi identity of [,]_gamma:
    sum_cyc (-1)^{p(A)p(C)} ( gamma(A,[B,C]_0) + (-1)^{p(A)} [A, gamma(B,C)]_0 ) = 0."""

    def gamma_vec(X, vec, g):  # gamma(X, sum v_W W) restricted to gb = g
        out = {}
        for W, c in vec.items():
            if W == "K":
                continue
            for Z, cs in gam.get((X, W), {}).items():
                if g in cs:
                    out[Z] = out.get(Z, 0) + c * cs[g]
        return out

    def br_vec(X, vec):  # [X, sum v_W W]_0, K central
        out = {}
        for W, c in vec.items():
            if W == "K":
                continue
            for Z, e in sc.get((X, W), {}).items():
                out[Z] = out.get(Z, 0) + c * e
        return out

    fails = 0
    for g in gbs:
        for X in basis:
            for Y in basis:
                for Z in basis:
                    tot = {}
                    for (A, B, Cc) in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
                        s = (-1) ** (par[A] * par[Cc])
                        inner0 = sc.get((B, Cc), {})
                        innerg = {W: cs[g] for W, cs in gam.get((B, Cc), {}).items() if g in cs}
                        for W, c in gamma_vec(A, inner0, g).items():
                            tot[W] = tot.get(W, 0) + s * c
                        for W, c in br_vec(A, innerg).items():
                            tot[W] = tot.get(W, 0) + s * (-1) ** par[A] * c
                    if any(v != 0 for v in tot.values()):
                        fails += 1
    return fails


def main(ns):
    for n in ns:
        s = build_schema2(n)
        p = write_json(s, f"C_{n}_gamma.json")
        m = s["metadata"]
        print(f"n={n}: gamma entries={m['n_gamma_entries']} central entries={m['n_central_entries']} "
              f"-> {os.path.relpath(p)}")
        print(f"   consistency: {check_consistency(n)}")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
