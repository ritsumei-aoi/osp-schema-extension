"""Schema 2 (gamma structure) for C(n+1): inhomogeneous deformation.

Deformation (docs/math/C_inhomogeneous_definition.md):
    [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa
    [X, Y}_gamma = [X, Y}_0 + kappa * gamma(X, Y),   gamma(X, Y) in g (+) C K.
gamma is linear in gb (kappa^2 = 0 allows exactly one deformed contraction), so it is
computed by evaluating the oscillator engine on the 4n unit vectors of gb-space.
The `K` component of gamma is the coefficient of kappa*1 (the central direction).
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
import C_generators as G  # noqa: E402

DATA_DIR = G.DATA_DIR
K_LABEL = "K"


def gb_keys(n):
    """Ordered gb index keys (sigma, j, s): rows sigma, columns (j, s)."""
    return [(sg, j, s) for sg in G.SIGNS for j in range(1, n + 1) for s in G.SIGNS]


def gb_name(key):
    sg, j, s = key
    return f"gb_a_1_{sg}_b_{j}_{s}"


def gb_matrix(n):
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in G.SIGNS]
    rows = ["a_1_p", "a_1_m"]
    entries = [[f"gb_{r}_{c}" for c in cols] for r in rows]
    return {"rows": rows, "cols": cols, "shape": [2, 2 * n], "entries": entries}


def gamma_sparse(n, gb):
    """gamma for a numerical gb ({key: value}); returns {(X, Y): {Z: Fraction}}
    including Z == 'K' for the central component."""
    sc0, sc1, resid = G.structure_constants(n, gb)
    g = {}
    for xy, d in sc1.items():
        g.setdefault(xy, {}).update(d)
    for (X, Y, tag), r in resid.items():
        assert tag == "k", "undeformed part must close without central constants"
        g.setdefault((X, Y), {})[K_LABEL] = r
    return g, sc0


def gamma_linear(n):
    """Symbolic gamma: {(X, Y): {Z: {param_name: Fraction}}}."""
    base0, _, _ = G.structure_constants(n)
    out = {}
    for key in gb_keys(n):
        g, sc0 = gamma_sparse(n, {key: 1})
        assert sc0 == base0, "undeformed part must not depend on gb"
        for xy, d in g.items():
            for Z, c in d.items():
                out.setdefault(xy, {}).setdefault(Z, {})[gb_name(key)] = c
    return out


def evaluate(lin, gb_values):
    """Evaluate a symbolic gamma at {param_name: value}; returns {(X, Y): {Z: Fraction}}."""
    out = {}
    for xy, d in lin.items():
        for Z, terms in d.items():
            v = sum(Fraction(c) * Fraction(gb_values.get(p, 0)) for p, c in terms.items())
            if v != 0:
                out.setdefault(xy, {})[Z] = v
    return out


def cocycle_failures(n, gamma, sc0=None):
    """First-order super Jacobi (kappa-part), g (+) C K valued gamma:
       g(X,[Y,Z]) + (-1)^{pX}[X,g(Y,Z)] - g([X,Y],Z) - [g(X,Y),Z]
         - s ( g(Y,[X,Z]) + (-1)^{pY}[Y,g(X,Z)] ) = 0,   s = (-1)^{pX pY}."""
    if sc0 is None:
        sc0, _, _ = G.structure_constants(n)
    par = G.parity_map(n)
    labels = G.all_labels(n)

    def b(X, Y):
        return sc0.get((X, Y), {})

    def gam(X, Y):
        return gamma.get((X, Y), {})

    def add(acc, vec, c):
        for z, v in vec.items():
            acc[z] = acc.get(z, 0) + c * v

    def gam_vec(X, vec):
        out = {}
        for y, cy in vec.items():
            add(out, gam(X, y), cy)
        return out

    def gam_vec_r(vec, Z):
        out = {}
        for x, cx in vec.items():
            add(out, gam(x, Z), cx)
        return out

    def br_left(X, vec):
        out = {}
        for y, cy in vec.items():
            if y != K_LABEL:
                add(out, b(X, y), cy)
        return out

    def br_right(vec, Z):
        out = {}
        for x, cx in vec.items():
            if x != K_LABEL:
                add(out, b(x, Z), cx)
        return out

    bad = []
    for X in labels:
        for Y in labels:
            s = -1 if (par[X] and par[Y]) else 1
            for Z in labels:
                tot = {}
                add(tot, gam_vec(X, b(Y, Z)), 1)
                add(tot, br_left(X, gam(Y, Z)), (-1) ** par[X])
                add(tot, gam_vec_r(b(X, Y), Z), -1)
                add(tot, br_right(gam(X, Y), Z), -1)
                add(tot, gam_vec(Y, b(X, Z)), -s)
                add(tot, br_left(Y, gam(X, Z)), -s * (-1) ** par[Y])
                if any(v != 0 for v in tot.values()):
                    bad.append((X, Y, Z))
    return bad


def build_schema2(n):
    lin = gamma_linear(n)
    base = G.build_schema1(n)
    labels = G.all_labels(n)
    entries = []
    for X in labels:
        for Y in labels:
            for Z, terms in sorted(lin.get((X, Y), {}).items(), key=lambda t: (t[0] == K_LABEL, labels.index(t[0]) if t[0] != K_LABEL else 0)):
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": {p: G.fstr(c) for p, c in terms.items()}})
    names = [gb_name(k) for k in gb_keys(n)]
    return {
        "schema_version": "5.0",
        "algebra": base["algebra"],
        "basis": base["basis"],
        "parity": base["parity"],
        "central_elements": base["central_elements"],
        "gb_matrix": gb_matrix(n),
        "inhomogeneous_deformation": {
            "description": "Inhomogeneous (gb) deformation of C(n+1); gamma is linear in gb.",
            "relation": "[b_j^s, a_1^σ] = -gb_{σ,j,s} κ",
            "bracket": "[X,Y}_γ = [X,Y}_0 + κ γ(X,Y), κ written on the left",
            "parameters": {"count": 4 * n, "parity": 1, "names": names,
                           "note": "gb are numeric scalars attached to the odd κ"},
            "central_direction": "Z = 'K' denotes the coefficient of κ·1 (K = 1) in γ(X,Y)",
            "gamma": entries,
        },
        "metadata": {
            "generated_by": "src/C_gamma.py",
            "generation_date": "2026-10-06",
            "schema1_file": f"C_{n}_structure.json",
            "references": base["metadata"]["references"],
        },
    }


def write_all(ns=(1, 2, 3), out_dir=DATA_DIR):
    for n in ns:
        path = os.path.join(out_dir, f"C_{n}_gamma.json")
        with open(path, "w") as fh:
            json.dump(build_schema2(n), fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print("wrote", path)


def load_gamma(n, data_dir=DATA_DIR):
    """Read C_{n}_gamma.json -> {(X, Y): {Z: {param: Fraction}}}."""
    with open(os.path.join(data_dir, f"C_{n}_gamma.json")) as fh:
        d = json.load(fh)
    lin = {}
    for e in d["inhomogeneous_deformation"]["gamma"]:
        lin.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {p: Fraction(c) for p, c in e["coeff"].items()}
    return d, lin


if __name__ == "__main__":
    write_all()
    for n in (1, 2, 3):
        lin = gamma_linear(n)
        k = {pq: v for pq, v in lin.items() if any(z == K_LABEL for z in v)}
        gb = {gb_name(key): 1 for key in gb_keys(n)}
        bad = cocycle_failures(n, evaluate(lin, gb))
        print(f"n={n}: nonzero gamma pairs={len(lin)}, with K-component={len(k)}, cocycle failures (gb=all 1)={len(bad)}")
