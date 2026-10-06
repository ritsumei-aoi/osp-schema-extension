"""Schema 4: coboundary structure delta f for C(n+1), f an odd linear map g -> g (+ C K).

f_c is induced by the oscillator shift  a_1^sigma -> a_1^sigma + kappa * l^sigma,  l^sigma = sum_{j,s} c[sigma,j,s] b_j^s,
i.e. f_c(X) = D_c(X) where D_c is the odd derivation of the oscillator algebra with D_c(a^sigma) = l^sigma, D_c(b) = 0.
It reverses parity, is linear in the 4n parameters c, and f_c(Z) lies in g (+) C K (the K part is a Weyl-ordering constant).
(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])  (docs/math/C_coboundary_definition.md).

Usage: python src/C_coboundary.py   (writes data/C_{n}_coboundary.json, n=1,2,3)
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import extended_decomposer, gb_name, gb_params  # noqa: E402
from C_generators import frac_str, structure_constants  # noqa: E402
from osc_algebra import add_to, bracket, lincomb, mul, scale  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def f_name(p):
    sg, j, s = p
    return f"f_a_1_{sg}_b_{j}_{s}"


def ell(n, sigma, c):
    """l^sigma = sum c[(sigma,j,s)] b_j^s as oscillator element."""
    out = {}
    for j in range(1, n + 1):
        for s in "pm":
            v = c.get((sigma, j, s), 0)
            if v:
                B = [0] * (2 * n)
                B[2 * (j - 1) + (0 if s == "p" else 1)] = 1
                add_to(out, (0, 0, 0, tuple(B)), Fraction(v))
    return out


def derivation(n, X, c):
    """Odd derivation D_c applied to an oscillator element X (kappa stripped)."""
    lp, lm = ell(n, "p", c), ell(n, "m", c)
    out = {}
    for (k, fp, fm, B), v in X.items():
        Bel = {(0, 0, 0, B): Fraction(1)}
        if fp and not fm:
            t = mul(lp, Bel, n)
        elif fm and not fp:
            t = mul(lm, Bel, n)
        elif fp and fm:
            # D(a+ a-) = l+ a- - a+ l-   (bosons commute with fermions)
            t1 = mul(mul(lp, {(0, 0, 1, (0,) * (2 * n)): Fraction(1)}, n), Bel, n)
            t2 = mul(mul({(0, 1, 0, (0,) * (2 * n)): Fraction(1)}, lm, n), Bel, n)
            t = lincomb(t1, t2, 1, -1)
        else:
            continue
        for m, cc in t.items():
            add_to(out, m, v * cc)
    return out


def compute_f(n, c):
    """f_c on the basis: {source: {target (basis name or 'K'): Fraction}}."""
    names, parity, R, dec = extended_decomposer(n)
    f = {}
    for Z in names:
        img = derivation(n, R[Z], c)
        if not img:
            continue
        coef, res = dec.decompose(img)
        assert not res, (Z, res)
        f[Z] = coef
    return names, parity, f


def coboundary(n, f, names, parity, sc):
    """delta f from structure constants sc[(X,Y)] = {Z: coeff} and f (dict of dicts). Returns {(X,Y): {Z|'K': coeff}}."""
    out = {}

    def apply_f(vec):
        r = {}
        for z, cz in vec.items():
            for t, v in f.get(z, {}).items():
                r[t] = r.get(t, 0) + cz * v
        return r

    def br_vec(X, vec):  # [X, vec] with K central
        r = {}
        for z, cz in vec.items():
            if z == "K":
                continue
            for w, v in sc.get((X, z), {}).items():
                r[w] = r.get(w, 0) + cz * v
        return r

    def br_vec2(vec, Y):
        r = {}
        for z, cz in vec.items():
            if z == "K":
                continue
            for w, v in sc.get((z, Y), {}).items():
                r[w] = r.get(w, 0) + cz * v
        return r

    for X in names:
        px = parity[X]
        for Y in names:
            py = parity[Y]
            t1 = br_vec(X, f.get(Y, {}))
            t2 = br_vec(Y, f.get(X, {}))
            t3 = apply_f(sc.get((X, Y), {}))
            r = {}
            for z, v in t1.items():
                r[z] = r.get(z, 0) + (-1) ** px * v
            for z, v in t2.items():
                r[z] = r.get(z, 0) - (-1) ** ((px + 1) * py) * v
            for z, v in t3.items():
                r[z] = r.get(z, 0) - v
            r = {z: v for z, v in r.items() if v}
            if r:
                out[(X, Y)] = r
    return out


def unit_data(n):
    """For each c-parameter: f and delta f (unit value on that parameter)."""
    names, parity, _, _ = extended_decomposer(n)
    _, _, _, sc = structure_constants(n)
    data = {}
    for p in gb_params(n):
        _, _, f = compute_f(n, {p: Fraction(1)})
        data[p] = (f, coboundary(n, f, names, parity, sc))
    return names, parity, data


def match_gamma(n, data):
    """Find gb = M c such that delta f_c = gamma(gb): returns {c-param: {gb-param: coeff}} (exact)."""
    from C_gamma import compute_gamma
    names, parity, gamma = compute_gamma(n)
    # gamma_unit[p] = {(X,Y): {Z: v}}
    gu = {p: {} for p in gb_params(n)}
    for (X, Y), per in gamma.items():
        for p, zs in per.items():
            gu[p][(X, Y)] = zs
    M = {}
    for q, (f, db) in data.items():
        found = None
        for p, g in gu.items():
            for sgn in (1, -1):
                if db == {k: {z: sgn * v for z, v in zs.items()} for k, zs in g.items()}:
                    found = (p, sgn)
        if found is None:
            raise RuntimeError(f"delta f_{q} is not +-gamma of a single gb parameter")
        M[q] = {found[0]: Fraction(found[1])}
    return M


def build_schema4(n, structure, date=None):
    names, parity, data = unit_data(n)
    params = gb_params(n)
    M = match_gamma(n, data)
    idx = {x: i for i, x in enumerate(names + ["K"])}
    fmap = {}
    for q, (f, _db) in data.items():
        for src, tg in f.items():
            for t, v in tg.items():
                fmap.setdefault((src, t), {})[f_name(q)] = frac_str(v)
    f_entries = [{"source": s, "target": t, "coeff": fmap[(s, t)]}
                 for (s, t) in sorted(fmap, key=lambda k: (idx[k[0]], idx[k[1]]))]
    cb = {}
    for q, (_f, db) in data.items():
        for (X, Y), zs in db.items():
            for Z, v in zs.items():
                cb.setdefault((X, Y, Z), {})[f_name(q)] = frac_str(v)
    cb_entries = [{"X": X, "Y": Y, "Z": Z, "coeff": cb[(X, Y, Z)]}
                  for (X, Y, Z) in sorted(cb, key=lambda k: (idx[k[0]], idx[k[1]], idx[k[2]]))]
    return {
        "schema_version": "5.0",
        "schema_layer": 4,
        "algebra": structure["algebra"],
        "central_elements": structure["central_elements"],
        "basis": structure["basis"],
        "parity": structure["parity"],
        "odd_linear_map": {
            "description": "f_c = odd derivation induced by a_1^sigma -> a_1^sigma + kappa * sum_{j,s} c[sigma,j,s] b_j^s. "
                           "f(Z_j) = sum_i phi_ij Z_i with phi linear in c; target 'K' is the central constant.",
            "parameters": [f_name(p) for p in params],
            "parity_rule": "p(f(Z)) = p(Z) + 1 (mod 2); K has parity 0 so it only occurs as image of odd Z",
            "f_structure": f_entries,
        },
        "coboundary_structure": {
            "formula": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            "entries": cb_entries,
        },
        "gb_correspondence": {
            "description": "gamma(gb) = delta f_c  exactly when gb = M c  (M is a signed permutation matrix of the 4n parameters)",
            "map": {f_name(q): {gb_name(p): frac_str(v) for p, v in M[q].items()} for q in params},
        },
        "metadata": {"generated_by": "src/C_coboundary.py",
                     "generation_date": date or datetime.date.today().isoformat(),
                     "references": ["docs/math/C_coboundary_definition.md"]},
    }


def main():
    for n in (1, 2, 3):
        st = json.load(open(os.path.join(DATA_DIR, f"C_{n}_structure.json")))
        d = build_schema4(n, st)
        path = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
        with open(path, "w") as fh:
            json.dump(d, fh, indent=1, ensure_ascii=False)
        print(f"n={n}: f entries={len(d['odd_linear_map']['f_structure'])}, "
              f"coboundary entries={len(d['coboundary_structure']['entries'])}")
        print("   gb correspondence:", {k: v for k, v in d["gb_correspondence"]["map"].items()})


if __name__ == "__main__":
    main()
