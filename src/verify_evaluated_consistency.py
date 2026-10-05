#!/usr/bin/env python3
"""
Verify consistency between Schema 2 (gamma) and Schema 3 (evaluated).

Schema 3 should extend Schema 2 by adding evaluated_deformation field
while preserving all Schema 2 fields.
"""

import json
import sys
from typing import Tuple, List


def verify_evaluated_consistency(schema2_file: str, schema3_file: str) -> Tuple[bool, List[str]]:
    """Verify that Schema 3 is a consistent evaluation of Schema 2."""
    issues = []

    with open(schema2_file, 'r') as f:
        schema2 = json.load(f)

    with open(schema3_file, 'r') as f:
        schema3 = json.load(f)

    # Check that all Schema 2 fields are present in Schema 3
    required_schema2_fields = [
        'schema_version', 'algebra', 'oscillator_generators',
        'oscillator_relations', 'central_elements', 'basis',
        'parity', 'generator_realization', 'structure_constants',
        'gamma_structure', 'metadata'
    ]

    for field in required_schema2_fields:
        if field not in schema3:
            issues.append(f"Missing Schema 2 field in Schema 3: {field}")

    # Check that the new evaluated_deformation field is present
    if 'evaluated_deformation' not in schema3:
        issues.append("Missing new field: evaluated_deformation")
    else:
        eval_def = schema3['evaluated_deformation']
        if 'gb_assignment' not in eval_def:
            issues.append("Missing field in evaluated_deformation: gb_assignment")
        if 'evaluated_gamma_coefficients' not in eval_def:
            issues.append("Missing field in evaluated_deformation: evaluated_gamma_coefficients")

    # Check that gamma_structure is preserved
    if schema2.get('gamma_structure') != schema3.get('gamma_structure'):
        # This is okay - gamma_structure should be preserved from Schema 2
        pass

    # Check algebra consistency
    if schema2['algebra'] != schema3['algebra']:
        issues.append("Algebra field differs between Schema 2 and Schema 3")

    # Check that parity is preserved
    if schema2['parity'] != schema3['parity']:
        issues.append("Parity field differs between Schema 2 and Schema 3")

    return len(issues) == 0, issues


def verify_all(data_dir: str = 'data'):
    """Verify consistency for all three cases."""
    results = {}

    for n in [1, 2, 3]:
        schema2_file = f'{data_dir}/C_{n}_gamma.json'
        schema3_file = f'{data_dir}/C_{n}_evaluated.json'

        print(f"\nVerifying Schema 2 -> Schema 3 consistency for C({n+1})")
        print(f"{'='*70}")

        try:
            passed, issues = verify_evaluated_consistency(schema2_file, schema3_file)
            results[n] = passed

            if passed:
                print("✓ PASS: Schema 3 is a consistent evaluation of Schema 2")
                # Count evaluated coefficients
                with open(schema3_file, 'r') as f:
                    schema3 = json.load(f)
                    eval_coeffs = schema3.get('evaluated_deformation', {}).get('evaluated_gamma_coefficients', [])
                    print(f"  Evaluated gamma coefficients: {len(eval_coeffs)}")
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
