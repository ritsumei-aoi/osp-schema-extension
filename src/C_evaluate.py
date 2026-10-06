"""Schema 3 (evaluated structure) builder for C(n+1).

Substitutes concrete rational values for the gb parameters into the Schema 2
gamma coefficients.
"""

from __future__ import annotations

import json
import os
from datetime import date
from typing import Dict

import sympy as sp

from src.C_gamma import build_gamma


def gb_labels(n: int):
    out = []
    for sigma in ("p", "m"):
        for j in range(1, n + 1):
            for s in ("p", "m"):
                out.append(f"gb_a1{sigma}_b{j}{s}")
    return out


def profile_all_plus_one(n: int) -> Dict[str, str]:
    return {lbl: "1" for lbl in gb_labels(n)}


def profile_fermion_parity_signs(n: int) -> Dict[str, str]:
    """Representative sign profile: +1 if σ matches s, -1 otherwise.

    This is the second profile in the Schema 3 record; it exposes
    sign-sensitive cancellation structure in the γ coefficients.
    """
    out = {}
    for lbl in gb_labels(n):
        _, a_part, b_part = lbl.split("_", 2)
        sigma = a_part[-1]
        s = b_part[-1]
        out[lbl] = "1" if sigma == s else "-1"
    return out


def evaluate_profile(entries, values: Dict[str, str]):
    subs = {sp.Symbol(k): sp.Rational(v) for k, v in values.items()}
    out = []
    for e in entries:
        expr = sp.sympify(e["coeff"]).subs(subs)
        expr = sp.simplify(expr)
        if expr == 0:
            continue
        out.append(
            {"X": e["X"], "Y": e["Y"], "Z": e["Z"], "coeff": str(expr)}
        )
    return out


def build_evaluated_json(n: int, profile_name: str, values: Dict[str, str]) -> dict:
    entries, even, odd = build_gamma(n)
    evaluated = evaluate_profile(entries, values)
    return {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": {
            "family": "C",
            "m": 1,
            "n": n,
            "cartan_type": f"C({n + 1})",
        },
        "evaluation": {
            "profile_name": profile_name,
            "gb_values": values,
        },
        "evaluated_gamma": evaluated,
        "basis": {"even": even, "odd": odd},
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": str(date.today()),
        },
    }


def main():
    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
    os.makedirs(out_dir, exist_ok=True)
    for n in (1, 2, 3):
        obj = build_evaluated_json(n, "all_plus_one", profile_all_plus_one(n))
        path = os.path.join(out_dir, f"C_{n}_evaluated.json")
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)
        print(f"wrote {path} ({len(obj['evaluated_gamma'])} entries)")


if __name__ == "__main__":
    main()
