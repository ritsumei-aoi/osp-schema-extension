"""
verify_C_structure.py: Verifies graded anti-symmetry and the Super Jacobi identity
for C(n+1) structure constants JSON files.
"""

from fractions import Fraction
import json
import os
import sys
from typing import Dict, Tuple, List, Any


def load_structure(json_path: str) -> Tuple[List[str], Dict[str, int], Dict[Tuple[str, str], Dict[str, Fraction]]]:
    """Loads basis, parity, and structure constants table from JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    basis = data["basis"]["odd"] + data["basis"]["even"]
    parity = data["parity"]

    # Table of brackets: (X, Y) -> {Z: coeff}
    brackets: Dict[Tuple[str, str], Dict[str, Fraction]] = {}
    for item in data["structure_constants"]:
        x, y, z = item["X"], item["Y"], item["Z"]
        c = Fraction(item["coeff"])
        if (x, y) not in brackets:
            brackets[(x, y)] = {}
        brackets[(x, y)][z] = c

    return basis, parity, brackets


def bracket_eval(brackets: Dict[Tuple[str, str], Dict[str, Fraction]],
                 v1: Dict[str, Fraction],
                 v2: Dict[str, Fraction]) -> Dict[str, Fraction]:
    """Evaluates bracket between two general elements in the superalgebra."""
    res: Dict[str, Fraction] = {}
    for g1, c1 in v1.items():
        if c1 == 0:
            continue
        for g2, c2 in v2.items():
            if c2 == 0:
                continue
            pair_br = brackets.get((g1, g2), {})
            for z, c_z in pair_br.items():
                tot = c1 * c2 * c_z
                res[z] = res.get(z, Fraction(0)) + tot
    return {k: v for k, v in res.items() if v != 0}


def verify_antisymmetry(basis: List[str], parity: Dict[str, int],
                        brackets: Dict[Tuple[str, str], Dict[str, Fraction]]) -> Tuple[int, List[str]]:
    """Checks [Y, X] = -(-1)^{p(X)p(Y)} [X, Y] for all generator pairs."""
    errors = []
    checked = 0
    for x in basis:
        px = parity[x]
        for y in basis:
            py = parity[y]
            sign = -1 if (px == 1 and py == 1) else 1
            # [Y, X] must equal -sign * [X, Y]
            xy_br = brackets.get((x, y), {})
            yx_br = brackets.get((y, x), {})
            all_z = set(xy_br.keys()).union(set(yx_br.keys()))
            for z in all_z:
                c_xy = xy_br.get(z, Fraction(0))
                c_yx = yx_br.get(z, Fraction(0))
                if c_yx != -sign * c_xy:
                    errors.append(f"Antisymmetry violation for ({x}, {y}) -> {z}: [X,Y]={c_xy}, [Y,X]={c_yx}")
            checked += 1
    return checked, errors


def verify_super_jacobi(basis: List[str], parity: Dict[str, int],
                        brackets: Dict[Tuple[str, str], Dict[str, Fraction]]) -> Tuple[int, List[str]]:
    """
    Checks the Super Jacobi identity for all triples (X, Y, Z):
    (-1)^{p(X)p(Z)} [X, [Y, Z]] + (-1)^{p(Y)p(X)} [Y, [Z, X]] + (-1)^{p(Z)p(Y)} [Z, [X, Y]] = 0
    """
    errors = []
    checked = 0
    for x in basis:
        px = parity[x]
        for y in basis:
            py = parity[y]
            for z in basis:
                pz = parity[z]
                checked += 1

                # Term 1: (-1)^{px * pz} [X, [Y, Z]]
                s1 = -1 if (px == 1 and pz == 1) else 1
                br_yz = brackets.get((y, z), {})
                term1 = bracket_eval(brackets, {x: Fraction(s1)}, br_yz)

                # Term 2: (-1)^{py * px} [Y, [Z, X]]
                s2 = -1 if (py == 1 and px == 1) else 1
                br_zx = brackets.get((z, x), {})
                term2 = bracket_eval(brackets, {y: Fraction(s2)}, br_zx)

                # Term 3: (-1)^{pz * py} [Z, [X, Y]]
                s3 = -1 if (pz == 1 and py == 1) else 1
                br_xy = brackets.get((x, y), {})
                term3 = bracket_eval(brackets, {z: Fraction(s3)}, br_xy)

                # Sum terms
                total: Dict[str, Fraction] = {}
                for term in (term1, term2, term3):
                    for gen, coeff in term.items():
                        total[gen] = total.get(gen, Fraction(0)) + coeff
                total = {k: v for k, v in total.items() if v != 0}

                if total:
                    errors.append(f"Super Jacobi failed for ({x}, {y}, {z}): residual = {total}")

    return checked, errors


def run_verification(data_dir: str = "data") -> Dict[str, Any]:
    summary = {}
    for n in [1, 2, 3]:
        filename = f"C_{n}_structure.json"
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            summary[f"C({n+1})"] = {"status": "FILE_NOT_FOUND", "path": filepath}
            continue

        basis, parity, brackets = load_structure(filepath)
        n_gens = len(basis)
        pairs_checked, asym_errors = verify_antisymmetry(basis, parity, brackets)
        triples_checked, jacobi_errors = verify_super_jacobi(basis, parity, brackets)

        status = "PASS" if (len(asym_errors) == 0 and len(jacobi_errors) == 0) else "FAIL"
        summary[f"C({n+1})"] = {
            "n": n,
            "generators_count": n_gens,
            "pairs_checked": pairs_checked,
            "antisymmetry_errors": len(asym_errors),
            "triples_checked": triples_checked,
            "jacobi_errors": len(jacobi_errors),
            "status": status,
            "asym_error_samples": asym_errors[:5],
            "jacobi_error_samples": jacobi_errors[:5]
        }
    return summary


if __name__ == "__main__":
    results = run_verification()
    print(json.dumps(results, indent=2))
    all_passed = all(r.get("status") == "PASS" for r in results.values())
    sys.exit(0 if all_passed else 1)
