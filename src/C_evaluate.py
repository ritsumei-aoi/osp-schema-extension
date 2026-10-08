"""I06: Schema 3 (evaluated structure) for C(n+1).

Substitutes concrete values for the 4n deformation parameters gb into the symbolic gamma
structure of Schema 2 and writes the numerically evaluated deformed structure constants
        [X, Y]_gamma = sum_Z (c0 + c1 kappa) Z .

Profiles (handover: "representative sign profiles"):
    all_plus (representative, -> C_{n}_evaluated.json), all_minus, row_sign, column_sign,
    single_a1p_b1p, generic (distinct small rationals), zero (control).

Usage:  python src/C_evaluate.py [n ...]  -> data/C_{n}_evaluated.json, data/C_{n}_evaluated_<profile>.json
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscillator_algebra import Poly  # noqa: E402
from C_generators import CBasis, DATA_DIR  # noqa: E402
from C_gamma import load_json  # noqa: E402

REPRESENTATIVE = "all_plus"


def gb_labels(n: int) -> list:
    return [f"gb_a1{sigma}_b{j}{s}" for sigma in "pm" for j in range(1, n + 1) for s in "pm"]


def profiles(n: int) -> dict:
    labs = gb_labels(n)

    def by(fn):
        out = {}
        for lab in labs:
            sigma, j, s = lab[5], int(lab[8:-1]), lab[-1]
            out[lab] = str(Fraction(fn(sigma, j, s)))
        return out

    generic_vals = {}
    for i, lab in enumerate(labs):
        generic_vals[lab] = str(Fraction((-1) ** i * (i + 2), 1 + (i % 3)))   # 2, -1, 4/3, -5, 6, -7/3, ...
    return {
        "all_plus": {"description": "all gb = +1", "values": by(lambda s_, j, s: 1)},
        "all_minus": {"description": "all gb = -1", "values": by(lambda s_, j, s: -1)},
        "row_sign": {"description": "gb = +1 on the a_1_p row, -1 on the a_1_m row",
                     "values": by(lambda sigma, j, s: 1 if sigma == "p" else -1)},
        "column_sign": {"description": "gb = +1 for b_j_p columns, -1 for b_j_m columns",
                        "values": by(lambda sigma, j, s: 1 if s == "p" else -1)},
        "single_a1p_b1p": {"description": "only gb_a1p_b1p = 1, all others 0",
                           "values": by(lambda sigma, j, s: 1 if (sigma, j, s) == ("p", 1, "p") else 0)},
        "generic": {"description": "distinct small rationals of mixed sign (generic point)", "values": generic_vals},
        "zero": {"description": "all gb = 0 (undeformed control)", "values": by(lambda s_, j, s: 0)},
    }


# ---------------------------------------------------------------------------
def evaluate_gamma(schema2: dict, values: dict) -> dict:
    """Substitute into Schema 2 coeff_terms: returns {(X,Y): {Z: Fraction}} (non-zero only)."""
    vals = {k: Fraction(v) for k, v in values.items()}
    out: dict = {}
    for e in schema2["inhomogeneous_deformation"]["gamma"]:
        c = Poly.from_terms_dict(e["coeff_terms"]).subs(vals)
        assert c.is_constant(), f"unsubstituted parameter in {e}"
        v = c.constant()
        if v != 0:
            out.setdefault((e["X"], e["Y"]), {})[e["Z"]] = v
    return out


def recompute_gamma(n: int, values: dict) -> dict:
    """Independent path: run the oscillator algebra with numeric gb."""
    B = CBasis(n, gb_values={k: Fraction(v) for k, v in values.items()})
    _, gamma = B.structure_constants()
    return {k: {z: c.constant() for z, c in v.items()} for k, v in gamma.items()}


def build_schema3(n: int, profile: str, date: str | None = None, schema1=None, schema2=None) -> dict:
    schema1 = schema1 or load_json(f"C_{n}_structure.json")
    schema2 = schema2 or load_json(f"C_{n}_gamma.json")
    prof = profiles(n)[profile]
    values = prof["values"]
    gamma = evaluate_gamma(schema2, values)
    labels = schema1["basis"]["pbw_order"]
    zorder = labels + ["K"]
    sc0: dict = {}
    for e in schema1["structure_constants"]:
        sc0.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])

    gamma_entries, deformed = [], []
    for x in labels:
        for y in labels:
            g = gamma.get((x, y), {})
            c0 = sc0.get((x, y), {})
            for z in zorder:
                if z in g:
                    gamma_entries.append({"X": x, "Y": y, "Z": z, "coeff": str(g[z])})
                if z in g or z in c0:
                    deformed.append({"X": x, "Y": y, "Z": z,
                                     "coeff_0": str(c0.get(z, Fraction(0))),
                                     "coeff_kappa": str(g.get(z, Fraction(0)))})
    date = date or datetime.date.today().isoformat()
    return {
        "schema_version": "5.0",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})",
                    "structure_file": f"C_{n}_structure.json", "gamma_file": f"C_{n}_gamma.json"},
        "gb_profile": {"name": profile, "description": prof["description"],
                       "gb_matrix_rows": ["a_1_p", "a_1_m"],
                       "gb_matrix_columns": [f"b_{j}_{s}" for j in range(1, n + 1) for s in "pm"],
                       "values": values,
                       "matrix": [[values[f"gb_a1{sigma}_b{j}{s}"] for j in range(1, n + 1) for s in "pm"]
                                  for sigma in "pm"]},
        "evaluated_structure": {
            "description": "[X, Y]_gamma = sum_Z (coeff_0 + coeff_kappa * kappa) Z, with gb substituted; "
                           "gamma_evaluated lists the kappa-part alone",
            "deformed_structure_constants": deformed,
            "gamma_evaluated": gamma_entries,
            "statistics": {"nonzero_gamma_pairs": len(gamma), "gamma_entries": len(gamma_entries),
                           "gamma_entries_with_K": sum(1 for e in gamma_entries if e["Z"] == "K")},
        },
        "metadata": {"generated_by": "src/C_evaluate.py", "generation_date": date,
                     "conventions": "handover/notation.md"},
    }


def check_profile(n: int, profile: str, schema2=None) -> bool:
    """Consistency with Schema 2: substitution path == independent recomputation path."""
    schema2 = schema2 or load_json(f"C_{n}_gamma.json")
    values = profiles(n)[profile]["values"]
    return evaluate_gamma(schema2, values) == recompute_gamma(n, values)


def write_schema3(n: int, out_dir: str = DATA_DIR) -> list:
    paths = []
    s1, s2 = load_json(f"C_{n}_structure.json"), load_json(f"C_{n}_gamma.json")
    for prof in profiles(n):
        d = build_schema3(n, prof, schema1=s1, schema2=s2)
        names = [f"C_{n}_evaluated_{prof}.json"]
        if prof == REPRESENTATIVE:
            names.insert(0, f"C_{n}_evaluated.json")
        for name in names:
            path = os.path.join(out_dir, name)
            with open(path, "w") as fh:
                json.dump(d, fh, indent=1, ensure_ascii=False)
                fh.write("\n")
            paths.append(path)
    return paths


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    ok = True
    for n in ns:
        paths = write_schema3(n)
        s2 = load_json(f"C_{n}_gamma.json")
        for prof in profiles(n):
            good = check_profile(n, prof, s2)
            d = build_schema3(n, prof, schema2=s2)
            st = d["evaluated_structure"]["statistics"]
            print(f"n={n} profile={prof:15s} {st}  schema2-consistency={'OK' if good else 'FAIL'}")
            ok &= good
        print("  wrote:", ", ".join(os.path.basename(p) for p in paths))
    print("SUMMARY:", "all profiles consistent with Schema 2" if ok else "FAILURES PRESENT")
    sys.exit(0 if ok else 1)
