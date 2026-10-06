"""Schema 2: inhomogeneous deformation (gamma structure) of C(n+1).

Deformed oscillator relation:  [b_j^s, a_1^sigma] = -gb[sigma,j,s] * kappa  (kappa odd, central, kappa^2 = 0).
The deformed bracket is  [X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y),  gamma linear in gb.
gamma takes values in g + C*K: the constant ("K") component is the central element kappa*K = kappa itself.

Usage: python src/C_gamma.py   (writes data/C_{n}_gamma.json, n=1,2,3)
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import Decomposer, build_basis, frac_str, mono  # noqa: E402
from osc_algebra import bracket  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def gb_params(n):
    """Ordered gb parameters: (sigma, j, s) rows a_1_p, a_1_m; columns b_1_p, b_1_m, ..., b_n_p, b_n_m."""
    return [(sg, j, s) for sg in "pm" for j in range(1, n + 1) for s in "pm"]


def gb_name(p):
    sg, j, s = p
    return f"gb_a_1_{sg}_b_{j}_{s}"


def extended_decomposer(n):
    names, parity, R = build_basis(n)
    R2 = dict(R)
    R2["K"] = {mono(n): Fraction(1)}
    return names, parity, R, Decomposer(names + ["K"], R2)


def compute_gamma(n):
    """Return (names, parity, gamma) with gamma[(X,Y)][param] = {Z: Fraction}, Z in names + ['K']."""
    names, parity, R, dec = extended_decomposer(n)
    gamma = {}
    for p in gb_params(n):
        gb = {p: Fraction(1)}
        for X in names:
            for Y in names:
                br = bracket(R[X], R[Y], n, parity[X], parity[Y], gb)
                p0 = {m: c for m, c in br.items() if m[0] == 0}
                q1 = {(0,) + m[1:]: c for m, c in br.items() if m[0] == 1}
                # kappa-free part must equal the undeformed bracket (checked in tests); not stored here.
                if not q1:
                    continue
                coef, res = dec.decompose(q1)
                if res:
                    raise RuntimeError(f"gamma({X},{Y}) leaves span of g+K: {res}")
                gamma.setdefault((X, Y), {})[p] = coef
    return names, parity, gamma


def build_schema2(n, structure, date=None):
    names, parity, gamma = compute_gamma(n)
    params = gb_params(n)
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in "pm"]
    idx = {x: i for i, x in enumerate(names + ["K"])}
    entries = []
    nzpairs = sorted(gamma, key=lambda t: (idx[t[0]], idx[t[1]]))
    for (X, Y) in nzpairs:
        zs = sorted({z for p in gamma[(X, Y)] for z in gamma[(X, Y)][p]}, key=lambda z: idx[z])
        for Z in zs:
            co = {gb_name(p): frac_str(gamma[(X, Y)][p][Z]) for p in params
                  if p in gamma[(X, Y)] and Z in gamma[(X, Y)][p]}
            entries.append({"X": X, "Y": Y, "Z": Z, "coeff": co})
    return {
        "schema_version": "5.0",
        "schema_layer": 2,
        "algebra": structure["algebra"],
        "central_elements": structure["central_elements"],
        "basis": structure["basis"],
        "parity": structure["parity"],
        "gb_matrix": {
            "shape": [2, 2 * n],
            "rows": ["a_1_p", "a_1_m"],
            "columns": cols,
            "parity": 1,
            "relation": "[b_j^s, a_1^sigma] = -gb_{sigma,j,s} * kappa",
            "entries": [[gb_name((sg, j, s)) for j in range(1, n + 1) for s in "pm"] for sg in "pm"],
            "parameter_count": 4 * n,
        },
        "inhomogeneous_deformation": {
            "description": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y); gamma linear in gb. "
                           "Z='K' denotes the central constant (kappa*K = kappa).",
            "bracket": "[X,Y]_gamma = [X,Y]_0 + kappa*gamma(X,Y)",
            "gamma_codomain": "g (+) C*K",
            "gamma_parity_rule": "p(Z) = p(X) + p(Y) + 1 (mod 2); Z='K' has parity 0",
            "parameters": [gb_name(p) for p in params],
            "gamma_structure": entries,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": date or datetime.date.today().isoformat(),
            "references": ["docs/math/C_inhomogeneous_definition.md"],
        },
    }


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    for n in (1, 2, 3):
        st = json.load(open(os.path.join(DATA_DIR, f"C_{n}_structure.json")))
        d = build_schema2(n, st)
        path = os.path.join(DATA_DIR, f"C_{n}_gamma.json")
        with open(path, "w") as f:
            json.dump(d, f, indent=1, ensure_ascii=False)
        ents = d["inhomogeneous_deformation"]["gamma_structure"]
        print(f"n={n}: {path}: gamma entries={len(ents)}, K-entries={sum(e['Z'] == 'K' for e in ents)}")


if __name__ == "__main__":
    main()
