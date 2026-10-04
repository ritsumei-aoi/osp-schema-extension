import json
import itertools
from collections import defaultdict
import fractions

def evaluate_jacobi_and_antisymmetry(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema = json.load(f)
        
    parity = schema['parity']
    sc_list = schema['structure_constants']
    
    # build a bracket function: [X, Y] -> dict of {Z: coeff}
    bracket = defaultdict(lambda: defaultdict(lambda: defaultdict(fractions.Fraction)))
    for entry in sc_list:
        X, Y, Z, c_str = entry['X'], entry['Y'], entry['Z'], entry['coeff']
        c = fractions.Fraction(c_str)
        bracket[X][Y][Z] += c
        
    all_gen = schema['basis']['even'] + schema['basis']['odd']
    
    # Check Anti-symmetry
    antisym_failures = []
    for X in all_gen:
        for Y in all_gen:
            b_XY = bracket[X][Y]
            b_YX = bracket[Y][X]
            sign = -1 if (parity[X] == 1 and parity[Y] == 1) else 1
            
            all_Z = set(b_XY.keys()) | set(b_YX.keys())
            for Z in all_Z:
                if b_XY[Z] != -sign * b_YX[Z]:
                    antisym_failures.append((X, Y, Z, b_XY[Z], b_YX[Z]))
                    
    print(f"n={n}: Anti-symmetry failures: {len(antisym_failures)}")
    if antisym_failures:
        print(f"Sample failure: {antisym_failures[0]}")
        
    # Check Jacobi
    def apply_bracket(c_dict, W):
        # [W, c_dict] = sum_Z c_dict[Z] * [W, Z]
        res = defaultdict(fractions.Fraction)
        for Z, c in c_dict.items():
            for R, c_R in bracket[W][Z].items():
                res[R] += c * c_R
        return res

    jacobi_failures = 0
    for X in all_gen:
        for Y in all_gen:
            for Z in all_gen:
                pX, pY, pZ = parity[X], parity[Y], parity[Z]
                
                # J1 = (-1)^{pX pZ} [X, [Y, Z]]
                s1 = -1 if (pX == 1 and pZ == 1) else 1
                J1 = apply_bracket(bracket[Y][Z], X) # Wait, apply_bracket(dict, W) computes [W, dict].
                
                # J2 = (-1)^{pY pX} [Y, [Z, X]]
                s2 = -1 if (pY == 1 and pX == 1) else 1
                J2 = apply_bracket(bracket[Z][X], Y)
                
                # J3 = (-1)^{pZ pY} [Z, [X, Y]]
                s3 = -1 if (pZ == 1 and pY == 1) else 1
                J3 = apply_bracket(bracket[X][Y], Z)
                
                # Sum = s1*J1 + s2*J2 + s3*J3
                total = defaultdict(fractions.Fraction)
                for R, c in J1.items(): total[R] += s1 * c
                for R, c in J2.items(): total[R] += s2 * c
                for R, c in J3.items(): total[R] += s3 * c
                
                for R, c in total.items():
                    if c != 0:
                        jacobi_failures += 1
                        if jacobi_failures == 1:
                            print(f"First Jacobi failure for ({X}, {Y}, {Z}) at {R}: {c}")
                            print(f"J1={s1}*{dict(J1)}")
                            print(f"J2={s2}*{dict(J2)}")
                            print(f"J3={s3}*{dict(J3)}")
                        break
                        
    print(f"n={n}: Jacobi failures: {jacobi_failures}")
    return len(antisym_failures) == 0 and jacobi_failures == 0

if __name__ == "__main__":
    all_pass = True
    for n in [1, 2, 3]:
        print(f"Verifying C({n+1})...")
        if not evaluate_jacobi_and_antisymmetry(n):
            all_pass = False
            
    if all_pass:
        print("All checks passed.")
    else:
        print("Some checks failed.")
