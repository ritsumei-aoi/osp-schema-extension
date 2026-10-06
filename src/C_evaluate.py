"""Schema 3 (evaluated structure): substitute concrete numbers for the gb parameters in Schema 2.

Usage: python src/C_evaluate.py     (writes data/C_{n}_evaluated.json  [profile "plus", all gb = +1]
                                      and data/C_{n}_evaluated_<profile>.json for the other profiles)
"""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import C_generators as cg  # noqa: E402

DATA = cg.DATA

PROFILE_NAMES = ["plus", "minus", "alt", "zero", "single"]


def profile(name, n):
    """gb assignment {symbol: Fraction} for a named profile (symbols in gb_matrix order, column-major by (j,s,σ))."""
    syms = cg.gb_names(n)
    if name == "plus":
        return {s: F(1) for s in syms}
    if name == "minus":
        return {s: F(-1) for s in syms}
    if name == "alt":
        return {s: F(1 if i % 2 == 0 else -1) for i, s in enumerate(syms)}
    if name == "zero":
        return {s: F(0) for s in syms}
    if name == "single":
        return {s: F(1 if i == 0 else 0) for i, s in enumerate(syms)}
    raise KeyError(name)


def substitute(coeff_map, values):
    return sum((F(c) * values[sym] for sym, c in coeff_map.items()), F(0))


def evaluate(s2, values):
    dfm = s2["inhomogeneous_deformation"]
    gam = []
    for e in dfm["gamma"]:
        v = substitute(e["coeff"], values)
        if v != 0:
            gam.append({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": cg.fstr(v)})
    cen = []
    for e in dfm["central_component"]["entries"]:
        v = substitute(e["coeff"], values)
        if v != 0:
            cen.append({"X": e["X"], "Y": e["Y"], "coeff": cg.fstr(v)})
    return gam, cen


def schema3(n, name):
    s2 = json.load(open(DATA / f"C_{n}_gamma.json"))
    values = profile(name, n)
    gam, cen = evaluate(s2, values)
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": s2["algebra"],
        "structure_file": f"C_{n}_structure.json",
        "gamma_file": f"C_{n}_gamma.json",
        "profile": {"name": name, "gb_values": {s: cg.fstr(v) for s, v in values.items()}},
        "evaluated_deformation": {
            "description": "[X,Y]_γ = [X,Y]_0 + κ γ(X,Y) with gb substituted; γ g-valued, central part = coefficient of κ·K",
            "gamma": gam,
            "central_component": cen,
            "counts": {"gamma_entries": len(gam), "central_entries": len(cen)},
        },
        "metadata": {"generated_by": "src/C_evaluate.py", "generation_date": "2026-10-06"},
    }


def output_path(n, name):
    return DATA / (f"C_{n}_evaluated.json" if name == "plus" else f"C_{n}_evaluated_{name}.json")


def main(ns=(1, 2, 3)):
    for n in ns:
        for name in PROFILE_NAMES:
            d = schema3(n, name)
            cg.write_json(output_path(n, name), d)
            c = d["evaluated_deformation"]["counts"]
            print(f"n={n} profile={name}: gamma entries={c['gamma_entries']} central entries={c['central_entries']}")


if __name__ == "__main__":
    main()
