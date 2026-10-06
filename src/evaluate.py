"""Schema 3: evaluate the symbolic gamma (Schema 2) at concrete gb sign profiles.

usage: python src/evaluate.py     # writes data/C_{n}_evaluated.json
"""
import itertools
import json
import os
from fractions import Fraction

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load_gamma(n):
    return json.load(open(os.path.join(DATA, f"C_{n}_gamma.json")))


def profiles(n, params):
    """Named gb assignments (param -> int). params are ordered gb_a_1_{σ}_b_{j}_{s}."""
    P = {}
    P["all_plus"] = {p: 1 for p in params}
    P["all_minus"] = {p: -1 for p in params}
    P["alternating"] = {p: (-1) ** i for i, p in enumerate(params)}
    P["row_a_1_p_only"] = {p: (1 if "_a_1_p_" in p else 0) for p in params}
    P["row_a_1_m_only"] = {p: (1 if "_a_1_m_" in p else 0) for p in params}
    P["plus_sector_only"] = {p: (1 if p.endswith("_p") else 0) for p in params}
    P["minus_sector_only"] = {p: (1 if p.endswith("_m") else 0) for p in params}
    P["diagonal_pm"] = {p: (1 if (("_a_1_p_" in p) == p.endswith("_p")) else 0) for p in params}
    P["antidiagonal_pm"] = {p: (1 if (("_a_1_p_" in p) != p.endswith("_p")) else 0) for p in params}
    for p in params:
        P["unit_" + p] = {q: (1 if q == p else 0) for q in params}
    if n == 1:  # all 16 sign profiles
        for signs in itertools.product((1, -1), repeat=len(params)):
            name = "sign_" + "".join("+" if s > 0 else "-" for s in signs)
            P[name] = dict(zip(params, signs))
    return P


def evaluate(gamma_json, gb):
    """gamma entries evaluated at gb -> list of {X,Y,Z,coeff} (non-zero only)."""
    out = []
    for e in gamma_json["inhomogeneous_deformation"]["gamma_structure"]:
        v = sum(Fraction(t["coeff"]) * gb[t["param"]] for t in e["gamma"])
        if v:
            out.append({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": str(v)})
    return out


def schema3(n):
    g = load_gamma(n)
    params = g["inhomogeneous_deformation"]["gb_matrix"]["parameters"]
    prof = []
    for name, gb in profiles(n, params).items():
        prof.append({"name": name, "gb": gb, "gamma_evaluated": evaluate(g, gb)})
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": g["algebra"],
        "basis": g["basis"],
        "parity": g["parity"],
        "central_elements": g["central_elements"],
        "gb_matrix": g["inhomogeneous_deformation"]["gb_matrix"],
        "convention": g["inhomogeneous_deformation"]["gamma_convention"],
        "profiles": prof,
        "metadata": {"generated_by": "src/evaluate.py", "generation_date": "2026-10-06", "n": n,
                     "source": f"C_{n}_gamma.json"},
    }


def main():
    for n in (1, 2, 3):
        d = schema3(n)
        with open(os.path.join(DATA, f"C_{n}_evaluated.json"), "w") as f:
            json.dump(d, f, indent=1, ensure_ascii=False)
        print(n, len(d["profiles"]), "profiles")


if __name__ == "__main__":
    main()
