"""Schema 3 (evaluated structure) for C(n+1): substitute concrete gb values into Schema 2.

Profiles (gb_{σ,j,s}, σ = fermion sign, s = boson sign):
  allplus  : +1 for all            -> data/C_{n}_evaluated.json  (default profile)
  allminus : -1 for all            -> data/C_{n}_evaluated_allminus.json
  checker  : +1 if σ == s else -1  -> data/C_{n}_evaluated_checker.json
  rowsign  : +1 if σ == '+' else -1
  single   : gb_{a1+,b1+} = 1, others 0
  zero     : all 0 (undeformed control)
Usage: python src/C_evaluate.py [n ...]
"""
import datetime
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_generators import DATA_DIR, write_json  # noqa: E402
from verify_C_structure import load_structure  # noqa: E402

PROFILES = ["allplus", "allminus", "checker", "rowsign", "single", "zero"]
DEFAULT_PROFILE = "allplus"
PROFILE_DESC = {
    "allplus": "gb = +1 for all 4n parameters",
    "allminus": "gb = -1 for all 4n parameters",
    "checker": "gb_{σ,j,s} = +1 if σ == s else -1",
    "rowsign": "gb_{σ,j,s} = +1 if σ == '+' else -1",
    "single": "gb_{a1+,b1+} = 1, all others 0",
    "zero": "all gb = 0 (undeformed control)",
}


def load_gamma(n):
    with open(os.path.join(DATA_DIR, f"C_{n}_gamma.json")) as fh:
        return json.load(fh)


def profile_values(labels, profile):
    """labels: gb labels 'gb_a1{σ}_b{j}{s}'."""
    vals = {}
    for g in labels:
        sigma, s = g[4], g[-1]
        if profile == "allplus":
            v = 1
        elif profile == "allminus":
            v = -1
        elif profile == "checker":
            v = 1 if sigma == s else -1
        elif profile == "rowsign":
            v = 1 if sigma == "p" else -1
        elif profile == "single":
            v = 1 if g == "gb_a1p_b1p" else 0
        elif profile == "zero":
            v = 0
        else:
            raise ValueError(profile)
        vals[g] = Fraction(v)
    return vals


def evaluate_gamma(gamma_entries, vals):
    """[(X,Y,Z,coeff-dict)] -> {(X,Y): {Z: Fraction}} (zeros dropped)."""
    out = {}
    for e in gamma_entries:
        c = sum((Fraction(v) * vals[g] for g, v in e["coeff"].items()), Fraction(0))
        if c:
            out.setdefault((e["X"], e["Y"]), {})[e["Z"]] = c
    return out


def evaluated_filename(n, profile):
    if profile == DEFAULT_PROFILE:
        return f"C_{n}_evaluated.json"
    return f"C_{n}_evaluated_{profile}.json"


def build_schema3(n, profile, date=None):
    s1, s2 = load_structure(n), load_gamma(n)
    labels = [g for row in s2["gb_matrix"]["labels"] for g in row]
    vals = profile_values(labels, profile)
    ev = evaluate_gamma(s2["inhomogeneous_deformation"]["entries"], vals)
    basis = s1["basis"]["ordering"]
    order = basis + ["K"]
    sc = [{"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": e["coeff"], "part": "g"}
          for e in s1["structure_constants"]]
    gam = []
    for X in basis:
        for Y in basis:
            v = ev.get((X, Y), {})
            for Z in order:
                if Z in v:
                    gam.append({"X": X, "Y": Y, "Z": Z, "coeff": str(v[Z])})
    sc += [dict(e, part="kappa") for e in gam]
    return {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": s2["algebra"],
        "structure_file": f"C_{n}_structure.json",
        "gamma_file": f"C_{n}_gamma.json",
        "basis_ordering": basis,
        "profile": {"name": profile, "description": PROFILE_DESC[profile]},
        "gb_values": {g: str(v) for g, v in vals.items()},
        "gb_matrix_values": [[str(vals[g]) for g in row] for row in s2["gb_matrix"]["labels"]],
        "evaluated_deformation": {
            "bracket": "[X,Y]_γ = [X,Y]_0 + κ γ(X,Y)  (κ on the left)",
            "value_space": "g ⊕ CK  (Z = 'K' is the central component)",
            "num_entries": len(gam),
            "num_K_entries": sum(1 for e in gam if e["Z"] == "K"),
            "entries": gam,
        },
        "evaluated_structure_constants": {
            "description": ("Full deformed bracket: part 'g' = undeformed constants "
                            "(Schema 1), part 'kappa' = coefficient of κ·Z"),
            "entries": sc,
        },
        "metadata": {"generated_by": "src/C_evaluate.py",
                     "generation_date": date or datetime.date.today().isoformat(),
                     "conventions": "handover/notation.md"},
    }


# ------------------------------------------------------------------ checks


def check_schema3(n, s3):
    """Independent consistency checks of a Schema 3 object against Schema 1/2."""
    from C_gamma import check_deformed_jacobi
    from verify_C_structure import bracket_table
    s1, s2 = load_structure(n), load_gamma(n)
    vals = {g: Fraction(v) for g, v in s3["gb_values"].items()}
    # (1) re-substitute Schema 2 and compare
    ev = evaluate_gamma(s2["inhomogeneous_deformation"]["entries"], vals)
    stored = {}
    for e in s3["evaluated_deformation"]["entries"]:
        stored.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    ok_subst = stored == ev
    # (2) undeformed part identical to Schema 1
    und = bracket_table([e for e in s3["evaluated_structure_constants"]["entries"]
                         if e["part"] == "g"])
    ok_s1 = und == bracket_table(s1["structure_constants"])
    # (3) deformed super-Jacobi with the evaluated numbers (gb label replaced by '1')
    gam_num = {k: {Z: {"num": c} for Z, c in v.items()} for k, v in stored.items()}
    _, fails = check_deformed_jacobi(s1["basis"]["ordering"], s1["parity"], und, gam_num)
    # (4) labels consistent with Schema 1 basis
    basis = set(s1["basis"]["ordering"])
    ok_labels = all(e["X"] in basis and e["Y"] in basis and (e["Z"] in basis or e["Z"] == "K")
                    for e in s3["evaluated_deformation"]["entries"])
    return {"substitution": ok_subst, "undeformed_eq_schema1": ok_s1,
            "deformed_jacobi_failures": len(fails), "labels": ok_labels}


def main(ns):
    for n in ns:
        for prof in PROFILES:
            s3 = build_schema3(n, prof)
            path = os.path.join(DATA_DIR, evaluated_filename(n, prof))
            write_json(s3, path)
            chk = check_schema3(n, s3)
            d = s3["evaluated_deformation"]
            print(f"n={n} {prof:8s}: gamma entries={d['num_entries']:4d} "
                  f"(K={d['num_K_entries']:3d}) checks={chk} -> {os.path.basename(path)}")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [1, 2, 3])
