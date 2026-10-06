"""Schema 3 (evaluated structure) for C(n+1): substitute numerical gb into Schema 2.

Writes data/C_{n}_evaluated.json (profile `all_plus`, the representative assignment)
and data/C_{n}_evaluated_<profile>.json for the additional sign profiles.
"""
import json
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(__file__))
import C_gamma as GM  # noqa: E402
import C_generators as G  # noqa: E402

DATA_DIR = G.DATA_DIR


def profiles(n):
    """Representative gb assignments, {profile: {param_name: Fraction}}.
    Parameter order (columns of gb_matrix): rows sigma=p,m; columns (j,s)."""
    keys = GM.gb_keys(n)
    names = [GM.gb_name(k) for k in keys]
    P = {}
    P["all_plus"] = {nm: Fraction(1) for nm in names}
    P["all_minus"] = {nm: Fraction(-1) for nm in names}
    P["alternating"] = {nm: Fraction((-1) ** i) for i, nm in enumerate(names)}
    P["sigma_p_only"] = {nm: Fraction(1 if k[0] == "p" else 0) for nm, k in zip(names, keys)}
    P["single_first"] = {nm: Fraction(1 if i == 0 else 0) for i, nm in enumerate(names)}
    P["zero"] = {nm: Fraction(0) for nm in names}
    return P


def build_schema3(n, profile, gb_values, lin=None):
    if lin is None:
        _, lin = GM.load_gamma(n)
    with open(os.path.join(DATA_DIR, f"C_{n}_structure.json")) as fh:
        s1 = json.load(fh)
    gamma = GM.evaluate(lin, gb_values)
    labels = G.all_labels(n)
    entries = []
    for X in labels:
        for Y in labels:
            for Z, c in sorted(gamma.get((X, Y), {}).items(), key=lambda t: (t[0] == GM.K_LABEL, labels.index(t[0]) if t[0] != GM.K_LABEL else 0)):
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": G.fstr(c)})
    return {
        "schema_version": "5.0",
        "algebra": s1["algebra"],
        "basis": s1["basis"],
        "parity": s1["parity"],
        "central_elements": s1["central_elements"],
        "gb_assignment": {"profile": profile, "values": {k: G.fstr(v) for k, v in gb_values.items()}},
        "evaluated_structure": {
            "description": "Deformed bracket [X,Y}_γ = [X,Y}_0 + κ γ(X,Y) with gb numerically substituted",
            "undeformed_structure_constants": s1["structure_constants"],
            "gamma": entries,
            "central_direction": "Z = 'K' is the coefficient of κ·1",
        },
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": "2026-10-06",
            "schema1_file": f"C_{n}_structure.json",
            "schema2_file": f"C_{n}_gamma.json",
        },
    }


def load_evaluated(n, profile="all_plus", data_dir=DATA_DIR):
    name = f"C_{n}_evaluated.json" if profile == "all_plus" else f"C_{n}_evaluated_{profile}.json"
    with open(os.path.join(data_dir, name)) as fh:
        d = json.load(fh)
    gamma = {}
    for e in d["evaluated_structure"]["gamma"]:
        gamma.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    gb = {k: Fraction(v) for k, v in d["gb_assignment"]["values"].items()}
    return d, gamma, gb


def write_all(ns=(1, 2, 3), out_dir=DATA_DIR):
    for n in ns:
        _, lin = GM.load_gamma(n)
        for prof, vals in profiles(n).items():
            name = f"C_{n}_evaluated.json" if prof == "all_plus" else f"C_{n}_evaluated_{prof}.json"
            with open(os.path.join(out_dir, name), "w") as fh:
                json.dump(build_schema3(n, prof, vals, lin), fh, indent=1, ensure_ascii=False)
                fh.write("\n")
            print("wrote", name)


def check_against_engine(n, profile, gb_values):
    """Independent check: recompute gamma with the deformed oscillator engine."""
    key_of = {GM.gb_name(k): k for k in GM.gb_keys(n)}
    direct, _ = GM.gamma_sparse(n, {key_of[nm]: v for nm, v in gb_values.items()})
    _, gamma, _ = load_evaluated(n, profile)
    return {xy: d for xy, d in direct.items() if d} == gamma


if __name__ == "__main__":
    write_all()
    for n in (1, 2, 3):
        for prof, vals in profiles(n).items():
            ok = check_against_engine(n, prof, vals)
            print(f"n={n} profile={prof}: matches engine = {ok}")
