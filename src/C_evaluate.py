"""Layer 3: evaluate the Schema 2 gamma structure at representative gb profiles (Issue I06).

Reads data/C_{n}_gamma.json and data/C_{n}_structure.json, substitutes numerical gb
values, and writes data/C_{n}_evaluated.json (Schema 3).

Profiles (representative assignments of the 4n parameters gb_{sigma,j,s}):
  all_plus_one    : every gb = +1                    (primary profile)
  all_zero        : every gb = 0                     (undeformed; gamma vanishes)
  sign_by_boson   : gb = +1 if s = p, -1 if s = m    (sign profile, mixes boson signs)

Usage: python3 src/C_evaluate.py
"""

import json
from fractions import Fraction
from pathlib import Path

import sympy

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_PROFILE = "all_plus_one"


def gb_names(n):
    return [f"gb_{sig}_{j}_{s}" for sig in ("p", "m") for j in range(1, n + 1) for s in ("p", "m")]


def profiles(n):
    """Return {profile_name: {gb_name: Fraction}} for rank n."""
    names = gb_names(n)
    return {
        "all_plus_one": {g: Fraction(1) for g in names},
        "all_zero": {g: Fraction(0) for g in names},
        "sign_by_boson": {g: Fraction(1 if g.endswith("_p") else -1) for g in names},
    }


def load_json(path):
    with Path(path).open() as f:
        return json.load(f)


def evaluate_entries(gamma_entries, values):
    """Substitute gb values into gamma entries; drop entries that vanish."""
    subs = {sympy.Symbol(k): sympy.Rational(v.numerator, v.denominator) for k, v in values.items()}
    out = []
    for e in gamma_entries:
        c = sympy.sympify(e["coeff"]).subs(subs)
        if c == 0:
            continue
        out.append({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": str(c), "sign_rule": e["sign_rule"]})
    return out


def build_evaluated(n, data_dir=DATA_DIR):
    gamma = load_json(Path(data_dir) / f"C_{n}_gamma.json")
    structure = load_json(Path(data_dir) / f"C_{n}_structure.json")
    entries = gamma["inhomogeneous_deformation"]["gamma"]
    prof_out = {}
    for name, values in profiles(n).items():
        prof_out[name] = {
            "gb_values": {g: str(v) for g, v in values.items()},
            "gamma_evaluated": evaluate_entries(entries, values),
        }
    return {
        "schema_version": "5.0",
        "schema": "evaluated",
        "algebra_ref": f"C_{n}_structure.json",
        "gamma_ref": f"C_{n}_gamma.json",
        "basis_ref": {"even": structure["basis"]["even"], "odd": structure["basis"]["odd"]},
        "default_profile": DEFAULT_PROFILE,
        "profiles": prof_out,
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": "2026-10-08",
        },
    }


def consistency_check(n, data_dir=DATA_DIR):
    """Check Schema 3 against Schema 2 and Schema 1. Returns a dict of counts."""
    gamma = load_json(Path(data_dir) / f"C_{n}_gamma.json")
    structure = load_json(Path(data_dir) / f"C_{n}_structure.json")
    evaluated = build_evaluated(n, data_dir)
    entries = gamma["inhomogeneous_deformation"]["gamma"]
    labels = set(structure["basis"]["even"] + structure["basis"]["odd"]) | {"K"}
    syms = [sympy.Symbol(g) for g in gb_names(n)]
    report = {"profiles": len(evaluated["profiles"]), "label_errors": 0,
              "zero_profile_nonzero": 0, "alt_route_mismatch": 0}
    for e in entries:
        if not {e["X"], e["Y"], e["Z"]} <= labels:
            report["label_errors"] += 1
    for name, prof in evaluated["profiles"].items():
        if name == "all_zero" and prof["gamma_evaluated"]:
            report["zero_profile_nonzero"] += len(prof["gamma_evaluated"])
        # alternative route: value of a linear form = sum of its coefficients times gb values
        values = {g: Fraction(v) for g, v in prof["gb_values"].items()}
        alt = {}
        for e in entries:
            expr = sympy.sympify(e["coeff"])
            total = sum(sympy.Poly(expr, *syms).coeff_monomial(s) * sympy.Rational(
                values[str(s)].numerator, values[str(s)].denominator) for s in syms)
            if total != 0:
                alt[(e["X"], e["Y"], e["Z"])] = total
        direct = {(e["X"], e["Y"], e["Z"]): sympy.sympify(e["coeff"]) for e in prof["gamma_evaluated"]}
        if set(alt) != set(direct) or any(alt[k] != direct[k] for k in alt):
            report["alt_route_mismatch"] += 1
    return report


def main():
    for rank in (1, 2, 3):
        out = build_evaluated(rank)
        path = DATA_DIR / f"C_{rank}_evaluated.json"
        with path.open("w") as f:
            json.dump(out, f, indent=2)
            f.write("\n")
        print(path)
        for name, prof in out["profiles"].items():
            print("  ", name, "nonzero gamma entries:", len(prof["gamma_evaluated"]))
        print("consistency", rank, consistency_check(rank))


if __name__ == "__main__":
    main()
