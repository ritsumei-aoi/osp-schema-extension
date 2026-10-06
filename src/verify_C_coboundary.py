#!/usr/bin/env python3
"""
src/verify_C_coboundary.py

Verify consistency between Schema 4 (C_{n}_coboundary.json) and Schema 1:

  Check 1 — Label validity:
    Every X, Y, Z in coboundary_entries exists in Schema 1 basis.

  Check 2 — phi label validity:
    Every phi label in phi_terms exists in the Schema 4 phi catalogue.

  Check 3 — Parity of output generator:
    (delta f)(X, Y; Z) is the coefficient of Z.
    f is odd, so (delta f)(X, Y) has parity p(X) + p(Y) + 1 (mod 2),
    meaning every non-zero Z must satisfy p(Z) == (p(X) + p(Y) + 1) % 2.

  Check 4 — Antisymmetry under (X, Y) <-> (Y, X):
    From the coboundary formula:
      (delta f)(Y, X) = (-1)^{p(Y)} [Y, f(X)]
                       - (-1)^{(p(Y)+1)*p(X)} [X, f(Y)]
                       - f([Y, X])
    And [Y, X} = -(-1)^{p(X)*p(Y)} [X, Y}, f([Y,X}) = -(-1)^{p(X)*p(Y)} f([X,Y}).
    Working through the signs, we expect:
      (delta f)(Y, X; Z)[phi] = -(-1)^{p(X)*p(Y)} * (delta f)(X, Y; Z)[phi].

  Check 5 — Linearity spot-check:
    Verify the coboundary formula directly for a few triples (X, Y, phi=e_k)
    by setting one phi=1, all others 0, and checking against the explicit
    bracket computation from Schema 1.

Usage:
    python3 src/verify_C_coboundary.py
"""

import json
import os
from fractions import Fraction


DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load(n: int):
    with open(os.path.join(DATA, f"C_{n}_structure.json")) as f:
        s1 = json.load(f)
    with open(os.path.join(DATA, f"C_{n}_coboundary.json")) as f:
        s4 = json.load(f)
    return s1, s4


def build_sc(s1: dict) -> dict:
    sc = {}
    for e in s1["structure_constants"]:
        key = (e["X"], e["Y"])
        sc.setdefault(key, {})
        sc[key][e["Z"]] = sc[key].get(e["Z"], Fraction(0)) + Fraction(e["coeff"])
    return sc


def verify_file(n: int):
    s1, s4 = load(n)
    basis_set = set(s1["basis"]["even"] + s1["basis"]["odd"])
    parity = {k: int(v) for k, v in s1["parity"].items()}

    cb_entries = s4["coboundary_entries"]
    phi_eo_set = {e["phi"] for e in s4["f_parametrization"]["phi_eo_labels"]}
    phi_oe_set = {e["phi"] for e in s4["f_parametrization"]["phi_oe_labels"]}
    valid_phi  = phi_eo_set | phi_oe_set

    # Build coboundary lookup: (X, Y, Z, phi) -> Fraction
    cb_map: dict = {}
    for e in cb_entries:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        for t in e["phi_terms"]:
            key = (X, Y, Z, t["phi"])
            cb_map[key] = cb_map.get(key, Fraction(0)) + Fraction(t["scalar"])

    print(f"\n{'='*60}")
    print(f"C({n+1}) = osp(2|{2*n}),  n={n}")
    print(f"  coboundary entries : {len(cb_entries)}")
    print(f"  phi parameters     : {len(valid_phi)}")
    print(f"{'='*60}")

    failures = {1: [], 2: [], 3: [], 4: [], 5: []}

    # ── Check 1: label validity ───────────────────────────────────────────────
    for e in cb_entries:
        for lbl, role in [(e["X"],"X"), (e["Y"],"Y"), (e["Z"],"Z")]:
            if lbl not in basis_set:
                failures[1].append(f"  Unknown {role}='{lbl}'")

    # ── Check 2: phi label validity ───────────────────────────────────────────
    for e in cb_entries:
        for t in e["phi_terms"]:
            if t["phi"] not in valid_phi:
                failures[2].append(f"  Unknown phi='{t['phi']}'")

    # ── Check 3: parity of Z ─────────────────────────────────────────────────
    for e in cb_entries:
        X, Y, Z = e["X"], e["Y"], e["Z"]
        if X in parity and Y in parity and Z in parity:
            expected_pz = (parity[X] + parity[Y] + 1) % 2
            if parity[Z] != expected_pz:
                failures[3].append(
                    f"  p({Z})={parity[Z]}, "
                    f"expected (p({X})+p({Y})+1)%2={expected_pz}"
                )

    # ── Check 4: antisymmetry (delta f)(Y,X;Z) = -(-1)^{px*py} (delta f)(X,Y;Z)
    checked = set()
    for (X, Y, Z, phi), fwd in cb_map.items():
        if (X, Y, Z, phi) in checked:
            continue
        if X not in parity or Y not in parity:
            continue
        px, py = parity[X], parity[Y]
        sign = Fraction((-1) ** (px * py))
        rev = cb_map.get((Y, X, Z, phi), Fraction(0))
        expected_rev = -sign * fwd
        if rev != expected_rev:
            failures[4].append(
                f"  (delta f)({X},{Y};{Z})[{phi}]={fwd}, "
                f"(delta f)({Y},{X};{Z})[{phi}]={rev}, expected {expected_rev}"
            )
        checked.add((X, Y, Z, phi))
        checked.add((Y, X, Z, phi))

    # ── Check 5: linearity spot-check ────────────────────────────────────────
    # For a sample phi=phi_eo_{O0}_{E0} set to 1 (all others 0):
    # f(E0) = O0, f(anything_else) = 0
    # Then (delta f)(X,Y;Z) from formula:
    #   = (-1)^px * [X, f(Y)][Z] - (-1)^{(px+1)*py} * [Y, f(X)][Z] - f([X,Y])[Z]
    # where f(Y) = O0 if Y==E0 else 0, etc.

    sc = build_sc(s1)
    even_gens = s1["basis"]["even"]
    odd_gens  = s1["basis"]["odd"]

    # pick first phi_eo entry
    if s4["f_parametrization"]["phi_eo_labels"]:
        sample = s4["f_parametrization"]["phi_eo_labels"][0]
        phi_lbl = sample["phi"]
        src     = sample["from"]   # even generator
        tgt     = sample["to"]     # odd generator
        # f(src) = tgt; f(anything else) = 0 for this one-hot phi
        def f_onehot(gen, par_dict):
            if gen == src and par_dict[gen] == 0:
                return {tgt: Fraction(1)}
            return {}

        basis = even_gens + odd_gens
        spot_failures = 0
        for X in basis[:6]:   # spot-check first 6 generators
            for Y in basis[:6]:
                px = parity[X]; py = parity[Y]
                s1_ = Fraction((-1)**px)
                s2_ = Fraction((-1)**((px+1)*py))
                # term1: s1 * [X, f(Y)]
                fY = f_onehot(Y, parity)
                t1 = {}
                for Z2, c2 in fY.items():
                    for W, sc_c in sc.get((X, Z2), {}).items():
                        t1[W] = t1.get(W, Fraction(0)) + s1_ * c2 * sc_c
                # term2: -s2 * [Y, f(X)]
                fX = f_onehot(X, parity)
                t2 = {}
                for Z2, c2 in fX.items():
                    for W, sc_c in sc.get((Y, Z2), {}).items():
                        t2[W] = t2.get(W, Fraction(0)) - s2_ * c2 * sc_c
                # term3: -f([X,Y])
                XY = sc.get((X, Y), {})
                t3 = {}
                for Z2, c2 in XY.items():
                    for W, v in f_onehot(Z2, parity).items():
                        t3[W] = t3.get(W, Fraction(0)) - c2 * v

                # expected = t1 + t2 + t3
                expected: dict = {}
                for d in [t1, t2, t3]:
                    for W, v in d.items():
                        expected[W] = expected.get(W, Fraction(0)) + v
                expected = {W: v for W, v in expected.items() if v}

                # actual from schema 4
                actual: dict = {}
                for W in set(expected) | {W for (X2,Y2,W,p),_ in cb_map.items()
                                           if X2==X and Y2==Y and p==phi_lbl}:
                    v = cb_map.get((X, Y, W, phi_lbl), Fraction(0))
                    if v:
                        actual[W] = v

                if expected != actual:
                    spot_failures += 1
                    failures[5].append(
                        f"  ({X},{Y}) phi={phi_lbl}: "
                        f"expected={dict(expected)}, got={dict(actual)}"
                    )

    # ── Report ────────────────────────────────────────────────────────────────
    names = {
        1: "Label validity",
        2: "phi label validity",
        3: "Parity of output Z",
        4: "Antisymmetry (delta f)(Y,X)=-(-1)^{px*py}(delta f)(X,Y)",
        5: "Linearity spot-check (one-hot phi)",
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
        parts = ["C" + str(k) + "=" + ("PASS" if ok else "FAIL(" + str(r["failures"][k]) + ")")
                 for k, ok in r["results"].items()]
        print(f"  n={r['n']}: {tag}  [{', '.join(parts)}]")
        overall = overall and r["all_pass"]
    print(f"\nOverall: {'ALL PASS' if overall else 'FAILURES DETECTED'}")


if __name__ == "__main__":
    main()
