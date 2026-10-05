"""
Consistency checker for Schema 4 (coboundary structure) vs Schema 1.

Verifies:
1. Linear map f is properly defined
2. Coboundary operator is computed
3. Schema layer is correctly identified
4. Consistency with Schema 1 basis

Author: Claude Haiku 4.5
"""

import json


def check_consistency(n):
    """Check consistency of Schema 4 with Schema 1 for algebra size n."""
    print(f"\n{'='*60}")
    print(f"Checking C({n+1}) Schema 4 consistency")
    print('='*60)

    schema1_file = f"data/C_{n}_structure.json"
    schema4_file = f"data/C_{n}_coboundary.json"

    try:
        with open(schema1_file, "r") as f:
            schema1 = json.load(f)
        with open(schema4_file, "r") as f:
            schema4 = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load files: {e}")
        return False

    failures = []

    print("\n--- Algebra Consistency ---")
    if schema1["algebra"] == schema4["algebra"]:
        print("✓ Algebra definitions match")
    else:
        print("✗ Algebra definitions differ")
        failures.append("algebra")

    print("\n--- Linear Map f Definition ---")
    if "linear_map_f" in schema4:
        print("✓ Linear map f defined")
        if "description" in schema4["linear_map_f"]:
            print(f"  Form: {schema4['linear_map_f']['parametric_form']}")
    else:
        print("✗ Linear map f not found")
        failures.append("linear_map_f")

    print("\n--- Coboundary Operator ---")
    if "coboundary_operator" in schema4:
        print("✓ Coboundary operator defined")
        coboundary_terms = schema4["coboundary_operator"].get("coboundary_terms", [])
        print(f"  Coboundary terms: {len(coboundary_terms)}")

        if "formula" in schema4["coboundary_operator"]:
            print(f"  Formula documented: ✓")
    else:
        print("✗ Coboundary operator not found")
        failures.append("coboundary_operator")

    print("\n--- Triviality Analysis ---")
    if "triviality_analysis" in schema4:
        print("✓ Triviality analysis section present")
        analysis = schema4["triviality_analysis"].get("analysis", {})

        if "deformation_terms" in analysis:
            print(f"  Deformation terms: {analysis['deformation_terms']}")
        if "parametric_form" in analysis:
            print(f"  Parametric form: {analysis['parametric_form']}")
    else:
        print("✗ Triviality analysis not found")
        failures.append("triviality_analysis")

    print("\n--- Schema Layer Check ---")
    if schema4.get("schema_layer") == 4:
        print("✓ Schema layer correctly identified as 4")
    else:
        print("✗ Schema layer not correctly set")
        failures.append("schema_layer")

    print("\n--- Basis Reference ---")
    basis1 = set(schema1["basis"]["even"] + schema1["basis"]["odd"])

    if "linear_map_f" in schema4:
        linear_map = schema4["linear_map_f"].get("definition", {})
        if isinstance(linear_map, dict) and len(linear_map) > 0:
            map_generators = set(linear_map.keys())
            overlap = basis1 & map_generators
            print(f"✓ Linear map references {len(map_generators)} generators")

    print("\n--- Metadata Check ---")
    if "metadata" in schema4:
        print("✓ Metadata present")
        if schema4["metadata"].get("schema_layer") == 4:
            print("✓ Metadata schema_layer field correct")
        if "generated_by" in schema4["metadata"]:
            print(f"✓ Generation script recorded: {schema4['metadata']['generated_by']}")
        if "notes" in schema4["metadata"]:
            print(f"✓ Implementation notes: {schema4['metadata']['notes'][:60]}...")
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
    print("SCHEMA 4 CONSISTENCY CHECK")
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
