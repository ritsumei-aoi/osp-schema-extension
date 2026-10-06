"""I08: triviality search for the inhomogeneous deformation of C(n+1) = osp(2|2n).

Compares Layer 3 (evaluated gamma) with Layer 4 (coboundary data), then solves the linear problem
"for which gb is gamma(gb) in the image of delta restricted to a class of odd maps f?" exactly.

usage: python src/triviality_search.py
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
import coboundary as cb  # noqa: E402
from gamma import DeformedC, param_keys, param_name  # noqa: E402
from oscalg import make_decomposer  # noqa: E402


def load(n):
    ev = json.load(open(os.path.join(cb.DATA, f"C_{n}_evaluated.json")))
    co = json.load(open(os.path.join(cb.DATA, f"C_{n}_coboundary.json")))
    return ev, co


def compare_layers(n):
    """Layer 3 vs Layer 4, profile by profile."""
    ev, co = load(n)
    rows = []
    for p3, p4 in zip(ev["profiles"], co["profiles"]):
        assert p3["name"] == p4["name"]
        g = cb.triple_dict(p3["gamma_evaluated"])
        d = cb.triple_dict(p4["delta_f"])
        bad = sorted(set(g) ^ set(d) | {k for k in set(g) & set(d) if g[k] != d[k]})
        rows.append((p3["name"], len(g), len(d), len(bad), p4["trivial"], len(p4["f"])))
    return rows


def nullspace(vectors):
    """Relations sum_i t_i v_i = 0 among sparse vectors (list of dicts); returns list of {index: coeff}."""
    reduced, rel = [], []
    for idx, v in enumerate(vectors):
        v = dict(v)
        t = {idx: Fraction(1)}
        for piv, rv, rt in reduced:
            c = v.get(piv, 0)
            if c:
                cb._add(v, rv, -c)
                cb._add(t, rt, -c)
        if not v:
            rel.append(t)
            continue
        piv = min(v)
        c = v[piv]
        reduced.append((piv, {k: x / c for k, x in v.items()}, {k: x / c for k, x in t.items()}))
    return rel


def trivial_subspace(n, allowed):
    """Subspace T of gb-space (dimension 4n) with gamma(gb) in delta(span of allowed elementary maps).

    allowed(to, frm, L) -> bool selects the class of odd maps f.  Returns (T basis as dicts param->coeff, rank info).
    """
    L = cb.Layer1(n)
    maps = [m for m in L.odd_map_basis() if allowed(m[0], m[1], L)]
    elem = [cb.delta_elementary(L, *m) for m in maps]
    decomp = make_decomposer(elem, skip_dependent=True)
    keys = param_keys(n)
    names = [param_name(k) for k in keys]
    ev = json.load(open(os.path.join(cb.DATA, f"C_{n}_gamma.json")))
    gam = {nm: {} for nm in names}
    for e in ev["inhomogeneous_deformation"]["gamma_structure"]:
        for t in e["gamma"]:
            gam[t["param"]][(e["X"], e["Y"], e["Z"])] = Fraction(t["coeff"])
    resid = []
    for nm in names:
        _, r = decomp(gam[nm])
        resid.append(r)
    rel = nullspace(resid)
    T = [{names[i]: str(c) for i, c in r.items()} for r in rel]
    return T, len(maps), len(names)


CLASSES = {
    "all odd maps f": lambda to, frm, L: True,
    "f vanishing on even generators (odd -> even only)": lambda to, frm, L: L.par[frm] == 1,
    "f vanishing on odd generators (even -> odd only)": lambda to, frm, L: L.par[frm] == 0,
    "f vanishing on Cartan generators": lambda to, frm, L: not frm.startswith("H_"),
    "f vanishing on E_2del / E_del_del (long and short even roots)": lambda to, frm, L: not frm.startswith(("E_2del", "E_del")),
}


def central_residual(n, key):
    """Un-symmetrised realization (odd generator = normal-ordered a b): kappa*K coefficient per pair."""
    alg = DeformedC(n, {key: 1}, symmetrize=False)
    base = DeformedC(n, {key: 1})
    cen, gdiff = {}, 0
    for X in alg.labels:
        for Y in alg.labels:
            g0, gam = alg.bracket(X, Y)
            c = alg.last_central
            if c:
                cen[(X, Y)] = c
            _, gam_s = base.bracket(X, Y)
            gdiff += gam != gam_s
    return cen, gdiff


def main():
    for n in (1, 2, 3):
        print(f"=== n={n} (C({n + 1}) = osp(2|{2 * n}))")
        for r in compare_layers(n):
            if r[0].startswith(("all_", "alternating", "unit_gb_a_1_p_b_1_p")) or r[0] == "sign_+--+":
                print("  L3 vs L4:", r)
        rows = compare_layers(n)
        print(f"  profiles={len(rows)}; all coincide: {all(r[3] == 0 for r in rows)}; all trivial: {all(r[4] for r in rows)}")
        for name, cls in CLASSES.items():
            T, nm, npar = trivial_subspace(n, cls)
            print(f"  [{name}] #maps={nm}: dim T = {len(T)} of {npar}")
            if 0 < len(T) < npar:
                for t in T:
                    print("     relation basis:", t)
        L = cb.Layer1(n)
        maps = L.odd_map_basis()
        dec = make_decomposer([cb.delta_elementary(L, *m) for m in maps], skip_dependent=True)
        print(f"  odd maps: {len(maps)}; rank of delta = {dec.rank}; dim ker(delta) = {len(maps) - dec.rank}")
    for n in (1, 2):
        print(f"--- un-symmetrised realization, n={n}")
        for key in param_keys(n):
            cen, gdiff = central_residual(n, key)
            print(f"  {param_name(key)}: pairs with kappa*K term = {len(cen)}; gamma(g-part) differs from symmetrised in {gdiff} pairs")


if __name__ == "__main__":
    main()
