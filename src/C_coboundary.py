"""Schema 4 (coboundary structure) for C(n+1) = osp(2|2n).

Odd linear map f: g -> g,  f(Z_j) = sum_i phi_{i}_{j} Z_i  (only p(Z_i) != p(Z_j)),
    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y])
(docs/math/C_coboundary_definition.md).  Optional central part h(Z_j) = psi_{j} K for odd Z_j
(needed to compare with the kappa K component of Schema 2):  (delta h)(X,Y) = -h([X,Y]).

Usage:  python3 src/C_coboundary.py      (writes data/C_{1,2,3}_coboundary.json)
"""
import datetime
import json
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import deformed_jacobi_failures, load_schema1  # noqa: E402
from C_generators import write_json  # noqa: E402
from C_oscillator import lin, lin_add, lin_scale, lin_str  # noqa: E402


def phi_name(i, j):
    return f"phi_{i}_{j}"


def psi_name(j):
    return f"psi_{j}"


def f_params(basis, parity):
    idx = {x: i for i, x in enumerate(basis)}
    return {y: {x: phi_name(idx[x], idx[y]) for x in basis if parity[x] != parity[y]} for y in basis}


def _add(acc, key, c):
    v = lin_add(acc.get(key, {}), c)
    if v:
        acc[key] = v
    else:
        acc.pop(key, None)


def coboundary(basis, parity, sc):
    """Returns ({(X,Y): {Z: Lin(phi)}}, {(X,Y): Lin(psi)}) for all ordered pairs."""
    fp = f_params(basis, parity)
    idx = {x: i for i, x in enumerate(basis)}
    df, dh = {}, {}
    for x in basis:
        for y in basis:
            px, py = parity[x], parity[y]
            acc = {}
            # (-1)^{p(X)} [X, f(Y)]
            s1 = (-1) ** px
            for zi, ph in fp[y].items():
                for w, c in sc.get((x, zi), {}).items():
                    _add(acc, w, lin(s1 * c, ph))
            # - (-1)^{(p(X)+1) p(Y)} [Y, f(X)]
            s2 = -(-1) ** ((px + 1) * py)
            for zi, ph in fp[x].items():
                for w, c in sc.get((y, zi), {}).items():
                    _add(acc, w, lin(s2 * c, ph))
            # - f([X, Y])
            cent = {}
            for wv, c in sc.get((x, y), {}).items():
                for zi, ph in fp[wv].items():
                    _add(acc, zi, lin(-c, ph))
                if parity[wv] == 1:
                    cent = lin_add(cent, lin(-c, psi_name(idx[wv])))
            if acc:
                df[(x, y)] = acc
            if cent:
                dh[(x, y)] = cent
    return df, dh


def evaluate(df, values):
    out = {}
    for key, r in df.items():
        for z, c in r.items():
            v = sum((cv * values.get(k, 0) for k, cv in c.items()), Fraction(0))
            if v:
                out.setdefault(key, {})[z] = lin(v, "1")
    return out


def build_schema4(n, seed=12345):
    d1, sc = load_schema1(n)
    basis = d1["basis"]["odd"] + d1["basis"]["even"]
    parity = d1["parity"]
    idx = {x: i for i, x in enumerate(basis)}
    df, dh = coboundary(basis, parity, sc)
    fp = f_params(basis, parity)
    phis = sorted({p for y in fp for p in fp[y].values()}, key=lambda s: tuple(map(int, s.split("_")[1:])))
    psis = [psi_name(idx[x]) for x in d1["basis"]["odd"]]

    checks = {}
    checks["labels_in_layer1_basis"] = all(
        x in idx and y in idx and z in idx for (x, y), r in df.items() for z in r)
    checks["odd_parity_shift"] = all(
        parity[z] == (parity[x] + parity[y] + 1) % 2 for (x, y), r in df.items() for z in r)
    anti = True
    for (x, y), r in df.items():
        s = -(-1) ** (parity[x] * parity[y])
        o = df.get((y, x), {})
        for z in set(r) | set(o):
            if lin_add(r.get(z, {}), lin_scale(o.get(z, {}), s), -1):
                anti = False
    checks["graded_antisymmetric"] = anti
    # delta^2 = 0: a random coboundary must satisfy the deformed Jacobi (cocycle) identity of Schema 2.
    rng = random.Random(seed)
    vals = {p: Fraction(rng.randint(-3, 3)) for p in phis + psis}
    num_g = evaluate(df, vals)
    num_c = {k: lin(sum((c * vals[p] for p, c in v.items()), Fraction(0)), "1") for k, v in dh.items()}
    num_c = {k: v for k, v in num_c.items() if v}
    checks["delta_squared_zero_random_f_failures"] = len(
        deformed_jacobi_failures(n, sc, num_g, num_c, parity, basis, with_central=True))

    entries = [{"X": x, "Y": y, "Z": z, "coeff": lin_str(df[(x, y)][z])}
               for i, x in enumerate(basis) for y in basis[i:] if (x, y) in df
               for z in basis if z in df[(x, y)]]
    central = [{"X": x, "Y": y, "coeff": lin_str(dh[(x, y)])}
               for i, x in enumerate(basis) for y in basis[i:] if (x, y) in dh]
    obj = {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": d1["algebra"],
        "basis": d1["basis"],
        "parity": parity,
        "global_index": {x: i for i, x in enumerate(basis)},
        "odd_linear_map": {
            "definition": "f(Z_j) = sum_i phi_{i}_{j} Z_i, Z = global basis (odd + even); phi_{i}_{j} = 0 unless p(Z_i) != p(Z_j)",
            "parameters": phis,
            "parameter_count": len(phis),
            "central_extension": {
                "definition": "h(Z_j) = psi_{j} K for odd Z_j (h: g -> C K, odd); (δh)(X,Y) = -h([X,Y])",
                "parameters": psis,
            },
        },
        "coboundary_formula": "(δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
        "pair_coverage": "unordered: index(X) <= index(Y); (δf)(Y,X) = -(-1)^{p(X)p(Y)} (δf)(X,Y)",
        "coboundary_coefficients": entries,
        "coboundary_central": central,
        "consistency_checks": checks,
        "metadata": {
            "generated_by": "src/C_coboundary.py",
            "generation_date": datetime.date.today().isoformat(),
            "source_schema1": f"C_{n}_structure.json",
            "random_seed_for_delta_squared_check": seed,
            "conventions": "handover/notation.md",
        },
    }
    return obj


def load_schema4(n):
    """Return (basis, parity, df {(X,Y): {Z: Lin}}, dh {(X,Y): Lin}) with all ordered pairs restored."""
    from C_generators import DATA
    from C_oscillator import lin_from_json
    with open(os.path.join(DATA, f"C_{n}_coboundary.json")) as fh:
        d = json.load(fh)
    basis = d["basis"]["odd"] + d["basis"]["even"]
    parity = d["parity"]
    df, dh = {}, {}
    for e in d["coboundary_coefficients"]:
        x, y, z, c = e["X"], e["Y"], e["Z"], lin_from_json(e["coeff"])
        df.setdefault((x, y), {})[z] = c
        if x != y:
            df.setdefault((y, x), {})[z] = lin_scale(c, -(-1) ** (parity[x] * parity[y]))
    for e in d["coboundary_central"]:
        x, y, c = e["X"], e["Y"], lin_from_json(e["coeff"])
        dh[(x, y)] = c
        if x != y:
            dh[(y, x)] = lin_scale(c, -(-1) ** (parity[x] * parity[y]))
    return d, basis, parity, df, dh


def main(ns=(1, 2, 3)):
    for n in ns:
        obj = build_schema4(n)
        p = write_json(obj, f"C_{n}_coboundary.json")
        print(f"n={n}: phi params={obj['odd_linear_map']['parameter_count']}, "
              f"psi params={len(obj['odd_linear_map']['central_extension']['parameters'])}, "
              f"entries={len(obj['coboundary_coefficients'])}, central entries={len(obj['coboundary_central'])}, "
              f"checks={obj['consistency_checks']} -> {p} ({os.path.getsize(p)//1024} KiB)")


if __name__ == "__main__":
    main()
