"""Triviality search for the inhomogeneous deformation of C(n+1) (Issue I08).

Part A: case-by-case comparison of Layer 3 (evaluated gamma) with Layer 4 (delta f_c at the matching c).
Part B: linear-algebra search: the set of gb for which gamma(gb) = delta f for SOME odd linear map f
        (variants: strict / gonly / const), with an exact rank certificate for the K-component.
Usage: python src/triviality_search.py
"""
import json
import os
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_triviality import System, solve_gb_subspace  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
PROFILES = ["all_plus", "zero", "alternating", "fermion_sign", "boson_sign", "single_first"]


def jload(name):
    return json.load(open(os.path.join(DATA, name)))


def eval_name(n, prof):
    return f"C_{n}_evaluated.json" if prof == "all_plus" else f"C_{n}_evaluated_{prof}.json"


def layer3(n, prof):
    d = jload(eval_name(n, prof))
    g = {}
    for e in d["evaluated_structure"]["entries"]:
        v = Fraction(e["kappa_coeff"])
        if v:
            g[(e["X"], e["Y"], e["Z"])] = v
    return {k: Fraction(v) for k, v in d["gb_assignment"]["values"].items()}, g


def layer4_at(n, gbvals):
    """delta f_c with c determined from gb through the stored correspondence (c = M^{-1} gb)."""
    d = jload(f"C_{n}_coboundary.json")
    cval = {}
    for cname, mp in d["gb_correspondence"]["map"].items():
        (g, sgn), = mp.items()
        cval[cname] = Fraction(sgn) * gbvals[g]  # M is +-permutation: c_q = sgn * gb_{p(q)}
    out = {}
    for e in d["coboundary_structure"]["entries"]:
        v = sum(Fraction(x) * cval[c] for c, x in e["coeff"].items())
        if v:
            out[(e["X"], e["Y"], e["Z"])] = v
    return cval, out


def compare(n, prof):
    gbv, l3 = layer3(n, prof)
    cval, l4 = layer4_at(n, gbv)
    l3g = {k: v for k, v in l3.items() if k[2] != "K"}
    l4g = {k: v for k, v in l4.items() if k[2] != "K"}
    l3K = {k: v for k, v in l3.items() if k[2] == "K"}
    l4K = {k: v for k, v in l4.items() if k[2] == "K"}
    # strict reading: f maps into g only  => delta f has no K part
    return {
        "n": n, "profile": prof,
        "full_coincide": l3 == l4,
        "g_part_coincide": l3g == l4g,
        "n_g_entries": len(l3g),
        "n_K_entries_layer3": len(l3K),
        "n_K_entries_layer4_strict": 0,
        "K_pairs": sorted({(k[0], k[1]) for k in l3K}),
        "K_values": l3K,
        "nonzero_gb": sum(1 for v in gbv.values() if v),
    }


def exact_rank(rows):
    """Exact rank of a list of Fraction rows (sparse dict rows allowed)."""
    rows = [dict(r) for r in rows if r]
    rank = 0
    pivots = {}
    for r in rows:
        r = dict(r)
        while r:
            k = min(r)
            if k in pivots:
                pr = pivots[k]
                f = r[k] / pr[k]
                for kk, vv in pr.items():
                    nv = r.get(kk, 0) - f * vv
                    if nv:
                        r[kk] = nv
                    else:
                        r.pop(kk, None)
            else:
                pivots[k] = r
                rank += 1
                break
    return rank


def K_functional_rank(n):
    """Rank of gb -> gamma_K(gb) (as a map into functions of (X,Y)): 4n  <=>  gamma_K(gb)=0 only for gb=0."""
    d = jload(f"C_{n}_gamma.json")
    params = d["inhomogeneous_deformation"]["parameters"]
    pi = {p: i for i, p in enumerate(params)}
    cols = {p: {} for p in params}
    for e in d["inhomogeneous_deformation"]["gamma_structure"]:
        if e["Z"] == "K":
            for p, c in e["coeff"].items():
                cols[p][(e["X"], e["Y"])] = Fraction(c)
    rows = {}
    for p, col in cols.items():
        for xy, v in col.items():
            rows.setdefault(xy, {})[pi[p]] = v
    return exact_rank(list(rows.values())), len(params)


def main():
    print("=== Part A: Layer 3 vs Layer 4 (c matched to gb) ===")
    for n in (1, 2, 3):
        for prof in PROFILES:
            r = compare(n, prof)
            print(f"n={n} {prof:13s} nonzero_gb={r['nonzero_gb']:2d} full_coincide={r['full_coincide']} "
                  f"g_part_coincide={r['g_part_coincide']} g-entries={r['n_g_entries']} "
                  f"K-entries(L3)={r['n_K_entries_layer3']}  K-entries(L4,f:g->g)=0")
    print("\n=== Part B: dimension of {gb : gamma(gb) = delta f for some odd f} ===")
    for n in (1, 2, 3):
        S = System(n)
        row = []
        for variant in ("strict", "gonly", "const"):
            B, null = solve_gb_subspace(S, variant)
            row.append(f"{variant}={B.shape[1]}/{len(S.params)}")
        rk, P = K_functional_rank(n)
        print(f"n={n}: " + "  ".join(row) + f"   exact rank of gb->gamma_K: {rk}/{P}")
    print("\n=== K-discrepancy details for n=1, all_plus ===")
    r = compare(1, "all_plus")
    for (X, Y) in r["K_pairs"]:
        print(f"  gamma_K({X}, {Y}) = {r['K_values'][(X, Y, 'K')]}")


if __name__ == "__main__":
    main()
