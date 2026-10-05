#!/usr/bin/env python3
"""
Schema 3 Consistency Checker

Verifies that Schema 3 (Evaluated Structure) is consistent with Schemas 1 and 2.
"""

import json
from pathlib import Path
from typing import Tuple, List


def check_schema3_consistency(n: int) -> Tuple[bool, List[str]]:
    """Check consistency between Schemas 1, 2, and 3 for C(n+1)."""
    schema1_file = f"data/C_{n}_structure.json"
    schema2_file = f"data/C_{n}_gamma.json"
    schema3_file = f"data/C_{n}_evaluated_trivial.json"

    errors = []

    # Check files exist
    for fname in [schema1_file, schema2_file, schema3_file]:
        if not Path(fname).exists():
            errors.append(f"File not found: {fname}")

    if errors:
        return False, errors

    # Load schemas
    with open(schema1_file) as f:
        schema1 = json.load(f)
    with open(schema2_file) as f:
        schema2 = json.load(f)
    with open(schema3_file) as f:
        schema3 = json.load(f)

    # Check schema versions
    if schema3['schema_version'] != "5.0":
        errors.append(f"Schema 3 version should be 5.0, got {schema3['schema_version']}")

    # Check algebra field
    if schema1['algebra'] != schema3['algebra']:
        errors.append("Algebra field differs between Schema 1 and 3")
    if schema2['algebra'] != schema3['algebra']:
        errors.append("Algebra field differs between Schema 2 and 3")

    # Check basis alignment
    schema3_even = schema3['basis_and_parity'].get('even_basis', [])
    schema3_odd = schema3['basis_and_parity'].get('odd_basis', [])
    schema1_even = schema1['basis']['even']
    schema1_odd = schema1['basis']['odd']

    if schema3_even != schema1_even:
        errors.append("Even basis differs between Schema 1 and 3")
    if schema3_odd != schema1_odd:
        errors.append("Odd basis differs between Schema 1 and 3")

    # Check parity alignment
    schema3_parity = schema3['basis_and_parity'].get('parity', {})
    schema1_parity = schema1['parity']

    if schema3_parity != schema1_parity:
        errors.append("Parity dictionary differs between Schema 1 and 3")

    # Check gb values count
    algebra_n = schema3['algebra']['n']
    expected_gb_count = 4 * algebra_n
    actual_gb_count = len(schema3['deformation_parameters']['gb_matrix']['values'])

    if actual_gb_count != expected_gb_count:
        errors.append(f"gb values count ({actual_gb_count}) != expected ({expected_gb_count})")

    # Check gb values are all zero for trivial case
    gb_values = schema3['deformation_parameters']['gb_matrix']['values']
    if not all(v == 0.0 for v in gb_values.values()):
        errors.append("Expected all gb values to be 0.0 for trivial case")

    # Check deformation strength
    expected_strength = sum(abs(v) for v in gb_values.values())
    reported_strength = schema3['deformation_parameters']['deformation_strength']

    if abs(expected_strength - reported_strength) > 1e-10:
        errors.append(f"Deformation strength mismatch: {reported_strength} != {expected_strength}")

    # Check consistency key references correct files
    consistency = schema3.get('consistency', {})
    if consistency.get('schema1_reference') != f"C_{n}_structure.json":
        errors.append(f"Schema 3 should reference C_{n}_structure.json")
    if consistency.get('schema2_reference') != f"C_{n}_gamma.json":
        errors.append(f"Schema 3 should reference C_{n}_gamma.json")

    return len(errors) == 0, errors


def main():
    """Check consistency for all C(n+1) algebras."""
    all_passed = True

    for n in [1, 2, 3]:
        print(f"\nConsistency Check for C({n+1}) Schema 3 (n={n})")
        print("=" * 70)

        passed, errors = check_schema3_consistency(n)

        if passed:
            print("✓ PASSED: Schema 3 is consistent with Schemas 1 and 2")
        else:
            print(f"✗ FAILED: {len(errors)} inconsistencies found")
            for error in errors:
                print(f"  - {error}")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("Overall: All Schema 3 consistency checks PASSED ✓")
    else:
        print("Overall: Some checks FAILED ✗")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
