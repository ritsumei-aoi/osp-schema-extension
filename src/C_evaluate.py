"""
I06: Schema 3 (evaluated structure) for C(n+1).

Substitutes concrete values for the 4n deformation parameters gb into the Schema 2 linear forms
(read from data/C_{n}_gamma.json) and writes

    data/C_{n}_evaluated.json               (default profile: all_plus)
    data/C_{n}_evaluated_{profile}.json     (every profile in PROFILES)

Consistency with Schema 2 is verified by recomputing gamma directly in the oscillator engine with the
numeric gb values substituted and comparing coefficient by coefficient.

Usage:  python src/C_evaluate.py [n ...]
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from fractions import Fraction
from typing import Callable, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import compute_gamma, gb_labels  # noqa: E402
from C_generators import DATA_DIR, pbw_order  # noqa: E402

# profile name -> function (sigma, k, s) -> value
PROFILES: Dict[str, Callable[[str, int, str], Fraction]] = {
    "all_plus": lambda sigma, k, s: Fraction(1),
    "all_minus": lambda sigma, k, s: Fraction(-1),
    "row_sign": lambda sigma, k, s: Fraction(1 if sigma == "p" else -1),          # a_1^+ row +1, a_1^- row -1
    "column_alternating": lambda sigma, k, s: Fraction(1 if s == "p" else -1),    # b^+ columns +1, b^- columns -1
    "unit_a1p_b1p": lambda sigma, k, s: Fraction(1 if (sigma, k, s) == ("p", 1, "p") else 0),
    "unit_a1m_b1m": lambda sigma, k, s: Fraction(1 if (sigma, k, s) == ("m", 1, "m") else 0),
    "generic": lambda sigma, k, s: Fraction(_PRIMES[(0 if sigma == "p" else 1) * 2 * 6 + 2 * (k - 1) + (0 if s == "p" else 1)]),
}
_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89]
DEFAULT_PROFILE = "all_plus"


def profile_values(n: int, name: str) -> Dict[str, Fraction]:
    fn = PROFILES[name]
    vals = {}
    for sigma in ("p", "m"):
        for k in range(1, n + 1):
            for s in ("p", "m"):
                vals[f"gb_a_1_{sigma}_b_{k}_{s}"] = fn(sigma, k, s)
    return vals


def eval_linear_form(coeff, values: Dict[str, Fraction]) -> Fraction:
    """Evaluate a Schema 2/4 coefficient (linear-form dict or rational string)."""
    if isinstance(coeff, str):
        return Fraction(coeff)
    total = Fraction(0)
    for sym, val in coeff.items():
        total += Fraction(val) * (Fraction(1) if sym == "1" else values[sym])
    return total


def evaluate_from_schema2(gamma_doc: dict, values: Dict[str, Fraction]) -> Dict[tuple, Fraction]:
    out = {}
    for e in gamma_doc["inhomogeneous_deformation"]["gamma"]:
        v = eval_linear_form(e["coeff"], values)
        if v != 0:
            out[(e["X"], e["Y"], e["Z"])] = v
    return out


def evaluate_direct(n: int, values: Dict[str, Fraction]) -> Dict[tuple, Fraction]:
    """Independent route: engine gamma with numeric substitution."""
    gamma, _, _ = compute_gamma(n)
    out = {}
    for (x, y), vec in gamma.items():
        for z, c in vec.items():
            v = c.substitute(values).scalar_value()
            if v != 0:
                out[(x, y, z)] = v
    return out


def build_evaluated_json(n: int, profile: str, data_dir: str = DATA_DIR):
    with open(os.path.join(data_dir, f"C_{n}_gamma.json")) as fh:
        gamma_doc = json.load(fh)
    with open(os.path.join(data_dir, f"C_{n}_structure.json")) as fh:
        struct = json.load(fh)
    values = profile_values(n, profile)
    rows, cols, entries = gb_labels(n)
    ev = evaluate_from_schema2(gamma_doc, values)
    direct = evaluate_direct(n, values)
    consistent = ev == direct

    order = pbw_order(n)
    idx = {l: i for i, l in enumerate(order)}
    base = {(e["X"], e["Y"], e["Z"]): Fraction(e["coeff"]) for e in struct["structure_constants"]}
    keys = sorted(set(base) | set(ev), key=lambda t: (idx[t[0]], idx[t[1]], idx[t[2]]))
    merged = [{"X": x, "Y": y, "Z": z, "coeff": str(base.get((x, y, z), Fraction(0))),
               "kappa_coeff": str(ev.get((x, y, z), Fraction(0)))} for (x, y, z) in keys]
    doc = {
        "schema_version": "5.0",
        "layer": 3,
        "algebra": gamma_doc["algebra"],
        "source_structure": f"C_{n}_structure.json",
        "source_gamma": f"C_{n}_gamma.json",
        "gb_profile": {
            "name": profile,
            "values": {k: str(v) for k, v in values.items()},
            "matrix": [[str(values[e]) for e in row] for row in entries],
            "rows": rows, "columns": cols,
        },
        "evaluated_gamma": [{"X": x, "Y": y, "Z": z, "coeff": str(ev[(x, y, z)])}
                            for (x, y, z) in sorted(ev, key=lambda t: (idx[t[0]], idx[t[1]], idx[t[2]]))],
        "evaluated_structure_constants": merged,
        "consistency": {"matches_direct_recomputation": consistent,
                        "nonzero_gamma_coefficients": len(ev)},
        "metadata": {"generated_by": "src/C_evaluate.py", "generation_date": date.today().isoformat(),
                     "available_profiles": list(PROFILES)},
    }
    return doc, consistent


def write_evaluated(n: int, profile: str, data_dir: str = DATA_DIR) -> List[str]:
    doc, ok = build_evaluated_json(n, profile, data_dir)
    names = [f"C_{n}_evaluated_{profile}.json"]
    if profile == DEFAULT_PROFILE:
        names.append(f"C_{n}_evaluated.json")
    paths = []
    for name in names:
        p = os.path.join(data_dir, name)
        with open(p, "w") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        paths.append(p)
    return paths, ok, doc


if __name__ == "__main__":
    ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    all_ok = True
    for n in ns:
        for prof in PROFILES:
            paths, ok, doc = write_evaluated(n, prof)
            all_ok &= ok
            print(f"n={n} profile={prof:18s} nonzero gamma coeffs={doc['consistency']['nonzero_gamma_coefficients']:5d} "
                  f"schema2-consistent={ok}  -> {', '.join(os.path.basename(p) for p in paths)}")
    print("ALL PASS" if all_ok else "SOME CHECKS FAILED")
    sys.exit(0 if all_ok else 1)
