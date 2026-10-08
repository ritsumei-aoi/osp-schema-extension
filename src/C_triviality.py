"""Triviality search for the C(n+1) inhomogeneous deformation (I08).

The deformation gamma(gb) (Schema 2) is trivial iff gamma(gb) = delta f for some
odd map f = sum phi_ij f_ij (Schema 4). Both sides are linear, so a scalar
multiple is absorbed into phi and "up to scalar" adds nothing.

Setup. Let D be the matrix with rows indexed by (X, Y, Z) and columns by phi_ij,
so that D phi is the coboundary. Let G be the matrix with the same rows and
columns indexed by gb, so that G gb is gamma(gb). Then

    gamma(gb) is trivial  <=>  exists phi with G gb = D phi,

and the set T of trivial gb is the projection to the gb coordinates of the null
space of [ -D | G ]. T is a linear subspace of Q^{4n}. We compute T exactly over Q,
and its annihilator, the explicit linear conditions on gb.

The K components of gamma have no counterpart in D (coboundaries of maps into
the basis carry no K), so they are included as rows that must vanish.
"""

import json
from pathlib import Path

import sympy
from sympy.polys.matrices import DomainMatrix
from sympy import QQ


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_gamma(n):
    doc = json.loads((DATA / f"C_{n}_gamma.json").read_text())
    rows, cols = doc["gb_matrix"]["rows"], doc["gb_matrix"]["columns"]
    gb = [sympy.Symbol(f"gb_{r}__{c}") for r in rows for c in cols]
    entries = {}
    for e in doc["inhomogeneous_deformation"]["gamma"]:
        entries.setdefault((e["X"], e["Y"], e["Z"]), 0)
        entries[(e["X"], e["Y"], e["Z"])] += sympy.sympify(e["coeff"])
    return gb, entries


def load_coboundary(n):
    doc = json.loads((DATA / f"C_{n}_coboundary.json").read_text())
    cols = [m["phi"] for m in doc["coboundary_maps"]]
    entries = {}
    for k, m in enumerate(doc["coboundary_maps"]):
        for e in m["coboundary_entries"]:
            entries[(e["X"], e["Y"], e["Z"], k)] = sympy.Rational(e["coeff"])
    return cols, entries


def trivial_subspace(n, include_K=True, G=None):
    """Return (gb symbols, basis of T as rows, conditions as rows v with v . gb = 0).

    include_K=False drops the K rows of gamma (K treated as an ignored scalar).
    G may be passed directly as {(X, Y, Z): linear form in gb}, for tests.
    """
    gb, G_file = load_gamma(n)
    G = G_file if G is None else G
    if not include_K:
        G = {k: v for k, v in G.items() if k[2] != "K"}
    phis, D = load_coboundary(n)
    rows = sorted({(X, Y, Z) for (X, Y, Z) in G} | {(X, Y, Z) for (X, Y, Z, _) in D})
    row_index = {r: i for i, r in enumerate(rows)}
    m, p, q = len(rows), len(phis), len(gb)
    # Augmented matrix [ -D | G ] over QQ, shape (m, p + q).
    M = [[QQ(0)] * (p + q) for _ in range(m)]
    for (X, Y, Z, k), c in D.items():
        M[row_index[(X, Y, Z)]][k] = -QQ(int(c.p), int(c.q))
    for (X, Y, Z), expr in G.items():
        for j, s in enumerate(gb):
            c = sympy.Rational(sympy.expand(expr).coeff(s))
            if c != 0:
                M[row_index[(X, Y, Z)]][p + j] = QQ(int(c.p), int(c.q))
    A = DomainMatrix(M, (m, p + q), QQ)
    N = A.nullspace()  # rows span the null space of [ -D | G ]
    # Project each null vector to its gb coordinates.
    proj = [[row[p + j] for j in range(q)] for row in N.to_Matrix().tolist()]
    W = sympy.Matrix(proj) if proj else sympy.zeros(0, q)
    # T = rowspace(W). Conditions on gb: v . gb = 0 for v in nullspace(W).
    if W.rows == 0:
        T_basis = sympy.zeros(0, q)
        conditions = sympy.eye(q)
    else:
        rref, _ = W.rref()
        nonzero = [rref.row(i) for i in range(rref.rows) if any(rref.row(i))]
        T_basis = sympy.Matrix.vstack(*nonzero) if nonzero else sympy.zeros(0, q)
        conditions = W.nullspace()
        conditions = sympy.Matrix.hstack(*conditions).T if conditions else sympy.zeros(0, q)
    return gb, T_basis, conditions


def torus_weights(n):
    """Weights of basis elements under the Cartan H_eps, H_1..H_n (from Schema 1)."""
    import C_coboundary as CB

    alg = CB.Schema1(n)
    cartan = ["H_eps"] + [f"H_{k}" for k in range(1, n + 1)]
    weights = {}
    for Z in alg.labels:
        w = []
        for H in cartan:
            br = alg.bracket(H, Z)
            # Cartan elements act diagonally: [H, Z] = c Z.
            assert set(br) <= {Z}, (H, Z, br)
            w.append(br.get(Z, 0))
        weights[Z] = tuple(w)
    return weights


def weight_obstruction(n):
    """For each gb_k: its torus weight, and the coboundaries of that weight.

    gamma_k (gb_k alone) has weight w_k = -wt(E_{sigma,j,s}). A coboundary delta f_ij
    has weight wt(Z_i) - wt(Z_j). If no nonzero delta f_ij has weight w_k, then gamma_k
    is not a coboundary, and this is an elementary proof of nontriviality.
    """
    import C_coboundary as CB

    wts = torus_weights(n)
    gb, _ = load_gamma(n)
    phis, D = load_coboundary(n)
    alg, params = CB.coboundary_basis(n)
    nonzero_cols = {k for (_, _, _, k) in D}
    report = {}
    for s in gb:
        # gb symbol gb_a_1_{x}__b_{j}_{y} pairs with odd label E_eps1_del{j}_{x}{y}.
        name = str(s)[len("gb_a_1_"):]  # e.g. "p__b_1_m"
        sig, rest = name.split("__")
        _, j, sign_s = rest.split("_")
        E = f"E_eps1_del{j}_{sig}{sign_s}"
        wk = tuple(-x for x in wts[E])
        matching = [
            k for k, (i, jj) in enumerate(params)
            if tuple(a - b for a, b in zip(wts[i], wts[jj])) == wk and k in nonzero_cols
        ]
        report[str(s)] = {
            "weight": [str(x) for x in wk],
            "nonzero_coboundaries_of_weight": len(matching),
        }
    return report


def summary(n):
    out = {"n": n, "variants": {}, "weight_obstruction": weight_obstruction(n)}
    for include_K in (True, False):
        gb, T, C = trivial_subspace(n, include_K=include_K)
        key = "K_included" if include_K else "K_dropped"
        out["variants"][key] = {
            "gb_symbols": [str(s) for s in gb],
            "trivial_subspace_dimension": T.rows,
            "conditions_on_gb": [[str(x) for x in C.row(i)] for i in range(C.rows)],
        }
    return out


def main(argv):
    ns = [int(a) for a in argv] or [1, 2, 3]
    for n in ns:
        doc = summary(n)
        for key, v in doc["variants"].items():
            print(f"n={n} ({key}): gb dimension={len(v['gb_symbols'])}, "
                  f"trivial subspace dim={v['trivial_subspace_dimension']}, "
                  f"independent conditions={len(v['conditions_on_gb'])}")
        if argv == []:
            path = DATA / f"C_{n}_triviality.json"
            path.write_text(json.dumps(doc, indent=2) + "\n")
            print(f"wrote {path.name}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))
