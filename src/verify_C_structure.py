#!/usr/bin/env python3
"""
src/verify_C_structure.py

Verify the C(n+1) Schema 1 JSON files satisfy:
  1. Graded antisymmetry:  c_XY^Z + (-1)^{px*py} c_YX^Z = 0
  2. Super Jacobi identity: sum of three cyclic terms = 0

Works entirely from the JSON data; no re-computation of oscillator algebra.

Usage:
    python3 src/verify_C_structure.py
"""

import json
import os
from fractions import Fraction
from itertools import product


# ── Load schema ───────────────────────────────────────────────────────────────

def load_schema(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def build_tables(schema: dict):
    """
    Return:
      basis  : list of generator labels (ordered)
      parity : dict label -> 0/1
      sc     : dict (X, Y) -> dict Z -> Fraction   (all stored pairs)
    """
    basis  = schema["basis"]["odd"] + schema["basis"]["even"]
    parity = {k: v for k, v in schema["parity"].items()}

    sc: dict = {}
    for entry in schema["structure_constants"]:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        key = (x, y)
        if key not in sc:
            sc[key] = {}
        sc[key][z] = sc[key].get(z, Fraction(0)) + c

    return basis, parity, sc


def bracket_result(x: str, y: str, sc: dict) -> dict:
    """Return {Z: Fraction} for [X, Y}, zero dict if not stored."""
    return dict(sc.get((x, y), {}))


# ── Check 1: Graded antisymmetry ──────────────────────────────────────────────

def check_antisymmetry(basis, parity, sc) -> tuple[bool, list]:
    """
    Verify [X,Y} = -(-1)^{px*py} [Y,X} for all pairs (X,Y).
    Returns (all_pass, list_of_failures).
    """
    failures = []
    for x in basis:
        for y in basis:
            px, py = parity[x], parity[y]
            sign = (-1) ** (px * py)
            fwd = bracket_result(x, y, sc)
            rev = bracket_result(y, x, sc)
            # Check: fwd[z] + sign * rev[z] == 0 for all z
            all_z = set(fwd) | set(rev)
            for z in all_z:
                lhs = fwd.get(z, Fraction(0)) + sign * rev.get(z, Fraction(0))
                if lhs != 0:
                    failures.append({
                        "X": x, "Y": y, "Z": z,
                        "expected": 0, "got": str(lhs),
                    })
    return len(failures) == 0, failures


# ── Check 2: Super Jacobi identity ────────────────────────────────────────────

def jacobi_sum(x, y, z, parity, sc) -> dict:
    """
    Compute the Jacobi sum for (X,Y,Z):
      (-1)^{px*pz} [X,[Y,Z]] + (-1)^{py*px} [Y,[Z,X]] + (-1)^{pz*py} [Z,[X,Y]]

    Returns {generator: Fraction}; should be the zero dict.
    """
    px, py, pz = parity[x], parity[y], parity[z]

    def nested(a, b, c, pa, pb, pc, sign_outer):
        """sign_outer * [A, [B, C]]"""
        inner = bracket_result(b, c, sc)
        result: dict = {}
        for w, cw in inner.items():
            pw = parity[w]
            outer = bracket_result(a, w, sc)
            for v, cv in outer.items():
                result[v] = result.get(v, Fraction(0)) + sign_outer * cw * cv
        return result

    s1 = (-1) ** (px * pz)
    s2 = (-1) ** (py * px)
    s3 = (-1) ** (pz * py)

    total: dict = {}
    for term in [
        nested(x, y, z, px, py, pz, s1),
        nested(y, z, x, py, pz, px, s2),
        nested(z, x, y, pz, px, py, s3),
    ]:
        for v, cv in term.items():
            total[v] = total.get(v, Fraction(0)) + cv

    return {v: c for v, c in total.items() if c != 0}


def check_jacobi(basis, parity, sc) -> tuple[bool, list]:
    """
    Check Super Jacobi identity for all unordered triples {X, Y, Z}.
    We fix one representative ordering (i ≤ j ≤ k by index) to avoid
    redundant checks; all orderings of the same triple give the same condition.
    """
    failures = []
    N = len(basis)
    for i in range(N):
        for j in range(i, N):
            for k in range(j, N):
                x, y, z = basis[i], basis[j], basis[k]
                res = jacobi_sum(x, y, z, parity, sc)
                if res:
                    failures.append({
                        "X": x, "Y": y, "Z": z,
                        "residual": {k: str(v) for k, v in res.items()},
                    })
    return len(failures) == 0, failures


# ── Main ──────────────────────────────────────────────────────────────────────

def verify_file(path: str) -> dict:
    schema = load_schema(path)
    n = schema["algebra"]["n"]
    basis, parity, sc = build_tables(schema)
    N = len(basis)

    print(f"\n{'='*60}")
    print(f"C({n+1}) = osp(2|{2*n}),  n={n},  dim={N},  SC entries={len(schema['structure_constants'])}")
    print(f"{'='*60}")

    # Antisymmetry
    asym_pass, asym_fail = check_antisymmetry(basis, parity, sc)
    n_pairs = N * N
    print(f"Antisymmetry  ({n_pairs} pairs): {'PASS' if asym_pass else f'FAIL  ({len(asym_fail)} violations)'}")
    if not asym_pass:
        for f in asym_fail[:5]:
            print(f"  [{f['X']},{f['Y']}]->{f['Z']}: {f['got']} (expected 0)")

    # Jacobi
    n_triples = N * (N + 1) * (N + 2) // 6
    jac_pass, jac_fail = check_jacobi(basis, parity, sc)
    print(f"Super Jacobi  ({n_triples} triples): {'PASS' if jac_pass else f'FAIL  ({len(jac_fail)} violations)'}")
    if not jac_pass:
        for f in jac_fail[:5]:
            print(f"  [{f['X']},{f['Y']},{f['Z']}]: {f['residual']}")

    return {
        "n": n,
        "antisymmetry": {"pass": asym_pass, "failures": len(asym_fail)},
        "jacobi":       {"pass": jac_pass,  "failures": len(jac_fail)},
    }


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    results = []
    for n in [1, 2, 3]:
        path = os.path.join(data_dir, f"C_{n}_structure.json")
        results.append(verify_file(path))

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    all_pass = True
    for r in results:
        asym = "PASS" if r["antisymmetry"]["pass"] else f"FAIL({r['antisymmetry']['failures']})"
        jac  = "PASS" if r["jacobi"]["pass"]       else f"FAIL({r['jacobi']['failures']})"
        ok = r["antisymmetry"]["pass"] and r["jacobi"]["pass"]
        all_pass = all_pass and ok
        print(f"  n={r['n']}: antisymmetry={asym}  jacobi={jac}  {'OK' if ok else 'FAILED'}")
    print(f"\nOverall: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")


if __name__ == "__main__":
    main()
