import json
import itertools
from collections import defaultdict

def verify_algebra(n):
    with open(f"data/C_{n}_structure.json") as f:
        data = json.load(f)
    
    basis = data["basis"]["odd"] + data["basis"]["even"]
    parities = data["parity"]
    
    # C[X][Y][Z] = coefficient
    C = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    for entry in data["structure_constants"]:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        c = int(entry["coeff"])
        C[X][Y][Z] += c
    
    # Fill in the Y, X using anti-symmetry if missing, or check if present
    for X in basis:
        for Y in basis:
            if X == Y:
                # [X, X] = -(-1)^{p(X)p(X)} [X, X] => if even, must be 0
                if parities[X] == 0:
                    for Z, c in C[X][X].items():
                        if c != 0:
                            return False, f"Anti-symmetry failed: [{X}, {X}] has term {c}{Z} but {X} is even."
            else:
                # Check if Y, X is in C
                sign = -1 if parities[X] * parities[Y] == 1 else 1
                expected_YX = {Z: -sign * c for Z, c in C[X][Y].items() if c != 0}
                
                # If Y, X is not in C, add it
                if not C[Y][X]:
                    for Z, c in expected_YX.items():
                        C[Y][X][Z] = c
                else:
                    # check consistency
                    actual_YX = {Z: c for Z, c in C[Y][X].items() if c != 0}
                    if actual_YX != expected_YX:
                        return False, f"Anti-symmetry failed for [{X}, {Y}] and [{Y}, {X}]: expected {expected_YX}, got {actual_YX}"

    # Super Jacobi identity
    # J(X, Y, Z) = (-1)^{p(X)p(Z)} [X, [Y, Z]] + (-1)^{p(Y)p(X)} [Y, [Z, X]] + (-1)^{p(Z)p(Y)} [Z, [X, Y]] == 0
    for X in basis:
        for Y in basis:
            for Z in basis:
                # Compute term 1: (-1)^{p(X)p(Z)} [X, [Y, Z]]
                term1 = defaultdict(int)
                sign1 = -1 if parities[X] * parities[Z] == 1 else 1
                for W, c1 in C[Y][Z].items():
                    for res, c2 in C[X][W].items():
                        term1[res] += sign1 * c1 * c2
                
                # Compute term 2: (-1)^{p(Y)p(X)} [Y, [Z, X]]
                term2 = defaultdict(int)
                sign2 = -1 if parities[Y] * parities[X] == 1 else 1
                for W, c1 in C[Z][X].items():
                    for res, c2 in C[Y][W].items():
                        term2[res] += sign2 * c1 * c2
                        
                # Compute term 3: (-1)^{p(Z)p(Y)} [Z, [X, Y]]
                term3 = defaultdict(int)
                sign3 = -1 if parities[Z] * parities[Y] == 1 else 1
                for W, c1 in C[X][Y].items():
                    for res, c2 in C[Z][W].items():
                        term3[res] += sign3 * c1 * c2
                        
                # Sum them up
                total = defaultdict(int)
                for res, c in term1.items(): total[res] += c
                for res, c in term2.items(): total[res] += c
                for res, c in term3.items(): total[res] += c
                
                for res, c in total.items():
                    if c != 0:
                        return False, f"Jacobi failed for {X}, {Y}, {Z} -> {res} has coeff {c}"
                        
    return True, "Passed all checks."

def main():
    results = []
    for n in [1, 2, 3]:
        print(f"Verifying C({n+1}) (n={n})...")
        ok, msg = verify_algebra(n)
        results.append(f"n={n}: {'PASS' if ok else 'FAIL'} - {msg}")
        print(results[-1])

    with open("docs/issues/I04_report.txt", "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    main()
