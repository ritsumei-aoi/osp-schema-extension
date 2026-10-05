"""
C(n+1) = osp(2|2n) triviality analysis.

Determines whether the inhomogeneous deformation gamma is a coboundary (delta f)
by solving the linear system gamma = delta f for the phi parameters.
"""

import json
import sys
from fractions import Fraction
import numpy as np


def load_gamma_symbolic(n):
    """Load symbolic gamma and return structured data."""
    with open(f'data/C_{n}_gamma.json') as f:
        data = json.load(f)
    return data


def load_coboundary(n):
    with open(f'data/C_{n}_coboundary.json') as f:
        return json.load(f)


def load_structure(n):
    with open(f'data/C_{n}_structure.json') as f:
        return json.load(f)


def analyze_triviality(n):
    """
    Analyze the triviality condition for C(n+1).

    The equation gamma = delta f means:
    For each (X, Y, Z): gamma(X,Y)^Z = (delta f)(X,Y)^Z

    gamma(X,Y)^Z = sum_alpha coeff_{XYZ,alpha} * gb_alpha  (from Schema 2)
    (delta f)(X,Y)^Z = sum_{s,t} M_{XYZ,s,t} * phi_{s,t}  (from Schema 4)

    So: sum_alpha coeff_{XYZ,alpha} * gb_alpha = sum_{s,t} M_{XYZ,s,t} * phi_{s,t}

    This is a linear system in phi for given gb values.
    """
    print(f"\n{'='*70}")
    print(f"Triviality Analysis for C({n+1}) = osp(2|{2*n})")
    print(f"{'='*70}")

    gamma_data = load_gamma_symbolic(n)
    cob_data = load_coboundary(n)
    struct_data = load_structure(n)

    basis = struct_data['basis']['odd'] + struct_data['basis']['even']
    parity = struct_data['parity']
    gb_labels = [p['label'] for p in gamma_data['gb_matrix']['parameters']]

    phi_labels = []
    for target in basis:
        for source in basis:
            if parity[source] != parity[target]:
                phi_labels.append((source, target))
    phi_index = {label: i for i, label in enumerate(phi_labels)}
    n_phi = len(phi_labels)

    xyz_set = set()
    for entry in gamma_data['gamma_coefficients']:
        xyz_set.add((entry['X'], entry['Y'], entry['Z']))
    for entry in cob_data['coboundary_coefficients']:
        xyz_set.add((entry['X'], entry['Y'], entry['Z']))
    xyz_list = sorted(xyz_set)
    xyz_index = {xyz: i for i, xyz in enumerate(xyz_list)}
    n_eq = len(xyz_list)

    print(f"Dimensions: {n_phi} phi params, {n_eq} equations (XYZ triples)")
    print(f"gb parameters: {len(gb_labels)}")

    cob_matrix = np.zeros((n_eq, n_phi), dtype=float)
    for entry in cob_data['coboundary_coefficients']:
        row = xyz_index.get((entry['X'], entry['Y'], entry['Z']))
        if row is None:
            continue
        col = phi_index.get((entry['phi_source'], entry['phi_target']))
        if col is None:
            continue
        cob_matrix[row, col] += float(Fraction(entry['coeff']))

    gamma_symbolic = {}
    for entry in gamma_data['gamma_coefficients']:
        key = (entry['X'], entry['Y'], entry['Z'])
        if key not in gamma_symbolic:
            gamma_symbolic[key] = {}
        gamma_symbolic[key][entry['gb_param']] = Fraction(entry['coeff'])

    cob_rank = np.linalg.matrix_rank(cob_matrix, tol=1e-10)
    print(f"\nCoboundary matrix rank: {cob_rank} (of {n_eq} rows x {n_phi} cols)")
    print(f"Kernel dimension: {n_phi - cob_rank}")

    results = {}

    print(f"\n--- Testing all-plus profile (all gb = +1) ---")
    gb_vals = {label: Fraction(1) for label in gb_labels}
    rhs = np.zeros(n_eq, dtype=float)
    for xyz, coeffs in gamma_symbolic.items():
        row = xyz_index.get(xyz)
        if row is None:
            continue
        val = sum(float(c) * float(gb_vals.get(g, 0)) for g, c in coeffs.items())
        rhs[row] = val

    aug = np.column_stack([cob_matrix, rhs.reshape(-1, 1)])
    aug_rank = np.linalg.matrix_rank(aug, tol=1e-10)

    if aug_rank == cob_rank:
        print(f"  TRIVIAL: System is consistent (rank {cob_rank} = augmented rank {aug_rank})")
        phi_solution, residuals, _, _ = np.linalg.lstsq(cob_matrix, rhs, rcond=None)
        max_residual = np.max(np.abs(cob_matrix @ phi_solution - rhs))
        print(f"  Max residual: {max_residual:.2e}")
        results['all_plus'] = 'trivial'
    else:
        print(f"  NON-TRIVIAL: Inconsistent (rank {cob_rank} vs augmented rank {aug_rank})")
        residual = rhs - cob_matrix @ np.linalg.lstsq(cob_matrix, rhs, rcond=None)[0]
        nonzero_residuals = [(i, r) for i, r in enumerate(residual) if abs(r) > 1e-10]
        print(f"  Inconsistent equations: {len(nonzero_residuals)}")
        if nonzero_residuals:
            print(f"  First 5 inconsistent (X, Y, Z) triples:")
            for idx, res in nonzero_residuals[:5]:
                xyz = xyz_list[idx]
                print(f"    {xyz}: residual = {res:.6f}")
        results['all_plus'] = 'non-trivial'

    print(f"\n--- Testing individual gb parameters ---")
    for gb_label in gb_labels:
        gb_vals_single = {gb_label: Fraction(1)}
        rhs_single = np.zeros(n_eq, dtype=float)
        for xyz, coeffs in gamma_symbolic.items():
            row = xyz_index.get(xyz)
            if row is None:
                continue
            val = float(coeffs.get(gb_label, 0))
            rhs_single[row] = val

        if np.max(np.abs(rhs_single)) < 1e-15:
            results[gb_label] = 'zero_gamma'
            continue

        aug_single = np.column_stack([cob_matrix, rhs_single.reshape(-1, 1)])
        aug_rank_single = np.linalg.matrix_rank(aug_single, tol=1e-10)

        if aug_rank_single == cob_rank:
            print(f"  {gb_label}: TRIVIAL")
            results[gb_label] = 'trivial'
        else:
            print(f"  {gb_label}: NON-TRIVIAL")
            results[gb_label] = 'non-trivial'

    print(f"\n--- Testing general gb (all independent) ---")
    all_trivial_individually = all(
        results.get(gl) in ('trivial', 'zero_gamma') for gl in gb_labels
    )
    if all_trivial_individually:
        print("  All individual gb parameters produce trivial deformations.")
        print("  By linearity, ANY gb assignment produces a trivial deformation.")
        results['general'] = 'always_trivial'
    else:
        nontrivial_params = [gl for gl in gb_labels if results.get(gl) == 'non-trivial']
        print(f"  Non-trivial gb parameters: {nontrivial_params}")

        print("\n  Testing: can a LINEAR COMBINATION be trivial?")
        gamma_matrix = np.zeros((n_eq, len(gb_labels)), dtype=float)
        for xyz, coeffs in gamma_symbolic.items():
            row = xyz_index.get(xyz)
            if row is None:
                continue
            for gi, gl in enumerate(gb_labels):
                gamma_matrix[row, gi] = float(coeffs.get(gl, 0))

        combined = np.column_stack([cob_matrix, -gamma_matrix])
        combined_rank = np.linalg.matrix_rank(combined, tol=1e-10)
        separate_rank = np.linalg.matrix_rank(cob_matrix, tol=1e-10)

        if combined_rank == separate_rank + len(gb_labels):
            print("  The gamma columns are fully independent of the coboundary image.")
            print("  CONJECTURE: The deformation is NON-TRIVIAL for all non-zero gb.")
            results['general'] = 'never_trivial'
        elif combined_rank < separate_rank + len(gb_labels):
            dim_trivial_space = separate_rank + len(gb_labels) - combined_rank
            print(f"  The trivial subspace of gb-space has dimension {dim_trivial_space}.")
            results['general'] = f'trivial_subspace_dim_{dim_trivial_space}'
        else:
            results['general'] = 'undetermined'

    return results


def main():
    all_results = {}
    for n_val in [1, 2, 3]:
        all_results[n_val] = analyze_triviality(n_val)

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for n_val in [1, 2, 3]:
        r = all_results[n_val]
        print(f"\nC({n_val+1}) = osp(2|{2*n_val}):")
        print(f"  All-plus profile: {r.get('all_plus', 'N/A')}")
        print(f"  General: {r.get('general', 'N/A')}")


if __name__ == '__main__':
    main()
