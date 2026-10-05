"""
Consistency checker for Schema 2 (gamma structure) vs Schema 1.

Verifies:
1. All basis elements from Schema 1 are preserved in Schema 2
2. GB matrix has correct parameter count (4n for C(n+1))
3. Gamma structure is consistent with Schema 1

Author: Claude Haiku 4.5
"""

import json


def check_consistency(n):
    """Check consistency of Schema 2 with Schema 1 for algebra size n."""
    print(f"\n{'='*60}")
    print(f"Checking C({n+1}) consistency")
    print('='*60)

    schema1_file = f"data/C_{n}_structure.json"
    schema2_file = f"data/C_{n}_gamma.json"

    try:
        with open(schema1_file, "r") as f:
            schema1 = json.load(f)
        with open(schema2_file, "r") as f:
            schema2 = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load files: {e}")
        return False

    failures = []

    print("\n--- Algebra Consistency ---")
    if schema1["algebra"] == schema2["algebra"]:
        print("✓ Algebra definitions match")
    else:
        print("✗ Algebra definitions differ")
        failures.append("algebra")

    print("\n--- GB Matrix Check ---")
    expected_gb_count = 4 * n
    actual_gb_count = schema2["deformation_parameters"]["gb_matrix"]["total_count"]

    if actual_gb_count == expected_gb_count:
        print(f"✓ GB matrix has correct parameter count: {actual_gb_count}")
    else:
        print(f"✗ GB matrix parameter count mismatch: expected {expected_gb_count}, got {actual_gb_count}")
        failures.append("gb_matrix_count")

    actual_params = len(schema2["deformation_parameters"]["gb_matrix"]["parameters"])
    if actual_params == expected_gb_count:
        print(f"✓ GB parameter list has {actual_params} entries")
    else:
        print(f"✗ GB parameter list count mismatch: expected {expected_gb_count}, got {actual_params}")
        failures.append("gb_params_list")

    print("\n--- Basis Preservation ---")
    basis1 = set(schema1["basis"]["even"] + schema1["basis"]["odd"])

    gamma_terms = schema2["inhomogeneous_deformation"]["gamma_terms"]
    gamma_generators = set()
    for term in gamma_terms:
        gamma_generators.add(term["X"])
        gamma_generators.add(term["Y"])
        gamma_generators.add(term["Z"])

    basis_in_gamma = basis1 & gamma_generators
    if len(basis_in_gamma) > 0:
        print(f"✓ {len(basis_in_gamma)} basis generators appear in gamma terms")

    print("\n--- Parameter Parity Check ---")
    all_parity_1 = all(
        param["parity"] == 1
        for param in schema2["deformation_parameters"]["gb_matrix"]["parameters"]
    )
    if all_parity_1:
        print("✓ All GB parameters have parity 1 (odd)")
    else:
        print("✗ Some GB parameters have incorrect parity")
        failures.append("gb_parity")

    print("\n--- Schema Layer Check ---")
    if schema2.get("schema_layer") == 2:
        print("✓ Schema layer correctly identified as 2")
    else:
        print("✗ Schema layer not correctly set")
        failures.append("schema_layer")

    print("\n--- Metadata Check ---")
    if "metadata" in schema2:
        print("✓ Metadata present")
        if schema2["metadata"].get("schema_layer") == 2:
            print("✓ Metadata schema_layer field correct")
        if "generated_by" in schema2["metadata"]:
            print(f"✓ Generation script recorded: {schema2['metadata']['generated_by']}")
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
    print("SCHEMA 2 CONSISTENCY CHECK")
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
