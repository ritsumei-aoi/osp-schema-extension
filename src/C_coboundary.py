"""Schema 4 for C(n+1): coboundary (delta f)(X,Y) of an odd linear map f.

    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])

f maps basis elements to elements of g (optionally g + C K, K the even central scalar),
reversing parity.  Brackets are the Schema 1 structure constants; K is central, so
[X, K] = 0 and f(K) is never needed (K is not an argument).
"""
import json
import os
from fractions import Fraction

import numpy as np

import C_generators as G
import C_gamma as CG

DATA_DIR = G.DATA_DIR


def load_bracket(n):
    """{(X,Y): {Z: Fraction}} from data/C_{n}_structure.json."""
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as f:
        d = json.load(f)
    br = {}
    for e in d["structure_constants"]:
        br.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return br


def bracket_lin(br, u, v):
    out = {}
    for x, cx in u.items():
        for y, cy in v.items():
            for z, c in br.get((x, y), {}).items():
                out[z] = out.get(z, 0) + cx * cy * c
    return {k: c for k, c in out.items() if c != 0}


def apply_f(f, u):
    """f: {X: {Z: coeff}} extended linearly to a vector u (K has no image)."""
    out = {}
    for x, cx in u.items():
        for z, c in f.get(x, {}).items():
            out[z] = out.get(z, 0) + cx * c
    return {k: c for k, c in out.items() if c != 0}


def delta_f(n, f, br=None):
    """Coboundary table {(X,Y): {Z: Fraction}} over all ordered basis pairs."""
    br = br or load_bracket(n)
    names = G.basis_names(n)
    out = {}
    for X in names:
        x = G.parity_of(X)
        for Y in names:
            y = G.parity_of(Y)
            t = {}
            for z, c in bracket_lin(br, {X: 1}, f.get(Y, {})).items():
                t[z] = t.get(z, 0) + (-1) ** x * c
            for z, c in bracket_lin(br, {Y: 1}, f.get(X, {})).items():
                t[z] = t.get(z, 0) - (-1) ** ((x + 1) * y) * c
            for z, c in apply_f(f, br.get((X, Y), {})).items():
                t[z] = t.get(z, 0) - c
            t = {k: c for k, c in t.items() if c != 0}
            if t:
                out[(X, Y)] = t
    return out


def f_is_odd(f):
    return all(G.parity_of(z) == (G.parity_of(x) + 1) % 2
               for x, zs in f.items() for z in zs)


# ------------------------------------------------------ linear algebra ----
def phi_slots(n, allow_K):
    """Free coefficients phi[(X, Z)] of an odd f: parity(Z) = parity(X) + 1 (K even)."""
    names = G.basis_names(n)
    targets = names + (["K"] if allow_K else [])
    return [(X, Z) for X in names for Z in targets
            if G.parity_of(Z) == (G.parity_of(X) + 1) % 2]


def coboundary_matrix(n, allow_K):
    """Dense matrix of phi -> delta f; rows indexed by (X,Y,Z)."""
    br = load_bracket(n)
    slots = phi_slots(n, allow_K)
    rows = {}
    cols = []
    entries = []
    for j, (A, B) in enumerate(slots):
        f = {A: {B: Fraction(1)}}
        for (X, Y), zs in delta_f(n, f, br).items():
            for Z, c in zs.items():
                r = rows.setdefault((X, Y, Z), len(rows))
                entries.append((r, j, float(c)))
        cols.append((A, B))
    return slots, rows, entries


def gamma_matrix(n, rows):
    """gamma per gb parameter as columns over the same row index (extends rows if needed)."""
    sym = CG.symbolic_gamma(n)
    keys = CG.gb_keys(n)
    kidx = {k: i for i, k in enumerate(keys)}
    entries = []
    for (X, Y, Z), cs in sym.items():
        r = rows.setdefault((X, Y, Z), len(rows))
        for k, c in cs.items():
            entries.append((r, kidx[k], float(c)))
    return keys, entries


def trivial_subspace(n, allow_K, tol=1e-9):
    """Dimension data of {gb : gamma(gb) in im(delta)} and a basis of it (numerical)."""
    slots, rows, ent_d = coboundary_matrix(n, allow_K)
    keys, ent_g = gamma_matrix(n, rows)
    R = len(rows)
    D = np.zeros((R, len(slots)))
    for r, j, v in ent_d:
        D[r, j] += v
    Gm = np.zeros((R, len(keys)))
    for r, j, v in ent_g:
        Gm[r, j] += v
    # nullspace of [D | -Gm]
    M = np.hstack([D, -Gm])
    u, s, vt = np.linalg.svd(M, full_matrices=True)
    rank = int((s > tol * max(1.0, s[0])).sum())
    null = vt[rank:].T
    gb_part = null[len(slots):, :]
    # dimension of projection onto gb coordinates
    sv = np.linalg.svd(gb_part, compute_uv=False) if gb_part.size else np.array([])
    dim_triv = int((sv > 1e-8).sum())
    rank_D = int((np.linalg.svd(D, compute_uv=False) > tol).sum())
    return {"n": n, "allow_K": allow_K, "num_phi": len(slots), "rank_delta": rank_D,
            "trivial_gb_dim": dim_triv, "num_gb": len(keys)}, keys, gb_part, slots, null


# ------------------------------------------- explicit f from a -> a + kappa c ----
def redefinition_c(n, gb):
    """c^sigma = sum_j gb[sigma,j,m] b_j^+ - gb[sigma,j,p] b_j^-  (as {word: coeff}),
    chosen so that [b_j^s, a^sigma + kappa c^sigma] = 0, i.e. the deformed relation is removed."""
    c = {}
    for sg in "pm":
        poly = {}
        for j in range(1, n + 1):
            poly[(f"b_{j}_p",)] = Fraction(gb.get((sg, j, "m"), 0))
            poly[(f"b_{j}_m",)] = -Fraction(gb.get((sg, j, "p"), 0))
        c[f"a_1_{sg}"] = {w: v for w, v in poly.items() if v != 0}
    return c


def f_from_redefinition(n, gb, ex=None):
    """f(X) = kappa-part of X(a -> a + kappa c), kappa moved to the left.  Values in g + C K."""
    ex = ex or G.BasisExpander(n, with_K=True)
    osc = G.Oscillators()
    c = redefinition_c(n, gb)
    f = {}
    for X in G.basis_names(n):
        total = {}
        for w, coef in ex.real[X].items():
            for i, letter in enumerate(w):
                if letter not in c:
                    continue
                # kappa c is inserted in place of the letter; the engine moves kappa left
                for cw, cc in c[letter].items():
                    word = w[:i] + ("K",) + cw + w[i + 1:]
                    for rw, rc in osc.reduce_word(word).items():
                        total[rw] = total.get(rw, 0) + coef * cc * rc
        total = dict((w, v) for w, v in total.items() if v != 0)
        if any(not w or w[0] != "K" for w in total):
            raise ValueError("unexpected non-kappa word")
        img = ex.expand(dict((w[1:], v) for w, v in total.items())) if total else {}
        if img:
            f[X] = img
    return f


def trivializing_map(n, gb, ex=None):
    """f_gb with  delta f_gb = gamma(gb)  exactly (values in g + C K).

    Derivation: X' = X + kappa f_red(X) satisfies the undeformed relations, so
    [X',Y'}_gamma-algebra = sum c Z' gives  gamma = -delta f_red;  hence f_gb = -f_red."""
    f = f_from_redefinition(n, gb, ex)
    return dict((X, dict((Z, -c) for Z, c in zs.items())) for X, zs in f.items())


def drop_K(f):
    """Strict variant f: g -> g (the K-components removed)."""
    out = {}
    for x, zs in f.items():
        z2 = dict((z, c) for z, c in zs.items() if z != "K")
        if z2:
            out[x] = z2
    return out


def ad_map(n, Z0, br=None):
    """f(X) = [Z0, X] for odd Z0: an odd derivation, so delta f = 0 (used as a sign check)."""
    br = br or load_bracket(n)
    return dict((X, br[(Z0, X)]) for X in G.basis_names(n) if (Z0, X) in br)


def build_schema4(n, profile, strict=False, today="2026-10-06"):
    import C_evaluate as E
    gb = E.profile_values(n, profile)
    f = trivializing_map(n, gb)
    if strict:
        f = drop_K(f)
    if not f_is_odd(f):
        raise ValueError("f is not odd")
    df = delta_f(n, f)
    names = G.basis_names(n)
    fmap = [{"from": X, "to": Z, "coeff": G.frac_str(c)}
            for X in names for Z, c in sorted(f.get(X, {}).items())]
    entries = [{"X": X, "Y": Y, "Z": Z, "coeff": G.frac_str(df[(X, Y)][Z]),
                "sign_rule": "graded"}
               for X in names for Y in names for Z in names + ["K"]
               if (X, Y) in df and Z in df[(X, Y)]]
    return {
        "schema_version": "5.0",
        "layer": "coboundary",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})"},
        "source_structure": f"C_{n}_structure.json",
        "gb_assignment": {"profile": profile,
                          "values": dict((CG.gb_name(k), G.frac_str(Fraction(v)))
                                         for k, v in gb.items())},
        "coboundary": {
            "formula": "(df)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            "odd_linear_map": {
                "description": "f(Z_j) = sum_i phi_ij Z_i, parity-reversing; K = even central scalar",
                "codomain": "g" if strict else "g + CK",
                "origin": ("trivializing map f_gb (delta f_gb = gamma(gb)) from a -> a + kappa c"
                           + ("; K-components dropped (strict f: g -> g)" if strict else "")),
                "phi": fmap,
            },
            "delta_f": entries,
            "nonzero_count": len(entries),
            "K_component_count": sum(1 for e in entries if e["Z"] == "K"),
        },
        "metadata": {"generated_by": "src/C_coboundary.py", "generation_date": today,
                     "note": "delta f is computed from Schema 1 brackets only (independent of Schema 2/3)"},
    }


def main(ns=(1, 2, 3)):
    import C_evaluate as E
    for n in ns:
        for profile in E.PROFILES:
            variants = [False] + ([True] if profile == "all_plus" else [])
            for strict in variants:
                d = build_schema4(n, profile, strict)
                suffix = ("" if profile == "all_plus" else f"_{profile}") + \
                    ("_strictg" if strict else "")
                path = os.path.join(DATA_DIR, f"C_{n}_coboundary{suffix}.json")
                with open(path, "w") as fh:
                    json.dump(d, fh, indent=1)
                cb = d["coboundary"]
                print(os.path.basename(path), len(cb["odd_linear_map"]["phi"]), "phi,",
                      cb["nonzero_count"], "delta_f entries")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "dims":
        for n in (1, 2, 3):
            for allow_K in (False, True):
                info, *_ = trivial_subspace(n, allow_K)
                print(info)
    else:
        main()
