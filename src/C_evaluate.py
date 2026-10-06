"""Schema 3: evaluated structure for C(n+1) (gb substituted by concrete numbers).

Reads data/C_{n}_structure.json and data/C_{n}_gamma.json and writes
  data/C_{n}_evaluated.json              (profile 'all_plus', the representative assignment)
  data/C_{n}_evaluated_<profile>.json    (other representative sign profiles)
Usage: python src/C_evaluate.py
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import frac_str  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def parse_name(name):
    """'gb_a_1_p_b_2_m' -> (sigma, j, s)"""
    t = name.split("_")
    return t[3], int(t[5]), t[6]


def profiles(n, names):
    """Representative sign profiles for the 4n gb parameters."""
    out = {}
    out["all_plus"] = {x: 1 for x in names}
    out["zero"] = {x: 0 for x in names}
    out["alternating"] = {x: (1 if i % 2 == 0 else -1) for i, x in enumerate(names)}
    out["fermion_sign"] = {x: (1 if parse_name(x)[0] == "p" else -1) for x in names}
    out["boson_sign"] = {x: (1 if parse_name(x)[2] == "p" else -1) for x in names}
    out["single_first"] = {x: (1 if i == 0 else 0) for i, x in enumerate(names)}
    return out


def evaluate(structure, gamma, assignment, profile, date=None):
    n = structure["algebra"]["n"]
    names = structure["basis"]["odd"] + structure["basis"]["even"]
    idx = {x: i for i, x in enumerate(names + ["K"])}
    c0 = {}
    for e in structure["structure_constants"]:
        c0[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])
    ck = {}
    for e in gamma["inhomogeneous_deformation"]["gamma_structure"]:
        v = sum(Fraction(c) * Fraction(assignment[p]) for p, c in e["coeff"].items())
        if v:
            ck[(e["X"], e["Y"], e["Z"])] = v
    keys = sorted(set(c0) | set(ck), key=lambda t: (idx[t[0]], idx[t[1]], idx[t[2]]))
    entries = [{"X": X, "Y": Y, "Z": Z, "coeff": frac_str(c0.get((X, Y, Z), 0)),
                "kappa_coeff": frac_str(ck.get((X, Y, Z), 0))} for (X, Y, Z) in keys]
    return {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": structure["algebra"],
        "central_elements": structure["central_elements"],
        "basis": structure["basis"],
        "parity": structure["parity"],
        "gb_assignment": {"profile": profile, "values": {p: frac_str(assignment[p]) for p in assignment}},
        "evaluated_structure": {
            "description": "[X,Y]_gamma = sum_Z (coeff + kappa_coeff * kappa) Z ; kappa_coeff = gamma(X,Y)_Z evaluated at gb. "
                           "Z='K' is the central constant (kappa*K = kappa); its coeff is always 0.",
            "entries": entries,
        },
        "metadata": {"generated_by": "src/C_evaluate.py",
                     "generation_date": date or datetime.date.today().isoformat(),
                     "source_files": [f"C_{n}_structure.json", f"C_{n}_gamma.json"]},
    }


def main():
    for n in (1, 2, 3):
        st = json.load(open(os.path.join(DATA_DIR, f"C_{n}_structure.json")))
        gm = json.load(open(os.path.join(DATA_DIR, f"C_{n}_gamma.json")))
        params = gm["inhomogeneous_deformation"]["parameters"]
        for prof, assign in profiles(n, params).items():
            d = evaluate(st, gm, assign, prof)
            fn = f"C_{n}_evaluated.json" if prof == "all_plus" else f"C_{n}_evaluated_{prof}.json"
            with open(os.path.join(DATA_DIR, fn), "w") as f:
                json.dump(d, f, indent=1, ensure_ascii=False)
            print(f"{fn}: entries={len(d['evaluated_structure']['entries'])}, "
                  f"kappa-nonzero={sum(e['kappa_coeff'] != '0' for e in d['evaluated_structure']['entries'])}")


if __name__ == "__main__":
    main()
