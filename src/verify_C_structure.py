import json
import os
from fractions import Fraction

def load_schema(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        return json.load(f)

def verify_structure(n):
    schema = load_schema(n)
    basis_list = schema["basis"]["even"] + schema["basis"]["odd"]
    parity = schema["parity"]
    
    # Load structure constants into a fast dict lookup
    # SC[X][Y] = {Z: coeff}
    SC = {x: {y: {} for y in basis_list} for x in basis_list}
    
    for sc in schema["structure_constants"]:
        X = sc["X"]
        Y = sc["Y"]
        Z = sc["Z"]
        coeff_str = sc["coeff"]
        if "/" in coeff_str:
            num, den = coeff_str.split("/")
            val = Fraction(int(num), int(den))
        else:
            val = Fraction(int(coeff_str))
            
        SC[X][Y][Z] = val
        
        # apply graded anti-symmetry for Y, X
        px = parity[X]
        py = parity[Y]
        sign = -1 if (px == 1 and py == 1) else 1
        SC[Y][X][Z] = -sign * val
        
    def comm(X, Y):
        return SC[X][Y]
        
    def comm_dict(poly1, Y):
        # [poly1, Y}
        # poly1 is {Z: coeff}
        res = {}
        for A, c_A in poly1.items():
            for Z, c_Z in SC[A][Y].items():
                res[Z] = res.get(Z, Fraction(0)) + c_A * c_Z
        return {k: v for k, v in res.items() if v != 0}

    # Verify anti-symmetry
    for X in basis_list:
        for Y in basis_list:
            px = parity[X]
            py = parity[Y]
            sign = -1 if (px == 1 and py == 1) else 1
            
            c_XY = SC[X][Y]
            c_YX = SC[Y][X]
            
            for Z in set(list(c_XY.keys()) + list(c_YX.keys())):
                v1 = c_XY.get(Z, Fraction(0))
                v2 = c_YX.get(Z, Fraction(0))
                if v1 != -sign * v2:
                    return False, f"Anti-symmetry failed for {X}, {Y}"

    # Verify Super Jacobi
    # (-1)^{px pz} [X, [Y, Z}} + (-1)^{py px} [Y, [Z, X}} + (-1)^{pz py} [Z, [X, Y}} = 0
    
    # We can iterate over all triples (X, Y, Z)
    # To save time, we can enforce X <= Y <= Z since Jacobi is totally anti-symmetric in graded sense
    for i, X in enumerate(basis_list):
        px = parity[X]
        for j in range(i, len(basis_list)):
            Y = basis_list[j]
            py = parity[Y]
            for k in range(j, len(basis_list)):
                Z = basis_list[k]
                pz = parity[Z]
                
                term1 = comm_dict(comm(Y, Z), X)  # [[Y,Z}, X} = -(-1)^{p_x(p_y+p_z)} [X, [Y,Z}}
                # Wait, it's easier to just do: [X, [Y, Z}} 
                # comm_dict(poly, Z) takes [poly, Z}.
                # Let's write a generic comm2:
                def comm_poly_basis(poly, basis_elem):
                    res = {}
                    for A, c in poly.items():
                        for R, rc in SC[A][basis_elem].items():
                            res[R] = res.get(R, Fraction(0)) + c * rc
                    return {k: v for k, v in res.items() if v != 0}
                    
                def comm_basis_poly(basis_elem, poly):
                    res = {}
                    for A, c in poly.items():
                        for R, rc in SC[basis_elem][A].items():
                            res[R] = res.get(R, Fraction(0)) + c * rc
                    return {k: v for k, v in res.items() if v != 0}

                T1 = comm_basis_poly(X, SC[Y][Z])
                T2 = comm_basis_poly(Y, SC[Z][X])
                T3 = comm_basis_poly(Z, SC[X][Y])
                
                s1 = (-1)**(px * pz)
                s2 = (-1)**(py * px)
                s3 = (-1)**(pz * py)
                
                jacobi = {}
                for R, c in T1.items(): jacobi[R] = jacobi.get(R, Fraction(0)) + s1 * c
                for R, c in T2.items(): jacobi[R] = jacobi.get(R, Fraction(0)) + s2 * c
                for R, c in T3.items(): jacobi[R] = jacobi.get(R, Fraction(0)) + s3 * c
                
                jacobi = {k: v for k, v in jacobi.items() if v != 0}
                
                if jacobi:
                    return False, f"Jacobi failed for {X}, {Y}, {Z}: {jacobi}"
                    
    return True, "Passed all checks"

if __name__ == "__main__":
    all_passed = True
    for n in [1, 2, 3]:
        print(f"Verifying C({n+1})...")
        passed, msg = verify_structure(n)
        if passed:
            print(f"  [OK] {msg}")
        else:
            print(f"  [FAIL] {msg}")
            all_passed = False
    
    if not all_passed:
        exit(1)
