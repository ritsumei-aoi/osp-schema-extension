import json
import sys
from fractions import Fraction

def load_algebra(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        data = json.load(f)
    
    generators = data['basis']['even'] + data['basis']['odd']
    parity = data['parity']
    
    # sc[X][Y] = {Z: coeff}
    sc = {x: {y: {} for y in generators} for x in generators}
    
    for term in data['structure_constants']:
        X = term['X']
        Y = term['Y']
        Z = term['Z']
        coeff = Fraction(term['coeff'])
        sc[X][Y][Z] = sc[X][Y].get(Z, Fraction(0)) + coeff
        
    return generators, parity, sc

def bracket(sc, X, Y):
    return sc[X][Y]

def check_anti_symmetry(generators, parity, sc):
    failures = 0
    for X in generators:
        for Y in generators:
            # [X, Y}
            xy = bracket(sc, X, Y)
            # [Y, X}
            yx = bracket(sc, Y, X)
            
            sign = -1 if (parity[X] == 1 and parity[Y] == 1) else 1
            # We expect [X, Y} = - (-1)^{p(X)p(Y)} [Y, X} = - sign * [Y, X}
            
            all_keys = set(xy.keys()).union(set(yx.keys()))
            for Z in all_keys:
                c_xy = xy.get(Z, Fraction(0))
                c_yx = yx.get(Z, Fraction(0))
                
                expected_c_xy = -sign * c_yx
                if c_xy != expected_c_xy:
                    failures += 1
                    # print(f"Anti-symmetry failure for {X}, {Y} -> {Z}: {c_xy} != {expected_c_xy}")
    return failures

def check_jacobi(generators, parity, sc):
    # (-1)^{xz} [X, [Y, Z]] + (-1)^{yx} [Y, [Z, X]] + (-1)^{zy} [Z, [X, Y]] = 0
    failures = 0
    
    # Helper to compute [A, dict_B]
    def bracket_dict(A, dict_B):
        res = {}
        for B, c_B in dict_B.items():
            if c_B == 0: continue
            curr_bracket = bracket(sc, A, B)
            for Z, c_Z in curr_bracket.items():
                if c_Z == 0: continue
                res[Z] = res.get(Z, Fraction(0)) + c_B * c_Z
        return res
        
    def add_dicts(d1, d2, d3, s1, s2, s3):
        res = {}
        for Z in set(d1.keys()).union(set(d2.keys())).union(set(d3.keys())):
            val = d1.get(Z, Fraction(0)) * s1 + d2.get(Z, Fraction(0)) * s2 + d3.get(Z, Fraction(0)) * s3
            if val != 0:
                res[Z] = val
        return res

    for X in generators:
        for Y in generators:
            for Z in generators:
                # [X, [Y, Z]]
                term1_inner = bracket(sc, Y, Z)
                term1 = bracket_dict(X, term1_inner)
                s1 = -1 if (parity[X] == 1 and parity[Z] == 1) else 1
                
                # [Y, [Z, X]]
                term2_inner = bracket(sc, Z, X)
                term2 = bracket_dict(Y, term2_inner)
                s2 = -1 if (parity[Y] == 1 and parity[X] == 1) else 1
                
                # [Z, [X, Y]]
                term3_inner = bracket(sc, X, Y)
                term3 = bracket_dict(Z, term3_inner)
                s3 = -1 if (parity[Z] == 1 and parity[Y] == 1) else 1
                
                total = add_dicts(term1, term2, term3, s1, s2, s3)
                if total:
                    failures += 1
                    # print(f"Jacobi failure for {X}, {Y}, {Z}: {total}")
                    
    return failures

def main():
    all_passed = True
    for n in [1, 2, 3]:
        generators, parity, sc = load_algebra(n)
        
        anti_sym_fails = check_anti_symmetry(generators, parity, sc)
        if anti_sym_fails == 0:
            print(f"n={n}: Anti-symmetry check PASSED.")
        else:
            print(f"n={n}: Anti-symmetry check FAILED with {anti_sym_fails} failures.")
            all_passed = False
            
        jacobi_fails = check_jacobi(generators, parity, sc)
        if jacobi_fails == 0:
            print(f"n={n}: Super Jacobi check PASSED.")
        else:
            print(f"n={n}: Super Jacobi check FAILED with {jacobi_fails} failures.")
            all_passed = False
            
    if all_passed:
        print("ALL CHECKS PASSED.")
        sys.exit(0)
    else:
        print("SOME CHECKS FAILED.")
        sys.exit(1)

if __name__ == '__main__':
    main()
