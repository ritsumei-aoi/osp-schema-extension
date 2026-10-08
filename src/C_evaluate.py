"""Schema 3: evaluated deformation structure of C(n+1) for concrete gb assignments  (Issue I06).

A *profile* assigns a rational value to each of the 4n parameters gb_a1{sigma}_b{j}{s}.
For a profile the script
  * evaluates every gamma coefficient of Schema 2 (linear forms in gb),
  * writes the full deformed bracket table of L = g~ (+) kappa g~ (kappa^0 and kappa^1 parts),
  * verifies super Jacobi of L with the I04 verifier and records the result.

Files: data/C_{n}_evaluated.json  (representative profile "all_plus")
       data/C_{n}_evaluated_<profile>.json for the other profiles.

Usage:
    python src/C_evaluate.py                 # all n, all profiles
    python src/C_evaluate.py 2 all_plus      # n = 2, one profile
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import C_gamma as CG  # noqa: E402
import C_generators as G  # noqa: E402
import verify_C_structure as V  # noqa: E402
from oscillator_algebra import gb_label, gb_labels  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
REPRESENTATIVE = "all_plus"


# ---------------------------------------------------------------------- profiles
def profile(name: str, n: int) -> Dict[str, Fraction]:
    """Representative sign profiles for the 2 x 2n gb matrix."""
    labs = gb_labels(n)
    one = Fraction(1)
    if name == "all_plus":
        return {l: one for l in labs}
    if name == "all_minus":
        return {l: -one for l in labs}
    if name == "row_sign":  # +1 on the a_1_p row, -1 on the a_1_m row
        return {gb_label(sg, j, s): (one if sg == "p" else -one) for sg in "pm" for j in range(1, n + 1) for s in "pm"}
    if name == "col_sign":  # +1 for b_j^+ columns, -1 for b_j^- columns
        return {gb_label(sg, j, s): (one if s == "p" else -one) for sg in "pm" for j in range(1, n + 1) for s in "pm"}
    if name == "checkerboard":  # (-1)^{row + col}
        out = {}
        for r, sg in enumerate("pm"):
            for c, (j, s) in enumerate((j, s) for j in range(1, n + 1) for s in "pm"):
                out[gb_label(sg, j, s)] = one if (r + c) % 2 == 0 else -one
        return out
    if name == "single_pp":  # only gb_{a_1^+, b_1^+} = 1
        return {l: (one if l == "gb_a1p_b1p" else Fraction(0)) for l in labs}
    if name == "zero":
        return {l: Fraction(0) for l in labs}
    raise ValueError(name)


PROFILES = ["all_plus", "all_minus", "row_sign", "col_sign", "checkerboard", "single_pp", "zero"]


def evaluated_path(n: int, name: str = REPRESENTATIVE) -> str:
    suffix = "" if name == REPRESENTATIVE else f"_{name}"
    return os.path.join(DATA_DIR, f"C_{n}_evaluated{suffix}.json")


# -------------------------------------------------------------------- building
def build_schema3(n: int, name: str) -> dict:
    gb = profile(name, n)
    with open(G.structure_path(n)) as fh:
        s1 = json.load(fh)
    s2 = CG.load_schema2(n)
    gamma_eval = []
    for e in s2["inhomogeneous_deformation"]["gamma"]:
        c = CG.evaluate_linear_form(e["linear_form"], gb)
        if c != 0:
            gamma_eval.append({"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": str(c)})
    basis, parity, table = CG.extended_algebra(n, gb, s1, s2)
    res = V.verify(basis, parity, table)
    deformed = []
    g_basis = s1["basis"]["odd"] + s1["basis"]["even"]
    for X in g_basis:
        for Y in g_basis:
            for Z, c in sorted(table.get((X, Y), {}).items(), key=lambda t: (t[0].startswith("kappa*"), t[0])):
                if Z.startswith("kappa*"):
                    deformed.append({"X": X, "Y": Y, "Z": Z[len("kappa*"):], "kappa_power": 1, "coeff": str(c)})
                else:
                    deformed.append({"X": X, "Y": Y, "Z": Z, "kappa_power": 0, "coeff": str(c)})
    return {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": s1["algebra"],
        "source_structure": os.path.basename(G.structure_path(n)),
        "source_gamma": os.path.basename(CG.gamma_path(n)),
        "central_elements": s1["central_elements"],
        "gb_assignment": {
            "profile": name,
            "description": {
                "all_plus": "all 4n parameters = +1 (representative assignment)",
                "all_minus": "all 4n parameters = -1",
                "row_sign": "+1 on the a_1_p row, -1 on the a_1_m row",
                "col_sign": "+1 for b_j^+ columns, -1 for b_j^- columns",
                "checkerboard": "(-1)^(row+col) on the 2 x 2n matrix",
                "single_pp": "only gb_a1p_b1p = 1, all others 0",
                "zero": "undeformed control (all gb = 0)",
            }[name],
            "values": {l: str(v) for l, v in gb.items()},
            "matrix": [[str(gb[gb_label(sg, j, s)]) for j in range(1, n + 1) for s in "pm"] for sg in "pm"],
        },
        "evaluated_structure": {
            "description": "Deformed graded bracket of basis elements X, Y of C(n+1) at the given gb values: "
                           "[X,Y}_gamma = sum_Z coeff * kappa^{kappa_power} Z, Z in basis or 'K'.",
            "gamma_evaluated": gamma_eval,
            "deformed_structure_constants": deformed,
            "summary": {
                "gamma_nonzero_entries": len(gamma_eval),
                "gamma_nonzero_pairs": len({(e["X"], e["Y"]) for e in gamma_eval}),
                "gamma_entries_with_Z_K": sum(1 for e in gamma_eval if e["Z"] == "K"),
                "deformed_entries": len(deformed),
            },
        },
        "verification": {
            "extended_algebra": "L = g~ (+) kappa g~, dim = 2 (dim g + 1)",
            "extended_dim": len(basis),
            "antisymmetry_failures": len(res["antisymmetry_failures"]),
            "jacobi_triples_checked": res["jacobi_triples_checked"],
            "jacobi_failures": len(res["jacobi_failures"]),
            "pass": res["pass"],
        },
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": _dt.date.today().isoformat(),
        },
    }


def write_schema3(n: int, name: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = evaluated_path(n, name)
    with open(path, "w") as fh:
        json.dump(build_schema3(n, name), fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return path


def main(argv):
    ns = [int(a) for a in argv if a.isdigit()] or [1, 2, 3]
    names = [a for a in argv if not a.isdigit()] or PROFILES
    ok = True
    for n in ns:
        for name in names:
            p = write_schema3(n, name)
            d = json.load(open(p))
            s, v = d["evaluated_structure"]["summary"], d["verification"]
            ok &= v["pass"]
            print(f"n={n} profile={name:12s} -> {os.path.relpath(p, ROOT)}: gamma entries={s['gamma_nonzero_entries']:4d} "
                  f"(K: {s['gamma_entries_with_Z_K']:3d}), L dim={v['extended_dim']}, "
                  f"Jacobi triples={v['jacobi_triples_checked']}, failures={v['jacobi_failures']}, "
                  f"{'PASS' if v['pass'] else 'FAIL'}")
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
