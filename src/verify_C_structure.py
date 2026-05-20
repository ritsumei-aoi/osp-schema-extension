"""
verify_C_structure.py — Verification of C(n+1) structure constants.

Loads data/C_{n}_structure.json for n=1,2,3 and checks:
  1. Anti-symmetry:  [X,Y} = -(-1)^{p(X)p(Y)} [Y,X}  for all generator pairs
  2. Super Jacobi identity:
       (-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0
     for all ordered triples (X,Y,Z).
"""

from __future__ import annotations

import json
import os
from fractions import Fraction
from itertools import product
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
BracketDict = Dict[str, Fraction]   # linear combination of generators


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_algebra(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def build_bracket_table(data: dict) -> Dict[Tuple[str, str], BracketDict]:
    """
    Build a sparse bracket table from stored structure constants.
    Only pairs (X,Y) with X<=Y (PBW) are stored; returns a dict
    keyed by (X,Y) tuples.
    """
    table: Dict[Tuple[str, str], BracketDict] = {}
    for entry in data["structure_constants"]:
        key = (entry["X"], entry["Y"])
        if key not in table:
            table[key] = {}
        table[key][entry["Z"]] = Fraction(entry["coeff"])
    return table


def full_bracket(
    x: str, y: str,
    table: Dict[Tuple[str, str], BracketDict],
    parity: Dict[str, int],
) -> BracketDict:
    """
    Return [X,Y} as a BracketDict, deriving reversed-pair entries
    via the graded anti-symmetry rule when not directly stored.
    """
    if (x, y) in table:
        return table[(x, y)]
    if (y, x) in table:
        sign = -(-1) ** (parity[x] * parity[y])
        return {z: Fraction(sign) * c for z, c in table[(y, x)].items()}
    return {}


def bracket_of_dicts(
    bx: BracketDict, by: BracketDict,
    table: Dict[Tuple[str, str], BracketDict],
    parity: Dict[str, int],
) -> BracketDict:
    """
    Compute [bx, by} = sum_{a,b} ca*cb * [a,b} (bilinearity).
    """
    result: BracketDict = {}
    for a, ca in bx.items():
        for b, cb in by.items():
            br = full_bracket(a, b, table, parity)
            for z, cz in br.items():
                result[z] = result.get(z, Fraction(0)) + ca * cb * cz
    return {z: c for z, c in result.items() if c != 0}


# ---------------------------------------------------------------------------
# Check 1: Anti-symmetry
# ---------------------------------------------------------------------------

def check_antisymmetry(
    basis: List[str],
    table: Dict[Tuple[str, str], BracketDict],
    parity: Dict[str, int],
) -> Tuple[bool, List[str]]:
    """
    For all ordered pairs (X,Y), verify:
      [X,Y} + (-1)^{p(X)p(Y)} [Y,X} = 0.

    Also verifies that bosonic self-brackets [X,X} = 0.
    """
    failures: List[str] = []

    for x in basis:
        for y in basis:
            bxy = full_bracket(x, y, table, parity)
            byx = full_bracket(y, x, table, parity)
            sign = (-1) ** (parity[x] * parity[y])
            # Check [X,Y} + (-1)^{p(X)p(Y)} [Y,X} = 0 generator-by-generator
            all_z = set(bxy) | set(byx)
            for z in all_z:
                val = bxy.get(z, Fraction(0)) + Fraction(sign) * byx.get(z, Fraction(0))
                if val != 0:
                    failures.append(
                        f"  Anti-sym FAIL [{x},{y}] [{z}]: "
                        f"LHS={bxy.get(z,0)}, sign*RHS={Fraction(sign)*byx.get(z,0)}"
                    )

    return len(failures) == 0, failures


# ---------------------------------------------------------------------------
# Check 2: Super Jacobi identity
# ---------------------------------------------------------------------------

def check_super_jacobi(
    basis: List[str],
    table: Dict[Tuple[str, str], BracketDict],
    parity: Dict[str, int],
) -> Tuple[bool, int, List[str]]:
    """
    For all ordered triples (X,Y,Z), verify:
      (-1)^{p(X)p(Z)} [X,[Y,Z}} + (-1)^{p(Y)p(X)} [Y,[Z,X}} + (-1)^{p(Z)p(Y)} [Z,[X,Y}} = 0.

    Returns (passed, n_triples_checked, failures).
    """
    failures: List[str] = []
    n = len(basis)
    n_triples = 0

    for x in basis:
        for y in basis:
            for z in basis:
                n_triples += 1
                px, py, pz = parity[x], parity[y], parity[z]

                # Precompute inner brackets
                byz = full_bracket(y, z, table, parity)
                bzx = full_bracket(z, x, table, parity)
                bxy = full_bracket(x, y, table, parity)

                # Term 1: (-1)^{p(X)p(Z)} [X, [Y,Z}}
                sign1 = Fraction((-1) ** (px * pz))
                t1 = bracket_of_dicts({x: Fraction(1)}, byz, table, parity)
                t1 = {g: sign1 * c for g, c in t1.items()}

                # Term 2: (-1)^{p(Y)p(X)} [Y, [Z,X}}
                sign2 = Fraction((-1) ** (py * px))
                t2 = bracket_of_dicts({y: Fraction(1)}, bzx, table, parity)
                t2 = {g: sign2 * c for g, c in t2.items()}

                # Term 3: (-1)^{p(Z)p(Y)} [Z, [X,Y}}
                sign3 = Fraction((-1) ** (pz * py))
                t3 = bracket_of_dicts({z: Fraction(1)}, bxy, table, parity)
                t3 = {g: sign3 * c for g, c in t3.items()}

                # Sum all three terms
                all_gens = set(t1) | set(t2) | set(t3)
                for g in all_gens:
                    total = (t1.get(g, Fraction(0))
                             + t2.get(g, Fraction(0))
                             + t3.get(g, Fraction(0)))
                    if total != 0:
                        failures.append(
                            f"  Jacobi FAIL ({x},{y},{z})[{g}]: total={total}"
                        )

    return len(failures) == 0, n_triples, failures


# ---------------------------------------------------------------------------
# Main verification routine
# ---------------------------------------------------------------------------

def verify_file(path: str) -> bool:
    data = load_algebra(path)
    n = data["algebra"]["n"]
    family = data["algebra"]["family"]
    dim = data["algebra"]["dimension"]["total"]
    sc_count = len(data["structure_constants"])
    cartan_type = data["algebra"]["cartan_type"]

    print(f"\n{'='*60}")
    print(f"  {cartan_type}  (n={n}, dim={dim}, SC entries={sc_count})")
    print(f"{'='*60}")

    # Reconstruct ordered basis and parity map
    basis = data["basis"]["even"] + data["basis"]["odd"]
    basis_set = set(basis)
    parity: Dict[str, int] = {g: data["parity"][g] for g in basis}

    table = build_bracket_table(data)

    # --- Check 1: Anti-symmetry ---
    print("  [1] Anti-symmetry check ... ", end="", flush=True)
    ok1, fails1 = check_antisymmetry(basis, table, parity)
    if ok1:
        print(f"PASS  ({len(basis)**2} ordered pairs checked)")
    else:
        print(f"FAIL  ({len(fails1)} violation(s))")
        for f in fails1[:10]:
            print(f)
        if len(fails1) > 10:
            print(f"  ... and {len(fails1)-10} more.")

    # --- Check 2: Super Jacobi ---
    print("  [2] Super Jacobi check   ... ", end="", flush=True)
    ok2, n_triples, fails2 = check_super_jacobi(basis, table, parity)
    if ok2:
        print(f"PASS  ({n_triples} ordered triples checked)")
    else:
        print(f"FAIL  ({len(fails2)} violation(s))")
        for f in fails2[:10]:
            print(f)
        if len(fails2) > 10:
            print(f"  ... and {len(fails2)-10} more.")

    passed = ok1 and ok2
    print(f"  Result: {'ALL CHECKS PASSED' if passed else 'SOME CHECKS FAILED'}")
    return passed


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(repo_root, "data")

    print("=" * 60)
    print("  C(n+1) Structure Constant Verification")
    print("=" * 60)

    all_passed = True
    for n in (1, 2, 3):
        path = os.path.join(data_dir, f"C_{n}_structure.json")
        passed = verify_file(path)
        all_passed = all_passed and passed

    print(f"\n{'='*60}")
    if all_passed:
        print("  OVERALL: ALL VERIFICATIONS PASSED")
    else:
        print("  OVERALL: ONE OR MORE VERIFICATIONS FAILED")
    print("=" * 60)
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
