#!/usr/bin/env python3
"""
Schema Consistency Checker

Verifies that Schema 2 is consistent with Schema 1 and properly extends it.
"""

import json
from pathlib import Path
from typing import Tuple, List


def check_schema_consistency(n: int) -> Tuple[bool, List[str]]:
    """Check consistency between Schema 1 and Schema 2 for C(n+1)."""
    schema1_file = f"data/C_{n}_structure.json"
    schema2_file = f"data/C_{n}_gamma.json"

    errors = []

    # Check files exist
    if not Path(schema1_file).exists():
        errors.append(f"Schema 1 file not found: {schema1_file}")
        return False, errors
    if not Path(schema2_file).exists():
        errors.append(f"Schema 2 file not found: {schema2_file}")
        return False, errors

    # Load schemas
    with open(schema1_file) as f:
        schema1 = json.load(f)
    with open(schema2_file) as f:
        schema2 = json.load(f)

    # Check algebra field consistency
    if schema1['algebra'] != schema2['algebra']:
        errors.append("Algebra field differs between Schema 1 and Schema 2")

    # Check schema version
    if schema1['schema_version'] != schema2['schema_version']:
        errors.append(f"Schema version mismatch: {schema1['schema_version']} vs {schema2['schema_version']}")

    if schema2['schema_version'] != "5.0":
        errors.append(f"Schema 2 version should be 5.0, got {schema2['schema_version']}")

    # Check algebra.n consistency with gb_matrix
    algebra_n = schema2['algebra']['n']
    gb_size = schema2['inhomogeneous_deformation']['gb_matrix']['size']
    expected_gb_size = 4 * algebra_n

    if gb_size != expected_gb_size:
        errors.append(f"gb_matrix size inconsistent: {gb_size} != 4*{algebra_n} = {expected_gb_size}")

    # Check gb_parameters count
    gb_params = schema2['inhomogeneous_deformation'].get('gb_parameters', [])
    if len(gb_params) != gb_size:
        errors.append(f"gb_parameters count ({len(gb_params)}) != gb_matrix size ({gb_size})")

    # Check that all gb_parameters have parity 1
    for param in gb_params:
        if param.get('parity') != 1:
            errors.append(f"gb_parameter {param.get('label')} has parity {param.get('parity')}, expected 1")

    # Check consistency key exists
    if 'consistency' not in schema2:
        errors.append("Schema 2 missing 'consistency' key")
    else:
        consistency = schema2['consistency']
        basis_size = len(schema1['basis']['even']) + len(schema1['basis']['odd'])
        reported_size = consistency.get('schema1_elements')
        if reported_size != basis_size:
            errors.append(f"Consistency element count ({reported_size}) != actual ({basis_size})")

    return len(errors) == 0, errors


def main():
    """Check consistency for all C(n+1) algebras."""
    all_passed = True

    for n in [1, 2, 3]:
        print(f"\nConsistency Check for C({n+1}) (n={n})")
        print("=" * 70)

        passed, errors = check_schema_consistency(n)

        if passed:
            print("✓ PASSED: Schema 1 and Schema 2 are consistent")
        else:
            print(f"✗ FAILED: {len(errors)} inconsistencies found")
            for error in errors:
                print(f"  - {error}")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("Overall: All consistency checks PASSED ✓")
    else:
        print("Overall: Some checks FAILED ✗")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
