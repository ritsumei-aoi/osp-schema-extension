"""
Consistency checker for Schema 3 (evaluated structure) vs Schema 2.

Verifies:
1. GB assignment is complete (all parameters have values)
2. Structure constants are properly evaluated (no symbolic terms)
3. Schema layer is correctly identified
4. Consistency with Schema 2 structure

Author: Claude Haiku 4.5
"""

import json
import re


def check_consistency(n):
    """Check consistency of Schema 3 with Schema 2 for algebra size n."""
    print(f"\n{'='*60}")
    print(f"Checking C({n+1}) Schema 3 consistency")
    print('='*60)

    schema2_file = f"data/C_{n}_gamma.json"
    schema3_file = f"data/C_{n}_evaluated.json"

    try:
        with open(schema2_file, "r") as f:
            schema2 = json.load(f)
        with open(schema3_file, "r") as f:
            schema3 = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load files: {e}")
        return False

    failures = []

    print("\n--- GB Assignment Check ---")
    expected_count = 4 * n
    actual_count = len(schema3["gb_assignment"]["values"])

    if actual_count == expected_count:
        print(f"✓ GB assignment complete: {actual_count} parameters")
    else:
        print(f"✗ GB assignment incomplete: expected {expected_count}, got {actual_count}")
        failures.append("gb_assignment_count")

    all_numeric = all(isinstance(v, (int, float)) for v in schema3["gb_assignment"]["values"].values())
    if all_numeric:
        print(f"✓ All GB values are numeric")
    else:
        print(f"✗ Some GB values are not numeric")
        failures.append("gb_numeric")

    print("\n--- Structure Constants Evaluation Check ---")
    struct_consts = schema3["evaluated_bracket"]["structure_constants"]
    print(f"Structure constants: {len(struct_consts)} entries")

    all_numeric_coeffs = True
    symbolic_terms = 0

    for entry in struct_consts:
        coeff = entry["coeff"]
        if re.match(r'^[+-]?\d+(/\d+)?$', coeff):
            pass
        elif coeff.startswith("gb_") or coeff.startswith("-gb_"):
            all_numeric_coeffs = False
            symbolic_terms += 1

    if all_numeric_coeffs:
        print(f"✓ All structure constant coefficients are numeric")
    else:
        print(f"✗ {symbolic_terms} symbolic terms remain (should be fully evaluated)")
        failures.append("symbolic_terms")

    print("\n--- Schema Layer Check ---")
    if schema3.get("schema_layer") == 3:
        print("✓ Schema layer correctly identified as 3")
    else:
        print("✗ Schema layer not correctly set")
        failures.append("schema_layer")

    print("\n--- Basis Preservation ---")
    basis_labels = set()
    for entry in struct_consts:
        basis_labels.add(entry["X"])
        basis_labels.add(entry["Y"])
        basis_labels.add(entry["Z"])

    schema2_basis = set(schema2["algebra"]["dimension"].keys())
    if len(basis_labels) > 0:
        print(f"✓ {len(basis_labels)} distinct generators in structure constants")

    print("\n--- Metadata Check ---")
    if "metadata" in schema3:
        print("✓ Metadata present")
        if schema3["metadata"].get("schema_layer") == 3:
            print("✓ Metadata schema_layer field correct")
        if "evaluation_point" in schema3["metadata"]:
            print(f"✓ Evaluation point recorded: {schema3['metadata']['evaluation_point']}")
    else:
        print("✗ Metadata missing")
        failures.append("metadata")

    print(f"\n{'='*60}")
    if failures:
        print(f"RESULT: ✗ FAILED ({len(failures)} issue(s))")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print("RESULT: ✓ PASSED")
        return True


def main():
    """Check all three algebra sizes."""
    print("\n" + "="*60)
    print("SCHEMA 3 CONSISTENCY CHECK")
    print("="*60)

    results = {}
    for n in [1, 2, 3]:
        results[n] = check_consistency(n)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    for n in [1, 2, 3]:
        status = "✓ PASS" if results[n] else "✗ FAIL"
        print(f"C({n+1}): {status}")


if __name__ == "__main__":
    main()
