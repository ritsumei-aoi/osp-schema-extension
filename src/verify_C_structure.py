"""
verify_C_structure.py
Independent verification of Schema 1 JSON structure constants for C(n+1).

Checks:
  1. Graded anti-symmetry: [X,Y} + (-1)^{pX*pY} [Y,X} = 0 for all pairs
  2. Super Jacobi identity:
       [X,[Y,Z}} + (-1)^{pX(pY+pZ)} [Y,[Z,X}} + (-1)^{pZ(pX+pY)} [Z,[X,Y}} = 0
     for all ordered triples (i < j < k in PBW basis order)

Usage:
  python src/verify_C_structure.py [data_dir]
  (default data_dir: data/)
"""

import json
import sys
from fractions import Fraction
from collections import defaultdict
from pathlib import Path


def load_schema(path):
    """
    Load C_n_structure.json.
    Returns (parity, basis, basis_idx, sc) where:
      parity    : {label: int}
      basis     : [label, ...]  (odd-first PBW order)
      basis_idx : {label: int}
      sc        : {(X, Y): {Z: Fraction}}   X < Y in PBW order
    """
    with open(path) as f:
        data = json.load(f)

    parity = {k: int(v) for k, v in data["parity"].items()}
    basis = data["basis"]["odd"] + data["basis"]["even"]
    basis_idx = {b: i for i, b in enumerate(basis)}

    sc = {}
    for entry in data["structure_constants"]:
        X, Y, Z = entry["X"], entry["Y"], entry["Z"]
        c = Fraction(entry["coeff"])
        key = (X, Y)
        if key not in sc:
            sc[key] = {}
        sc[key][Z] = sc[key].get(Z, Fraction(0)) + c
    # Drop exact zeros (shouldn't exist, but be safe)
    sc = {k: {z: c for z, c in v.items() if c != 0} for k, v in sc.items()}

    return parity, basis, basis_idx, sc


def br(sc, parity, basis_idx, X, Y):
    """
    Compute [X, Y} from stored structure constants.
    Returns {Z: Fraction coeff}.
    """
    if X == Y:
        return {}
    ix, iy = basis_idx[X], basis_idx[Y]
    if ix < iy:
        return dict(sc.get((X, Y), {}))
    # X > Y in PBW: use anti-symmetry  [X,Y} = -(-1)^{pX*pY} [Y,X}
    sign = Fraction((-1) ** (parity[X] * parity[Y]))
    raw = sc.get((Y, X), {})
    return {z: -sign * c for z, c in raw.items() if -sign * c != 0}


def br_poly(sc, parity, basis_idx, X, poly):
    """
    Compute [X, poly} where poly = {Z: Fraction coeff}.
    Linearity: [X, sum c_i Z_i} = sum c_i [X, Z_i}.
    """
    result = defaultdict(Fraction)
    for Z, cz in poly.items():
        if cz == 0:
            continue
        for W, cw in br(sc, parity, basis_idx, X, Z).items():
            result[W] += cz * cw
    return {k: v for k, v in result.items() if v != 0}


# ---------------------------------------------------------------------------
# Check 1: Graded anti-symmetry
# ---------------------------------------------------------------------------

def check_antisymmetry(sc, parity, basis_idx):
    """
    For every stored pair (X, Y) with X < Y, verify:
      [X, Y} + (-1)^{pX*pY} * [Y, X} = 0
    where [Y, X} is reconstructed via br().
    """
    failures = []
    for (X, Y) in sc:
        sign = (-1) ** (parity[X] * parity[Y])
        br_XY = sc.get((X, Y), {})
        br_YX = br(sc, parity, basis_idx, Y, X)  # reconstructed
        combined = defaultdict(Fraction, br_XY)
        for z, c in br_YX.items():
            combined[z] += Fraction(sign) * c
        nonzero = {k: v for k, v in combined.items() if v != 0}
        if nonzero:
            failures.append((X, Y, nonzero))
    return failures


# ---------------------------------------------------------------------------
# Check 2: Super Jacobi identity
# ---------------------------------------------------------------------------

def check_jacobi(sc, parity, basis, basis_idx):
    """
    For all ordered triples (i < j < k), verify:
      J(X,Y,Z) = [X,[Y,Z}} + (-1)^{pX(pY+pZ)} [Y,[Z,X}}
                            + (-1)^{pZ(pX+pY)} [Z,[X,Y}} = 0
    """
    failures = []
    n = len(basis)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                X, Y, Z = basis[i], basis[j], basis[k]
                pX, pY, pZ = parity[X], parity[Y], parity[Z]

                bYZ = br(sc, parity, basis_idx, Y, Z)
                t1 = br_poly(sc, parity, basis_idx, X, bYZ)

                bZX = br(sc, parity, basis_idx, Z, X)
                t2 = br_poly(sc, parity, basis_idx, Y, bZX)
                s2 = (-1) ** (pX * (pY + pZ))

                bXY = br(sc, parity, basis_idx, X, Y)
                t3 = br_poly(sc, parity, basis_idx, Z, bXY)
                s3 = (-1) ** (pZ * (pX + pY))

                residual = defaultdict(Fraction, t1)
                for w, c in t2.items():
                    residual[w] += Fraction(s2) * c
                for w, c in t3.items():
                    residual[w] += Fraction(s3) * c
                nonzero = {k: v for k, v in residual.items() if v != 0}
                if nonzero:
                    failures.append((X, Y, Z, nonzero))
    return failures


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def verify(path):
    print(f"\n{'=' * 64}")
    print(f"Verifying: {path}")
    parity, basis, basis_idx, sc = load_schema(path)
    n_basis = len(basis)
    n_odd = sum(1 for b in basis if parity[b] == 1)
    n_even = n_basis - n_odd
    n_pairs = len(sc)
    n_sc_entries = sum(len(v) for v in sc.values())
    n_triples = n_basis * (n_basis - 1) * (n_basis - 2) // 6

    print(f"  Basis: {n_basis} ({n_odd} odd + {n_even} even)")
    print(f"  Structure constant pairs: {n_pairs}  entries: {n_sc_entries}")
    print(f"  Triples to check: {n_triples}")

    # Anti-symmetry
    print("  [1] Anti-symmetry ...", end=" ", flush=True)
    asym_fails = check_antisymmetry(sc, parity, basis_idx)
    if asym_fails:
        print(f"FAIL ({len(asym_fails)} failure(s))")
        for X, Y, res in asym_fails[:3]:
            print(f"      [{X}, {Y}]: residual = {res}")
    else:
        print(f"PASS ({n_pairs} pairs checked)")

    # Jacobi
    print("  [2] Super Jacobi     ...", end=" ", flush=True)
    jac_fails = check_jacobi(sc, parity, basis, basis_idx)
    if jac_fails:
        print(f"FAIL ({len(jac_fails)} failure(s))")
        for X, Y, Z, res in jac_fails[:3]:
            print(f"      [{X}, {Y}, {Z}]: residual = {res}")
    else:
        print(f"PASS ({n_triples} triples checked)")

    return len(asym_fails) == 0 and len(jac_fails) == 0


def main():
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data")
    results = {}
    for n in [1, 2, 3]:
        path = data_dir / f"C_{n}_structure.json"
        results[n] = verify(path)

    print(f"\n{'=' * 64}")
    print("SUMMARY")
    all_pass = True
    for n, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  C({n+1}) = osp(2|{2*n})  [n={n}]:  {status}")
        if not ok:
            all_pass = False
    print(f"\nOverall: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
