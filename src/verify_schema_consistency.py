#!/usr/bin/env python3
"""
Verify consistency between Schema 1 and Schema 2.

Schema 2 should extend Schema 1 with gamma structure while preserving
all fields from Schema 1.
"""

import json
import sys
from typing import Tuple, List


def verify_schema_consistency(schema1_file: str, schema2_file: str) -> Tuple[bool, List[str]]:
    """Verify that Schema 2 is a consistent extension of Schema 1."""
    issues = []

    with open(schema1_file, 'r') as f:
        schema1 = json.load(f)

    with open(schema2_file, 'r') as f:
        schema2 = json.load(f)

    # Check that all Schema 1 fields are present in Schema 2
    required_fields = [
        'schema_version', 'algebra', 'oscillator_generators',
        'oscillator_relations', 'central_elements', 'basis',
        'parity', 'generator_realization', 'structure_constants', 'metadata'
    ]

    for field in required_fields:
        if field not in schema2:
            issues.append(f"Missing field in Schema 2: {field}")

    # Check that the new gamma_structure field is present
    if 'gamma_structure' not in schema2:
        issues.append("Missing new field: gamma_structure")
    else:
        gamma = schema2['gamma_structure']
        if 'deformation_parameters' not in gamma:
            issues.append("Missing field in gamma_structure: deformation_parameters")
        if 'gb_matrix_size' not in gamma:
            issues.append("Missing field in gamma_structure: gb_matrix_size")

    # Check algebra consistency
    if schema1['algebra'] != schema2['algebra']:
        issues.append("Algebra field differs between Schema 1 and Schema 2")

    # Check that parity is preserved
    if schema1['parity'] != schema2['parity']:
        issues.append("Parity field differs between Schema 1 and Schema 2")

    # Check that basis is preserved
    if schema1['basis'] != schema2['basis']:
        issues.append("Basis field differs between Schema 1 and Schema 2")

    return len(issues) == 0, issues


def verify_all(data_dir: str = 'data'):
    """Verify consistency for all three cases."""
    results = {}

    for n in [1, 2, 3]:
        schema1_file = f'{data_dir}/C_{n}_structure.json'
        schema2_file = f'{data_dir}/C_{n}_gamma.json'

        print(f"\nVerifying Schema 1 -> Schema 2 consistency for C({n+1})")
        print(f"{'='*70}")

        passed, issues = verify_schema_consistency(schema1_file, schema2_file)
        results[n] = passed

        if passed:
            print("✓ PASS: Schema 2 is a consistent extension of Schema 1")
        else:
            print(f"✗ FAIL: {len(issues)} consistency issues found:")
            for issue in issues:
                print(f"  - {issue}")

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
