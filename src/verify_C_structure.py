import json
import os
import sys

def verify_algebra(n):
    path = f'data/C_{n}_structure.json'
    with open(path, 'r') as f:
        data = json.load(f)
        
    parity = data['parity']
    struct = data['structure_constants']
    basis = data['basis']['odd'] + data['basis']['even']
    
    def get_bracket(x, y):
        key = f"{x},{y}"
        if key in struct:
            return struct[key]
        return {}

    def add_expr(expr1, expr2, coef=1.0):
        res = dict(expr1)
        for k, v in expr2.items():
            res[k] = res.get(k, 0.0) + v * coef
            if abs(res[k]) < 1e-9:
                del res[k]
        return res
        
    def mult_expr(expr, coef):
        if coef == 0:
            return {}
        return {k: v * coef for k, v in expr.items() if v != 0}

    # Verify anti-symmetry
    for x in basis:
        for y in basis:
            br_xy = get_bracket(x, y)
            br_yx = get_bracket(y, x)
            
            pX = parity.get(x, 0)
            pY = parity.get(y, 0)
            sign = -1 if pX == 1 and pY == 1 else 1
            
            check = add_expr(br_xy, br_yx, sign)
            if check:
                print(f"Anti-symmetry failed for {x}, {y}: {check}")
                return False

    def bracket_with_expr(x, expr):
        res = {}
        for g, c in expr.items():
            res = add_expr(res, get_bracket(x, g), c)
        return res

    # Verify Super Jacobi
    # Graded Jacobi identity:
    # [X, [Y, Z]] = [[X, Y], Z] + (-1)^{pX pY} [Y, [X, Z]]
    # => [X, [Y, Z]] - [[X, Y], Z] - (-1)^{pX pY} [Y, [X, Z]] = 0
    for x in basis:
        pX = parity.get(x, 0)
        for y in basis:
            pY = parity.get(y, 0)
            for z in basis:
                pZ = parity.get(z, 0)
                
                br_yz = get_bracket(y, z)
                term1 = bracket_with_expr(x, br_yz)  # [X, [Y, Z]]
                
                br_xy = get_bracket(x, y)
                term2 = bracket_with_expr(z, br_xy)  # [Z, [X, Y]]
                # [[X, Y], Z] = - (-1)^{p([X, Y]) p(Z)} [Z, [X, Y]]
                # p([X, Y]) = (pX + pY) % 2
                p_xy = (pX + pY) % 2
                sign_xy_z = -1 if p_xy == 1 and pZ == 1 else 1
                term2_bracket = mult_expr(term2, -sign_xy_z)
                
                br_xz = get_bracket(x, z)
                term3 = bracket_with_expr(y, br_xz)  # [Y, [X, Z]]
                sign_x_y = -1 if pX == 1 and pY == 1 else 1
                term3_bracket = mult_expr(term3, sign_x_y)
                
                # We want term1 - term2_bracket - term3_bracket == 0
                res = add_expr(term1, term2_bracket, -1.0)
                res = add_expr(res, term3_bracket, -1.0)
                
                if res:
                    print(f"Jacobi failed for {x}, {y}, {z}: {res}")
                    return False
                    
    return True

if __name__ == '__main__':
    all_passed = True
    for n in [1, 2, 3]:
        print(f"Verifying C({n+1})...")
        if verify_algebra(n):
            print(f"C({n+1}) verified successfully.")
        else:
            print(f"C({n+1}) verification failed.")
            all_passed = False
    
    if not all_passed:
        sys.exit(1)
