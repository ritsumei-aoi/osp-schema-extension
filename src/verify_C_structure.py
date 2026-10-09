import json
import sys
from collections import defaultdict

def verify_structure(n):
    with open(f"data/C_{n}_structure.json") as f:
        schema = json.load(f)
    
    basis = schema["basis"]["even"] + schema["basis"]["odd"]
    parity = schema["parity"]
    sc = schema["structure_constants"]
    
    # Build a fast lookup dictionary: (X, Y) -> dict(Z -> coeff)
    bracket = defaultdict(lambda: defaultdict(float))
    for entry in sc:
        x, y, z = entry["X"], entry["Y"], entry["Z"]
        c = float(entry["coeff"])
        bracket[(x, y)][z] += c
        
        if x != y:
            px = parity[x]
            py = parity[y]
            sign = -1 if (px * py == 1) else 1
            bracket[(y, x)][z] += -sign * c
        
    print(f"--- Verifying C({n+1}) ---")
    
    # 1. Anti-symmetry: [X, Y] = - (-1)^{p(X) p(Y)} [Y, X]
    # => [X, Y] + (-1)^{p(X) p(Y)} [Y, X] = 0
    anti_sym_errors = 0
    for x in basis:
        for y in basis:
            p_xy = parity[x] * parity[y]
            sign = -1 if p_xy == 1 else 1
            
            res_xy = bracket[(x, y)]
            res_yx = bracket[(y, x)]
            
            # Combine
            sum_z = defaultdict(float)
            for z, c in res_xy.items():
                sum_z[z] += c
            for z, c in res_yx.items():
                sum_z[z] += sign * c
                
            for z, c in sum_z.items():
                if abs(c) > 1e-7:
                    print(f"Anti-symmetry failed for {x}, {y} -> {z}: sum = {c}")
                    anti_sym_errors += 1
                    break
    
    print(f"Anti-symmetry errors: {anti_sym_errors}")
    
    def compute_bracket(X, Y):
        return bracket[(X, Y)]
    
    def bracket_linear(expr, Z):
        # expr is dict(W -> coeff)
        res = defaultdict(float)
        for W, c in expr.items():
            if W == "K":
                # K is central, [K, Z] = 0
                continue
            bwz = compute_bracket(W, Z)
            for out, cout in bwz.items():
                res[out] += c * cout
        return res
        
    # 2. Super Jacobi: (-1)^{p_x p_z} [X, [Y, Z]] + cyclic = 0
    # Equivalently: [X, [Y, Z]] = [[X, Y], Z] + (-1)^{p_x p_y} [Y, [X, Z]]
    jacobi_errors = 0
    for i, x in enumerate(basis):
        for j, y in enumerate(basis):
            for k, z in enumerate(basis):
                if k < j: continue # Symmetry reduces work
                
                # Compute LHS: [X, [Y, Z]]
                yz = compute_bracket(y, z)
                lhs = bracket_linear(yz, x) # Wait, bracket_linear takes (expr, Z) meaning [expr, Z]. So [Y, Z] is expr, then [expr, X]. But we want [X, [Y,Z]].
                # By anti-symmetry [X, W] = -(-1)^{p_X p_W} [W, X].
                
                # [A, [B, C]] = [[A, B], C] + (-1)^{pA pB} [B, [A, C]]
                # so: [X, [Y, Z]] - [[X, Y], Z] - (-1)^{pX pY} [Y, [X, Z]] = 0
                
                px, py, pz = parity[x], parity[y], parity[z]
                
                # term1 = [X, [Y, Z]]
                term1 = defaultdict(float)
                for w, c in compute_bracket(y, z).items():
                    if w != "K":
                        for out, cout in compute_bracket(x, w).items():
                            term1[out] += c * cout
                            
                # term2 = [[X, Y], Z]
                term2 = defaultdict(float)
                for w, c in compute_bracket(x, y).items():
                    if w != "K":
                        for out, cout in compute_bracket(w, z).items():
                            term2[out] += c * cout
                            
                # term3 = (-1)^{px py} [Y, [X, Z]]
                term3 = defaultdict(float)
                sign = -1 if (px * py == 1) else 1
                for w, c in compute_bracket(x, z).items():
                    if w != "K":
                        for out, cout in compute_bracket(y, w).items():
                            term3[out] += sign * c * cout
                            
                total = defaultdict(float)
                for w, c in term1.items(): total[w] += c
                for w, c in term2.items(): total[w] -= c
                for w, c in term3.items(): total[w] -= c
                
                for w, c in total.items():
                    if abs(c) > 1e-7:
                        if jacobi_errors == 0:
                            print(f"DEBUG: {x}, {y}, {z}")
                            print(f"term1: {dict(term1)}")
                            print(f"term2: {dict(term2)}")
                            print(f"term3: {dict(term3)}")
                        print(f"Jacobi failed for {x}, {y}, {z} -> {w}: sum = {c}")
                        jacobi_errors += 1
                        break
    
    print(f"Jacobi errors: {jacobi_errors}")
    return anti_sym_errors == 0 and jacobi_errors == 0

if __name__ == "__main__":
    all_passed = True
    for n in [1, 2, 3]:
        passed = verify_structure(n)
        if not passed:
            all_passed = False
    if all_passed:
        print("ALL PASSED")
        sys.exit(0)
    else:
        print("FAILED")
        sys.exit(1)
