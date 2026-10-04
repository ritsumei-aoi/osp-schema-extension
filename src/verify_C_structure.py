"""
Super Jacobi Identity and Anti-symmetry Verification Script for C(n+1) Structure Constants
"""

import os
import json
from fractions import Fraction

def load_structure_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def build_bracket_lookup(structure_constants):
    """
    Builds a nested dict lookup: bracket[X][Y][Z] = Fraction(coeff)
    """
    lookup = {}
    for entry in structure_constants:
        X = entry["X"]
        Y = entry["Y"]
        Z = entry["Z"]
        coeff = Fraction(entry["coeff"])
        
        if X not in lookup:
            lookup[X] = {}
        if Y not in lookup[X]:
            lookup[X][Y] = {}
        lookup[X][Y][Z] = coeff
    return lookup

def get_bracket_coeff(lookup, X, Y, Z):
    return lookup.get(X, {}).get(Y, {}).get(Z, Fraction(0))

def verify_anti_symmetry(data):
    """
    Verifies graded anti-symmetry: [Y, X} = -(-1)^(pX*pY) [X, Y}
    """
    even = data["basis"]["even"]
    odd = data["basis"]["odd"]
    all_basis = even + odd
    parity = data["parity"]
    lookup = build_bracket_lookup(data["structure_constants"])
    
    failures = []
    total_pairs = 0
    
    for X in all_basis:
        for Y in all_basis:
            total_pairs += 1
            pX = parity[X]
            pY = parity[Y]
            expected_factor = Fraction(1 if (pX == 1 and pY == 1) else -1)
            
            # Check for all Z in basis
            for Z in all_basis:
                c_XY_Z = get_bracket_coeff(lookup, X, Y, Z)
                c_YX_Z = get_bracket_coeff(lookup, Y, X, Z)
                
                if c_YX_Z != expected_factor * c_XY_Z:
                    failures.append({
                        "pair": (X, Y),
                        "Z": Z,
                        "c_XY_Z": str(c_XY_Z),
                        "c_YX_Z": str(c_YX_Z),
                        "expected_factor": str(expected_factor)
                    })
                    
    return {
        "passed": len(failures) == 0,
        "total_pairs": total_pairs,
        "failures_count": len(failures),
        "failures": failures[:10]  # sample first 10 if any
    }

def verify_super_jacobi(data):
    """
    Verifies Super Jacobi Identity for all triples (X, Y, Z):
    (-1)^(pX pZ) [X, [Y, Z}] + (-1)^(pY pX) [Y, [Z, X}] + (-1)^(pZ pY) [Z, [X, Y}] = 0
    """
    even = data["basis"]["even"]
    odd = data["basis"]["odd"]
    all_basis = even + odd
    parity = data["parity"]
    lookup = build_bracket_lookup(data["structure_constants"])
    
    failures = []
    total_triples = 0
    
    for i, X in enumerate(all_basis):
        for j, Y in enumerate(all_basis):
            for k, Z in enumerate(all_basis):
                total_triples += 1
                pX, pY, pZ = parity[X], parity[Y], parity[Z]
                
                sign1 = Fraction(-1 if ((pX * pZ) % 2 == 1) else 1)
                sign2 = Fraction(-1 if ((pY * pX) % 2 == 1) else 1)
                sign3 = Fraction(-1 if ((pZ * pY) % 2 == 1) else 1)
                
                # Check for every target U in all_basis
                for U in all_basis:
                    # Term 1: sign1 * sum_W ( c_YZ^W * c_XW^U )
                    term1 = Fraction(0)
                    if Y in lookup and Z in lookup[Y]:
                        for W, c_YZ_W in lookup[Y][Z].items():
                            c_XW_U = get_bracket_coeff(lookup, X, W, U)
                            term1 += c_YZ_W * c_XW_U
                    term1 *= sign1
                    
                    # Term 2: sign2 * sum_W ( c_ZX^W * c_YW^U )
                    term2 = Fraction(0)
                    if Z in lookup and X in lookup[Z]:
                        for W, c_ZX_W in lookup[Z][X].items():
                            c_YW_U = get_bracket_coeff(lookup, Y, W, U)
                            term2 += c_ZX_W * c_YW_U
                    term2 *= sign2
                    
                    # Term 3: sign3 * sum_W ( c_XY^W * c_ZW^U )
                    term3 = Fraction(0)
                    if X in lookup and Y in lookup[X]:
                        for W, c_XY_W in lookup[X][Y].items():
                            c_ZW_U = get_bracket_coeff(lookup, Z, W, U)
                            term3 += c_XY_W * c_ZW_U
                    term3 *= sign3
                    
                    total_sum = term1 + term2 + term3
                    if total_sum != Fraction(0):
                        failures.append({
                            "triple": (X, Y, Z),
                            "U": U,
                            "sum": str(total_sum),
                            "term1": str(term1),
                            "term2": str(term2),
                            "term3": str(term3)
                        })
                        
    return {
        "passed": len(failures) == 0,
        "total_triples": total_triples,
        "failures_count": len(failures),
        "failures": failures[:10]
    }

def run_verification(data_dir="data"):
    results = {}
    for n in [1, 2, 3]:
        filepath = os.path.join(data_dir, f"C_{n}_structure.json")
        data = load_structure_data(filepath)
        
        print(f"Verifying C({n+1}) from {filepath}...")
        as_res = verify_anti_symmetry(data)
        sj_res = verify_super_jacobi(data)
        
        results[f"C_{n}"] = {
            "anti_symmetry": as_res,
            "super_jacobi": sj_res
        }
        
        print(f"  Anti-symmetry check: {'PASS' if as_res['passed'] else 'FAIL'} ({as_res['total_pairs']} pairs checked)")
        print(f"  Super Jacobi check:  {'PASS' if sj_res['passed'] else 'FAIL'} ({sj_res['total_triples']} triples checked)")
        
    return results

if __name__ == "__main__":
    run_verification()
