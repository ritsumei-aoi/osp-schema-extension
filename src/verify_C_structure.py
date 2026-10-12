"""
Verification script for C(n+1) Schema 1 structure constants.
Validates graded anti-symmetry and Super Jacobi identities for C_n_structure.json (n=1, 2, 3).
"""

from fractions import Fraction
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Tuple


def load_schema(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_algebra(file_path: Path) -> Dict[str, Any]:
    data = load_schema(file_path)
    alg = data["algebra"]
    n = alg["n"]
    cartan_type = alg["cartan_type"]
    basis_odd = data["basis"]["odd"]
    basis_even = data["basis"]["even"]
    full_basis = basis_odd + basis_even
    dim = len(full_basis)
    parities = data["parity"]

    # Verify basis size
    expected_dim = alg["dimension"]["total"]
    assert dim == expected_dim, f"Basis length {dim} != expected {expected_dim}"

    # Load structure constants into dict
    sc_list = data["structure_constants"]
    sc_dict: Dict[Tuple[str, str, str], Fraction] = {}
    for entry in sc_list:
        sc_dict[(entry["X"], entry["Y"], entry["Z"])] = Fraction(entry["coeff"])

    # 1. Graded Anti-symmetry Check
    # [Y, X} = - (-1)^{p(X) p(Y)} [X, Y}
    anti_failures = []
    pairs_checked = 0
    for x in full_basis:
        for y in full_basis:
            pairs_checked += 1
            px, py = parities[x], parities[y]
            factor = - (-1)**(px * py)
            for z in full_basis:
                c_xy = sc_dict.get((x, y, z), Fraction(0))
                c_yx = sc_dict.get((y, x, z), Fraction(0))
                if c_yx != factor * c_xy:
                    anti_failures.append({
                        "X": x, "Y": y, "Z": z,
                        "c_xy": str(c_xy), "c_yx": str(c_yx),
                        "expected_c_yx": str(factor * c_xy)
                    })

    # 2. Super Jacobi Identity Check
    # (-1)^{p(X) p(Z)} [X, [Y, Z}} + (-1)^{p(Y) p(X)} [Y, [Z, X}} + (-1)^{p(Z) p(Y)} [Z, [X, Y}} = 0
    # For each triple (X, Y, Z) and for each basis component W:
    # J(X, Y, Z; W) = 0
    jacobi_failures = []
    triples_checked = 0
    t0 = time.time()

    for i in range(dim):
        x = full_basis[i]
        px = parities[x]
        for j in range(dim):
            y = full_basis[j]
            py = parities[y]
            for k in range(dim):
                z = full_basis[k]
                pz = parities[z]
                triples_checked += 1

                s_x = (-1)**(px * pz)
                s_y = (-1)**(py * px)
                s_z = (-1)**(pz * py)

                for l in range(dim):
                    w = full_basis[l]
                    val = Fraction(0)
                    for m in range(dim):
                        u = full_basis[m]
                        # Term 1: s_x * [X, [Y, Z]] -> sum_u c(Y, Z, u) * c(X, u, W)
                        c_yz = sc_dict.get((y, z, u), Fraction(0))
                        if c_yz != 0:
                            c_xu = sc_dict.get((x, u, w), Fraction(0))
                            if c_xu != 0:
                                val += s_x * c_yz * c_xu

                        # Term 2: s_y * [Y, [Z, X]] -> sum_u c(Z, X, u) * c(Y, u, W)
                        c_zx = sc_dict.get((z, x, u), Fraction(0))
                        if c_zx != 0:
                            c_yu = sc_dict.get((y, u, w), Fraction(0))
                            if c_yu != 0:
                                val += s_y * c_zx * c_yu

                        # Term 3: s_z * [Z, [X, Y]] -> sum_u c(X, Y, u) * c(Z, u, W)
                        c_xy = sc_dict.get((x, y, u), Fraction(0))
                        if c_xy != 0:
                            c_zu = sc_dict.get((z, u, w), Fraction(0))
                            if c_zu != 0:
                                val += s_z * c_xy * c_zu

                    if val != 0:
                        jacobi_failures.append({
                            "X": x, "Y": y, "Z": z, "W": w,
                            "residual": str(val)
                        })

    elapsed = time.time() - t0

    result = {
        "n": n,
        "cartan_type": cartan_type,
        "dimension": dim,
        "even_dim": len(basis_even),
        "odd_dim": len(basis_odd),
        "total_brackets": len(sc_list),
        "pairs_checked": pairs_checked,
        "anti_failures": len(anti_failures),
        "triples_checked": triples_checked,
        "jacobi_failures": len(jacobi_failures),
        "elapsed_seconds": round(elapsed, 3),
        "passed": (len(anti_failures) == 0 and len(jacobi_failures) == 0),
        "anti_failure_details": anti_failures[:5],
        "jacobi_failure_details": jacobi_failures[:5],
    }
    return result


def run_full_verification(data_dir: Path) -> bool:
    print("=" * 70)
    print("MATHEMATICAL VERIFICATION OF C(n+1) STRUCTURE CONSTANTS")
    print("=" * 70)

    all_passed = True
    for n in [1, 2, 3]:
        file_path = data_dir / f"C_{n}_structure.json"
        print(f"\nVerifying {file_path.name} (Cartan C({n+1}))...")
        res = verify_algebra(file_path)
        print(f"  Dimension: {res['dimension']} ({res['even_dim']} even | {res['odd_dim']} odd)")
        print(f"  Non-zero structure constants: {res['total_brackets']}")
        print(f"  Graded anti-symmetry: {res['pairs_checked']} pairs checked -> {res['anti_failures']} failures")
        print(f"  Super Jacobi identity: {res['triples_checked']} triples checked -> {res['jacobi_failures']} failures ({res['elapsed_seconds']}s)")
        print(f"  Result: {'PASS' if res['passed'] else 'FAIL'}")
        if not res['passed']:
            all_passed = False

    print("\n" + "=" * 70)
    print(f"OVERALL VERIFICATION STATUS: {'ALL PASSED' if all_passed else 'FAILURES DETECTED'}")
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"
    success = run_full_verification(data_dir)
    sys.exit(0 if success else 1)
