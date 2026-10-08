"""
Schema 3 generator (Issue I06): evaluated deformation structure for C(n+1).

Substitutes a concrete numeric assignment ("profile") for the 4n deformation
parameters gb_* into the symbolic Schema 2 data (C_{n}_gamma.json) and writes

    data/C_{n}_evaluated.json               (representative profile: all_plus)
    data/C_{n}_evaluated_<profile>.json     (other profiles)

Each file contains the evaluated gamma entries and the full deformed structure
constants  [X,Y}_gamma = coeff_0 * Z + kappa * coeff_kappa * Z.

Usage: python3 src/C_evaluate.py [n ...]   (default 1 2 3; all profiles)
"""
from __future__ import annotations

import datetime
import json
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import C_generators as G  # noqa: E402
import C_gamma as Gm  # noqa: E402
from osc_algebra import gb_label  # noqa: E402

DATA_DIR = G.DATA_DIR
REPRESENTATIVE = "all_plus"


def _parse(label):
    # gb_a1{sigma}_b{k}{s}
    _, a, b = label.split("_")
    return a[-1], int(b[1:-1]), b[-1]


def profile_values(name, n):
    """Return {gb_label: Fraction} for the named sign profile."""
    labels = [gb_label(sig, k, s) for sig in "pm" for k in range(1, n + 1) for s in "pm"]
    if name == "all_plus":
        return {l: Fraction(1) for l in labels}
    if name == "zero":
        return {l: Fraction(0) for l in labels}
    if name == "single":           # only gb_{+,1,+} = 1
        return {l: Fraction(1 if l == "gb_a1p_b1p" else 0) for l in labels}
    if name == "alternating":      # +1 if sigma == s else -1
        return {l: Fraction(1 if _parse(l)[0] == _parse(l)[2] else -1) for l in labels}
    if name == "random":           # deterministic, values in {-2,-1,1,2}
        rng = random.Random(20261009 + n)
        return {l: Fraction(rng.choice([-2, -1, 1, 2])) for l in labels}
    raise KeyError(name)


PROFILES = ["all_plus", "zero", "single", "alternating", "random"]


def evaluate_entries(gamma_doc, values):
    """Substitute values into Schema 2 entries; merge terms; drop zeros."""
    acc = {}
    for e in gamma_doc["inhomogeneous_deformation"]["entries"]:
        c = sum(Fraction(coef) * values[g] for g, coef in e["linear_form"].items())
        key = (e["X"], e["Y"], e["Z"])
        acc[key] = acc.get(key, Fraction(0)) + c
    return [{"X": X, "Y": Y, "Z": Z, "coeff": str(c)}
            for (X, Y, Z), c in acc.items() if c != 0]


def build_schema3(n, profile=REPRESENTATIVE, date=None):
    date = date or datetime.date.today().isoformat()
    g2 = Gm.load_gamma(n)
    s1 = G.load_structure(n)
    values = profile_values(profile, n)
    gamma_entries = evaluate_entries(g2, values)
    # merged deformed structure constants
    merged = {}
    for e in s1["structure_constants"]:
        merged[(e["X"], e["Y"], e["Z"])] = [e["coeff"], "0"]
    for e in gamma_entries:
        key = (e["X"], e["Y"], e["Z"])
        merged.setdefault(key, ["0", "0"])[1] = e["coeff"]
    deformed = [{"X": X, "Y": Y, "Z": Z, "coeff_0": c0, "coeff_kappa": ck}
                for (X, Y, Z), (c0, ck) in merged.items()]
    n_K = sum(1 for e in gamma_entries if e["Z"] == "K")
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": g2["algebra"],
        "schema1_file": f"C_{n}_structure.json",
        "schema2_file": f"C_{n}_gamma.json",
        "profile": profile,
        "gb_assignment": {l: str(v) for l, v in values.items()},
        "gb_matrix": {"rows": g2["gb_matrix"]["rows"], "columns": g2["gb_matrix"]["columns"],
                      "values": [[str(values[l]) for l in row] for row in g2["gb_matrix"]["labels"]]},
        "evaluated_gamma": {
            "description": "gamma(X,Y) = sum_Z coeff * Z with gb substituted; Z in basis or K",
            "entries": gamma_entries,
        },
        "deformed_structure_constants": {
            "description": "[X,Y}_gamma = sum_Z (coeff_0 + kappa * coeff_kappa) * Z",
            "entries": deformed,
        },
        "summary": {
            "gamma_entries": len(gamma_entries),
            "gamma_entries_with_Z_K": n_K,
            "pairs_with_nonzero_gamma": len({(e["X"], e["Y"]) for e in gamma_entries}),
        },
        "metadata": {"generated_by": "src/C_evaluate.py", "generation_date": date},
    }


def evaluated_path(n, profile=REPRESENTATIVE):
    suffix = "" if profile == REPRESENTATIVE else f"_{profile}"
    return os.path.join(DATA_DIR, f"C_{n}_evaluated{suffix}.json")


def write_schema3(n, profile=REPRESENTATIVE):
    d = build_schema3(n, profile)
    with open(evaluated_path(n, profile), "w") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    return d


def load_evaluated(n, profile=REPRESENTATIVE):
    with open(evaluated_path(n, profile)) as f:
        return json.load(f)


def check_against_schema2(n, profile=REPRESENTATIVE):
    """Independent re-substitution using sympy on the `coeff` strings (not linear_form)."""
    import sympy
    d3 = load_evaluated(n, profile)
    g2 = Gm.load_gamma(n)
    subs = {sympy.Symbol(l): sympy.Rational(v) for l, v in d3["gb_assignment"].items()}
    acc = {}
    for e in g2["inhomogeneous_deformation"]["entries"]:
        c = sympy.sympify(e["coeff"]).subs(subs)
        key = (e["X"], e["Y"], e["Z"])
        acc[key] = acc.get(key, 0) + c
    expect = {k: sympy.Rational(v) for k, v in acc.items() if v != 0}
    got = {(e["X"], e["Y"], e["Z"]): sympy.Rational(e["coeff"])
           for e in d3["evaluated_gamma"]["entries"]}
    return expect == got


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for n in ns:
        for prof in PROFILES:
            d = write_schema3(n, prof)
            ok = check_against_schema2(n, prof)
            s = d["summary"]
            print(f"C({n+1}) n={n} profile={prof:12s}: {s['gamma_entries']:4d} gamma terms "
                  f"({s['gamma_entries_with_Z_K']} with Z=K), schema2 check={ok} "
                  f"-> {os.path.relpath(evaluated_path(n, prof), G.ROOT)}")
