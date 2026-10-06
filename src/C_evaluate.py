"""Schema 3 (evaluated structure) for C(n+1): substitute concrete gb sign profiles into Schema 2.

Usage:  python3 src/C_evaluate.py        (writes data/C_{1,2,3}_evaluated.json)
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import DATA, make_algebra, write_json  # noqa: E402
from C_oscillator import ONE, lin_from_json  # noqa: E402

PRIMARY = "all_plus"


def gb_profiles(n):
    """Representative assignments of the 4n parameters (values in {-1, 0, +1})."""
    names = [f"gb_a1{sg}_b{j}{s}" for sg in "pm" for j in range(1, n + 1) for s in "pm"]

    def prof(fn):
        return {nm: fn(nm) for nm in names}

    return [
        ("all_plus", "every gb = +1 (primary profile)", prof(lambda nm: 1)),
        ("all_minus", "every gb = -1", prof(lambda nm: -1)),
        ("row_sign", "gb_{a1p,*} = +1, gb_{a1m,*} = -1", prof(lambda nm: 1 if nm[5] == "p" else -1)),
        ("boson_sign", "gb_{*,b_j^+} = +1, gb_{*,b_j^-} = -1", prof(lambda nm: 1 if nm[-1] == "p" else -1)),
        ("alternating_j", "gb = (-1)^{j+1} (sign alternates with the boson index j)",
         prof(lambda nm: 1 if int(nm[8:-1]) % 2 == 1 else -1)),
        ("single_a1p_b1p", "only gb_{a1p,b1p} = +1, all others 0", prof(lambda nm: int(nm == "gb_a1p_b1p"))),
        ("zero", "all gb = 0 (undeformed control)", prof(lambda nm: 0)),
    ]


def evaluate_lin(c, values):
    return sum((Fraction(v) * Fraction(values[k]) for k, v in c.items()), Fraction(0))


def load_schema2(n):
    with open(os.path.join(DATA, f"C_{n}_gamma.json")) as fh:
        return json.load(fh)


def evaluate_profile(d2, values):
    idf = d2["inhomogeneous_deformation"]
    gam = []
    for e in idf["gamma_coefficients"]:
        v = evaluate_lin(lin_from_json(e["coeff"]), values)
        if v:
            gam.append({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": str(v)})
    cen = []
    for e in idf["gamma_central"]:
        v = evaluate_lin(lin_from_json(e["coeff"]), values)
        if v:
            cen.append({"X": e["X"], "Y": e["Y"], "coeff": str(v)})
    return gam, cen


def direct_evaluation(n, values):
    """Independent path: numeric gb inserted directly in [b, a] = -gb kappa, brackets recomputed."""
    alg = make_algebra(n, gb_values=values)
    gam, cen = {}, {}
    for x in alg.basis:
        for y in alg.basis:
            p1 = alg.decompose(alg.bracket_labels(x, y)).get(1, {})
            for z, c in p1.items():
                v = c.get(ONE, Fraction(0))
                if not v:
                    continue
                if z == "K":
                    cen[(x, y)] = v
                else:
                    gam[(x, y, z)] = v
    return gam, cen


def build_schema3(n, direct_check=True):
    d2 = load_schema2(n)
    profiles = []
    for name, desc, values in gb_profiles(n):
        gam, cen = evaluate_profile(d2, values)
        entry = {
            "name": name,
            "description": desc,
            "gb_values": {k: str(v) for k, v in values.items()},
            "gb_matrix_values": [[str(values[s]) for s in row]
                                 for row in d2["inhomogeneous_deformation"]["gb_matrix"]["symbols"]],
            "gamma_evaluated": gam,
            "gamma_central_evaluated": cen,
        }
        if direct_check:
            dg, dc = direct_evaluation(n, values)
            entry["check_direct_oscillator_substitution"] = (
                dg == {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in gam}
                and dc == {(e["X"], e["Y"]): Fraction(e["coeff"]) for e in cen})
        profiles.append(entry)
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": d2["algebra"],
        "basis": d2["basis"],
        "parity": d2["parity"],
        "bracket_form": d2["inhomogeneous_deformation"]["bracket_form"],
        "undeformed_structure_constants": f"C_{n}_structure.json (κ⁰ part, unchanged by gb)",
        "primary_profile": PRIMARY,
        "profiles": profiles,
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": datetime.date.today().isoformat(),
            "source_schema2": f"C_{n}_gamma.json",
            "conventions": "handover/notation.md",
        },
    }


def main(ns=(1, 2, 3)):
    for n in ns:
        obj = build_schema3(n)
        p = write_json(obj, f"C_{n}_evaluated.json")
        for pr in obj["profiles"]:
            print(f"n={n} {pr['name']:>15}: gamma entries={len(pr['gamma_evaluated']):5d} "
                  f"central={len(pr['gamma_central_evaluated']):4d} "
                  f"direct-substitution check={pr['check_direct_oscillator_substitution']}")
        print("  ->", p)


if __name__ == "__main__":
    main()
