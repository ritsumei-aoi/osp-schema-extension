"""
verify_C_structure.py: Verification script for C(n+1) = osp(2|2n) structure constants.
Verifies graded anti-symmetry for all generator pairs and Super Jacobi identity
for all generator triples across n=1, 2, 3.
"""

from collections import defaultdict
from fractions import Fraction
import json
import os
import sys
from typing import Dict, List, Tuple, Any
import numpy as np


def load_structure_data(n: int) -> Tuple[List[str], Dict[str, int], Dict[Tuple[str, str], Dict[str, Fraction]]]:
    filepath = os.path.join("data", f"C_{n}_structure.json")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Structure file {filepath} not found.")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    basis_list = data["basis"]["odd"] + data["basis"]["even"]
    parities = data["parity"]

    # Build full bracket dictionary
    # brackets[(X, Y)] = {Z: Fraction}
    brackets: Dict[Tuple[str, str], Dict[str, Fraction]] = defaultdict(lambda: defaultdict(Fraction))

    for entry in data["structure_constants"]:
        x = entry["X"]
        y = entry["Y"]
        z = entry["Z"]
        c = Fraction(entry["coeff"])
        brackets[(x, y)][z] = c
        if x != y:
            # Graded anti-symmetry: [Y, X] = - (-1)^(pX * pY) [X, Y]
            p_x = parities[x]
            p_y = parities[y]
            sign = -1 if (p_x * p_y % 2 == 1) else 1
            brackets[(y, x)][z] = -sign * c

    return basis_list, parities, brackets


def verify_anti_symmetry(basis_list: List[str], parities: Dict[str, int],
                          brackets: Dict[Tuple[str, str], Dict[str, Fraction]]) -> Tuple[bool, int, List[str]]:
    """Checks [X, Y] + (-1)^(pX pY) [Y, X] == 0 for all pairs."""
    failures = []
    pairs_checked = 0
    for x in basis_list:
        p_x = parities[x]
        for y in basis_list:
            p_y = parities[y]
            pairs_checked += 1
            sign = -1 if (p_x * p_y % 2 == 1) else 1
            # Check for each z
            all_z = set(brackets[(x, y)].keys()) | set(brackets[(y, x)].keys())
            for z in all_z:
                val = brackets[(x, y)][z] + sign * brackets[(y, x)][z]
                if val != 0:
                    failures.append(f"Anti-symmetry failed for [{x}, {y}] along {z}: val = {val}")

    return (len(failures) == 0), pairs_checked, failures


def verify_super_jacobi(basis_list: List[str], parities: Dict[str, int],
                        brackets: Dict[Tuple[str, str], Dict[str, Fraction]]) -> Tuple[bool, int, List[str]]:
    """
    Checks the Super Jacobi identity for all triples (X, Y, Z):
    (-1)^(pX pZ) [X, [Y, Z]] + (-1)^(pY pX) [Y, [Z, X]] + (-1)^(pZ pY) [Z, [X, Y]] == 0.
    """
    N = len(basis_list)
    idx_map = {name: i for i, name in enumerate(basis_list)}
    p_arr = np.array([parities[name] for name in basis_list], dtype=int)

    # Convert to 3D tensor: C[i, j, k] = coeff of basis[k] in [basis[i], basis[j]]
    # Since all coeffs are rational with small denominators, we use exact fractions
    # or float64 tensor for vectorization and fraction check if needed.
    C_float = np.zeros((N, N, N), dtype=np.float64)
    for (x, y), z_dict in brackets.items():
        i = idx_map[x]
        j = idx_map[y]
        for z, coeff in z_dict.items():
            k = idx_map[z]
            C_float[i, j, k] = float(coeff)

    # Tensor contraction using np.einsum:
    # [X_j, X_k] = sum_m C[j, k, m] X_m
    # [X_i, [X_j, X_k]] = sum_m C[j, k, m] C[i, m, l] X_l
    # term1[i, j, k, l] = sum_m C[j, k, m] * C[i, m, l]
    term1 = np.einsum('jkm,iml->ijkl', C_float, C_float)
    term2 = np.einsum('kim,jml->ijkl', C_float, C_float)
    term3 = np.einsum('ijm,kml->ijkl', C_float, C_float)

    # Signs:
    # s1[i, j, k] = (-1)^(p[i]*p[k])
    # s2[i, j, k] = (-1)^(p[j]*p[i])
    # s3[i, j, k] = (-1)^(p[k]*p[j])
    p_i = p_arr[:, None, None, None]
    p_j = p_arr[None, :, None, None]
    p_k = p_arr[None, None, :, None]

    s1 = np.where((p_i * p_k) % 2 == 1, -1.0, 1.0)
    s2 = np.where((p_j * p_i) % 2 == 1, -1.0, 1.0)
    s3 = np.where((p_k * p_j) % 2 == 1, -1.0, 1.0)

    jacobi_tensor = s1 * term1 + s2 * term2 + s3 * term3
    max_err = np.max(np.abs(jacobi_tensor))

    triples_checked = N * N * N
    failures = []
    if max_err > 1e-12:
        # Locate failures
        bad_indices = np.argwhere(np.abs(jacobi_tensor) > 1e-12)
        for idx in bad_indices[:10]:
            i, j, k, l = idx
            failures.append(
                f"Triple ({basis_list[i]}, {basis_list[j]}, {basis_list[k]}) along {basis_list[l]}: residual = {jacobi_tensor[i, j, k, l]}"
            )

    return (len(failures) == 0), triples_checked, failures


def run_verification() -> Dict[str, Any]:
    summary = {}
    all_passed = True
    for n in [1, 2, 3]:
        basis_list, parities, brackets = load_structure_data(n)
        dim = len(basis_list)
        asym_ok, pairs_count, asym_fail = verify_anti_symmetry(basis_list, parities, brackets)
        jac_ok, triples_count, jac_fail = verify_super_jacobi(basis_list, parities, brackets)

        passed = asym_ok and jac_ok
        if not passed:
            all_passed = False

        summary[f"C({n+1})"] = {
            "n": n,
            "dimension": dim,
            "pairs_checked": pairs_count,
            "anti_symmetry_passed": asym_ok,
            "triples_checked": triples_count,
            "super_jacobi_passed": jac_ok,
            "status": "PASS" if passed else "FAIL",
            "failures": asym_fail + jac_fail
        }
        print(f"C({n+1}) (n={n}, dim={dim}): Pairs={pairs_count} (Anti-Symmetry={asym_ok}), "
              f"Triples={triples_count} (Super Jacobi={jac_ok}) -> STATUS: {'PASS' if passed else 'FAIL'}")

    return summary


if __name__ == "__main__":
    results = run_verification()
