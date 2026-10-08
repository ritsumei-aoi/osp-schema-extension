import json
import fractions

def verify_structure(n):
    with open(f"data/C_{n}_structure.json", "r") as f:
        schema = json.load(f)
        
    parity = schema["parity"]
    parity["K"] = 0
    
    basis_elements = schema["basis"]["even"] + schema["basis"]["odd"] + ["K"]
    
    # Build full bracket dictionary
    # C[X][Y] = {Z: coeff}
    C = {x: {y: {} for y in basis_elements} for x in basis_elements}
    
    for const in schema["structure_constants"]:
        x, y, z, coeff_str = const["X"], const["Y"], const["Z"], const["coeff"]
        coeff = fractions.Fraction(coeff_str)
        C[x][y][z] = coeff
        
        # enforce anti-symmetry
        px, py = parity[x], parity[y]
        sign = -1 if (px == 1 and py == 1) else 1
        C[y][x][z] = -sign * coeff
        
    # Super Jacobi identity
    # (-1)^{p(X)p(Z)} [X, [Y, Z\}\} + (-1)^{p(Y)p(X)} [Y, [Z, X\}\} + (-1)^{p(Z)p(Y)} [Z, [X, Y\}\} = 0
    def bracket(x, y):
        return C[x][y]
    
    def bracket_linear(x, poly_y):
        res = {}
        for y, c in poly_y.items():
            for z, cz in bracket(x, y).items():
                res[z] = res.get(z, fractions.Fraction(0)) + c * cz
        return {k: v for k, v in res.items() if v != 0}

    def add_polys(p1, p2):
        res = dict(p1)
        for k, v in p2.items():
            res[k] = res.get(k, fractions.Fraction(0)) + v
            if res[k] == 0: del res[k]
        return res
        
    def mul_poly(p, scalar):
        return {k: v * scalar for k, v in p.items() if v * scalar != 0}

    failures = 0
    checks = 0
    for x in basis_elements:
        if x == "K": continue
        for y in basis_elements:
            if y == "K": continue
            for z in basis_elements:
                if z == "K": continue
                
                checks += 1
                
                px, py, pz = parity[x], parity[y], parity[z]
                
                # term 1: (-1)^{p(X)p(Z)} [X, [Y, Z\}\}
                t1_sign = -1 if (px == 1 and pz == 1) else 1
                t1 = mul_poly(bracket_linear(x, bracket(y, z)), t1_sign)
                
                # term 2: (-1)^{p(Y)p(X)} [Y, [Z, X\}\}
                t2_sign = -1 if (py == 1 and px == 1) else 1
                t2 = mul_poly(bracket_linear(y, bracket(z, x)), t2_sign)
                
                # term 3: (-1)^{p(Z)p(Y)} [Z, [X, Y\}\}
                t3_sign = -1 if (pz == 1 and py == 1) else 1
                t3 = mul_poly(bracket_linear(z, bracket(x, y)), t3_sign)
                
                res = add_polys(add_polys(t1, t2), t3)
                if res:
                    failures += 1
                    if failures < 5:
                        print(f"Jacobi failed for {x}, {y}, {z}: {res}")
                        
    return checks, failures

if __name__ == "__main__":
    for n in [1, 2, 3]:
        checks, fails = verify_structure(n)
        if fails == 0:
            print(f"n={n}: All {checks} Super Jacobi triples passed.")
        else:
            print(f"n={n}: FAILED {fails} out of {checks} Super Jacobi triples.")
