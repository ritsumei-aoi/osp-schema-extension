"""Schema 3 (evaluated structure) for C(n+1): substitute concrete gb values
into the symbolic gamma of C_{n}_gamma.json and write C_{n}_evaluated.json.

Usage:  python3 src/C_evaluate.py [n ...]      (default: 1 2 3)
"""
import datetime
import os
import random
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import load_gamma  # noqa: E402
from C_generators import DATA_DIR, SIGNS, frac_str, write_json  # noqa: E402
from oscillator import gb_label  # noqa: E402


def gb_profiles(n):
    """Representative assignments of the 4n gb parameters (values in {-1, 0, +1})."""
    labels = [(sg, j, s) for sg in SIGNS for j in range(1, n + 1) for s in SIGNS]
    prof = {}

    def mk(fn):
        return {gb_label(sg, j, s): fn(sg, j, s) for sg, j, s in labels}

    prof["zero"] = mk(lambda sg, j, s: 0)
    prof["all_plus"] = mk(lambda sg, j, s: 1)
    prof["all_minus"] = mk(lambda sg, j, s: -1)
    prof["row_sign"] = mk(lambda sg, j, s: 1 if sg == "p" else -1)          # a_1^+ row +, a_1^- row -
    prof["col_sign"] = mk(lambda sg, j, s: 1 if s == "p" else -1)           # b^+ cols +, b^- cols -
    prof["checkerboard"] = mk(lambda sg, j, s: 1 if (sg == s) else -1)      # +1 iff sigma == s
    prof["index_parity"] = mk(lambda sg, j, s: (-1) ** (j + 1))             # sign alternates with j
    prof["single_p_1_p"] = mk(lambda sg, j, s: 1 if (sg, j, s) == ("p", 1, "p") else 0)
    rng = random.Random(20261006 + n)
    prof["random_signs"] = mk(lambda sg, j, s: rng.choice([-1, 1]))
    return prof


def evaluate(gam, values):
    """{(X,Y): {Z: {gb: c}}} -> {(X,Y): {Z: value}} (zeros dropped)."""
    out = {}
    for key, res in gam.items():
        r = {}
        for Z, cs in res.items():
            v = sum((c * values[g] for g, c in cs.items()), Fraction(0))
            if v != 0:
                r[Z] = v
        if r:
            out[key] = r
    return out


def build_schema3(n):
    d2, gam = load_gamma(n)
    profs = gb_profiles(n)
    rows = d2["gb_matrix"]["entries"]
    evaluated = {}
    for name, vals in profs.items():
        ev = evaluate(gam, vals)
        g_list, k_list = [], []
        for (X, Y), r in ev.items():
            for Z, v in r.items():
                (k_list if Z == "K" else g_list).append({"X": X, "Y": Y, "Z": Z, "coeff": frac_str(v)})
        evaluated[name] = {
            "gb_values": vals,
            "gb_matrix_values": [[vals[g] for g in row] for row in rows],
            "gamma": g_list,
            "central_component": k_list,
            "n_gamma_entries": len(g_list),
            "n_central_entries": len(k_list),
        }
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
                    "structure_file": f"C_{n}_structure.json", "gamma_file": f"C_{n}_gamma.json"},
        "convention": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y) with gb substituted; [X,Y]_0 in structure_file",
        "gb_matrix_layout": {"rows": d2["gb_matrix"]["rows"], "cols": d2["gb_matrix"]["cols"], "entries": rows},
        "profiles": evaluated,
        "metadata": {"generated_by": "src/C_evaluate.py",
                     "generation_date": datetime.date.today().isoformat(),
                     "profile_names": list(profs),
                     "notation": "handover/notation.md"},
    }


def check_against_schema2(n, d3):
    """Every evaluated entry equals sum(coeff * gb) from Schema 2, and nothing is missing."""
    _, gam = load_gamma(n)
    bad = 0
    for name, p in d3["profiles"].items():
        got = {}
        for e in p["gamma"] + p["central_component"]:
            got[(e["X"], e["Y"], e["Z"])] = Fraction(e["coeff"])
        expect = {}
        for (X, Y), res in gam.items():
            for Z, cs in res.items():
                v = sum((c * p["gb_values"][g] for g, c in cs.items()), Fraction(0))
                if v != 0:
                    expect[(X, Y, Z)] = v
        bad += int(got != expect)
    return bad


def main(ns):
    import json
    for n in ns:
        d3 = build_schema3(n)
        p = write_json(d3, f"C_{n}_evaluated.json")
        with open(p) as f:
            back = json.load(f)
        bad = check_against_schema2(n, back)
        summary = ", ".join(f"{k}:{v['n_gamma_entries']}+{v['n_central_entries']}K"
                            for k, v in d3["profiles"].items())
        print(f"n={n}: -> {os.path.relpath(p)}  mismatching profiles vs Schema 2: {bad}\n   {summary}")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
