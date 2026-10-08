"""Issue I06: Schema 3 (evaluated structure) for C(n+1).

Substitutes concrete values of the 4n deformation parameters gb into the symbolic
gamma of Schema 2 and writes data/C_{n}_evaluated.json (representative profile
``all_plus``) and data/C_{n}_evaluated_<profile>.json for the other profiles.

Usage: python3 src/C_evaluate.py [n ...]
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_common import DATA_DIR, LieSuperalgebra, frac_str, lf_eval  # noqa: E402
from C_gamma import check_L_jacobi, check_gamma_antisymmetry, load_gamma  # noqa: E402
from C_generators import REFERENCES, algebra_block, central_elements_block, pbw_order  # noqa: E402

EvalTable = Dict[Tuple[str, str], Dict[str, Fraction]]


def gb_profiles(n: int) -> Dict[str, Dict[str, Fraction]]:
    """Representative sign assignments for the gb matrix."""
    names = [f"gb_a1{sig}_b{j}{s}" for sig in ("p", "m") for j in range(1, n + 1) for s in ("p", "m")]

    def profile(rule):
        return {name: Fraction(rule(name)) for name in names}

    return {
        # every parameter +1 (representative assignment)
        "all_plus": profile(lambda nm: 1),
        # sign by fermionic row: a_1^+ row +1, a_1^- row -1
        "fermion_sign": profile(lambda nm: 1 if nm.startswith("gb_a1p") else -1),
        # sign by bosonic column: b^+ columns +1, b^- columns -1
        "boson_sign": profile(lambda nm: 1 if nm.endswith("p") else -1),
        # a single non-zero parameter
        "single_a1p_b1m": profile(lambda nm: 1 if nm == "gb_a1p_b1m" else 0),
        # only the a_1^+ row (so(2)-charge +1 sector) deformed
        "row_a1p_only": profile(lambda nm: 1 if nm.startswith("gb_a1p") else 0),
        # all zero (undeformed; sanity profile)
        "zero": profile(lambda nm: 0),
    }


def evaluate_gamma(gamma_sym, values: Dict[str, Fraction]) -> EvalTable:
    out: EvalTable = {}
    for (X, Y), entry in gamma_sym.items():
        ev = {Z: lf_eval(lf, values) for Z, lf in entry.items()}
        ev = {Z: c for Z, c in ev.items() if c != 0}
        if ev:
            out[(X, Y)] = ev
    return out


def build_schema3(n: int, profile: str, values: Dict[str, Fraction], gamma_sym) -> Tuple[dict, EvalTable]:
    labels = pbw_order(n)
    order = {lab: i for i, lab in enumerate(labels + ["K"])}
    ev = evaluate_gamma(gamma_sym, values)
    entries = []
    for X in labels:
        for Y in labels:
            for Z in sorted(ev.get((X, Y), {}), key=lambda z: order[z]):
                entries.append({"X": X, "Y": Y, "Z": Z, "coeff": frac_str(ev[(X, Y)][Z])})
    doc = {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": algebra_block(n),
        "central_elements": central_elements_block(),
        "basis_ref": f"C_{n}_structure.json",
        "gamma_ref": f"C_{n}_gamma.json",
        "gb_assignment": {
            "profile": profile,
            "values": {k: frac_str(v) for k, v in values.items()},
            "description": {
                "all_plus": "every gb parameter = +1 (representative assignment)",
                "fermion_sign": "gb = +1 on the a_1^+ row, -1 on the a_1^- row",
                "boson_sign": "gb = +1 on b^+ columns, -1 on b^- columns",
                "single_a1p_b1m": "only gb_a1p_b1m = 1, all others 0",
                "row_a1p_only": "a_1^+ row = 1, a_1^- row = 0",
                "zero": "undeformed (all gb = 0)",
            }[profile],
        },
        "evaluated_deformation": {
            "bracket": "[X,Y]_gamma = [X,Y]_0 + kappa * gamma(X,Y) with gb substituted",
            "target": "g + C K (entries with Z = 'K' are constant terms)",
            "gamma": entries,
            "count": len(entries),
            "K_count": sum(1 for e in entries if e["Z"] == "K"),
        },
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": _dt.date.today().isoformat(),
            "notation": "handover/notation.md",
            "references": REFERENCES,
        },
    }
    return doc, ev


def evaluated_path(n: int, profile: str, data_dir: str = DATA_DIR) -> str:
    name = f"C_{n}_evaluated.json" if profile == "all_plus" else f"C_{n}_evaluated_{profile}.json"
    return os.path.join(data_dir, name)


def write_schema3(n: int, data_dir: str = DATA_DIR) -> Dict[str, Tuple[str, EvalTable]]:
    _, gamma_sym = load_gamma(n, data_dir)
    out = {}
    for profile, values in gb_profiles(n).items():
        doc, ev = build_schema3(n, profile, values, gamma_sym)
        path = evaluated_path(n, profile, data_dir)
        with open(path, "w") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        out[profile] = (path, ev)
    return out


def load_evaluated(n: int, profile: str = "all_plus", data_dir: str = DATA_DIR) -> Tuple[dict, EvalTable]:
    with open(evaluated_path(n, profile, data_dir)) as fh:
        doc = json.load(fh)
    ev: EvalTable = {}
    for e in doc["evaluated_deformation"]["gamma"]:
        ev.setdefault((e["X"], e["Y"]), {})[e["Z"]] = Fraction(e["coeff"])
    return doc, ev


def check_consistency_with_schema2(n: int, profile: str, data_dir: str = DATA_DIR) -> bool:
    """Schema 3 == Schema 2 with gb substituted, antisymmetric, and Jacobi on L holds."""
    doc, ev = load_evaluated(n, profile, data_dir)
    _, gamma_sym = load_gamma(n, data_dir)
    values = {k: Fraction(v) for k, v in doc["gb_assignment"]["values"].items()}
    ok = ev == evaluate_gamma(gamma_sym, values)
    g = LieSuperalgebra.load(n, data_dir)
    as_lf = {k: {Z: {"": c} for Z, c in e.items()} for k, e in ev.items()}
    ok &= check_gamma_antisymmetry(as_lf, g.parity, g.labels) == []
    _, jf = check_L_jacobi(as_lf, g)
    ok &= jf == []
    return ok


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    ok_all = True
    for n in ns:
        written = write_schema3(n)
        for profile, (path, ev) in written.items():
            ok = check_consistency_with_schema2(n, profile)
            ok_all &= ok
            nK = sum(1 for e in ev.values() for Z in e if Z == "K")
            print(f"C({n+1}) {os.path.basename(path):34s} profile={profile:15s} "
                  f"pairs={len(ev):4d} K-entries={nK:3d}  substitution/antisymmetry/Jacobi: {'PASS' if ok else 'FAIL'}")
    print("SUMMARY:", "ALL PASS" if ok_all else "FAILURES")
    sys.exit(0 if ok_all else 1)
