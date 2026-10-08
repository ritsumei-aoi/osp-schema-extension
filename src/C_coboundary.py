"""I07: Schema 4 (coboundary structure) for C(n+1).

Odd linear map f : g -> g (+) C K, parametrised by phi with f(Z_j) = sum_i phi_{ij} Z_i, and its
coboundary (docs/math/C_coboundary_definition.md)
    (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X, Y]) .

Canonical choice of f ("shift map"): the oscillator substitution
    psi(b_j^s) = b_j^s + kappa * ( gb_{-,j,s} a_1^+ + gb_{+,j,s} a_1^- ),   psi(a_1^±) = a_1^±,
undoes the deformed relation [b_j^s, a_1^sigma] = -gb_{sigma,j,s} kappa.  For X in g,
psi(X) = X + kappa * f_0(X); we set f := SIGN * f_0 with SIGN chosen so that gamma = delta f
(SIGN is determined by the computation and recorded in the JSON).

Usage: python src/C_coboundary.py [n ...]
   -> data/C_{n}_coboundary.json (symbolic in gb) and data/C_{n}_coboundary_<profile>.json
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import Poly, el_add, el_scale  # noqa: E402
from C_generators import CBasis, DATA_DIR  # noqa: E402
from C_gamma import compute_gamma, load_json  # noqa: E402
from C_evaluate import profiles  # noqa: E402


# ---------------------------------------------------------------------------
# generic coboundary of an odd linear map
# ---------------------------------------------------------------------------
def vec_add(target: dict, comps: dict, scale) -> None:
    for z, c in comps.items():
        s = target.get(z, Poly()) + c * scale
        if s:
            target[z] = s
        elif z in target:
            del target[z]


def apply_f(f: dict, vec: dict) -> dict:
    """f extended linearly; f(K) = 0."""
    out: dict = {}
    for x, cx in vec.items():
        if x == "K":
            continue
        vec_add(out, f.get(x, {}), cx)
    return out


def bracket_vec(table: dict, x: str, vec: dict) -> dict:
    """[x, vec]_0 with [x, K] = 0."""
    out: dict = {}
    for y, cy in vec.items():
        if y == "K":
            continue
        vec_add(out, table.get((x, y), {}), cy)
    return out


def coboundary(labels, parity, table, f):
    """(delta f)(X,Y) for all ordered pairs. Returns {(X,Y): {Z: Poly}} (non-zero only)."""
    out = {}
    for x in labels:
        for y in labels:
            px, py = parity[x], parity[y]
            res: dict = {}
            vec_add(res, bracket_vec(table, x, f.get(y, {})), -1 if px else 1)
            vec_add(res, bracket_vec(table, y, f.get(x, {})), -((-1) ** ((px + 1) * py)))
            vec_add(res, apply_f(f, table.get((x, y), {})), -1)
            if res:
                out[(x, y)] = res
    return out


def check_f_odd(B: CBasis, f: dict) -> bool:
    for x, comps in f.items():
        for z in comps:
            pz = 0 if z == "K" else B.parity[z]
            if pz != (B.parity[x] + 1) % 2:
                return False
    return True


# ---------------------------------------------------------------------------
# canonical shift map
# ---------------------------------------------------------------------------
def shift_map(B: CBasis) -> dict:
    """f_0 with psi(X) = X + kappa f_0(X); returns {X: {Z or K: Poly}}."""
    A = B.alg
    n = B.n
    psi = {}
    for g in A.gens:
        psi[g] = {(g,): Poly.const(1)}
    for j in range(1, n + 1):
        for s in "pm":
            lab = f"b_{j}_{s}"
            psi[lab] = {(lab,): Poly.const(1),
                        ("kappa", "a_1_p"): Poly.var(A.gb_label("m", j, s)),
                        ("kappa", "a_1_m"): Poly.var(A.gb_label("p", j, s))}
    f0 = {}
    for x in B.labels:
        img: dict = {}
        for w, c in B.real[x].items():
            prod = {(): Poly.const(1)}
            for g in w:
                prod = A.mul(prod, psi[g])
            img = el_add(img, el_scale(prod, c))
        diff = el_add(img, el_scale(B.real[x], -1))
        plain, kap = B.decompose(diff)
        assert not plain, f"psi({x}) - {x} has a kappa-free part: {plain}"
        if kap:
            f0[x] = kap
    return f0


def canonical_f(n: int):
    """Return (B, table, gamma, f, sign) with gamma == coboundary(f) verified symbolically."""
    B, table, gamma = compute_gamma(n)
    f0 = shift_map(B)
    for sign in (1, -1):
        f = {x: {z: c * sign for z, c in comps.items()} for x, comps in f0.items()}
        if coboundary(B.labels, B.parity, table, f) == gamma:
            return B, table, gamma, f, sign
    raise RuntimeError("shift map does not reproduce gamma with either sign")


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------
def entries_from(B: CBasis, pairs: dict, values: dict | None = None) -> list:
    zorder = B.labels + ["K"]
    out = []
    for x in B.labels:
        for y in B.labels:
            comps = pairs.get((x, y))
            if not comps:
                continue
            for z in zorder:
                if z in comps:
                    c = comps[z]
                    if values is None:
                        out.append({"X": x, "Y": y, "Z": z, "coeff": str(c), "coeff_terms": c.to_terms_dict()})
                    else:
                        v = c.subs(values)
                        if v:
                            out.append({"X": x, "Y": y, "Z": z, "coeff": str(v.constant())})
    return out


def f_entries(B: CBasis, f: dict, values: dict | None = None) -> list:
    zorder = B.labels + ["K"]
    out = []
    for x in B.labels:
        for z in zorder:
            if z in f.get(x, {}):
                c = f[x][z]
                if values is None:
                    out.append({"X": x, "Z": z, "coeff": str(c), "coeff_terms": c.to_terms_dict()})
                else:
                    v = c.subs(values)
                    if v:
                        out.append({"X": x, "Z": z, "coeff": str(v.constant())})
    return out


def build_schema4(n: int, profile: str | None = None, date: str | None = None, cache=None) -> dict:
    B, table, gamma, f, sign = cache or canonical_f(n)
    df = coboundary(B.labels, B.parity, table, f)
    values = None
    if profile is not None:
        values = {k: Fraction(v) for k, v in profiles(n)[profile]["values"].items()}
    fe = f_entries(B, f, values)
    de = entries_from(B, df, values)
    date = date or datetime.date.today().isoformat()
    d = {
        "schema_version": "5.0",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
                    "structure_file": f"C_{n}_structure.json", "gamma_file": f"C_{n}_gamma.json"},
        "odd_linear_map": {
            "description": "f : g -> g (+) C K, odd (parity-reversing), f(Z_j) = sum_i phi_ij Z_i; entries give phi_{Z X} for f(X)",
            "definition": ("f = SIGN * f_0 where psi(X) = X + kappa f_0(X) for the oscillator substitution "
                           "psi(b_j^s) = b_j^s + kappa (gb_a1m_bjs a_1^+ + gb_a1p_bjs a_1^-), psi(a_1^±) = a_1^±"),
            "SIGN": sign,
            "codomain_note": "Z = 'K' entries are constant components (K acts trivially in the adjoint representation)",
            "entries": fe,
            "statistics": {"generators_with_nonzero_image": len({e['X'] for e in fe}), "entries": len(fe),
                           "entries_with_K": sum(1 for e in fe if e["Z"] == "K")},
        },
        "coboundary": {
            "formula": "(delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y]),  [., K] = 0, f(K) = 0",
            "pairs_stored": "all ordered pairs (X, Y) with (delta f)(X, Y) != 0",
            "entries": de,
            "statistics": {"nonzero_pairs": len({(e['X'], e['Y']) for e in de}), "entries": len(de),
                           "entries_with_K": sum(1 for e in de if e["Z"] == "K")},
            "equals_gamma_symbolically": True,
        },
        "metadata": {"generated_by": "src/C_coboundary.py", "generation_date": date,
                     "conventions": "handover/notation.md",
                     "references": ["docs/math/C_coboundary_definition.md"]},
    }
    if profile is not None:
        d["gb_profile"] = {"name": profile, "description": profiles(n)[profile]["description"],
                           "values": profiles(n)[profile]["values"],
                           "evaluated_file": f"C_{n}_evaluated_{profile}.json"}
    return d


def write_schema4(n: int, out_dir: str = DATA_DIR) -> list:
    cache = canonical_f(n)
    paths = []
    for prof in [None] + list(profiles(n)):
        name = f"C_{n}_coboundary.json" if prof is None else f"C_{n}_coboundary_{prof}.json"
        path = os.path.join(out_dir, name)
        with open(path, "w") as fh:
            json.dump(build_schema4(n, prof, cache=cache), fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        paths.append(path)
    return paths


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        B, table, gamma, f, sign = canonical_f(n)
        assert check_f_odd(B, f)
        paths = write_schema4(n)
        d = build_schema4(n, cache=(B, table, gamma, f, sign))
        print(f"n={n}: SIGN={sign}, f-entries={d['odd_linear_map']['statistics']}, "
              f"delta f={d['coboundary']['statistics']}, gamma == delta f: True")
        print("  wrote:", ", ".join(os.path.basename(p) for p in paths))
