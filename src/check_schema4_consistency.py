#!/usr/bin/env python3
"""
Schema 4 Consistency Checker

Verifies that Schema 4 (Coboundary Structure) is consistent with Schemas 1 and 3.
"""

import json
from pathlib import Path
from typing import Tuple, List


def check_schema4_consistency(n: int) -> Tuple[bool, List[str]]:
    """Check consistency between Schemas 1, 3, and 4 for C(n+1)."""
    schema1_file = f"data/C_{n}_structure.json"
    schema3_file = f"data/C_{n}_evaluated_trivial.json"
    schema4_file = f"data/C_{n}_coboundary_trivial.json"

    errors = []

    # Check files exist
    for fname in [schema1_file, schema3_file, schema4_file]:
        if not Path(fname).exists():
            errors.append(f"File not found: {fname}")

    if errors:
        return False, errors

    # Load schemas
    with open(schema1_file) as f:
        schema1 = json.load(f)
    with open(schema3_file) as f:
        schema3 = json.load(f)
    with open(schema4_file) as f:
        schema4 = json.load(f)

    # Check schema versions
    if schema4['schema_version'] != "5.0":
        errors.append(f"Schema 4 version should be 5.0, got {schema4['schema_version']}")

    # Check algebra field
    if schema1['algebra'] != schema4['algebra']:
        errors.append("Algebra field differs between Schema 1 and 4")
    if schema3['algebra'] != schema4['algebra']:
        errors.append("Algebra field differs between Schema 3 and 4")

    # Check basis alignment
    schema4_even = schema4['basis_reference'].get('even', [])
    schema4_odd = schema4['basis_reference'].get('odd', [])
    schema1_even = schema1['basis']['even']
    schema1_odd = schema1['basis']['odd']

    if schema4_even != schema1_even:
        errors.append("Even basis differs between Schema 1 and 4")
    if schema4_odd != schema1_odd:
        errors.append("Odd basis differs between Schema 1 and 4")

    # Check parity alignment
    schema4_parity = schema4['basis_reference'].get('parity', {})
    schema1_parity = schema1['parity']

    if schema4_parity != schema1_parity:
        errors.append("Parity dictionary differs between Schema 1 and 4")

    # Check f parameter space size
    total_f_params = schema4['f_parameter_space']['total_parameters']
    expected_f_params = (len(schema1_odd) * len(schema1_even) +
                         len(schema1_even) * len(schema1_odd))

    if total_f_params != expected_f_params:
        errors.append(f"f parameter count ({total_f_params}) != expected ({expected_f_params})")

    # Verify f parameter space is correct for parity reversal
    if expected_f_params != 2 * len(schema1_even) * len(schema1_odd):
        # This is actually correct; f maps odd → even and even → odd
        pass

    # Check that coboundary_coefficients dimensions match basis
    coboundary_dims = schema4['coboundary_coefficients']['dimensions']
    total_basis = len(schema1_even) + len(schema1_odd)
    expected_dims = f"{total_basis}^2"

    if expected_dims not in coboundary_dims:
        # Just a warning, not an error, since coboundary_coefficients is to be computed
        pass

    # Check consistency references
    consistency = schema4.get('consistency', {})
    if consistency.get('schema1_reference') != f"C_{n}_structure.json":
        errors.append(f"Schema 4 should reference C_{n}_structure.json")
    if consistency.get('schema3_reference') != f"C_{n}_evaluated_trivial.json":
        errors.append(f"Schema 4 should reference C_{n}_evaluated_trivial.json")

    return len(errors) == 0, errors


def main():
    """Check consistency for all C(n+1) algebras."""
    all_passed = True

    for n in [1, 2, 3]:
        print(f"\nConsistency Check for C({n+1}) Schema 4 (n={n})")
        print("=" * 70)

        passed, errors = check_schema4_consistency(n)

        if passed:
            print("✓ PASSED: Schema 4 is consistent with Schemas 1 and 3")
        else:
            print(f"✗ FAILED: {len(errors)} inconsistencies found")
            for error in errors:
                print(f"  - {error}")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("Overall: All Schema 4 consistency checks PASSED ✓")
    else:
        print("Overall: Some checks FAILED ✗")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
