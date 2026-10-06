#!/usr/bin/env python3
"""
src/verify_C_gamma.py

Verify consistency between Schema 2 (C_{n}_gamma.json) and Schema 1 (C_{n}_structure.json):

  Check 1 — Label validity:
    Every X, Y, Z in gamma_entries must appear in Schema 1's basis.

  Check 2 — gb label validity:
    Every gb label in gb_terms must appear in Schema 2's gb_matrix.labels.

  Check 3 — Parity consistency:
    gamma(X, Y) = kappa-coefficient of [X,Y]_gamma.
    Since [X,Y]_gamma has parity p(X)+p(Y) and kappa has parity 1,
    the coefficient gamma(X,Y) must have parity p(X)+p(Y)+1 mod 2.
    Hence every Z with a non-zero coefficient satisfies p(Z) == (p(X)+p(Y)+1) % 2.

  Check 4 — Antisymmetry:
    gamma(Y, X; Z)[gb] = -(-1)^{p(X)*p(Y)} * gamma(X, Y; Z)[gb]
    for every (X, Y, Z, gb) pair.

Usage:
    python3 src/verify_C_gamma.py
"""

import json
import os
import sys
from fractions import Fraction


DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load(n: int):
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    with open(os.path.join(DATA, f"C_{n}_gamma.json")) as f:
        s2 = json.load(f)
    return s1, s2


def verify_file(n: int):
    s1, s2 = load(n)

    # ── Schema 1 reference data ───────────────────────────────────────────────
    basis_set = set(s1["basis"]["even"] + s1["basis"]["odd"])
    parity = {k: int(v) for k, v in s1["parity"].items()}

    # ── Schema 2 data ─────────────────────────────────────────────────────────
    dinfo = s2["inhomogeneous_deformation"]
    gamma_entries = dinfo["gamma_entries"]
    gb_matrix_labels = dinfo["gb_matrix"]["labels"]
    valid_gb = {lbl for row in gb_matrix_labels for lbl in row}

    print(f"\n{'='*60}")
    print(f"C({n+1}) = osp(2|{2*n}),  n={n}")
    print(f"  Schema 1 basis size : {len(basis_set)}")
    print(f"  Schema 2 gb params  : {len(valid_gb)}")
    print(f"  gamma entries       : {len(gamma_entries)}")
    print(f"{'='*60}")

    failures = {1: [], 2: [], 3: [], 4: []}

    # Build lookup: (X, Y, Z, gb) -> Fraction
    gamma_map = {}
    for e in gamma_entries:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        for t in e["gb_terms"]:
            key = (X, Y, Z, t["gb"])
            gamma_map[key] = gamma_map.get(key, Fraction(0)) + Fraction(t["scalar"])

    for e in gamma_entries:
        X, Y, Z = e["X"], e["Y"], e["Z"]

        # ── Check 1: label validity ───────────────────────────────────────────
        for lbl, role in [(X, "X"), (Y, "Y"), (Z, "Z")]:
            if lbl not in basis_set:
                failures[1].append(f"  Unknown {role}='{lbl}' in entry ({X},{Y},{Z})")

        # ── Check 2: gb label validity ────────────────────────────────────────
        for t in e["gb_terms"]:
            if t["gb"] not in valid_gb:
                failures[2].append(
                    f"  Unknown gb='{t['gb']}' in entry ({X},{Y},{Z})"
                )

        # ── Check 3: parity consistency ───────────────────────────────────────
        if X in parity and Y in parity and Z in parity:
            px, py, pz = parity[X], parity[Y], parity[Z]
            # kappa is odd (parity 1); gamma(X,Y) has parity (px+py+1) % 2
            expected_pz = (px + py + 1) % 2
            if pz != expected_pz:
                failures[3].append(
                    f"  Parity fail: Z='{Z}' has p={pz}, "
                    f"expected (p({X})+p({Y})+1)%2 = {expected_pz}  entry ({X},{Y},{Z})"
                )

    # ── Check 4: antisymmetry ─────────────────────────────────────────────────
    checked = set()
    for (X, Y, Z, gb), fwd in gamma_map.items():
        if (X, Y, Z, gb) in checked:
            continue
        if X not in parity or Y not in parity:
            continue
        px, py = parity[X], parity[Y]
        sign = Fraction((-1) ** (px * py))
        rev = gamma_map.get((Y, X, Z, gb), Fraction(0))
        expected_rev = -sign * fwd
        if rev != expected_rev:
            failures[4].append(
                f"  Antisymmetry fail: gamma({X},{Y};{Z})[{gb}]={fwd}, "
                f"gamma({Y},{X};{Z})[{gb}]={rev}, expected {expected_rev}"
            )
        checked.add((X, Y, Z, gb))
        checked.add((Y, X, Z, gb))

    # ── Report ────────────────────────────────────────────────────────────────
    checks = {
        1: "Label validity",
        2: "gb label validity",
        3: "Parity consistency",
        4: "Antisymmetry",
    }
    all_pass = True
    results = {}
    for k, name in checks.items():
        fl = failures[k]
        ok = len(fl) == 0
        all_pass = all_pass and ok
        results[k] = ok
        status = "PASS" if ok else f"FAIL ({len(fl)} violations)"
        print(f"  Check {k} — {name}: {status}")
        for msg in fl[:5]:
            print(msg)
        if len(fl) > 5:
            print(f"    ... ({len(fl)-5} more)")

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
            parts.append(f"C{k}={'PASS' if ok else 'FAIL(' + str(fc) + ')'}")
        detail = "  ".join(parts)
        print(f"  n={r['n']}: {tag}  [{detail}]")
        overall = overall and r["all_pass"]
    print(f"\nOverall: {'ALL PASS' if overall else 'FAILURES DETECTED'}")


if __name__ == "__main__":
    main()
