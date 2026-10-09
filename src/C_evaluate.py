"""Schema 3 (evaluated structure) for C(n+1)  (Issue I06).

Substitutes a numeric assignment of the 4n deformation parameters gb into the symbolic
gamma structure of Schema 2 and writes data/C_{n}_evaluated[_<profile>].json.

Built-in gb profiles (--profile):
    all_plus_one   every gb = +1                                   (representative, default)
    all_minus_one  every gb = -1
    alternating    gb_{a_1^sigma, b_k^s} = sigma * s  (signs as ±1)
    fermion_sign   gb_{a_1^sigma, b_k^s} = sigma
    boson_sign     gb_{a_1^sigma, b_k^s} = s
    row_plus       gb_{a_1^+, *} = +1, gb_{a_1^-, *} = 0
    unit:<label>   a single parameter = 1, all others 0 (e.g. unit:gb_a1p_b1m)
    custom JSON    --values '{"gb_a1p_b1p": "1", ...}'   (unspecified entries = 0)

Consistency checks (check_schema3):
  1. evaluated gamma == independent recomputation with numeric gb in the oscillator engine
  2. evaluated gamma == substitution into the Schema 2 records (what the file stores)
  3. kappa^0 records == Schema 1
  4. first-order cocycle identity with numeric coefficients

Usage: python src/C_evaluate.py [--n 1 2 3] [--profile all_plus_one] [--suffix ""]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from fractions import Fraction
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_gamma import (Table, bracket_table_from_schema1, cocycle_residuals,  # noqa: E402
                     compute_gamma, gamma_table_from_records, load_json, _padd, _pscale)
from C_generators import write_json  # noqa: E402
from osc_algebra import OscillatorAlgebra, Poly, frac_str  # noqa: E402

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


# --------------------------------------------------------------------------- profiles


def gb_profile(n: int, profile: str, values: Dict[str, str] | None = None) -> Dict[str, Fraction]:
    labels = OscillatorAlgebra(n).gb_labels()
    sgn = {"p": 1, "m": -1}

    def parts(lab: str) -> Tuple[int, int, int]:
        # gb_a1{sigma}_b{k}{s}
        sig = sgn[lab[5]]
        rest = lab[8:]
        k, s = int(rest[:-1]), sgn[rest[-1]]
        return sig, k, s

    if profile == "custom":
        vals = {lab: Fraction(0) for lab in labels}
        for k, v in (values or {}).items():
            if k not in vals:
                raise KeyError(f"unknown gb label {k}")
            vals[k] = Fraction(v)
        return vals
    if profile.startswith("unit:"):
        target = profile[5:]
        if target not in labels:
            raise KeyError(f"unknown gb label {target}")
        return {lab: Fraction(int(lab == target)) for lab in labels}
    rules = {
        "all_plus_one": lambda sig, k, s: 1,
        "all_minus_one": lambda sig, k, s: -1,
        "alternating": lambda sig, k, s: sig * s,
        "fermion_sign": lambda sig, k, s: sig,
        "boson_sign": lambda sig, k, s: s,
        "row_plus": lambda sig, k, s: 1 if sig == 1 else 0,
    }
    if profile not in rules:
        raise KeyError(f"unknown profile {profile}")
    return {lab: Fraction(rules[profile](*parts(lab))) for lab in labels}


# --------------------------------------------------------------------------- evaluation


def evaluate_gamma(doc2: dict, gb: Dict[str, Fraction]) -> Dict[Tuple[str, str], Dict[str, Fraction]]:
    """Substitute gb into Schema 2 records: {(X,Y): {Z: Fraction}} (zeros dropped)."""
    out: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for r in doc2["gamma"]:
        val = Fraction(0)
        for t in r["terms"]:
            c = Fraction(t["coeff"])
            val += c if t["gb"] == "1" else c * gb[t["gb"]]
        if val != 0:
            out.setdefault((r["X"], r["Y"]), {})[r["Z"]] = val
    return out


def build_schema3(n: int, profile: str = "all_plus_one", values=None, today=None,
                  doc1: dict | None = None, doc2: dict | None = None) -> dict:
    doc1 = doc1 or load_json(os.path.join(DATADIR, f"C_{n}_structure.json"))
    doc2 = doc2 or load_json(os.path.join(DATADIR, f"C_{n}_gamma.json"))
    gb = gb_profile(n, profile, values)
    labels = doc1["basis"]["pbw_order"]
    idx = {l: i for i, l in enumerate(labels)}
    key = lambda lab: idx.get(lab, len(labels))
    ev = evaluate_gamma(doc2, gb)
    ev_recs = []
    for (x, y), comps in sorted(ev.items(), key=lambda kv: (idx[kv[0][0]], idx[kv[0][1]])):
        for z, c in sorted(comps.items(), key=lambda kv: key(kv[0])):
            ev_recs.append({"X": x, "Y": y, "Z": z, "coeff": frac_str(c)})
    deformed = []
    br = bracket_table_from_schema1(doc1)
    for x in labels:
        for y in labels:
            for z, c in sorted(br.get((x, y), {}).items(), key=lambda kv: key(kv[0])):
                deformed.append({"X": x, "Y": y, "Z": z, "coeff": frac_str(c), "kappa_order": 0})
            for z, c in sorted(ev.get((x, y), {}).items(), key=lambda kv: key(kv[0])):
                deformed.append({"X": x, "Y": y, "Z": z, "coeff": frac_str(c), "kappa_order": 1})
    return {
        "schema_version": "5.0",
        "schema_layer": 3,
        "algebra": doc1["algebra"],
        "source_structure": f"C_{n}_structure.json",
        "source_gamma": f"C_{n}_gamma.json",
        "central_elements": doc1["central_elements"],
        "inhomogeneous_deformation": doc2["inhomogeneous_deformation"],
        "gb_assignment": {"profile": profile, "values": {k: frac_str(v) for k, v in gb.items()}},
        "evaluated_gamma": ev_recs,
        "deformed_structure_constants": deformed,
        "deformed_bracket_form": "[X,Y]_gamma = sum_Z coeff(kappa_order=0) Z + kappa * sum_Z coeff(kappa_order=1) Z",
        "metadata": {
            "generated_by": "src/C_evaluate.py",
            "generation_date": today or _dt.date.today().isoformat(),
            "schema_specification": "docs/json_schema_specification.md",
            "notation": "handover/notation.md",
        },
    }


# --------------------------------------------------------------------------- checks


def check_schema3(doc3: dict, doc1: dict, doc2: dict) -> dict:
    n = doc1["algebra"]["n"]
    labels, parity = doc1["basis"]["pbw_order"], doc1["parity"]
    gb = {k: Fraction(v) for k, v in doc3["gb_assignment"]["values"].items()}
    stored = gamma_table_from_records(doc3["evaluated_gamma"], key="coeff")
    rep = {"n": n, "failures": {}, "counts": {}}

    # 1. independent recomputation with numeric gb in the engine
    _, br0, gam_num = compute_gamma(n, deformation=gb)
    fails = []
    for key in set(stored) | set(gam_num):
        if _padd(stored.get(key, {}), _pscale(gam_num.get(key, {}), -1)):
            fails.append(f"evaluated gamma{key} differs from direct numeric recomputation")
    rep["failures"]["matches_engine_recomputation"] = fails

    # 2. substitution into Schema 2
    subs = {k: {z: Poly.const(c) for z, c in v.items()} for k, v in evaluate_gamma(doc2, gb).items()}
    fails = []
    for key in set(stored) | set(subs):
        if _padd(stored.get(key, {}), _pscale(subs.get(key, {}), -1)):
            fails.append(f"evaluated gamma{key} differs from substitution into Schema 2")
    rep["failures"]["matches_schema2_substitution"] = fails

    # 3. kappa^0 records == Schema 1
    br = bracket_table_from_schema1(doc1)
    k0: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    k1 = 0
    for r in doc3["deformed_structure_constants"]:
        if r["kappa_order"] == 0:
            k0.setdefault((r["X"], r["Y"]), {})[r["Z"]] = Fraction(r["coeff"])
        else:
            k1 += 1
    rep["failures"]["kappa0_equals_schema1"] = [] if k0 == br else ["kappa_order 0 records differ from Schema 1"]
    if k1 != len(doc3["evaluated_gamma"]):
        rep["failures"]["kappa0_equals_schema1"].append("kappa_order 1 record count mismatch")

    # 4. numeric cocycle identity
    rep["failures"]["cocycle"] = cocycle_residuals(labels, parity, br, stored)
    rep["counts"]["nonzero_pairs"] = len(stored)
    rep["counts"]["pairs_with_K_component"] = sum(1 for v in stored.values() if "K" in v)
    rep["counts"]["triples_checked"] = len(labels) ** 3
    rep["passed"] = all(not v for v in rep["failures"].values())
    return rep


def print_report(rep: dict, title: str) -> None:
    print(f"== {title} (n={rep['n']}) ==")
    for k, v in rep["counts"].items():
        print(f"  {k}: {v}")
    for name, fails in rep["failures"].items():
        print(f"  {name:32s}: {'PASS' if not fails else f'FAIL ({len(fails)})'}")
        for line in fails[:5]:
            print("     ", line)
    print(f"  overall: {'PASS' if rep['passed'] else 'FAIL'}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--profile", default="all_plus_one")
    ap.add_argument("--values", default=None, help="JSON dict of gb values for --profile custom")
    ap.add_argument("--suffix", default=None, help="file suffix; default '' for all_plus_one, else '_<profile>'")
    ap.add_argument("--datadir", default=DATADIR)
    ap.add_argument("--no-check", action="store_true")
    args = ap.parse_args(argv)
    values = json.loads(args.values) if args.values else None
    suffix = args.suffix if args.suffix is not None else ("" if args.profile == "all_plus_one" else "_" + args.profile.replace(":", "_"))
    ok = True
    for n in args.n:
        doc1 = load_json(os.path.join(args.datadir, f"C_{n}_structure.json"))
        doc2 = load_json(os.path.join(args.datadir, f"C_{n}_gamma.json"))
        doc3 = build_schema3(n, args.profile, values, doc1=doc1, doc2=doc2)
        path = os.path.join(args.datadir, f"C_{n}_evaluated{suffix}.json")
        write_json(doc3, path)
        print(f"wrote {path}: profile={args.profile}, {len(doc3['evaluated_gamma'])} evaluated gamma records")
        if not args.no_check:
            rep = check_schema3(doc3, doc1, doc2)
            print_report(rep, "Schema 3 consistency")
            ok = ok and rep["passed"]
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
