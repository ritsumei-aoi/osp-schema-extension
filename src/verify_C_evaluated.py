#!/usr/bin/env python3
"""
src/verify_C_evaluated.py

Verify consistency between Schema 3 (C_{n}_evaluated.json) and Schema 2
(C_{n}_gamma.json):

  Check 1 — structure_constants match Schema 1:
    Every entry in Schema 3's structure_constants appears verbatim in Schema 1.
    Schema 1 entry count == Schema 3 structure_constant count.

  Check 2 — kappa coefficient count consistency:
    For each (X, Y, Z) in kappa_structure_constants, verify that the
    coefficient equals sum over gb_terms in Schema 2 of (scalar * gb_value).

  Check 3 — label validity:
    Every X, Y, Z in kappa_structure_constants appears in Schema 1 basis.

  Check 4 — parity consistency (kappa part):
    p(Z) == (p(X) + p(Y) + 1) % 2  for every kappa entry
    (same rule as Schema 2 verification).

  Check 5 — antisymmetry of kappa part:
    kappa_coeff(Y, X; Z) == -(-1)^{p(X)*p(Y)} * kappa_coeff(X, Y; Z).

Usage:
    python3 src/verify_C_evaluated.py
"""

import json
import os
from fractions import Fraction


DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load(n: int):
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    with open(os.path.join(DATA, f"C_{n}_gamma.json")) as f:
        s2 = json.load(f)
    with open(os.path.join(DATA, f"C_{n}_evaluated.json")) as f:
        s3 = json.load(f)
    return s1, s2, s3


def verify_file(n: int):
    s1, s2, s3 = load(n)

    basis_set = set(s1["basis"]["even"] + s1["basis"]["odd"])
    parity = {k: int(v) for k, v in s1["parity"].items()}

    sc3 = s3["structure_constants"]
    ksc3 = s3["kappa_structure_constants"]
    gb_values = {k: Fraction(v) for k, v in s3["evaluation"]["gb_values"].items()}

    print(f"\n{'='*60}")
    print(f"C({n+1}) = osp(2|{2*n}),  n={n}")
    print(f"  s.c. entries   : {len(sc3)}")
    print(f"  kappa s.c.     : {len(ksc3)}")
    print(f"{'='*60}")

    failures = {1: [], 2: [], 3: [], 4: [], 5: []}

    # ── Check 1: structure_constants match Schema 1 ──────────────────────────
    sc1_set = {(e["X"], e["Y"], e["Z"], e["coeff"]) for e in s1["structure_constants"]}
    sc3_set = {(e["X"], e["Y"], e["Z"], e["coeff"]) for e in sc3}
    for key in sc1_set - sc3_set:
        failures[1].append(f"  In S1 but not S3: {key}")
    for key in sc3_set - sc1_set:
        failures[1].append(f"  In S3 but not S1: {key}")

    # ── Build Schema 2 expected kappa coefficients ───────────────────────────
    # Accumulate (X,Y,Z) -> Fraction from gamma_entries with gb substituted
    expected_kappa: dict = {}
    for e in s2["inhomogeneous_deformation"]["gamma_entries"]:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        total = sum(Fraction(t["scalar"]) * gb_values.get(t["gb"], Fraction(0))
                    for t in e["gb_terms"])
        if total:
            key = (X, Y, Z)
            expected_kappa[key] = expected_kappa.get(key, Fraction(0)) + total

    # actual kappa coefficients from Schema 3
    actual_kappa: dict = {}
    for e in ksc3:
        key = (e["X"], e["Y"], e["Z"])
        actual_kappa[key] = actual_kappa.get(key, Fraction(0)) + Fraction(e["coeff"])

    # ── Check 2: numeric coefficients match Schema 2 evaluation ──────────────
    all_keys = set(expected_kappa) | set(actual_kappa)
    for key in sorted(all_keys):
        exp = expected_kappa.get(key, Fraction(0))
        act = actual_kappa.get(key, Fraction(0))
        if exp != act:
            failures[2].append(
                f"  ({key[0]},{key[1]};{key[2]}): expected={exp}, got={act}"
            )

    # ── Check 3: label validity ───────────────────────────────────────────────
    for e in ksc3:
        for lbl, role in [(e["X"], "X"), (e["Y"], "Y"), (e["Z"], "Z")]:
            if lbl not in basis_set:
                failures[3].append(f"  Unknown {role}='{lbl}'")

    # ── Check 4: parity consistency ──────────────────────────────────────────
    for e in ksc3:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        if X in parity and Y in parity and Z in parity:
            expected_pz = (parity[X] + parity[Y] + 1) % 2
            if parity[Z] != expected_pz:
                failures[4].append(
                    f"  p({Z})={parity[Z]}, expected (p({X})+p({Y})+1)%2={expected_pz}"
                )

    # ── Check 5: antisymmetry of kappa part ──────────────────────────────────
    checked = set()
    for (X, Y, Z), fwd in actual_kappa.items():
        if (X, Y, Z) in checked:
            continue
        if X not in parity or Y not in parity:
            continue
        px, py = parity[X], parity[Y]
        sign = Fraction((-1) ** (px * py))
        rev = actual_kappa.get((Y, X, Z), Fraction(0))
        expected_rev = -sign * fwd
        if rev != expected_rev:
            failures[5].append(
                f"  kappa({X},{Y};{Z})={fwd}, kappa({Y},{X};{Z})={rev} "
                f"(expected {expected_rev})"
            )
        checked.add((X, Y, Z))
        checked.add((Y, X, Z))

    # ── Report ────────────────────────────────────────────────────────────────
    names = {
        1: "structure_constants match Schema 1",
        2: "kappa numeric coefficients match Schema 2",
        3: "kappa label validity",
        4: "kappa parity consistency",
        5: "kappa antisymmetry",
    }
    all_pass = True
    results = {}
    for k, name in names.items():
        fl = failures[k]
        ok = len(fl) == 0
        all_pass = all_pass and ok
        results[k] = ok
        status = "PASS" if ok else f"FAIL ({len(fl)} violations)"
        print(f"  Check {k} — {name}: {status}")
        for msg in fl[:3]:
            print(msg)
        if len(fl) > 3:
            print(f"    ... ({len(fl)-3} more)")

    return {"n": n, "all_pass": all_pass, "results": results,
            "failures": {k: len(v) for k, v in failures.items()}}


def main():
    all_results = []
    for n in [1, 2, 3]:
        all_results.append(verify_file(n))

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    overall = True
    for r in all_results:
        tag = "OK" if r["all_pass"] else "FAILED"
        parts = []
        for k, ok in r["results"].items():
            fc = r["failures"][k]
            parts.append("C" + str(k) + "=" + ("PASS" if ok else "FAIL(" + str(fc) + ")"))
        print(f"  n={r['n']}: {tag}  [{', '.join(parts)}]")
        overall = overall and r["all_pass"]
    print(f"\nOverall: {'ALL PASS' if overall else 'FAILURES DETECTED'}")


if __name__ == "__main__":
    main()
