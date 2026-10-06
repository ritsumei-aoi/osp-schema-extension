"""Schema 3 (evaluated structure) for C(n+1): substitute sign profiles into the Schema 2 gb matrix.

Usage:  python3 src/C_evaluate.py      # writes data/C_{1,2,3}_evaluated.json and checks them
"""
from __future__ import annotations

import datetime
import json
import os
import random
import sys
from fractions import Fraction

import sympy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import _parse_lin, gb_symbols  # noqa: E402
from C_generators import DATA_DIR, SCHEMA_VERSION, write_json  # noqa: E402


def sign_profiles(n: int) -> list[dict]:
    """Representative assignments of the 4n parameters gb_{sigma,j,s}."""
    syms = gb_symbols(n)

    def prof(name, desc, f):
        return {"name": name, "description": desc, "gb_values": {s: f(s) for s in syms}}

    def parts(s):  # gb_{sigma}_{j}_{s}
        _, sig, j, b = s.split("_")
        return sig, int(j), b

    rng = random.Random(20261006 + n)
    rand = {s: rng.choice([1, -1]) for s in syms}
    first = syms[0]
    return [
        prof("zero", "undeformed reference: all gb = 0", lambda s: 0),
        prof("all_plus", "all gb = +1", lambda s: 1),
        prof("all_minus", "all gb = -1", lambda s: -1),
        prof("single_p1p", f"only {first} = +1, others 0", lambda s: 1 if s == first else 0),
        prof("fermion_sign", "gb_{a_1^sigma, b} = +1 for sigma=+, -1 for sigma=-", lambda s: 1 if parts(s)[0] == "p" else -1),
        prof("boson_sign", "gb_{a, b_j^s} = +1 for s=+, -1 for s=-", lambda s: 1 if parts(s)[2] == "p" else -1),
        prof("alternating_j", "gb = (-1)^(j+1) (sign alternates with the boson mode j)",
             lambda s: (-1) ** (parts(s)[1] + 1)),
        prof("random_signs", f"random +-1 signs (seed {20261006 + n})", lambda s: rand[s]),
    ]


def evaluate(gamma_entries: list, values: dict) -> list[dict]:
    out = []
    for e in gamma_entries:
        v = _parse_lin(e["coeff"]).evaluate(values)
        if v:
            out.append({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": str(v)})
    return out


def build_evaluated(n: int, gam: dict) -> dict:
    ent = gam["inhomogeneous_deformation"]["gamma"]
    profiles = []
    for p in sign_profiles(n):
        p = dict(p)
        p["gamma"] = evaluate(ent, p["gb_values"])
        profiles.append(p)
    return {
        "schema_version": SCHEMA_VERSION,
        "algebra": gam["algebra"],
        "basis_ref": gam["basis_ref"],
        "gamma_ref": f"C_{n}_gamma.json",
        "central_elements": gam["central_elements"],
        "evaluated_bracket": "[X,Y]_gamma = [X,Y]_0 (Schema 1) + kappa * sum_Z coeff * Z ;  Z='K' = central kappa*1",
        "profiles": profiles,
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": datetime.date.today().isoformat(),
            "notation": "handover/notation.md",
        },
    }


def check(n: int, ev: dict, gam: dict) -> dict:
    """Independent re-evaluation with sympy.subs + linearity / schema checks."""
    ent = gam["inhomogeneous_deformation"]["gamma"]
    exprs = {(e["X"], e["Y"], e["Z"]): sympy.sympify(e["coeff"]) for e in ent}
    res = {"basis_ref_match": ev["basis_ref"] == gam["basis_ref"], "subs_match": True,
           "profile_count": len(ev["profiles"]), "zero_profile_empty": True, "linearity_ok": True,
           "values_are_signs": True}
    by_name = {}
    for p in ev["profiles"]:
        if not set(p["gb_values"]) == set(gb_symbols(n)):
            res["subs_match"] = False
        if any(v not in (-1, 0, 1) for v in p["gb_values"].values()):
            res["values_are_signs"] = False
        subs = {sympy.Symbol(k): v for k, v in p["gb_values"].items()}
        expected = {k: sympy.nsimplify(e.subs(subs)) for k, e in exprs.items()}
        expected = {k: v for k, v in expected.items() if v != 0}
        got = {(g["X"], g["Y"], g["Z"]): sympy.Rational(g["coeff"]) for g in p["gamma"]}
        if expected != got:
            res["subs_match"] = False
        by_name[p["name"]] = {k: Fraction(str(v)) for k, v in got.items()}
    if by_name["zero"]:
        res["zero_profile_empty"] = False
    if {k: -v for k, v in by_name["all_plus"].items()} != by_name["all_minus"]:
        res["linearity_ok"] = False
    res["passed"] = all(v for k, v in res.items() if k != "profile_count")
    return res


def main(ns=(1, 2, 3)) -> int:
    ok = True
    for n in ns:
        with open(os.path.join(DATA_DIR, f"C_{n}_gamma.json")) as fh:
            gam = json.load(fh)
        ev = build_evaluated(n, gam)
        write_json(ev, f"C_{n}_evaluated.json")
        res = check(n, ev, gam)
        sizes = ", ".join(f"{p['name']}:{len(p['gamma'])}" for p in ev["profiles"])
        print(f"n={n}: profiles [{sizes}]; checks {res}")
        ok &= res["passed"]
    print("OVERALL:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
