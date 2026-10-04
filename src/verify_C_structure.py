"""
verify_C_structure.py: Verifies graded anti-symmetry and Super Jacobi identity
for C(n+1) structure constants loaded from Schema 1 JSON files (n=1, 2, 3).
"""

import json
import os
from fractions import Fraction
from collections import defaultdict


def load_structure_data(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def build_bracket_map(data):
    bracket_map = defaultdict(lambda: defaultdict(Fraction))
    for entry in data["structure_constants"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        coeff = Fraction(entry["coeff"])
        bracket_map[(X, Y)][Z] = coeff
    return bracket_map


def compute_bracket(bracket_map, X_dict, Y_dict, parity):
    """Compute [X_dict, Y_dict} where X_dict and Y_dict are linear combinations of generators."""
    result = defaultdict(Fraction)
    for X, cx in X_dict.items():
        if cx == 0:
            continue
        pX = parity[X]
        for Y, cy in Y_dict.items():
            if cy == 0:
                continue
            pair_brackets = bracket_map.get((X, Y), {})
            for Z, cz in pair_brackets.items():
                result[Z] += cx * cy * cz
                if result[Z] == 0:
                    del result[Z]
    return result


def verify_antisymmetry(data):
    """Check [Y, X} = -(-1)^{p(X)p(Y)} [X, Y} for all generator pairs."""
    basis = data["basis"]["even"] + data["basis"]["odd"]
    parity = data["parity"]
    bracket_map = build_bracket_map(data)

    failures = []
    checked = 0
    for X in basis:
        pX = parity[X]
        for Y in basis:
            pY = parity[Y]
            pXY = (-1) ** (pX * pY)
            checked += 1

            xy_dict = bracket_map.get((X, Y), {})
            yx_dict = bracket_map.get((Y, X), {})

            all_targets = set(xy_dict.keys()) | set(yx_dict.keys())
            for Z in all_targets:
                c_xy = xy_dict.get(Z, Fraction(0))
                c_yx = yx_dict.get(Z, Fraction(0))
                expected_yx = - pXY * c_xy
                if c_yx != expected_yx:
                    failures.append((X, Y, Z, c_xy, c_yx, expected_yx))

    return checked, failures


def verify_super_jacobi(data):
    """
    Check Super Jacobi identity for all triples:
    (-1)^{p(X)p(Z)} [X, [Y, Z}} + (-1)^{p(Y)p(X)} [Y, [Z, X}} + (-1)^{p(Z)p(Y)} [Z, [X, Y}} = 0
    """
    basis = data["basis"]["even"] + data["basis"]["odd"]
    parity = data["parity"]
    bracket_map = build_bracket_map(data)

    failures = []
    checked = 0

    for X in basis:
        pX = parity[X]
        for Y in basis:
            pY = parity[Y]
            for Z in basis:
                pZ = parity[Z]
                checked += 1

                # Term 1: (-1)^{pX pZ} [X, [Y, Z}}
                yz_bracket = bracket_map.get((Y, Z), {})
                term1 = compute_bracket(bracket_map, {X: Fraction(1)}, yz_bracket, parity)
                sign1 = (-1) ** (pX * pZ)

                # Term 2: (-1)^{pY pX} [Y, [Z, X}}
                zx_bracket = bracket_map.get((Z, X), {})
                term2 = compute_bracket(bracket_map, {Y: Fraction(1)}, zx_bracket, parity)
                sign2 = (-1) ** (pY * pX)

                # Term 3: (-1)^{pZ pY} [Z, [X, Y}}
                xy_bracket = bracket_map.get((X, Y), {})
                term3 = compute_bracket(bracket_map, {Z: Fraction(1)}, xy_bracket, parity)
                sign3 = (-1) ** (pZ * pY)

                # Combine all three terms
                all_basis_keys = set(term1.keys()) | set(term2.keys()) | set(term3.keys())
                jacobi_sum = {}
                for W in all_basis_keys:
                    val = sign1 * term1.get(W, Fraction(0)) + sign2 * term2.get(W, Fraction(0)) + sign3 * term3.get(W, Fraction(0))
                    if val != 0:
                        jacobi_sum[W] = val

                if jacobi_sum:
                    failures.append((X, Y, Z, jacobi_sum))

    return checked, failures


def run_verification(data_dir="data"):
    results = {}
    for n in [1, 2, 3]:
        filepath = os.path.join(data_dir, f"C_{n}_structure.json")
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
        data = load_structure_data(filepath)
        n_pairs, asym_fails = verify_antisymmetry(data)
        n_triples, jacobi_fails = verify_super_jacobi(data)
        results[n] = {
            "n": n,
            "cartan_type": data["algebra"]["cartan_type"],
            "dim_total": data["algebra"]["dimension"]["total"],
            "pairs_checked": n_pairs,
            "antisymmetry_failures": len(asym_fails),
            "triples_checked": n_triples,
            "super_jacobi_failures": len(jacobi_fails),
            "status": "PASS" if len(asym_fails) == 0 and len(jacobi_fails) == 0 else "FAIL"
        }
        print(f"C({n+1}) [n={n}]: Checked {n_pairs} pairs (fails={len(asym_fails)}), {n_triples} triples (fails={len(jacobi_fails)}) -> {results[n]['status']}")
    return results


if __name__ == "__main__":
    run_verification()
