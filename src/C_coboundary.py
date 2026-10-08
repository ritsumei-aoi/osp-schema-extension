"""Schema 4: coboundary data for C(n+1), from parity-reversing linear maps f.

f is parameterized as f(Z_j) = sum_i phi_{ij} Z_i, with p(Z_i) != p(Z_j) for each
nonzero phi_{ij} (odd map). The coboundary is

    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y]),

with the kappa-free bracket of Schema 1. Since f is linear in phi, we compute
delta f for each unit map f_{ij} (Z_j -> Z_i) and store the dependence on phi.

Checks:
  parity:  parity(delta f (X,Y)) = p(X)+p(Y)+1 for each unit map;
  cocycle: each unit delta f satisfies the kappa-linear super Jacobi condition.

Usage:  python src/C_coboundary.py N [N ...]   -> writes data/C_{N}_coboundary.json
"""
from fractions import Fraction
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import kappa_jacobi_ok, b0_table  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCHEMA_VERSION = "5.0"


def frac_json(v):
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def unit_coboundary(labels, parity, B0, i, j):
    """delta f for the single-entry map f(Z_j) = Z_i; returns {(X,Y): {Z: coeff}}."""
    zi, zj = labels[i], labels[j]
    out = {}
    for x, X in enumerate(labels):
        for y, Y in enumerate(labels):
            vec = {}

            def acc(z, c):
                if c != 0:
                    vec[z] = vec.get(z, Fraction(0)) + c

            px, py = parity[X], parity[Y]
            # (-1)^{p(X)} [X, f(Y)]: f(Y) = Z_i when y == j
            if y == j:
                for z, c in B0.get((X, zi), {}).items():
                    acc(z, (-1) ** px * c)
            # -(-1)^{(p(X)+1)p(Y)} [Y, f(X)]: f(X) = Z_i when x == j
            if x == j:
                sgn = -((-1) ** ((px + 1) * py))
                for z, c in B0.get((Y, zi), {}).items():
                    acc(z, sgn * c)
            # -f([X,Y]): coefficient of Z_j in [X,Y] times Z_i
            c_j = B0.get((X, Y), {}).get(zj, Fraction(0))
            acc(zi, -c_j)
            vec = {z: c for z, c in vec.items() if c != 0}
            if vec:
                out[(X, Y)] = vec
    return out


def build_schema4(n):
    base = json.load(open(os.path.join(ROOT, "data", f"C_{n}_structure.json")))
    labels = base["basis"]["odd"] + base["basis"]["even"]
    parity = base["parity"]
    B0 = b0_table(base)

    params, terms, parity_ok, cocycle_ok = [], {}, True, True
    units = []
    for i, zi in enumerate(labels):
        for j, zj in enumerate(labels):
            if parity[zi] == parity[zj]:
                continue  # f must reverse parity
            name = f"phi_{i}_{j}"
            params.append({"name": name, "target": zi, "source": zj})
            cob = unit_coboundary(labels, parity, B0, i, j)
            for (X, Y), vec in cob.items():
                for Z, c in vec.items():
                    if parity[Z] != (parity[X] + parity[Y] + 1) % 2:
                        parity_ok = False
                    terms.setdefault((X, Y, Z), {})[name] = c
            units.append(cob)

    # Cocycle check. The Jacobi expression is linear in the 2-cochain, so for
    # n <= 2 every unit is checked; for n = 3 (too slow per unit) one seeded
    # random integer combination of all units is checked instead.
    if n <= 2:
        cocycle_ok = all(kappa_jacobi_ok(labels, parity, B0, cob) for cob in units)
        cocycle_mode = "per-unit"
    else:
        rng = random.Random(20261008)
        combo = {}
        for cob in units:
            r = Fraction(rng.randint(-9, 9))
            for key, vec in cob.items():
                for Z, c in vec.items():
                    combo.setdefault(key, {})[Z] = combo.get(key, {}).get(Z, Fraction(0)) + r * c
        cocycle_ok = kappa_jacobi_ok(labels, parity, B0, combo)
        cocycle_mode = "seeded random combination of all units"

    entries = [{"X": X, "Y": Y, "Z": Z, "phi": {k: frac_json(v) for k, v in sorted(t.items())}}
               for (X, Y, Z), t in sorted(terms.items())]
    return {
        "schema_version": SCHEMA_VERSION,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})"},
        "linear_map": {
            "parameterization": "f(Z_j) = sum_i phi_{ij} Z_i, parity-reversing (odd)",
            "parameter_count": len(params),
            "parameters": params,
        },
        "coboundary": {
            "definition": "(delta f)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
            "kappa_free_bracket": "Schema 1",
            "independent_of_gb": True,
            "terms": entries,
        },
        "consistency": {
            "parity_ok": parity_ok,
            "cocycle_ok": cocycle_ok,
            "cocycle_check": cocycle_mode,
        },
        "metadata": {"generated_by": "src/C_coboundary.py",
                     "references": ["docs/math/C_coboundary_definition.md"]},
    }


def main(argv):
    for arg in argv:
        n = int(arg)
        data = build_schema4(n)
        path = os.path.join(ROOT, "data", f"C_{n}_coboundary.json")
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
        c = data["consistency"]
        print(f"n={n}: parameters={data['linear_map']['parameter_count']} "
              f"terms={len(data['coboundary']['terms'])} parity={c['parity_ok']} "
              f"cocycle={c['cocycle_ok']} ({c['cocycle_check']}) -> {path}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["1", "2", "3"])
