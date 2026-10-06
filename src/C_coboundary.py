"""Schema 4 (coboundary structure) for C(n+1).

Odd linear map  f(Z_j) = sum_i phi[i,j] Z_i,  phi[i,j] free only if p(Z_i) != p(Z_j)
(docs/math/C_coboundary_definition.md), optionally extended by a scalar part
f(Z_j) += psi[j] K for odd Z_j (K even), used for the "exact, including central part" reading.

    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X, Y])

Coefficients (delta f)^W_{XY} are linear in phi/psi and are stored as linear forms.

Usage:  python3 src/C_coboundary.py     -> data/C_{n}_coboundary.json, n = 1, 2, 3
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import global_order, parity_map, write_json, frac_str, DATA_DIR  # noqa: E402
from C_gamma import lin_expr  # noqa: E402


def phi_label(i, j):
    return f"phi__{i}__{j}"


def psi_label(j):
    return f"psi__{j}"


def load_sc(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as f:
        d = json.load(f)
    sc = {}
    for e in d["structure_constants"]:
        sc.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return d["basis"]["global_order"], d["parity"], sc


def unknowns(basis, par):
    phis = [(i, j) for j in basis for i in basis if par[i] != par[j]]
    psis = [j for j in basis if par[j] == 1]
    return phis, psis


def coboundary_symbolic(basis, par, sc):
    """{(X, Y): {W: {unknown_label: Fraction}}} for all ordered pairs (W may be 'K')."""
    opp = {j: [i for i in basis if par[i] != par[j]] for j in basis}
    out = {}

    def acc(pair, W, lab, c):
        d = out.setdefault(pair, {}).setdefault(W, {})
        d[lab] = d.get(lab, 0) + c
        if d[lab] == 0:
            del d[lab]

    for X in basis:
        for Y in basis:
            pX, pY = par[X], par[Y]
            s1 = -1 if pX else 1
            s2 = -1 if ((pX + 1) * pY) % 2 else 1
            for i in opp[Y]:                      # (-1)^{p(X)} [X, f(Y)]
                for W, c in sc.get((X, i), {}).items():
                    acc((X, Y), W, phi_label(i, Y), s1 * c)
            for i in opp[X]:                      # -(-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                for W, c in sc.get((Y, i), {}).items():
                    acc((X, Y), W, phi_label(i, X), -s2 * c)
            for V, c in sc.get((X, Y), {}).items():   # -f([X, Y])
                for W in opp[V]:
                    acc((X, Y), W, phi_label(W, V), -c)
                if par[V] == 1:
                    acc((X, Y), "K", psi_label(V), -c)
    return {p: {W: d for W, d in ws.items() if d} for p, ws in out.items()
            if any(ws.values())}


def evaluate_linear(sym, values):
    out = {}
    for pair, ws in sym.items():
        for W, lin in ws.items():
            v = sum((Fraction(values.get(k, 0)) * c for k, c in lin.items()), Fraction(0))
            if v:
                out.setdefault(pair, {})[W] = v
    return out


def build_schema4(n, date=None):
    date = date or datetime.date.today().isoformat()
    basis, par, sc = load_sc(n)
    assert basis == global_order(n) and par == parity_map(n)
    idx = {x: i for i, x in enumerate(basis + ["K"])}
    phis, psis = unknowns(basis, par)
    sym = coboundary_symbolic(basis, par, sc)
    entries = []
    for (X, Y) in sorted(sym, key=lambda p: (idx[p[0]], idx[p[1]])):
        if idx[X] > idx[Y]:
            continue
        for W in sorted(sym[(X, Y)], key=idx.get):
            lin = sym[(X, Y)][W]
            entries.append({"X": X, "Y": Y, "Z": W,
                            "coeff": {k: frac_str(c) for k, c in lin.items()},
                            "expr": lin_expr(lin)})
    return {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})", "osp": f"osp(2|{2*n})"},
        "structure_ref": f"C_{n}_structure.json",
        "basis_order": basis,
        "coboundary": {
            "definition": "(δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            "odd_map": {
                "parametrization": "f(Z_j) = Σ_i phi__{Z_i}__{Z_j} Z_i  (+ psi__{Z_j} K for odd Z_j)",
                "phi_unknowns": len(phis),
                "phi_rule": "phi__{Z_i}__{Z_j} is free iff p(Z_i) != p(Z_j) (f reverses parity)",
                "psi_unknowns": len(psis),
                "psi_rule": ("optional scalar part f(Z_j) ∋ psi__{Z_j} K for odd Z_j (K is even); it only "
                             "contributes to the central component Z = 'K' as -psi([X,Y]). Set psi = 0 for the "
                             "strict reading f: g -> g."),
                "phi_order": [phi_label(i, j) for i, j in phis],
                "psi_order": [psi_label(j) for j in psis],
            },
            "symmetry": ("Stored only for index(X) <= index(Y) in basis_order; "
                         "(δf)(Y,X) = -(-1)^{p(X)p(Y)} (δf)(X,Y)"),
            "target_space": "g ⊕ C K (Z = 'K' is the central component)",
            "parity_rule": "p(Z) = p(X) + p(Y) + 1 mod 2",
            "entries": entries,
            "statistics": {"entries": len(entries),
                           "pairs_stored": len({(e['X'], e['Y']) for e in entries}),
                           "central_entries": sum(e["Z"] == "K" for e in entries)},
        },
        "metadata": {"generated_by": "src/C_coboundary.py", "generation_date": date,
                     "conventions": "handover/notation.md",
                     "math_reference": "docs/math/C_coboundary_definition.md"},
    }


def load_coboundary(n):
    """Read Schema 4 back, restoring all ordered pairs via the symmetry rule."""
    with open(os.path.join(DATA_DIR, f"C_{n}_coboundary.json")) as f:
        d = json.load(f)
    par = {}
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as f:
        par = json.load(f)["parity"]
    sym = {}
    for e in d["coboundary"]["entries"]:
        lin = {k: Fraction(c) for k, c in e["coeff"].items()}
        X, Y, W = e["X"], e["Y"], e["Z"]
        sym.setdefault((X, Y), {})[W] = lin
        if X != Y:
            s = -1 if (par[X] and par[Y]) else 1
            sym.setdefault((Y, X), {})[W] = {k: -s * c for k, c in lin.items()}
    return d, sym


def main(ns=(1, 2, 3)):
    for n in ns:
        s = build_schema4(n)
        p = write_json(s, f"C_{n}_coboundary.json")
        cb = s["coboundary"]
        print(f"n={n}: phi={cb['odd_map']['phi_unknowns']}, psi={cb['odd_map']['psi_unknowns']}, "
              f"{cb['statistics']} -> {os.path.relpath(p)} ({os.path.getsize(p)//1024} KiB)")


if __name__ == "__main__":
    main()
