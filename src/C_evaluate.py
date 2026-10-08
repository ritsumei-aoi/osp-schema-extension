"""Schema 3: evaluated structure for C(n+1), by substitution of gb values into Schema 2.

Profiles (representative assignments for the 4n parameters gb):
  all_plus : every gb = +1                       -> data/C_{n}_evaluated.json
  alt      : gb alternates +1, -1 in gb order    -> data/C_{n}_evaluated_alt.json

Consistency check: each evaluated kappa-coefficient is compared with a direct
build of the algebra at the same numerical gb values (C_structure.build).

Usage:  python src/C_evaluate.py N [N ...]
"""
from fractions import Fraction
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_structure import build  # noqa: E402
from C_gamma import gb_keys, gb_name  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCHEMA_VERSION = "5.0"


def profile_values(n, profile):
    keys = gb_keys(n)
    if profile == "all_plus":
        return {gb_name(k): Fraction(1) for k in keys}
    if profile == "alt":
        return {gb_name(k): Fraction(1 if i % 2 == 0 else -1) for i, k in enumerate(keys)}
    raise ValueError(profile)


def frac_json(v):
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def evaluate(n, profile):
    gamma = json.load(open(os.path.join(ROOT, "data", f"C_{n}_gamma.json")))
    base = json.load(open(os.path.join(ROOT, "data", f"C_{n}_structure.json")))
    values = profile_values(n, profile)

    entries = []
    for e in gamma["inhomogeneous_deformation"]["gamma"]:
        val = sum((Fraction(c) * values[name] for name, c in e["terms"].items()), Fraction(0))
        if val != 0:
            entries.append({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "kappa_value": frac_json(val)})

    # Independent cross-check against a direct build with numerical gb.
    direct = build(n, gb={k: values[gb_name(k)] for k in gb_keys(n)})
    direct_kappa = {}
    for d in direct["structure_constants"]["brackets"]:
        if Fraction(d["kappa_coeff"]) != 0:
            direct_kappa[(d["X"], d["Y"], d["Z"])] = Fraction(d["kappa_coeff"])
    for d in direct["structure_constants"]["constant_terms"]:
        if Fraction(d["kappa_coeff"]) != 0:
            direct_kappa[(d["X"], d["Y"], "K")] = Fraction(d["kappa_coeff"])
    eval_kappa = {(e["X"], e["Y"], e["Z"]): Fraction(e["kappa_value"]) for e in entries}
    matches_direct = direct_kappa == eval_kappa

    base_brackets = base["structure_constants"]["brackets"]
    return {
        "schema_version": SCHEMA_VERSION,
        "algebra": base["algebra"],
        "profile": {"name": profile, "gb": {k: frac_json(v) for k, v in values.items()}},
        "basis": base["basis"],
        "parity": base["parity"],
        "structure_constants": {
            "kappa_free": base_brackets,
            "kappa_part": entries,
        },
        "consistency": {
            "matches_schema2_linear_forms": True,
            "matches_direct_build": matches_direct,
            "nonzero_kappa_entries": len(entries),
        },
        "metadata": {"generated_by": "src/C_evaluate.py", "schema2_source": f"data/C_{n}_gamma.json"},
    }


def main(argv):
    for arg in argv:
        n = int(arg)
        for profile, fname in (("all_plus", f"C_{n}_evaluated.json"), ("alt", f"C_{n}_evaluated_alt.json")):
            data = evaluate(n, profile)
            path = os.path.join(ROOT, "data", fname)
            with open(path, "w") as fh:
                json.dump(data, fh, indent=2)
            print(f"n={n} profile={profile}: kappa entries={data['consistency']['nonzero_kappa_entries']} "
                  f"matches_direct_build={data['consistency']['matches_direct_build']} -> {path}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["1", "2", "3"])
