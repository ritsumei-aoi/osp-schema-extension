"""
Verification script for C(n+1) structure constants.

Checks:
1. Anti-symmetry: [X, Y] = -(-1)^{p(X)p(Y)} [Y, X]
2. Super Jacobi identity: [[X, Y], Z] + (-1)^{p(X)(p(Y)+p(Z))} [[Y, Z], X] + (-1)^{p(Z)(p(X)+p(Y))} [[Z, X], Y] = 0

Author: Claude Haiku 4.5
"""

import json
import sys
from fractions import Fraction


def load_schema(filename):
    """Load Schema 1 JSON file."""
    with open(filename, "r") as f:
        return json.load(f)


def get_brackets_dict(schema):
    """Convert structure constants list to dict for easy lookup."""
    brackets = {}
    for entry in schema["structure_constants"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        coeff = Fraction(entry["coeff"])

        key = (X, Y, Z)
        brackets[key] = coeff

    return brackets


def find_bracket(X, Y, brackets_dict):
    """Find [X, Y] in brackets dict. Return None if not found."""
    key = (X, Y)
    for (x, y, z), coeff in brackets_dict.items():
        if x == X and y == Y:
            if z not in [None]:
                return {z: coeff}
    return {}


def check_anti_symmetry(schema):
    """
    Check anti-symmetry: [X, Y] = -(-1)^{p(X)p(Y)} [Y, X].
    Returns (passed, failures_list).
    """
    brackets = get_brackets_dict(schema)
    parity = schema["parity"]
    failures = []

    checked_pairs = set()

    for (X, Y, Z_1), coeff_XY in brackets.items():
        if (X, Y) in checked_pairs or (Y, X) in checked_pairs:
            continue
        checked_pairs.add((X, Y))

        p_X = parity[X]
        p_Y = parity[Y]
        sign_factor = (-1) ** (p_X * p_Y)

        found_YX = False
        for (X2, Y2, Z_2), coeff_YX in brackets.items():
            if X2 == Y and Y2 == X:
                found_YX = True
                expected_coeff = -sign_factor * coeff_YX
                if coeff_XY != expected_coeff:
                    failures.append({
                        "type": "anti-symmetry",
                        "X": X, "Y": Y,
                        "coeff_XY": str(coeff_XY),
                        "coeff_YX": str(coeff_YX),
                        "expected": str(expected_coeff),
                        "message": f"[{X}, {Y}] coeff mismatch"
                    })
                break

    return len(failures) == 0, failures


def check_jacobi_identity(schema):
    """
    Check Super Jacobi identity.
    [[X, Y], Z] + (-1)^{p(X)(p(Y)+p(Z))} [[Y, Z], X] + (-1)^{p(Z)(p(X)+p(Y))} [[Z, X], Y] = 0

    Returns (passed, failures_list).
    """
    brackets = get_brackets_dict(schema)
    parity = schema["parity"]
    basis = schema["basis"]["even"] + schema["basis"]["odd"]
    failures = []

    checked_triples = set()
    checked_count = 0

    for X in basis:
        for Y in basis:
            for Z in basis:
                triple = tuple(sorted([X, Y, Z]))
                if triple in checked_triples:
                    continue
                checked_triples.add(triple)

                checked_count += 1

                p_X = parity[X]
                p_Y = parity[Y]
                p_Z = parity[Z]

                bracket_XY = {}
                bracket_YZ = {}
                bracket_ZX = {}

                for (x, y, z), coeff in brackets.items():
                    if x == X and y == Y:
                        bracket_XY[z] = coeff
                    if x == Y and y == Z:
                        bracket_YZ[z] = coeff
                    if x == Z and y == X:
                        bracket_ZX[z] = coeff

                if not bracket_XY and not bracket_YZ and not bracket_ZX:
                    continue

                bracket_XY_Z = {}
                for W, c_XY in bracket_XY.items():
                    for (w, z_inner, z_result), coeff in brackets.items():
                        if w == W and z_inner == Z:
                            if z_result not in bracket_XY_Z:
                                bracket_XY_Z[z_result] = Fraction(0)
                            bracket_XY_Z[z_result] += c_XY * coeff

                bracket_YZ_X = {}
                for W, c_YZ in bracket_YZ.items():
                    for (w, z_inner, z_result), coeff in brackets.items():
                        if w == W and z_inner == X:
                            if z_result not in bracket_YZ_X:
                                bracket_YZ_X[z_result] = Fraction(0)
                            bracket_YZ_X[z_result] += c_YZ * coeff

                bracket_ZX_Y = {}
                for W, c_ZX in bracket_ZX.items():
                    for (w, z_inner, z_result), coeff in brackets.items():
                        if w == W and z_inner == Y:
                            if z_result not in bracket_ZX_Y:
                                bracket_ZX_Y[z_result] = Fraction(0)
                            bracket_ZX_Y[z_result] += c_ZX * coeff

                sign1 = (-1) ** (p_X * (p_Y + p_Z))
                sign2 = (-1) ** (p_Z * (p_X + p_Y))

                all_generators = set(bracket_XY_Z.keys()) | set(bracket_YZ_X.keys()) | set(bracket_ZX_Y.keys())

                for gen in all_generators:
                    lhs = (bracket_XY_Z.get(gen, Fraction(0)) +
                           sign1 * bracket_YZ_X.get(gen, Fraction(0)) +
                           sign2 * bracket_ZX_Y.get(gen, Fraction(0)))

                    if lhs != 0:
                        failures.append({
                            "type": "jacobi",
                            "X": X, "Y": Y, "Z": Z,
                            "generator": gen,
                            "coefficient": str(lhs),
                            "message": f"Jacobi identity fails for triple ({X}, {Y}, {Z})"
                        })

    return len(failures) == 0, failures


def verify_all(n_values=[1, 2, 3]):
    """Verify all schema files."""
    results = {}

    for n in n_values:
        filename = f"data/C_{n}_structure.json"
        print(f"\n{'='*60}")
        print(f"Verifying {filename}")
        print('='*60)

        try:
            schema = load_schema(filename)
        except Exception as e:
            print(f"ERROR: Failed to load {filename}: {e}")
            continue

        n_sym = n + 1
        n_str = f"C({n_sym})"
        print(f"Algebra: {n_str} = osp(2|{2*n})")
        print(f"Dimensions: even={schema['algebra']['dimension']['even']}, "
              f"odd={schema['algebra']['dimension']['odd']}, "
              f"total={schema['algebra']['dimension']['total']}")
        print(f"Structure constants: {len(schema['structure_constants'])} entries")

        if not schema["structure_constants"]:
            print("WARNING: No structure constants found. Skipping verification.")
            results[n] = {"status": "skipped", "reason": "No structure constants"}
            continue

        print("\n--- Anti-symmetry Check ---")
        anti_sym_pass, anti_sym_failures = check_anti_symmetry(schema)
        if anti_sym_pass:
            print("✓ All checked pairs satisfy anti-symmetry")
        else:
            print(f"✗ Anti-symmetry FAILED for {len(anti_sym_failures)} pair(s)")
            for failure in anti_sym_failures[:3]:
                print(f"  {failure['message']}")
            if len(anti_sym_failures) > 3:
                print(f"  ... and {len(anti_sym_failures)-3} more")

        print("\n--- Super Jacobi Identity Check ---")
        jacobi_pass, jacobi_failures = check_jacobi_identity(schema)
        if jacobi_pass:
            print("✓ All checked triples satisfy Jacobi identity")
        else:
            print(f"✗ Jacobi identity FAILED for {len(jacobi_failures)} triple(s)")
            for failure in jacobi_failures[:3]:
                print(f"  {failure['message']}")
            if len(jacobi_failures) > 3:
                print(f"  ... and {len(jacobi_failures)-3} more")

        results[n] = {
            "status": "pass" if (anti_sym_pass and jacobi_pass) else "fail",
            "anti_symmetry": {"passed": anti_sym_pass, "failures": len(anti_sym_failures)},
            "jacobi": {"passed": jacobi_pass, "failures": len(jacobi_failures)}
        }

    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    for n, result in results.items():
        status = "✓ PASS" if result["status"] == "pass" else ("✗ FAIL" if result["status"] == "fail" else "⊘ SKIPPED")
        print(f"C({n+1}): {status}")
        if result["status"] not in ["skipped"]:
            anti_status = "PASS" if result['anti_symmetry']['passed'] else f"FAIL ({result['anti_symmetry']['failures']} failures)"
            jacobi_status = "PASS" if result['jacobi']['passed'] else f"FAIL ({result['jacobi']['failures']} failures)"
            print(f"  Anti-symmetry: {anti_status}")
            print(f"  Jacobi: {jacobi_status}")


if __name__ == "__main__":
    verify_all()
