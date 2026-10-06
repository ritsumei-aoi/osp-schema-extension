"""Schema 4 (coboundary structure): odd linear map f and its coboundary (delta f).

Choice of f.  Let D be the odd derivation of the undeformed oscillator algebra with
    D(a_1^±) = 0,   D(b_j^s) = sum_{σ'} c_{j,s,σ'} a_1^{σ'},   c_{j,s,σ'} := gb_{-σ',j,s},
extended by D(xy) = D(x) y + (-1)^{|x|} x D(y).  Redefining b_j^s -> b_j^s + κ D(b_j^s) removes the
deformation [b,a] = -gb κ, and on quadratic generators it induces the odd map
    f := -D : g -> g (+ CK),        f(Z_j) = sum_i φ_ij Z_i  (+ f_K(Z_j) K).
The coboundary is (δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])
(docs/math/C_coboundary_definition.md).  f is stored g-valued; its K-component (which is not
part of g) is recorded separately as `central_component` and does NOT enter δf.

Usage: python src/C_coboundary.py   (writes data/C_{n}_coboundary.json [profile plus] and
                                      data/C_{n}_coboundary_<profile>.json)
"""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import C_evaluate as ev  # noqa: E402
import C_generators as cg  # noqa: E402

DATA = cg.DATA


def derivation_D(word_poly):
    """Apply D to {word: {'': F}} (undeformed normal ordering). Returns {word: {gb_sym: F}}."""
    out = {}
    for w, c in word_poly.items():
        coeff = c[""]
        sign = 1
        for i, x in enumerate(w):
            if x >= 3:  # boson: D(b_j^s) = sum_σ' gb_{-σ',j,s} a_σ'
                j, r = divmod(x - 3, 2)
                s = "p" if r == 0 else "m"
                for sp, a_letter in (("p", cg.AP), ("m", cg.AM)):
                    sym = cg.gb_name("m" if sp == "p" else "p", j + 1, s)
                    for w2, c2 in cg.nord(w[:i] + (a_letter,) + w[i + 1:]).items():
                        if w2 and w2[0] == cg.KAPPA:
                            continue  # undeformed ordering: drop kappa words (they carry gb)
                        d = out.setdefault(w2, {})
                        d[sym] = d.get(sym, F(0)) + sign * coeff * c2[""]
            if cg.is_odd_letter(x):
                sign = -sign
    return {w: {s: v for s, v in d.items() if v} for w, d in out.items() if any(d.values())}


def f_symbolic(alg):
    """f = -D on the basis. Returns (phi, fK): phi[X][Z][sym] and fK[X][sym]."""
    phi, fK = {}, {}
    for X in alg.basis:
        DX = derivation_D(alg.poly[X])
        syms = {s for d in DX.values() for s in d}
        for s in syms:
            vec = {w: -d[s] for w, d in DX.items() if s in d}
            comps, k = alg.decompose(vec)
            for Z, c in comps.items():
                phi.setdefault(X, {}).setdefault(Z, {})[s] = c
            if k:
                fK.setdefault(X, {})[s] = k
    return phi, fK


def eval_phi(phi, values):
    out = {}
    for X, comps in phi.items():
        for Z, cm in comps.items():
            v = sum((c * values[s] for s, c in cm.items()), F(0))
            if v:
                out.setdefault(X, {})[Z] = v
    return out


def eval_fK(fK, values):
    out = {}
    for X, cm in fK.items():
        v = sum((c * values[s] for s, c in cm.items()), F(0))
        if v:
            out[X] = v
    return out


def coboundary(alg, table, f):
    """(δf)(X,Y) for all basis pairs; f = {X: {Z: coeff}} (g-valued). Returns {(X,Y): {Z: F}}."""
    par = alg.parity

    def apply_f(u):
        out = {}
        for x, c in u.items():
            for z, v in f.get(x, {}).items():
                out[z] = out.get(z, F(0)) + c * v
        return out

    def br_left(X, u):
        out = {}
        for y, c in u.items():
            for z, v in table.get((X, y), {}).items():
                out[z] = out.get(z, F(0)) + c * v
        return out

    res = {}
    for X in alg.basis:
        for Y in alg.basis:
            pX, pY = par[X], par[Y]
            t1 = br_left(X, f.get(Y, {}))
            t2 = br_left(Y, f.get(X, {}))
            t3 = apply_f(table.get((X, Y), {}))
            s1 = (-1) ** pX
            s2 = (-1) ** ((pX + 1) * pY)
            tot = {}
            for z in set(t1) | set(t2) | set(t3):
                v = s1 * t1.get(z, F(0)) - s2 * t2.get(z, F(0)) - t3.get(z, F(0))
                if v:
                    tot[z] = v
            if tot:
                res[(X, Y)] = tot
    return res


def schema4(n, name, alg=None, table=None, sym=None):
    alg = alg or cg.CAlgebra(n)
    table = table if table is not None else cg.structure_table(alg)
    phi_s, fK_s = sym or f_symbolic(alg)
    values = ev.profile(name, n)
    f = eval_phi(phi_s, values)
    fK = eval_fK(fK_s, values)
    df = coboundary(alg, table, f)
    order = {b: i for i, b in enumerate(alg.basis)}
    phi_list = [{"X": X, "Z": Z, "coeff": cg.fstr(c)}
                for X in alg.basis for Z, c in sorted(f.get(X, {}).items(), key=lambda t: order[t[0]])]
    df_list = [{"X": X, "Y": Y, "Z": Z, "coeff": cg.fstr(c)}
               for (X, Y) in sorted(df, key=lambda k: (order[k[0]], order[k[1]]))
               for Z, c in sorted(df[(X, Y)].items(), key=lambda t: order[t[0]])]
    return {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})",
                    "dimension": {"even": len(alg.even), "odd": len(alg.odd), "total": len(alg.basis)}},
        "structure_file": f"C_{n}_structure.json",
        "evaluated_file": f"C_{n}_evaluated.json" if name == "plus" else f"C_{n}_evaluated_{name}.json",
        "profile": {"name": name, "gb_values": {s: cg.fstr(v) for s, v in values.items()}},
        "odd_map": {
            "description": ("f = -D with D the odd derivation D(a_1^±)=0, D(b_j^s)=Σ_σ' gb_{-σ',j,s} a_1^σ'; "
                            "f(Z_X) = Σ_Z φ[X→Z] Z. f maps even->odd and odd->even."),
            "phi": phi_list,
            "central_component": [{"X": X, "coeff": cg.fstr(v)} for X, v in sorted(fK.items(), key=lambda t: order[t[0]])],
            "central_component_note": "K-component of f(X) (outside g); not used in δf",
            "counts": {"phi_entries": len(phi_list), "central_entries": len(fK)},
        },
        "coboundary": {
            "formula": "(δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            "delta_f": df_list,
            "counts": {"delta_f_entries": len(df_list)},
        },
        "metadata": {"generated_by": "src/C_coboundary.py", "generation_date": "2026-10-06",
                     "references": ["docs/math/C_coboundary_definition.md"]},
    }


def output_path(n, name):
    return DATA / (f"C_{n}_coboundary.json" if name == "plus" else f"C_{n}_coboundary_{name}.json")


def main(ns=(1, 2, 3)):
    for n in ns:
        alg = cg.CAlgebra(n)
        table = cg.structure_table(alg)
        sym = f_symbolic(alg)
        for name in ev.PROFILE_NAMES:
            d = schema4(n, name, alg, table, sym)
            cg.write_json(output_path(n, name), d)
            print(f"n={n} profile={name}: phi entries={d['odd_map']['counts']['phi_entries']} "
                  f"K entries={d['odd_map']['counts']['central_entries']} "
                  f"delta_f entries={d['coboundary']['counts']['delta_f_entries']}")


if __name__ == "__main__":
    main()
