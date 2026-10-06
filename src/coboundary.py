"""Schema 4: coboundary delta f of odd linear maps f: g -> g  (docs/math/C_coboundary_definition.md).

    (delta f)(X,Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1) p(Y)} [Y, f(X)] - f([X,Y])

f is parametrised by phi_{ij}: f(Z_j) = sum_i phi_ij Z_i with p(Z_i) != p(Z_j).
Layer 4 stores (a) delta of every elementary odd map E_{ij} (Z_j -> Z_i) and (b) for each Layer-3 profile the
closed-form odd map f = -D_gb (src/gauge_f.py), its coboundary delta f and the residual gamma - delta f.
Triviality is cross-checked by exact elimination (is gamma in the span of all elementary delta E_ij?).

usage: python src/coboundary.py     # writes data/C_{n}_coboundary.json
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
from gamma import param_keys, param_name  # noqa: E402
from gauge_f import trivializing_f  # noqa: E402
from oscalg import make_decomposer  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def _add(acc, other, c):
    for k, v in other.items():
        nv = acc.get(k, 0) + c * v
        if nv:
            acc[k] = nv
        elif k in acc:
            del acc[k]


class Layer1:
    """Schema 1 data (brackets, parity) loaded from JSON."""

    def __init__(self, n):
        d = json.load(open(os.path.join(DATA, f"C_{n}_structure.json")))
        self.n = n
        self.labels = d["basis"]["odd"] + d["basis"]["even"]
        self.par = d["parity"]
        self.br = {}
        self.inv = {}  # Z -> [(X, Y, c)] with Z in [X,Y}
        for t in d["structure_constants"]:
            c = Fraction(t["coeff"])
            self.br.setdefault((t["X"], t["Y"]), {})[t["Z"]] = c
            self.inv.setdefault(t["Z"], []).append((t["X"], t["Y"], c))

    def odd_map_basis(self):
        """All elementary odd maps as (to, from) pairs, parity-reversing."""
        return [(i, j) for j in self.labels for i in self.labels if self.par[i] != self.par[j]]


def delta_elementary(L, to, frm):
    """delta of f = (Z_frm -> Z_to) as {(X,Y,Z): coeff}."""
    par, br = L.par, L.br
    out = {}
    # (-1)^{p(X)} [X, f(Y)] with Y = frm
    for X in L.labels:
        _add(out, {(X, frm, Z): c for Z, c in br.get((X, to), {}).items()}, (-1) ** par[X])
    # -(-1)^{(p(X)+1)p(Y)} [Y, f(X)] with X = frm
    for Y in L.labels:
        sgn = -(-1) ** ((par[frm] + 1) * par[Y])
        _add(out, {(frm, Y, Z): c for Z, c in br.get((Y, to), {}).items()}, sgn)
    # - f([X,Y])
    for X, Y, c in L.inv.get(frm, []):
        _add(out, {(X, Y, to): c}, -1)
    return out


def triple_dict(entries):
    return {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in entries}


def triple_list(d):
    return [{"X": x, "Y": y, "Z": z, "coeff": str(c)} for (x, y, z), c in sorted(d.items())]


def delta_of_f(f, elem):
    """delta f for f = {(to, frm): phi}, from the elementary table."""
    out = {}
    for key, phi in f.items():
        _add(out, elem[key], phi)
    return out


def schema4(n):
    L = Layer1(n)
    maps = L.odd_map_basis()
    elem = {m: delta_elementary(L, *m) for m in maps}
    decomp = make_decomposer([elem[m] for m in maps], skip_dependent=True)
    ev = json.load(open(os.path.join(DATA, f"C_{n}_evaluated.json")))
    profs = []
    keys = {param_name(k): k for k in param_keys(n)}
    for p in ev["profiles"]:
        gam = triple_dict(p["gamma_evaluated"])
        co, resid_elim = decomp(gam)  # independent exact test: is gamma in the image of delta?
        gbk = {keys[q]: v for q, v in p["gb"].items()}
        f = trivializing_f(n, gbk)  # closed-form odd map (src/gauge_f.py)
        df = delta_of_f(f, elem)
        resid = dict(gam)
        _add(resid, df, -1)
        assert bool(resid) == bool(resid_elim), "closed-form f and elimination disagree"
        profs.append({
            "name": p["name"], "gb": p["gb"],
            "trivial": not resid,
            "f": [{"from": frm, "to": to, "coeff": str(c)} for (to, frm), c in sorted(f.items(), key=lambda t: (t[0][1], t[0][0]))],
            "delta_f": triple_list(df),
            "residual": triple_list(resid),
        })
    return {
        "schema_version": "5.0", "layer": 4,
        "algebra": ev["algebra"], "basis": ev["basis"], "parity": ev["parity"],
        "central_elements": ev["central_elements"],
        "coboundary_formula": "(df)(X,Y) = (-1)^{p(X)}[X,f(Y)] - (-1)^{(p(X)+1)p(Y)}[Y,f(X)] - f([X,Y])",
        "f_parametrization": "f(Z_j) = sum_i phi_ij Z_i, p(Z_i) != p(Z_j); elementary map = (from Z_j, to Z_i)",
        "elementary_maps": [
            {"from": frm, "to": to, "delta_f": triple_list(elem[(to, frm)])} for (to, frm) in maps
        ],
        "profiles": profs,
        "metadata": {"generated_by": "src/coboundary.py", "generation_date": "2026-10-06", "n": n,
                     "sources": [f"C_{n}_structure.json", f"C_{n}_evaluated.json"],
                     "number_of_elementary_maps": len(maps)},
    }


def main():
    for n in (1, 2, 3):
        d = schema4(n)
        with open(os.path.join(DATA, f"C_{n}_coboundary.json"), "w") as f:
            json.dump(d, f, indent=1, ensure_ascii=False)
        t = sum(p["trivial"] for p in d["profiles"])
        print(n, len(d["elementary_maps"]), "maps;", t, "/", len(d["profiles"]), "profiles with delta f = gamma")


if __name__ == "__main__":
    main()
