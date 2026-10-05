#!/usr/bin/env python3
"""
Verify consistency of Schema 4 (coboundary) with Schema 1 (basis).

Schema 4 should be consistent with the basis and parity from Layer 1.
"""

import json
import sys
from typing import Tuple, List


def verify_coboundary_consistency(schema1_file: str, schema4_file: str) -> Tuple[bool, List[str]]:
    """Verify that Schema 4 coboundary is consistent with Schema 1 basis."""
    issues = []

    with open(schema1_file, 'r') as f:
        schema1 = json.load(f)

    with open(schema4_file, 'r') as f:
        schema4 = json.load(f)

    # Check that basis is unchanged
    if schema1['basis'] != schema4['basis']:
        issues.append("Basis field differs between Schema 1 and Schema 4")

    # Check that parity is unchanged
    if schema1['parity'] != schema4['parity']:
        issues.append("Parity field differs between Schema 1 and Schema 4")

    # Check that coboundary_structure field is present
    if 'coboundary_structure' not in schema4:
        issues.append("Missing field: coboundary_structure")
    else:
        cobndry = schema4['coboundary_structure']
        if 'odd_linear_map' not in cobndry:
            issues.append("Missing field in coboundary_structure: odd_linear_map")
        if 'coboundary_operator' not in cobndry:
            issues.append("Missing field in coboundary_structure: coboundary_operator")
        if 'triviality_condition' not in cobndry:
            issues.append("Missing field in coboundary_structure: triviality_condition")

    # Check parity reversal property of f
    if 'coboundary_structure' in schema4 and 'odd_linear_map' in schema4['coboundary_structure']:
        f_map = schema4['coboundary_structure']['odd_linear_map'].get('map_entries', {})
        parity = schema4['parity']

        for X, targets in f_map.items():
            p_X = parity.get(X, -1)
            for Y in targets.keys():
                p_Y = parity.get(Y, -1)

                # f should reverse parity: p(f(X)) != p(X)
                if p_X != -1 and p_Y != -1:
                    if p_X == p_Y:
                        issues.append(f"f({X}) -> {Y}: parity not reversed (both {p_X})")

    # Check that coboundary coefficients reference valid generators
    if 'coboundary_structure' in schema4 and 'coboundary_operator' in schema4['coboundary_structure']:
        coeff_sample = schema4['coboundary_structure']['coboundary_operator'].get('coefficients', [])
        all_gens = set(schema4['basis']['even'] + schema4['basis']['odd'])

        for coeff in coeff_sample:
            if coeff.get('X') not in all_gens:
                issues.append(f"Coefficient references unknown generator: {coeff.get('X')}")
            if coeff.get('Y') not in all_gens:
                issues.append(f"Coefficient references unknown generator: {coeff.get('Y')}")

    return len(issues) == 0, issues


def verify_all(data_dir: str = 'data'):
    """Verify consistency for all three cases."""
    results = {}

    for n in [1, 2, 3]:
        schema1_file = f'{data_dir}/C_{n}_structure.json'
        schema4_file = f'{data_dir}/C_{n}_coboundary.json'

        print(f"\nVerifying Schema 4 consistency with Schema 1 basis for C({n+1})")
        print(f"{'='*70}")

        try:
            passed, issues = verify_coboundary_consistency(schema1_file, schema4_file)
            results[n] = passed

            if passed:
                print("✓ PASS: Schema 4 is consistent with Schema 1 basis")
                # Count coboundary structure
                with open(schema4_file, 'r') as f:
                    schema4 = json.load(f)
                    cobndry = schema4.get('coboundary_structure', {})
                    f_entries = len(cobndry.get('odd_linear_map', {}).get('map_entries', {}))
                    coeff_count = cobndry.get('coboundary_operator', {}).get('total_coefficients', 0)
                    print(f"  Odd linear map f entries: {f_entries}")
                    print(f"  Coboundary coefficients: {coeff_count}")
            else:
                print(f"✗ FAIL: {len(issues)} consistency issues found:")
                for issue in issues:
                    print(f"  - {issue}")
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results[n] = False

    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    for n, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"C({n+1}): {status}")

    return all(results.values())


if __name__ == '__main__':
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    success = verify_all(data_dir)
    sys.exit(0 if success else 1)
