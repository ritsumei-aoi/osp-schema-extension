"""I08: triviality analysis for the inhomogeneous deformation of C(n+1).

(1) Compare Layer 3 (evaluated gamma) with Layer 4 (delta f) file by file.
(2) Locate the discrepancies of the strict variant f: g -> g.
(3) Solve for the set of gb with gamma(gb) in im(delta) (SVD, both codomains of f).
(4) Exact check of the closed form of the trivializing map.
Run:  python3 src/C_triviality.py
"""
import json
import os
from fractions import Fraction

import sympy

import C_coboundary as B
import C_evaluate as E
import C_gamma as CG
import C_generators as G

D = G.DATA_DIR


def _load(name):
    with open(os.path.join(D, name)) as f:
        return json.load(f)


def table(entries):
    return dict(((e["X"], e["Y"], e["Z"]), Fraction(e["coeff"])) for e in entries)


def compare(n, profile, strict=False):
    """Compare Layer 3 gamma with Layer 4 delta f; returns summary dict."""
    s3 = "" if profile == "all_plus" else f"_{profile}"
    s4 = s3 + ("_strictg" if strict else "")
    l3 = table(_load(f"C_{n}_evaluated{s3}.json")["evaluated_deformation"]["gamma"])
    l4 = table(_load(f"C_{n}_coboundary{s4}.json")["coboundary"]["delta_f"])
    only3 = sorted(k for k in l3 if k not in l4)
    only4 = sorted(k for k in l4 if k not in l3)
    diff = sorted(k for k in l3 if k in l4 and l3[k] != l4[k])
    return {"n": n, "profile": profile, "strict": strict, "coincide": l3 == l4,
            "n3": len(l3), "n4": len(l4), "only_L3": only3, "only_L4": only4, "differ": diff,
            "l3": l3, "l4": l4}


def K_obstruction(n):
    """Rank of the linear map gb -> (K-component of gamma); exact."""
    sym = CG.symbolic_gamma(n)
    keys = CG.gb_keys(n)
    kidx = dict((k, i) for i, k in enumerate(keys))
    rows = {}
    for (X, Y, Z), cs in sym.items():
        if Z != "K":
            continue
        r = rows.setdefault((X, Y), [0] * len(keys))
        for k, c in cs.items():
            r[kidx[k]] = sympy.Rational(c.numerator, c.denominator)
    M = sympy.Matrix(list(rows.values()))
    # witness pairs: rows with a single nonzero entry
    wit = {}
    for (X, Y), r in rows.items():
        nz = [i for i, v in enumerate(r) if v != 0]
        if len(nz) == 1 and keys[nz[0]] not in wit:
            wit[keys[nz[0]]] = (X, Y, r[nz[0]])
    return M.rank(), len(keys), len(rows), wit


def closed_form_f(n, gb):
    """f_gb in closed form:  f(a^s b_k^t) = -c^s b_k^t ,  f(H_1) = a^+ c^- - c^+ a^- ,
    f = 0 on all bosonic generators (E_2del, E_del_del, H_2..H_{n+1})."""
    ex = G.BasisExpander(n, with_K=True)
    osc = G.Oscillators()
    c = B.redefinition_c(n, gb)
    f = {}

    def put(X, poly):
        poly = dict((w, v) for w, v in poly.items() if v != 0)
        if poly:
            f[X] = ex.expand(poly)

    for X in G.odd_names(n):
        sg = X.split("_")[3][0]
        word = ex.real[X]
        (w0, _), = word.items()
        poly = {}
        for cw, cc in c[f"a_1_{sg}"].items():
            for rw, rc in osc.reduce_word(cw + (w0[1],)).items():
                poly[rw] = poly.get(rw, 0) - cc * rc
        put(X, poly)
    poly = {}
    # a^+ c^- - c^+ a^-  (normal ordered with the undeformed engine)
    for cw, cc in c["a_1_m"].items():
        for rw, rc in osc.reduce_word(("a_1_p",) + cw).items():
            poly[rw] = poly.get(rw, 0) + cc * rc
    for cw, cc in c["a_1_p"].items():
        for rw, rc in osc.reduce_word(cw + ("a_1_m",)).items():
            poly[rw] = poly.get(rw, 0) - cc * rc
    put("H_1", poly)
    return f


def main():
    print("=== (1) Layer 3 vs Layer 4: coincidence table (extended f: g -> g + CK) ===")
    for n in (1, 2, 3):
        row = []
        for p in E.PROFILES:
            r = compare(n, p)
            row.append(f"{p}:{'=' if r['coincide'] else '!='}({r['n3']})")
        print(f"n={n}: " + "  ".join(row))
    print("\n=== (2) strict f: g -> g, profile all_plus ===")
    for n in (1, 2, 3):
        r = compare(n, "all_plus", strict=True)
        zs = set(k[2] for k in r["only_L3"])
        print(f"n={n}: coincide={r['coincide']} L3={r['n3']} L4={r['n4']} "
              f"only_in_L3={len(r['only_L3'])} (targets {sorted(zs)}) "
              f"only_in_L4={len(r['only_L4'])} differ={len(r['differ'])}")
    n = 1
    r = compare(n, "all_plus", strict=True)
    print("n=1 sample discrepancies (X, Y, Z): gamma coeff, strict-delta coeff")
    for k in r["only_L3"][:6]:
        print("   ", k, r["l3"][k], "vs", r["l4"].get(k, 0))
    print("\n=== K-component obstruction (exact rank of gb -> gamma^K) ===")
    for n in (1, 2, 3):
        rank, npar, npairs, wit = K_obstruction(n)
        print(f"n={n}: rank={rank} of {npar} parameters, {npairs} generator pairs carry K; "
              f"witnesses for {len(wit)} params")
        if n == 1:
            for k, (X, Y, v) in sorted(wit.items()):
                print(f"    {CG.gb_name(k)}: gamma({X},{Y})^K = {v} * gb")
    print("\n=== (3) trivial gb-subspace dimension {gb: gamma(gb) in im delta} ===")
    for n in (1, 2, 3):
        a, *_ = B.trivial_subspace(n, False)
        b, *_ = B.trivial_subspace(n, True)
        c, *_ = B.trivial_subspace(n, False, gamma_K=False)
        print(f"n={n}: #gb={a['num_gb']}  strict f:g->g -> {a['trivial_gb_dim']}  "
              f"f:g->g+CK -> {b['trivial_gb_dim']}  strict f vs g-part of gamma -> "
              f"{c['trivial_gb_dim']}   odd derivations = #phi - rank = "
              f"{b['num_phi'] - b['rank_delta']} (odd generators: {4 * n})")
    print("\n=== (4) closed form of f_gb (random integer gb) ===")
    import random
    for n in (1, 2, 3):
        ok = True
        for seed in range(5):
            rnd = random.Random(seed)
            gb = dict((k, rnd.randint(-3, 3)) for k in CG.gb_keys(n))
            f = closed_form_f(n, gb)
            _, gam = CG.gamma_table(n, gb)
            ok &= (B.delta_f(n, f) == gam)
        print(f"n={n}: delta(closed form f) == gamma for 5 random gb: {ok}")


if __name__ == "__main__":
    main()
