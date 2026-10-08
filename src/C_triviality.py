"""I08: exact triviality analysis for the C(n+1) inhomogeneous deformation.

Question: for which gb is gamma(gb) in the image of delta (coboundaries)?

gamma(gb) = sum_g gb_g * Gamma_g  (Schema 2, linear in gb)
delta(phi) = sum_p phi_p * D_p   (Schema 4, linear in phi)

Augmented system, one row per component (X,Y,Z):
    [ D | Gamma ] (params | gb).
Gaussian elimination on the param columns. Rows left with no param part give
linear conditions L_k(gb) = 0; gamma(gb) is a coboundary iff all L_k(gb) = 0.

Provenance: each reduced row keeps the set of (X,Y,Z) rows it was built from,
so each obstruction can be traced to generator pairs (an upper bound on the
true support, since rows can cancel).

Usage: python src/C_triviality.py N [N ...]  -> data/C_{N}_triviality.json
"""
from fractions import Fraction
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import gb_keys, gb_name  # noqa: E402


def load(n):
    gam = json.load(open(os.path.join(ROOT, "data", f"C_{n}_gamma.json")))
    cob = json.load(open(os.path.join(ROOT, "data", f"C_{n}_coboundary.json")))
    rows = {}
    for e in cob["coboundary"]["terms"]:
        key = (e["X"], e["Y"], e["Z"])
        rows.setdefault(key, {"D": {}, "G": {}})["D"] = {p: Fraction(c) for p, c in e["phi"].items()}
    for e in gam["inhomogeneous_deformation"]["gamma"]:
        key = (e["X"], e["Y"], e["Z"])
        rows.setdefault(key, {"D": {}, "G": {}})["G"] = {g: Fraction(c) for g, c in e["terms"].items()}
    return rows


def _subtract(row, coef, pivot_row):
    """row -= coef * pivot_row, for (param dict, gb dict) pairs."""
    for part, src in ((0, pivot_row[0]), (1, pivot_row[1])):
        dst = row[part]
        for c, v in src.items():
            nv = dst.get(c, Fraction(0)) - coef * v
            if nv == 0:
                dst.pop(c, None)
            else:
                dst[c] = nv


def eliminate(rows):
    """Return (rank of D, list of obstructions as (gb-form dict, support set)).

    Invariant (full reduction): no pivot row contains another pivot column, so
    reducing a new row by each of its pivot columns once is enough.
    """
    pivots = {}  # param name -> [param dict, gb dict, support set]; pivot coeff = 1
    obstructions = []
    for key, r in rows.items():
        row = [dict(r["D"]), dict(r["G"])]
        supp = {key}
        for c in [c for c in row[0] if c in pivots]:
            if c in row[0]:
                coef = row[0][c]
                _subtract(row, coef, pivots[c])
                supp = supp | pivots[c][2]
        if not row[0]:
            if row[1]:
                obstructions.append((row[1], supp))
            continue
        piv = min(row[0])
        lead = row[0][piv]
        row = [{c: v / lead for c, v in row[0].items()}, {c: v / lead for c, v in row[1].items()}]
        # back-substitute the new pivot column into existing pivot rows
        for other in pivots.values():
            if piv in other[0]:
                _subtract(other, other[0][piv], row + [supp])
        pivots[piv] = row + [supp]
    return len(pivots), obstructions


def reduce_forms(forms, names):
    """Row-reduce the gb-forms; return an independent basis (as dicts)."""
    basis = []
    for form, _ in forms:
        f = dict(form)
        for b in basis:
            piv = b[0]
            if piv in f:
                c = f[piv]
                for k, v in b[1].items():
                    nv = f.get(k, Fraction(0)) - c * v
                    if nv == 0:
                        f.pop(k, None)
                    else:
                        f[k] = nv
        if f:
            piv = min(f, key=lambda k: names.index(k))
            lead = f[piv]
            basis.append((piv, {k: v / lead for k, v in f.items()}))
    return [b[1] for b in basis]


def add_K_image(rows, n):
    """Extended variant: allow f(Z_j) = psi_j * K for odd Z_j (K even, central).

    Then delta f(X,Y)^K = -(coefficient of Z_j in [X,Y]_0) for each such psi_j,
    since [X, K] = 0. Rows (X,Y,K) receive these new parameters.
    """
    base = json.load(open(os.path.join(ROOT, "data", f"C_{n}_structure.json")))
    parity = base["parity"]
    for e in base["structure_constants"]["brackets"]:
        if parity[e["Z"]] == 1:
            key = (e["X"], e["Y"], "K")
            row = rows.setdefault(key, {"D": {}, "G": {}})
            row["D"]["psiK_" + e["Z"]] = -Fraction(e["coeff"])
    return rows


def analyse(n, drop_K=False, allow_K_image=False):
    rows = load(n)
    if drop_K:
        rows = {k: v for k, v in rows.items() if k[2] != "K"}
    if allow_K_image:
        rows = add_K_image(rows, n)
    names = [gb_name(k) for k in gb_keys(n)]
    rank, obs = eliminate(rows)
    basis = reduce_forms(obs, names)
    # rows with a gb part but no param part (immediate obstructions) are included in obs
    supports = {}
    for form, supp in obs:
        for k in form:
            supports.setdefault(k, set()).update(supp)
    return rows, rank, basis, obs, names, supports


def profile_trivial(basis, values):
    return all(sum(c * values[k] for k, c in f.items()) == 0 for f in basis)


def main(argv):
    for arg in argv:
        n = int(arg)
        rows, rank, basis, obs, names, supports = analyse(n)
        profiles = {
            "all_plus": {nm: Fraction(1) for nm in names},
            "alt": {nm: Fraction(1 if i % 2 == 0 else -1) for i, nm in enumerate(names)},
        }
        out = {
            "n": n,
            "rows_total": len(rows),
            "rank_D": rank,
            "gb_count": len(names),
            "independent_obstructions": len(basis),
            "trivial_locus_dimension": len(names) - len(basis),
            "obstruction_forms": [{k: str(v) for k, v in f.items()} for f in basis],
            "profile_trivial": {p: profile_trivial(basis, v) for p, v in profiles.items()},
        }
        rows_nk, rank_nk, basis_nk, _, _, _ = analyse(n, drop_K=True)
        out["without_K_rows"] = {
            "rank_D": rank_nk,
            "independent_obstructions": len(basis_nk),
            "trivial_locus_dimension": len(names) - len(basis_nk),
            "obstruction_forms": [{k: str(v) for k, v in f.items()} for f in basis_nk],
            "profile_trivial": {p: profile_trivial(basis_nk, v) for p, v in profiles.items()},
        }
        _, rank_ext, basis_ext, _, _, _ = analyse(n, allow_K_image=True)
        out["extended_K_image"] = {
            "definition": "f(Z_j) = psi_j K allowed for odd Z_j (variant, not the strict definition)",
            "rank_D": rank_ext,
            "independent_obstructions": len(basis_ext),
            "trivial_locus_dimension": len(names) - len(basis_ext),
            "obstruction_forms": [{k: str(v) for k, v in f.items()} for f in basis_ext],
            "profile_trivial": {p: profile_trivial(basis_ext, v) for p, v in profiles.items()},
        }
        path = os.path.join(ROOT, "data", f"C_{n}_triviality.json")
        with open(path, "w") as fh:
            json.dump(out, fh, indent=2)
        print(f"n={n}: rank(D)={rank} independent gb-obstructions={len(basis)} "
              f"trivial-locus dim={out['trivial_locus_dimension']} / {len(names)} "
              f"profiles trivial={out['profile_trivial']} | without K rows: "
              f"obstructions={len(basis_nk)} trivial-locus dim={out['without_K_rows']['trivial_locus_dimension']} "
              f"profiles={out['without_K_rows']['profile_trivial']} | with K-image variant: "
              f"obstructions={len(basis_ext)} trivial-locus dim={out['extended_K_image']['trivial_locus_dimension']} "
              f"profiles={out['extended_K_image']['profile_trivial']} -> {path}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["1", "2", "3"])
