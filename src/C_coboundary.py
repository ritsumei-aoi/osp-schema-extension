"""Schema 4 (coboundary structure) for C(n+1).

Odd linear map  f(Z_j) = sum_i phi[Z_i|Z_j] Z_i  with p(Z_i) != p(Z_j)
(optionally also phi[K|Z_j] for odd Z_j: component along the central K = 1).

Coboundary (docs/math/C_coboundary_definition.md):
  (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])

Sign convention check: if X' = X + kappa F(X) satisfies [X',Y']_gamma = ([X,Y]_0)',
then gamma = -delta F, i.e. gamma = delta f with f = -F.

Reference map f_gb: the odd shift of the fermions
  a'^sigma = a^sigma + kappa * sum_j ( gb_{sigma,j,-} b_j^+  -  gb_{sigma,j,+} b_j^- )
satisfies [b, a'] = 0, {a'^-, a'^+} = 1, (a'^±)^2 = 0, so X(a', b) obeys the
undeformed brackets.  F(X) := kappa-part of X(a', b) - X(a, b);  f_gb := -F.

Usage:  python3 src/C_coboundary.py [n ...]      (default: 1 2 3)
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_evaluate import gb_profiles  # noqa: E402
from C_generators import DATA_DIR, SIGNS, CAlgebra, frac_str, write_json  # noqa: E402
from oscillator import gb_label  # noqa: E402
from verify_C_structure import load_structure  # noqa: E402


def phi_label(i, j):
    return f"phi[{i}|{j}]"


def odd_map_unknowns(basis, par, include_K=False):
    """Labels phi[Z_i|Z_j] allowed for an odd map (parity-reversing)."""
    labs = [phi_label(i, j) for j in basis for i in basis if par[i] != par[j]]
    if include_K:
        labs += [phi_label("K", j) for j in basis if par[j] == 1]
    return labs


def _add(d, Z, ph, c):
    if c == 0:
        return
    e = d.setdefault(Z, {})
    e[ph] = e.get(ph, 0) + c
    if e[ph] == 0:
        del e[ph]
        if not e:
            del d[Z]


def general_coboundary(basis, par, sc, include_K=False):
    """(delta f)(X,Y) for generic odd f: {(X,Y): {Z: {phi_label: coeff}}}."""
    targets = {j: [i for i in basis if par[i] != par[j]] + (["K"] if include_K and par[j] == 1 else [])
               for j in basis}
    out = {}
    for X in basis:
        for Y in basis:
            d = {}
            sX = (-1) ** par[X]
            sY = -((-1) ** ((par[X] + 1) * par[Y]))
            for i in targets[Y]:  # (-1)^{pX} [X, f(Y)]
                if i == "K":
                    continue
                for Z, c in sc.get((X, i), {}).items():
                    _add(d, Z, phi_label(i, Y), sX * c)
            for i in targets[X]:  # -(-1)^{(pX+1)pY} [Y, f(X)]
                if i == "K":
                    continue
                for Z, c in sc.get((Y, i), {}).items():
                    _add(d, Z, phi_label(i, X), sY * c)
            for W, c in sc.get((X, Y), {}).items():  # - f([X,Y])
                for i in targets[W]:
                    _add(d, i, phi_label(i, W), -c)
            if d:
                out[(X, Y)] = d
    return out


# ------------------------------------------------------ reference map ----
def shift_map(n):
    """F(X) = kappa-part of X(a',b) - X(a,b), as {X: {Z or 'K': {gb: coeff}}}."""
    C = CAlgebra(n, deformed=True)
    A = C.alg
    osc = {}
    for x in A.order:
        e = {(0, None, (x,)): Fraction(1)}
        if x.startswith("a_"):
            sg = x.split("_")[2]
            for j in range(1, n + 1):
                e[(1, gb_label(sg, j, "m"), (f"b_{j}_p",))] = Fraction(1)
                e[(1, gb_label(sg, j, "p"), (f"b_{j}_m",))] = Fraction(-1)
        osc[x] = e
    F = {}
    for X in C.basis:
        tot = {}
        for t in C.real[X][0]:
            prod = {(0, None, ()): Fraction(t["coeff"])}
            for x in t["words"]:
                prod = A.mul(prod, osc[x])
            for k, c in prod.items():
                tot[k] = tot.get(k, 0) + c
        tot = {k: v for k, v in tot.items() if v != 0}
        r0, rk = C.split(tot)
        assert r0 == C.dec.decompose({k[2]: c for k, c in C.elem[X].items()})
        res = {}
        for g, vec in rk.items():
            for Z, c in vec.items():
                res.setdefault(Z, {})[g] = c
        F[X] = res
    return F


def reference_f(n):
    F = shift_map(n)
    return {X: {Z: {g: -c for g, c in cs.items()} for Z, cs in r.items()} for X, r in F.items()}


def apply_coboundary(delta, fmap):
    """Substitute phi[Z_i|Z_j] = fmap[Z_j][Z_i] (linear forms in gb) into delta."""
    out = {}
    for key, res in delta.items():
        r = {}
        for Z, phis in res.items():
            acc = {}
            for ph, c in phis.items():
                i, j = ph[4:-1].split("|")
                for g, v in fmap.get(j, {}).get(i, {}).items():
                    acc[g] = acc.get(g, 0) + c * v
            acc = {g: v for g, v in acc.items() if v != 0}
            if acc:
                r[Z] = acc
        if r:
            out[key] = r
    return out


def build_schema4(n):
    basis, par, sc = load_structure(n)
    order = {lab: i for i, lab in enumerate(basis)}
    okey = lambda z: order.get(z, 10 ** 6)  # noqa: E731
    delta = general_coboundary(basis, par, sc, include_K=True)
    fref = reference_f(n)
    dref = apply_coboundary(delta, fref)
    gbs = [gb_label(sg, j, s) for sg in SIGNS for j in range(1, n + 1) for s in SIGNS]
    gk = {g: i for i, g in enumerate(gbs)}

    def lf(cs, keyf):
        return {k: frac_str(v) for k, v in sorted(cs.items(), key=lambda t: keyf(t[0]))}

    delta_list = [{"X": X, "Y": Y, "Z": Z, "coeff": lf(ph, lambda p: p)}
                  for (X, Y), r in delta.items() for Z in sorted(r, key=okey) for ph in [r[Z]]]
    f_list = [{"generator": X, "Z": Z, "coeff": lf(cs, gk.get)}
              for X in basis for Z in sorted(fref[X], key=okey) for cs in [fref[X][Z]]]
    d_list = [{"X": X, "Y": Y, "Z": Z, "coeff": lf(r[Z], gk.get)}
              for (X, Y), r in dref.items() for Z in sorted(r, key=okey)]
    profiles = {}
    for name, vals in gb_profiles(n).items():
        ev_f, ev_d = [], []
        for e in f_list:
            v = sum(Fraction(c) * vals[g] for g, c in e["coeff"].items())
            if v:
                ev_f.append({"generator": e["generator"], "Z": e["Z"], "coeff": frac_str(v)})
        for e in d_list:
            v = sum(Fraction(c) * vals[g] for g, c in e["coeff"].items())
            if v:
                ev_d.append({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": frac_str(v)})
        profiles[name] = {"gb_values": vals, "f": ev_f,
                          "delta_f": [e for e in ev_d if e["Z"] != "K"],
                          "delta_f_central": [e for e in ev_d if e["Z"] == "K"]}
    return {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
                    "structure_file": f"C_{n}_structure.json"},
        "odd_linear_map": {
            "definition": "f(Z_j) = sum_i phi[Z_i|Z_j] Z_i, parity-reversing (p(Z_i) != p(Z_j)); "
                          "phi[K|Z_j] (odd Z_j) is the optional central component",
            "unknowns_g": len(odd_map_unknowns(basis, par)),
            "unknowns_central": len(odd_map_unknowns(basis, par, True)) - len(odd_map_unknowns(basis, par)),
        },
        "coboundary_formula": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
        "general_coboundary": delta_list,
        "reference_map": {
            "description": ("f_gb = -F, F(X) = kappa-part of X(a',b) - X(a,b) with the odd fermion shift "
                            "a'^sigma = a^sigma + kappa sum_j (gb_{sigma,j,-} b_j^+ - gb_{sigma,j,+} b_j^-)"),
            "f": f_list,
            "delta_f": [e for e in d_list if e["Z"] != "K"],
            "delta_f_central": [e for e in d_list if e["Z"] == "K"],
        },
        "profiles": profiles,
        "metadata": {"generated_by": "src/C_coboundary.py",
                     "generation_date": datetime.date.today().isoformat(),
                     "n_general_entries": len(delta_list), "n_f_entries": len(f_list),
                     "n_delta_f_entries": len(d_list), "notation": "handover/notation.md"},
    }


def check_layer1_consistency(n, d4):
    """Labels in the Layer 1 basis; f odd; delta f odd (p(Z) = p(X)+p(Y)+1)."""
    basis, par, _ = load_structure(n)
    P = dict(par, K=0)
    bad = 0
    for e in d4["reference_map"]["f"]:
        bad += e["generator"] not in par or e["Z"] not in P or P[e["Z"]] == par[e["generator"]]
    for e in d4["general_coboundary"] + d4["reference_map"]["delta_f"] + d4["reference_map"]["delta_f_central"]:
        bad += not ({e["X"], e["Y"]} <= set(basis)) or P[e["Z"]] != (par[e["X"]] + par[e["Y"]] + 1) % 2
    for e in d4["general_coboundary"]:
        for ph in e["coeff"]:
            i, j = ph[4:-1].split("|")
            bad += P[i] == par[j]
    return bad


def main(ns):
    from C_gamma import cocycle_failures
    for n in ns:
        d4 = build_schema4(n)
        p = write_json(d4, f"C_{n}_coboundary.json")
        with open(p) as f:
            back = json.load(f)
        bad = check_layer1_consistency(n, back)
        # delta(f_gb) must itself be a cocycle (delta^2 = 0 sanity check)
        basis, par, sc = load_structure(n)
        dref = {}
        for e in back["reference_map"]["delta_f"] + back["reference_map"]["delta_f_central"]:
            dref.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {g: Fraction(c) for g, c in e["coeff"].items()}
        gbs = [g for g in back["profiles"]["all_plus"]["gb_values"]]
        cf = cocycle_failures(basis, par, sc, dref, gbs)
        m = back["metadata"]
        print(f"n={n}: general={m['n_general_entries']} f_gb={m['n_f_entries']} delta_f_gb={m['n_delta_f_entries']} "
              f"layer1_failures={bad} delta^2_failures={cf} -> {os.path.relpath(p)} "
              f"({os.path.getsize(p)//1024} KiB)")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
