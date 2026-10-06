"""Schema 3 for C(n+1): gamma evaluated at a concrete gb assignment.

Substitutes numbers into the symbolic Schema 2 (data/C_{n}_gamma.json) and cross-checks the
result against a direct computation in the deformed oscillator algebra (C_gamma.gamma_table).
Canonical file  C_{n}_evaluated.json  uses the profile "all_plus" (every gb = +1);
other sign profiles are written to  C_{n}_evaluated_<profile>.json.
"""
import json
import os
from fractions import Fraction

import C_gamma as CG
import C_generators as G

PROFILES = ["all_plus", "all_minus", "zero", "sigma_p_only", "sigma_m_only", "alternating",
            "unit_first"]


def profile_values(n, profile):
    """{(sigma, j, s): int} for a named profile; keys in CG.gb_keys(n) order."""
    keys = CG.gb_keys(n)
    if profile == "all_plus":
        return dict((k, 1) for k in keys)
    if profile == "all_minus":
        return dict((k, -1) for k in keys)
    if profile == "zero":
        return dict((k, 0) for k in keys)
    if profile == "sigma_p_only":
        return dict((k, 1 if k[0] == "p" else 0) for k in keys)
    if profile == "sigma_m_only":
        return dict((k, 1 if k[0] == "m" else 0) for k in keys)
    if profile == "alternating":
        return dict((k, 1 if i % 2 == 0 else -1) for i, k in enumerate(keys))
    if profile == "unit_first":
        return dict((k, 1 if i == 0 else 0) for i, k in enumerate(keys))
    raise ValueError(profile)


def load_schema2(n):
    with open(os.path.join(G.DATA_DIR, f"C_{n}_gamma.json")) as f:
        return json.load(f)


def evaluate_from_schema2(n, gb):
    """{(X,Y,Z): Fraction} by substituting gb (keys (sigma,j,s)) into Schema 2."""
    s2 = load_schema2(n)["inhomogeneous_deformation"]
    val = dict((CG.gb_name(k), Fraction(v)) for k, v in gb.items())
    out = {}
    for e in s2["gamma"]:
        v = sum(Fraction(c) * val[p] for p, c in e["coeff"].items())
        if v != 0:
            out[(e["X"], e["Y"], e["Z"])] = v
    return out


def evaluate_direct(n, gb):
    _, gam = CG.gamma_table(n, gb)
    return dict(((X, Y, Z), c) for (X, Y), zs in gam.items() for Z, c in zs.items())


def build_schema3(n, profile, today="2026-10-06"):
    gb = profile_values(n, profile)
    ev = evaluate_from_schema2(n, gb)
    direct = evaluate_direct(n, gb)
    if ev != direct:
        raise ValueError("Schema 2 substitution disagrees with direct computation")
    names = G.basis_names(n)
    entries = [{"X": X, "Y": Y, "Z": Z, "coeff": G.frac_str(ev[(X, Y, Z)]),
                "sign_rule": "graded"}
               for X in names for Y in names for Z in names + ["K"] if (X, Y, Z) in ev]
    return {
        "schema_version": "5.0",
        "layer": "evaluated",
        "algebra": {"family": "C", "m": 1, "n": n, "cartan_type": f"C({n+1})"},
        "source_structure": f"C_{n}_structure.json",
        "source_gamma": f"C_{n}_gamma.json",
        "gb_assignment": {
            "profile": profile,
            "values": dict((CG.gb_name(k), G.frac_str(Fraction(v))) for k, v in gb.items()),
        },
        "evaluated_deformation": {
            "description": "[X,Y}_gamma = [X,Y]_0 + kappa * sum_Z gamma_{XY}^Z Z, gb numeric",
            "target_labels": "Schema 1 basis names plus 'K' (even central scalar)",
            "gamma": entries,
            "nonzero_count": len(entries),
            "K_component_count": sum(1 for e in entries if e["Z"] == "K"),
        },
        "metadata": {"generated_by": "src/C_evaluate.py", "generation_date": today,
                     "cross_check": "substitution into Schema 2 == direct deformed oscillator computation"},
    }


def main(ns=(1, 2, 3)):
    for n in ns:
        for profile in PROFILES:
            d = build_schema3(n, profile)
            suffix = "" if profile == "all_plus" else f"_{profile}"
            path = os.path.join(G.DATA_DIR, f"C_{n}_evaluated{suffix}.json")
            with open(path, "w") as f:
                json.dump(d, f, indent=1)
            ed = d["evaluated_deformation"]
            print(os.path.basename(path), ed["nonzero_count"], "entries,",
                  ed["K_component_count"], "with K")


if __name__ == "__main__":
    main()
