"""Schema 4 (coboundary structure) for C(n+1) = osp(2|2n).

General odd linear map (docs/math/C_coboundary_definition.md):
    f(Z_j) = sum_{i: p(Z_i) = p(Z_j)+1} phi[Z_i,Z_j] Z_i  +  phi[K,Z_j] K   (K-term only for odd Z_j)
Coboundary:
    (δf)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X,Y])
δf is stored as linear forms in the unknowns phi, for PBW-ordered pairs X <= Y
(δf(Y,X) = -(-1)^{p(X)p(Y)} δf(X,Y), verified).
Usage: python src/C_coboundary.py [n ...]
"""
import datetime
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import DATA_DIR, write_json  # noqa: E402
from verify_C_structure import bracket_table, load_structure  # noqa: E402


def phi_label(i, j):
    return f"phi[{i},{j}]"


def unknowns(basis, parity, include_K=True):
    """Ordered list of (Z_i, Z_j) pairs with p(Z_i) != p(Z_j); plus (K, Z_j) for odd Z_j."""
    out = [(i, j) for j in basis for i in basis if parity[i] != parity[j]]
    if include_K:
        out += [("K", j) for j in basis if parity[j] == 1]
    return out


def coboundary_forms(basis, parity, tab, include_K=True, term_signs=(1, 1, 1)):
    """{(X,Y): {Z: {(i,j): Fraction}}} for all ordered pairs.
    term_signs multiplies the three terms of δf (only for negative-control tests)."""
    unk = unknowns(basis, parity, include_K)
    f_of = {}  # f(Z_j) = {Z_i: (i,j)}
    for (i, j) in unk:
        f_of.setdefault(j, []).append(i)

    def add(acc, Z, key, c):
        d = acc.setdefault(Z, {})
        v = d.get(key, 0) + c
        if v:
            d[key] = v
        else:
            d.pop(key)
            if not d:
                acc.pop(Z)

    forms = {}
    for X in basis:
        for Y in basis:
            acc = {}
            pX, pY = parity[X], parity[Y]
            s1 = term_signs[0] * (-1) ** pX
            s2 = -term_signs[1] * (-1) ** ((pX + 1) * pY)
            for i in f_of.get(Y, []):          # (-1)^{pX} [X, f(Y)]
                if i == "K":
                    continue
                for Z, c in tab.get((X, i), {}).items():
                    add(acc, Z, (i, Y), s1 * c)
            for i in f_of.get(X, []):          # - (-1)^{(pX+1)pY} [Y, f(X)]
                if i == "K":
                    continue
                for Z, c in tab.get((Y, i), {}).items():
                    add(acc, Z, (i, X), s2 * c)
            for W, c in tab.get((X, Y), {}).items():   # - f([X,Y])
                for i in f_of.get(W, []):
                    add(acc, i, (i, W), -term_signs[2] * c)
            if acc:
                forms[(X, Y)] = acc
    return unk, forms


def evaluate_forms(forms, phi):
    """Substitute numeric phi {(i,j): value} -> {(X,Y): {Z: value}}."""
    out = {}
    for k, v in forms.items():
        for Z, lin in v.items():
            c = sum((phi.get(u, 0) * a for u, a in lin.items()), Fraction(0))
            if c:
                out.setdefault(k, {})[Z] = c
    return out


def check_coboundary(n, basis, parity, tab, unk, forms, trials=2, seed=1):
    """(a) super-antisymmetry and parity rule of δf (symbolic),
    (b) δf is a 2-cocycle in the convention of Schema 2 (deformed Jacobi), random phi."""
    from C_gamma import check_deformed_jacobi
    fails = []
    par = dict(parity, K=0)
    for X in basis:
        for Y in basis:
            s = -(-1) ** (parity[X] * parity[Y])
            a, b = forms.get((X, Y), {}), forms.get((Y, X), {})
            for Z in set(a) | set(b):
                la, lb = a.get(Z, {}), b.get(Z, {})
                if any(lb.get(u, 0) != s * la.get(u, 0) for u in set(la) | set(lb)):
                    fails.append(("antisym", X, Y, Z))
                if par[Z] != (parity[X] + parity[Y] + 1) % 2:
                    fails.append(("parity", X, Y, Z))
    rng = random.Random(seed)
    jac = 0
    for _ in range(trials):
        phi = {u: Fraction(rng.randint(-5, 5)) for u in unk}
        ev = evaluate_forms(forms, phi)
        gam_num = {k: {Z: {"phi": c} for Z, c in v.items()} for k, v in ev.items()}
        _, jf = check_deformed_jacobi(basis, parity, tab, gam_num)
        jac += len(jf)
    return fails, jac


def build_schema4(n, date=None):
    s1 = load_structure(n)
    basis, parity = s1["basis"]["ordering"], s1["parity"]
    tab = bracket_table(s1["structure_constants"])
    unk, forms = coboundary_forms(basis, parity, tab)
    idx = {u: k for k, u in enumerate(unk)}
    pos = {x: k for k, x in enumerate(basis)}
    order = basis + ["K"]
    entries = []
    for X in basis:
        for Y in basis:
            if pos[X] > pos[Y]:
                continue
            v = forms.get((X, Y), {})
            for Z in order:
                if Z in v:
                    terms = sorted([idx[u], str(c)] for u, c in v[Z].items())
                    entries.append({"X": X, "Y": Y, "Z": Z, "terms": terms})
    n_even = sum(1 for x in basis if parity[x] == 0)
    n_odd = len(basis) - n_even
    return {
        "schema_version": "5.0",
        "layer": 4,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
                    "osp": f"osp(2|{2*n})"},
        "structure_file": f"C_{n}_structure.json",
        "basis_ordering": basis,
        "odd_linear_map": {
            "definition": ("f(Z_j) = sum_i phi[Z_i,Z_j] Z_i (p(Z_i) = p(Z_j)+1)  "
                           "+ phi[K,Z_j] K (odd Z_j only)"),
            "parity": "odd: f(g_0) ⊂ g_1, f(g_1) ⊂ g_0 ⊕ CK",
            "K_component_note": ("phi[K,*] allow f to take values in g ⊕ CK, matching the value "
                                 "space of γ (Schema 2). Set them to 0 for f: g -> g."),
            "num_unknowns": len(unk),
            "num_unknowns_breakdown": {"even_to_odd": n_even * n_odd,
                                       "odd_to_even": n_odd * n_even, "odd_to_K": n_odd},
            "unknowns": [phi_label(i, j) for (i, j) in unk],
        },
        "coboundary": {
            "formula": ("(δf)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] "
                        "- f([X,Y])"),
            "pairs": ("PBW-ordered pairs X <= Y only; "
                      "(δf)(Y,X) = -(-1)^{p(X)p(Y)} (δf)(X,Y)"),
            "entry_format": ("{X, Y, Z, terms: [[unknown index, coeff], ...]}: "
                             "(δf)(X,Y)_Z = sum coeff * unknowns[index]"),
            "num_entries": len(entries),
            "entries": entries,
        },
        "metadata": {"generated_by": "src/C_coboundary.py",
                     "generation_date": date or datetime.date.today().isoformat(),
                     "conventions": "handover/notation.md",
                     "math_reference": "docs/math/C_coboundary_definition.md"},
    }


def load_coboundary(n):
    """Schema 4 file -> (basis, parity, unknown labels, forms over all ordered pairs)."""
    import json
    with open(os.path.join(DATA_DIR, f"C_{n}_coboundary.json")) as fh:
        s4 = json.load(fh)
    s1 = load_structure(n)
    basis, parity = s1["basis"]["ordering"], s1["parity"]
    labels = s4["odd_linear_map"]["unknowns"]
    forms = {}
    for e in s4["coboundary"]["entries"]:
        lin = {k: Fraction(c) for k, c in e["terms"]}
        X, Y = e["X"], e["Y"]
        forms.setdefault((X, Y), {})[e["Z"]] = lin
        if X != Y:
            s = -(-1) ** (parity[X] * parity[Y])
            forms.setdefault((Y, X), {})[e["Z"]] = {k: s * c for k, c in lin.items()}
    return basis, parity, labels, forms


def main(ns):
    for n in ns:
        s4 = build_schema4(n)
        path = os.path.join(DATA_DIR, f"C_{n}_coboundary.json")
        write_json(s4, path)
        s1 = load_structure(n)
        basis, parity = s1["basis"]["ordering"], s1["parity"]
        tab = bracket_table(s1["structure_constants"])
        unk, forms = coboundary_forms(basis, parity, tab)
        fails, jac = check_coboundary(n, basis, parity, tab, unk, forms)
        # round trip through the file
        _, _, labels, forms_file = load_coboundary(n)
        rt = _roundtrip_ok(unk, forms, forms_file)
        print(f"n={n}: unknowns={len(unk)}, entries={s4['coboundary']['num_entries']}, "
              f"antisym/parity failures={len(fails)}, cocycle(Jacobi) failures={jac}, "
              f"file round-trip ok={rt} -> {os.path.basename(path)}")


def _roundtrip_ok(unk, forms, forms_file):
    idx = {u: k for k, u in enumerate(unk)}
    conv = {k: {Z: {idx[u]: c for u, c in lin.items()} for Z, lin in v.items()}
            for k, v in forms.items()}
    return conv == forms_file


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
