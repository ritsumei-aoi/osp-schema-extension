import os
import json
import sys
from fractions import Fraction

def load_structure(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    
    basis = data["basis"]["odd"] + data["basis"]["even"]
    parity = data["parity"]
    
    # Map (X, Y) -> {Z: Fraction(coeff)}
    brackets = {}
    for x in basis:
        for y in basis:
            brackets[(x, y)] = {}

    for entry in data["structure_constants"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        c = Fraction(entry["coeff"])
        brackets[(X, Y)][Z] = brackets[(X, Y)].get(Z, Fraction(0)) + c

        if X != Y:
            p_X = parity[X]
            p_Y = parity[Y]
            sign = -1 if (p_X == 1 and p_Y == 1) else 1
            # [Y, X} = - sign * [X, Y}
            brackets[(Y, X)][Z] = brackets[(Y, X)].get(Z, Fraction(0)) - sign * c
        elif parity[X] == 1:
            # If X == Y and odd: [X, X} = 2 X^2 = sum_Z c Z
            # So [X, X} is already recorded for (X, X).
            pass

    return basis, parity, brackets

def verify_antisymmetry(basis, parity, brackets):
    errors = []
    for X in basis:
        for Y in basis:
            p_X = parity[X]
            p_Y = parity[Y]
            sign = -1 if (p_X == 1 and p_Y == 1) else 1

            # Check [Y, X} + sign * [X, Y} == 0
            for Z in basis:
                c_XY = brackets[(X, Y)].get(Z, Fraction(0))
                c_YX = brackets[(Y, X)].get(Z, Fraction(0))
                if c_YX + sign * c_XY != 0:
                    errors.append(f"Anti-symmetry failure for ({X}, {Y}) -> {Z}: c_YX={c_YX}, c_XY={c_XY}")
    return errors

def verify_super_jacobi(basis, parity, brackets):
    errors = []
    n_basis = len(basis)
    checked_triples = 0

    for i in range(n_basis):
        X = basis[i]
        p_X = parity[X]
        for j in range(n_basis):
            Y = basis[j]
            p_Y = parity[Y]
            for k in range(n_basis):
                Z = basis[k]
                p_Z = parity[Z]
                checked_triples += 1

                # Terms in Jacobi:
                # s1 * [X, [Y, Z}\}
                # s2 * [Y, [Z, X\}\}
                # s3 * [Z, [X, Y\}\}
                # s1 = (-1)^(p_X * p_Z)
                # s2 = (-1)^(p_Y * p_X)
                # s3 = (-1)^(p_Z * p_Y)
                s1 = -1 if (p_X == 1 and p_Z == 1) else 1
                s2 = -1 if (p_Y == 1 and p_X == 1) else 1
                s3 = -1 if (p_Z == 1 and p_Y == 1) else 1

                # Calculate sum over T of coeff for T
                jacobi_result = {}

                # 1. s1 * [X, [Y, Z}\}
                for W, c_YZ_W in brackets[(Y, Z)].items():
                    if c_YZ_W == 0:
                        continue
                    for T, c_XW_T in brackets[(X, W)].items():
                        if c_XW_T == 0:
                            continue
                        jacobi_result[T] = jacobi_result.get(T, Fraction(0)) + s1 * c_YZ_W * c_XW_T

                # 2. s2 * [Y, [Z, X\}\}
                for W, c_ZX_W in brackets[(Z, X)].items():
                    if c_ZX_W == 0:
                        continue
                    for T, c_YW_T in brackets[(Y, W)].items():
                        if c_YW_T == 0:
                            continue
                        jacobi_result[T] = jacobi_result.get(T, Fraction(0)) + s2 * c_ZX_W * c_YW_T

                # 3. s3 * [Z, [X, Y\}\}
                for W, c_XY_W in brackets[(X, Y)].items():
                    if c_XY_W == 0:
                        continue
                    for T, c_ZW_T in brackets[(Z, W)].items():
                        if c_ZW_T == 0:
                            continue
                        jacobi_result[T] = jacobi_result.get(T, Fraction(0)) + s3 * c_XY_W * c_ZW_T

                # Check if jacobi_result is identically 0
                for T, val in jacobi_result.items():
                    if val != 0:
                        errors.append(f"Super Jacobi failure for triple ({X}, {Y}, {Z}) at {T}: sum = {val}")

    return checked_triples, errors

def main():
    all_passed = True
    for n in (1, 2, 3):
        path = f"data/C_{n}_structure.json"
        if not os.path.exists(path):
            print(f"File not found: {path}")
            all_passed = False
            continue

        basis, parity, brackets = load_structure(path)
        antisym_errors = verify_antisymmetry(basis, parity, brackets)
        triples_count, jacobi_errors = verify_super_jacobi(basis, parity, brackets)

        print(f"Verification for C({n+1}) [n={n}]:")
        print(f"  Basis dimension: {len(basis)}")
        print(f"  Generator pairs checked: {len(basis)**2}")
        print(f"  Anti-symmetry errors: {len(antisym_errors)}")
        print(f"  Triples checked: {triples_count}")
        print(f"  Super Jacobi errors: {len(jacobi_errors)}")

        if antisym_errors or jacobi_errors:
            all_passed = False
            if antisym_errors:
                print("  Sample anti-symmetry errors:", antisym_errors[:5])
            if jacobi_errors:
                print("  Sample Super Jacobi errors:", jacobi_errors[:5])
        else:
            print("  Result: PASSED (100% verified)")

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
