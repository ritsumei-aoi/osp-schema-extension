"""Schema 3 (evaluated structure) for C(n+1): substitute gb sign profiles into Schema 2.

Usage:  python3 src/C_evaluate.py      -> data/C_{n}_evaluated.json, n = 1, 2, 3
The full deformed bracket is [X,Y]_gb = (Schema 1 constants) + kappa * (gamma_evaluated).
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import gb_labels  # noqa: E402
from C_generators import global_order, write_json, frac_str, DATA_DIR  # noqa: E402
from C_gamma import evaluate_gamma, deformed_bracket_parts  # noqa: E402


def _parse(label):
    _, sig, j, s = label.split("_")
    return sig, int(j), s


def sign_profiles(n):
    """Representative gb assignments: name -> (description, {gb_label: int})."""
    labs = gb_labels(n)
    sg = {"p": 1, "m": -1}
    P = {
        "zero": ("control: undeformed (all gb = 0)", {g: 0 for g in labs}),
        "all_plus": ("all gb = +1", {g: 1 for g in labs}),
        "all_minus": ("all gb = -1", {g: -1 for g in labs}),
        "row_split": ("gb = +1 on row a_1_p, -1 on row a_1_m (sign of σ)",
                      {g: sg[_parse(g)[0]] for g in labs}),
        "column_split": ("gb = +1 on columns b_j_p, -1 on columns b_j_m (sign of s)",
                         {g: sg[_parse(g)[2]] for g in labs}),
        "alternating_j": ("gb = (-1)^(j+1) (sign alternates with boson index j)",
                          {g: (-1) ** (_parse(g)[1] + 1) for g in labs}),
        "checkerboard": ("gb = sign(σ)·sign(s)·(-1)^(j+1)",
                         {g: sg[_parse(g)[0]] * sg[_parse(g)[2]] * (-1) ** (_parse(g)[1] + 1)
                          for g in labs}),
        "unit_p_1_p": ("single non-zero parameter gb_p_1_p = +1", {g: int(g == "gb_p_1_p") for g in labs}),
        "unit_m_1_m": ("single non-zero parameter gb_m_1_m = +1", {g: int(g == "gb_m_1_m") for g in labs}),
    }
    return P


def load_gamma_symbolic(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_gamma.json")) as f:
        d = json.load(f)
    gamma = {}
    for e in d["inhomogeneous_deformation"]["gamma"]:
        gamma.setdefault((e["X"], e["Y"]), {})[e["Z"]] = {g: Fraction(c) for g, c in e["coeff"].items()}
    return gamma


def build_schema3(n, date=None):
    date = date or datetime.date.today().isoformat()
    basis = global_order(n)
    idx = {x: i for i, x in enumerate(basis + ["K"])}
    gamma = load_gamma_symbolic(n)
    cols = [f"b_{j}_{s}" for j in range(1, n + 1) for s in ("p", "m")]
    profiles = []
    for name, (desc, gb) in sign_profiles(n).items():
        ev = evaluate_gamma(gamma, gb)
        entries = [{"X": X, "Y": Y, "Z": Z, "coeff": frac_str(ev[(X, Y)][Z])}
                   for (X, Y) in sorted(ev, key=lambda p: (idx[p[0]], idx[p[1]]))
                   for Z in sorted(ev[(X, Y)], key=idx.get)]
        profiles.append({
            "name": name, "description": desc,
            "gb": {g: v for g, v in gb.items()},
            "gb_matrix": [[gb[f"gb_{sig}_{c[2:]}"] for c in cols] for sig in ("p", "m")],
            "gamma_evaluated": entries,
            "statistics": {"entries": len(entries),
                           "central_entries": sum(e["Z"] == "K" for e in entries),
                           "nonzero_pairs": len(ev)},
        })
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})", "osp": f"osp(2|{2*n})"},
        "structure_ref": f"C_{n}_structure.json",
        "gamma_ref": f"C_{n}_gamma.json",
        "basis_order": basis,
        "evaluation": {
            "bracket_convention": "[X,Y]_gb = [X,Y]_0 (structure_ref) + κ Σ_Z gamma_evaluated[X,Y,Z] Z;  Z = 'K' is the central part",
            "gb_matrix_layout": {"rows": ["a_1_p", "a_1_m"], "columns": cols},
            "profiles": profiles,
        },
        "metadata": {"generated_by": "src/C_evaluate.py", "generation_date": date,
                     "conventions": "handover/notation.md"},
    }


def check_against_engine(n, schema3):
    """Independent path: recompute gamma in U(A) with numeric gb and compare to the file."""
    mismatches = {}
    for prof in schema3["evaluation"]["profiles"]:
        stored = {}
        for e in prof["gamma_evaluated"]:
            stored.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
        direct = {p: g for p, (_, g) in deformed_bracket_parts(n, prof["gb"]).items() if g}
        mismatches[prof["name"]] = sum(1 for p in set(stored) | set(direct)
                                       if stored.get(p, {}) != direct.get(p, {}))
    return mismatches


def main(ns=(1, 2, 3)):
    for n in ns:
        s = build_schema3(n)
        p = write_json(s, f"C_{n}_evaluated.json")
        stats = {pr["name"]: pr["statistics"]["entries"] for pr in s["evaluation"]["profiles"]}
        print(f"n={n}: entries per profile {stats} -> {os.path.relpath(p)}")
        mm = check_against_engine(n, s)
        print(f"      Schema 2 vs direct U(A) recomputation, mismatching pairs: {mm}")


if __name__ == "__main__":
    main()
