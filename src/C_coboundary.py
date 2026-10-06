"""Schema 4 (coboundary structure) for C(n+1).

Odd linear map f: g -> g (+) C K, f(Z_j) = sum_i phi_ij Z_i (phi_ij != 0 only if p(Z_i) != p(Z_j),
with p(K) = 0), and its coboundary (docs/math/C_coboundary_definition.md)

    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y]).

Family of maps used here (a shift of the fermionic oscillators):
    a_1^sigma  ->  a_1^sigma + kappa * sum_{j,s} c^sigma_{j,s} b_j^s ,
X' = X(a', b) = X + kappa F_c(X); f_c := F_c, computed exactly in the undeformed oscillator algebra.
c is parametrised by the same 4n labels as gb; the dictionary c <-> gb is `c_from_gb`.
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
import C_evaluate as EV  # noqa: E402
import C_gamma as GM  # noqa: E402
import C_generators as G  # noqa: E402
from C_oscillator import OscAlgebra, A_P, A_M, b_index  # noqa: E402

DATA_DIR = G.DATA_DIR
K = GM.K_LABEL


def c_from_gb(n, gb_values, sign=1):
    """gb (by name) -> c (by key (sigma, j, s)).
    With [b_j^s, a'^sigma] = kappa [b_j^s, w^sigma] one gets gb_{sigma,j,m} = -c_{sigma,j,p} and
    gb_{sigma,j,p} = +c_{sigma,j,m}; inverted here (overall `sign` kept for convention checks)."""
    c = {}
    for (sg, j, s) in GM.gb_keys(n):
        other = "p" if s == "m" else "m"
        gbv = Fraction(gb_values.get(GM.gb_name((sg, j, other)), 0))
        c[(sg, j, s)] = sign * (-gbv if s == "p" else gbv)
    return c


def f_from_c(n, c):
    """Odd map f = F_c as {Z_j: {Z_i or 'K': coeff}}."""
    alg = OscAlgebra(n)
    dec = G.Decomposer(n)
    real = dec.real
    shifted = {}
    for sg, a in (("p", A_P), ("m", A_M)):
        el = {(a,): Fraction(1)}
        for j in range(1, n + 1):
            for s in G.SIGNS:
                v = c.get((sg, j, s), 0)
                if v != 0:
                    el[(0, b_index(j, s))] = el.get((0, b_index(j, s)), 0) + Fraction(v)
        shifted[a] = el
    f = {}
    for lab in G.all_labels(n):
        total = {}
        for word, coef in real[lab].items():
            factors = [shifted[g] if g in (A_P, A_M) else {(g,): Fraction(1)} for g in word]
            prod = {(): Fraction(coef)}
            for fac in factors:
                prod = alg.mul(prod, fac)
            for w, v in prod.items():
                total[w] = total.get(w, 0) + v
        total = {w: v for w, v in total.items() if v != 0}
        _, kpart = G.split_kappa(total)
        if kpart:
            d, resid = dec.decompose(kpart)
            if resid != 0:
                d[K] = resid
            f[lab] = d
    return f


def check_odd(n, f):
    par = G.parity_map(n)
    par[K] = 0
    return [(zj, zi) for zj, d in f.items() for zi in d if par[zi] == par[zj]]


def delta_f(n, f, sc0=None):
    """(delta f)(X,Y) as {(X, Y): {Z: coeff}}; K-valued entries use Z == 'K'."""
    if sc0 is None:
        sc0, _, _ = G.structure_constants(n)
    par = G.parity_map(n)
    labels = G.all_labels(n)

    def br_X(X, vec):  # [X, vec] with K central
        out = {}
        for y, cy in vec.items():
            if y == K:
                continue
            for z, v in sc0.get((X, y), {}).items():
                out[z] = out.get(z, 0) + cy * v
        return out

    out = {}
    for X in labels:
        for Y in labels:
            acc = {}
            s1 = (-1) ** par[X]
            for z, v in br_X(X, f.get(Y, {})).items():
                acc[z] = acc.get(z, 0) + s1 * v
            s2 = (-1) ** ((par[X] + 1) * par[Y])
            for z, v in br_X(Y, f.get(X, {})).items():
                acc[z] = acc.get(z, 0) - s2 * v
            for w, v in sc0.get((X, Y), {}).items():
                for z, u in f.get(w, {}).items():
                    acc[z] = acc.get(z, 0) - v * u
            acc = {z: v for z, v in acc.items() if v != 0}
            if acc:
                out[(X, Y)] = acc
    return out


def build_schema4(n, profile, gb_values):
    c = c_from_gb(n, gb_values)
    f = f_from_c(n, c)
    assert not check_odd(n, f)
    df = delta_f(n, f)
    labels = G.all_labels(n)
    order = lambda z: (z == K, labels.index(z) if z != K else 0)  # noqa: E731
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as fh:
        s1 = json.load(fh)
    f_entries = [
        {"from": zj, "to": zi, "phi": G.fstr(v)}
        for zj in labels for zi, v in sorted(f.get(zj, {}).items(), key=lambda t: order(t[0]))
    ]
    entries = [
        {"X": X, "Y": Y, "Z": Z, "coeff": G.fstr(v)}
        for X in labels for Y in labels
        for Z, v in sorted(df.get((X, Y), {}).items(), key=lambda t: order(t[0]))
    ]
    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "basis": s1["basis"],
        "parity": s1["parity"],
        "central_elements": s1["central_elements"],
        "odd_linear_map": {
            "description": "f(Z_j) = sum_i phi_ij Z_i, induced by a_1^σ -> a_1^σ + κ Σ c^σ_{j,s} b_j^s; "
                           "targets may include the central direction K; nonzero only if p(Z_i) != p(Z_j) (p(K)=0)",
            "family": "fermion shift",
            "profile": profile,
            "c_parameters": {f"c_a_1_{sg}_b_{j}_{s}": G.fstr(v) for (sg, j, s), v in c.items()},
            "gb_correspondence": "c_{σ,j,p} = -gb_{σ,j,m}, c_{σ,j,m} = +gb_{σ,j,p}",
            "phi": f_entries,
        },
        "coboundary": {
            "formula": "(δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            "central_direction": "Z = 'K' is the coefficient of κ·1 (same convention as Schema 2/3)",
            "delta_f": entries,
        },
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": "2026-10-06",
            "schema1_file": f"C_{n}_structure.json",
        },
    }


def coboundary_name(n, profile):
    return f"C_{n}_coboundary.json" if profile == "all_plus" else f"C_{n}_coboundary_{profile}.json"


def load_coboundary(n, profile="all_plus", data_dir=DATA_DIR):
    with open(os.path.join(data_dir, coboundary_name(n, profile))) as fh:
        d = json.load(fh)
    df = {}
    for e in d["coboundary"]["delta_f"]:
        df.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    f = {}
    for e in d["odd_linear_map"]["phi"]:
        f.setdefault(e["from"], {})[e["to"]] = Fraction(e["phi"])
    return d, f, df


def write_all(ns=(1, 2, 3), out_dir=DATA_DIR):
    for n in ns:
        for prof, vals in EV.profiles(n).items():
            with open(os.path.join(out_dir, coboundary_name(n, prof)), "w") as fh:
                json.dump(build_schema4(n, prof, vals), fh, indent=1, ensure_ascii=False)
                fh.write("\n")
            print("wrote", coboundary_name(n, prof))


if __name__ == "__main__":
    write_all()
