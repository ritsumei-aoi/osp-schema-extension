import json
import os
import sys
from fractions import Fraction

def load_schema(n):
    path = f"data/C_{n}_structure.json"
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)

class Algebra:
    def __init__(self, schema):
        self.schema = schema
        self.even = schema["basis"]["even"]
        self.odd = schema["basis"]["odd"]
        self.basis = self.even + self.odd
        self.parity = schema["parity"]
        
        self.bracket_table = {}
        for c in schema["structure_constants"]:
            X, Y, Z, coeff = c["X"], c["Y"], c["Z"], c["coeff"]
            val = Fraction(coeff)
            if (X, Y) not in self.bracket_table:
                self.bracket_table[(X, Y)] = {}
            self.bracket_table[(X, Y)][Z] = self.bracket_table[(X, Y)].get(Z, 0) + val
            
    def bracket(self, X, Y):
        return self.bracket_table.get((X, Y), {})

def bracket_linear(alg, coeff_dict_1, Y):
    res = {}
    for X, c1 in coeff_dict_1.items():
        b = alg.bracket(X, Y)
        for Z, cb in b.items():
            res[Z] = res.get(Z, Fraction(0)) + c1 * cb
    
    final_res = {}
    for k, v in res.items():
        if v != 0:
            final_res[k] = v
    return final_res

def check_antisymmetry(alg):
    failures = []
    for X in alg.basis:
        for Y in alg.basis:
            px = alg.parity[X]
            py = alg.parity[Y]
            
            bXY = alg.bracket(X, Y)
            bYX = alg.bracket(Y, X)
            
            sign = -1 if (px == 1 and py == 1) else 1
            
            # Check if bXY = -sign * bYX
            expected_bYX = {}
            for k, v in bXY.items():
                expected_bYX[k] = -sign * v
                
            match = True
            all_keys = set(bYX.keys()).union(set(expected_bYX.keys()))
            for k in all_keys:
                if bYX.get(k, Fraction(0)) != expected_bYX.get(k, Fraction(0)):
                    match = False
                    break
                    
            if not match:
                failures.append((X, Y, bXY, bYX))
    return failures

def check_jacobi(alg):
    failures = []
    for X in alg.basis:
        for Y in alg.basis:
            for Z in alg.basis:
                px = alg.parity[X]
                py = alg.parity[Y]
                pz = alg.parity[Z]
                
                # [X, [Y, Z]]
                bYZ = alg.bracket(Y, Z)
                term1 = {}
                for W, coeff in bYZ.items():
                    bXW = alg.bracket(X, W)
                    for R, c2 in bXW.items():
                        term1[R] = term1.get(R, Fraction(0)) + coeff * c2
                        
                # [Y, [Z, X]]
                bZX = alg.bracket(Z, X)
                term2 = {}
                for W, coeff in bZX.items():
                    bYW = alg.bracket(Y, W)
                    for R, c2 in bYW.items():
                        term2[R] = term2.get(R, Fraction(0)) + coeff * c2
                        
                # [Z, [X, Y]]
                bXY = alg.bracket(X, Y)
                term3 = {}
                for W, coeff in bXY.items():
                    bZW = alg.bracket(Z, W)
                    for R, c2 in bZW.items():
                        term3[R] = term3.get(R, Fraction(0)) + coeff * c2
                        
                # (-1)^{|X||Z|} term1 + (-1)^{|Y||X|} term2 + (-1)^{|Z||Y|} term3 = 0
                sign1 = -1 if (px == 1 and pz == 1) else 1
                sign2 = -1 if (py == 1 and px == 1) else 1
                sign3 = -1 if (pz == 1 and py == 1) else 1
                
                sum_res = {}
                for k, v in term1.items():
                    sum_res[k] = sum_res.get(k, Fraction(0)) + sign1 * v
                for k, v in term2.items():
                    sum_res[k] = sum_res.get(k, Fraction(0)) + sign2 * v
                for k, v in term3.items():
                    sum_res[k] = sum_res.get(k, Fraction(0)) + sign3 * v
                    
                is_zero = True
                for k, v in sum_res.items():
                    if v != 0:
                        is_zero = False
                        break
                        
                if not is_zero:
                    failures.append((X, Y, Z, sum_res))
    return failures

def verify():
    results = {}
    for n in [1, 2, 3]:
        print(f"--- Verifying C({n+1}) ---")
        schema = load_schema(n)
        alg = Algebra(schema)
        
        anti_failures = check_antisymmetry(alg)
        if not anti_failures:
            print(f"[OK] Anti-symmetry passed for all {len(alg.basis)**2} pairs.")
        else:
            print(f"[FAIL] Anti-symmetry failed for {len(anti_failures)} pairs.")
            for f in anti_failures[:3]:
                print(f"  Example fail: [{f[0]}, {f[1]}] = {f[2]} vs [{f[1]}, {f[0]}] = {f[3]}")
                
        jacobi_failures = check_jacobi(alg)
        if not jacobi_failures:
            print(f"[OK] Super Jacobi passed for all {len(alg.basis)**3} triples.")
        else:
            print(f"[FAIL] Super Jacobi failed for {len(jacobi_failures)} triples.")
            for f in jacobi_failures[:3]:
                print(f"  Example fail: X={f[0]}, Y={f[1]}, Z={f[2]} => sum = {f[3]}")
        
        results[n] = {
            "anti": len(anti_failures) == 0,
            "jacobi": len(jacobi_failures) == 0,
            "anti_fails": anti_failures[:3],
            "jacobi_fails": jacobi_failures[:3]
        }
    return results

if __name__ == "__main__":
    verify()
