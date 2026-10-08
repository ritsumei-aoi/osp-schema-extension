"""Schema 2: inhomogeneous deformation (gamma structure) for C(n+1).

The kappa-linear part of every bracket is linear in the gb parameters, because
kappa^2 = 0 allows at most one boson-fermion contraction per term. So gamma is
obtained exactly by building the algebra for each unit vector e_g of gb.

Checks written into the JSON:
  1. kappa-free coefficients equal Schema 1 for every gb unit build;
  2. parity: parity(gamma(X,Y)) = p(X)+p(Y)+1 (mod 2);
  3. cocycle: the kappa-linear part of super Jacobi vanishes for each gb unit.

Usage:  python src/C_gamma.py N [N ...]   -> writes data/C_{N}_gamma.json
"""
from fractions import Fraction
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_structure import build  # noqa: E402
from verify_C_structure import br, br_vec, add  # noqa: E402

SCHEMA_VERSION = "5.0"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ONE = Fraction(1)


def gb_keys(n):
    """All 4n parameters gb[sigma, j, s] in a fixed order."""
    return [(sigma, j, s) for sigma in ("p", "m") for j in range(1, n + 1) for s in ("p", "m")]


def gb_name(key):
    sigma, j, s = key
    return f"gb_a1{sigma}_b{j}{s}"


def frac_json(v):
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def unit_tables(n):
    """Per gb-unit: kappa-linear table {(X,Y): {Z: coeff}} and kappa-free check."""
    base = json.load(open(os.path.join(ROOT, "data", f"C_{n}_structure.json")))
    base_coeff = {(e["X"], e["Y"], e["Z"]): e["coeff"] for e in base["structure_constants"]["brackets"]}
    units, coeff_ok = {}, True
    for key in gb_keys(n):
        data = build(n, gb={key: ONE})
        table = {}
        for e in data["structure_constants"]["brackets"]:
            if e["coeff"] != base_coeff.get((e["X"], e["Y"], e["Z"]), "0"):
                coeff_ok = False
            kc = Fraction(e["kappa_coeff"])
            if kc != 0:
                table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = kc
        base_keys = set(base_coeff)
        for e in data["structure_constants"]["brackets"]:
            if e["coeff"] != "0" and (e["X"], e["Y"], e["Z"]) not in base_keys:
                coeff_ok = False
        for e in data["structure_constants"]["constant_terms"]:
            table.setdefault((e["X"], e["Y"]), {})["K"] = Fraction(e["kappa_coeff"])
        units[key] = table
    return base, units, coeff_ok


def kappa_jacobi_ok(labels, parity, B0, G):
    """kappa-linear part of super Jacobi: sum_cyc s*[G(x,B0(y,z)) + (-1)^{px} B0(x,G(y,z))] = 0."""
    def one(a):
        return {a: ONE}
    for x in labels:
        for y in labels:
            for z in labels:
                s1 = -1 if (parity[x] and parity[z]) else 1
                s2 = -1 if (parity[y] and parity[x]) else 1
                s3 = -1 if (parity[z] and parity[y]) else 1
                yz0 = br_vec(B0, one(y), one(z))
                zx0 = br_vec(B0, one(z), one(x))
                xy0 = br_vec(B0, one(x), one(y))
                yz1 = br_vec(G, one(y), one(z))
                zx1 = br_vec(G, one(z), one(x))
                xy1 = br_vec(G, one(x), one(y))
                t1 = add(br_vec(G, one(x), yz0), {k: (-1) ** parity[x] * c for k, c in br_vec(B0, one(x), yz1).items()})
                t2 = add(br_vec(G, one(y), zx0), {k: (-1) ** parity[y] * c for k, c in br_vec(B0, one(y), zx1).items()})
                t3 = add(br_vec(G, one(z), xy0), {k: (-1) ** parity[z] * c for k, c in br_vec(B0, one(z), xy1).items()})
                total = add(add({k: s1 * c for k, c in t1.items()}, {k: s2 * c for k, c in t2.items()}),
                            {k: s3 * c for k, c in t3.items()})
                if total:
                    return False
    return True


def b0_table(base):
    table = {}
    for e in base["structure_constants"]["brackets"]:
        table.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return table


def build_schema2(n):
    base, units, coeff_ok = unit_tables(n)
    labels = base["basis"]["odd"] + base["basis"]["even"]
    parity = base["parity"]
    B0 = b0_table(base)

    parity_ok = True
    cocycle_ok = True
    merged = {}
    for key, table in units.items():
        for (x, y), zs in table.items():
            for z in zs:
                if z != "K" and parity[z] != (parity[x] + parity[y] + 1) % 2:
                    parity_ok = False
                merged.setdefault((x, y, z), {})[gb_name(key)] = zs[z]
        if not kappa_jacobi_ok(labels, parity, B0, table):
            cocycle_ok = False

    entries = []
    for (x, y, z), terms in sorted(merged.items()):
        entries.append({"X": x, "Y": y, "Z": z,
                        "terms": {k: frac_json(v) for k, v in sorted(terms.items())}})

    return {
        "schema_version": SCHEMA_VERSION,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n + 1})"},
        "deformation_parameters": {
            "names": [gb_name(k) for k in gb_keys(n)],
            "parity": 1,
            "count": 4 * n,
        },
        "gb_matrix": {
            "rows": ["a_1_p", "a_1_m"],
            "columns": [f"b_{j}_{s}" for j in range(1, n + 1) for s in ("p", "m")],
            "entries": [[gb_name((sigma, j, s)) for j in range(1, n + 1) for s in ("p", "m")]
                        for sigma in ("p", "m")],
        },
        "inhomogeneous_deformation": {
            "definition": "[b_j^s, a_1^sigma] = -gb[sigma,j,s] kappa; [X,Y]_gamma = [X,Y]_0 + kappa gamma(X,Y)",
            "parity_rule": "parity(gamma(X,Y)) = p(X)+p(Y)+1 (mod 2), since p(kappa)=1",
            "gamma": entries,
        },
        "consistency": {
            "kappa_free_part_matches_schema1": coeff_ok,
            "gamma_parity_ok": parity_ok,
            "kappa_linear_jacobi_cocycle_ok": cocycle_ok,
        },
        "metadata": {"generated_by": "src/C_gamma.py",
                     "references": ["docs/math/C_inhomogeneous_definition.md"]},
    }


def main(argv):
    out_dir = os.path.join(ROOT, "data")
    for arg in argv:
        n = int(arg)
        data = build_schema2(n)
        path = os.path.join(out_dir, f"C_{n}_gamma.json")
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
        c = data["consistency"]
        print(f"n={n}: gamma entries={len(data['inhomogeneous_deformation']['gamma'])} "
              f"schema1_match={c['kappa_free_part_matches_schema1']} "
              f"parity={c['gamma_parity_ok']} cocycle={c['kappa_linear_jacobi_cocycle_ok']} -> {path}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["1", "2", "3"])
