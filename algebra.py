import sympy as sp
import json
import sys

def solve_for_n(n):
    # Basis of g:
    # A = a+a-
    # B_{j,s1, k,s2} = b_j^s1 b_k^s2 (j <= k, if j==k then s1 >= s2)
    # O_{sigma, j, s} = a_1^sigma b_j^s

    # Let's map pairs to flat indices
    even_basis = [("A",)]
    for j in range(1, n+1):
        for k in range(j, n+1):
            for s1 in [1, -1]:
                for s2 in [1, -1]:
                    if j == k and s1 < s2: continue
                    even_basis.append(("B", j, s1, k, s2))
                    
    odd_basis = []
    for sigma in [1, -1]:
        for j in range(1, n+1):
            for s in [1, -1]:
                odd_basis.append(("O", sigma, j, s))
                
    basis = even_basis + odd_basis
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    dim = len(basis)
    
    b_idx = {b: i for i, b in enumerate(basis)}
    
    def get_B(j, s1, k, s2):
        if j > k:
            return get_B(k, s2, j, s1)
        if j == k and s1 < s2:
            return get_B(j, s2, k, s1)
        return ("B", j, s1, k, s2)
        
    def comm_b(j, s1, k, s2):
        # [b_j^s1, b_k^s2] = delta_{jk} (s1 - s2)/2 ?
        # [b_j^-, b_j^+] = 1 => b^- b^+ - b^+ b^- = 1.
        if j != k: return 0
        if s1 == s2: return 0
        if s1 == -1 and s2 == 1: return 1
        if s1 == 1 and s2 == -1: return -1
        return 0
        
    # We will write everything as dictionaries {basis_index: coeff}
    def bracket(i1, i2):
        b1 = basis[i1]
        b2 = basis[i2]
        res = {}
        
        def add(idx, c):
            if c != 0: res[idx] = res.get(idx, 0) + c

        if b1[0] == "A" and b2[0] == "A":
            pass # 0
        elif b1[0] == "A" and b2[0] == "B":
            pass # 0
        elif b1[0] == "B" and b2[0] == "A":
            pass # 0
        elif b1[0] == "A" and b2[0] == "O":
            # [A, O^sigma] = sigma O^sigma
            sigma = b2[1]
            add(i2, sigma)
        elif b1[0] == "O" and b2[0] == "A":
            sigma = b1[1]
            add(i1, -sigma)
            
        elif b1[0] == "B" and b2[0] == "B":
            # [b1b2, b3b4] = b1[b2,b3]b4 + b1b3[b2,b4] + [b1,b3]b2b4 + b3[b1,b4]b2
            _, j1, s1, j2, s2 = b1
            _, j3, s3, j4, s4 = b2
            
            # [XY, ZW] = X[Y, Z]W + X Z [Y, W] + [X, Z] Y W + Z [X, W] Y
            # Using: X Y Z W - Z W X Y = X (Y Z - Z Y) W + X Z Y W - Z W X Y
            # = X [Y,Z] W + (X Z - Z X) Y W + Z X Y W - Z W X Y
            # = X [Y,Z] W + [X, Z] Y W + Z (X Y - W X) ... wait.
            # Standard formula: [AB, CD] = A[B,C]D + C[A,D]B + [A,C]BD + CA[B,D] is messy.
            # Easier: [AB, CD] = A[B,C]D + A C [B,D] + [A,C]DB + C[A,D]B
            c23 = comm_b(j2, s2, j3, s3)
            c24 = comm_b(j2, s2, j4, s4)
            c13 = comm_b(j1, s1, j3, s3)
            c14 = comm_b(j1, s1, j4, s4)
            
            if c23: add(b_idx[get_B(j1, s1, j4, s4)], c23)
            if c24: add(b_idx[get_B(j1, s1, j3, s3)], c24)
            if c13: add(b_idx[get_B(j4, s4, j2, s2)], c13)
            if c14: add(b_idx[get_B(j3, s3, j2, s2)], c14)
            
        elif b1[0] == "B" and b2[0] == "O":
            # [B, a b_k] = a [B, b_k]
            _, j1, s1, j2, s2 = b1
            _, sigma, j3, s3 = b2
            c23 = comm_b(j2, s2, j3, s3)
            c13 = comm_b(j1, s1, j3, s3)
            if c23: add(b_idx[("O", sigma, j1, s1)], c23)
            if c13: add(b_idx[("O", sigma, j2, s2)], c13)
            
        elif b1[0] == "O" and b2[0] == "B":
            # [O, B] = -[B, O]
            res_opp = bracket(i2, i1)
            for k, v in res_opp.items(): add(k, -v)
            
        elif b1[0] == "O" and b2[0] == "O":
            # {a1 b1, a2 b2} = a1 a2 b1 b2 + a2 a1 b2 b1
            _, sig1, j1, s1 = b1
            _, sig2, j2, s2 = b2
            if sig1 == sig2:
                pass # 0
            else:
                # a1 a2 b1 b2 + a2 a1 b2 b1
                # sig1 != sig2, so one is +, one is -
                c = comm_b(j1, s1, j2, s2)
                if sig1 == 1 and sig2 == -1:
                    # a+ a- b1 b2 + a- a+ b2 b1 = A b1 b2 + (1-A) b2 b1
                    # = A [b1, b2] + b2 b1 = c A + b2 b1
                    add(0, c)
                    add(b_idx[get_B(j2, s2, j1, s1)], 1)
                else:
                    # a- a+ b1 b2 + a+ a- b2 b1 = (1-A) b1 b2 + A b2 b1
                    # = b1 b2 + A [b2, b1] = b1 b2 - c A
                    add(0, -c)
                    add(b_idx[get_B(j1, s1, j2, s2)], 1)
        return res

    def get_gb(sig, j, s):
        return f"gb_{'+' if sig==1 else '-'}_{j}_{'+' if s==1 else '-'}"

    def gamma(i1, i2):
        b1 = basis[i1]
        b2 = basis[i2]
        res = {}
        
        def add(idx, var_name, coeff):
            if coeff != 0:
                res[idx] = res.get(idx, []) + [(var_name, coeff)]

        if b1[0] == "A" and b2[0] == "A":
            pass
        elif b1[0] == "B" and b2[0] == "B":
            pass
        elif b1[0] == "A" and b2[0] == "O":
            # gamma(A, O^sigma_j^s) = sigma gb_{sigma, j, s} A
            sig, j, s = b2[1], b2[2], b2[3]
            add(0, get_gb(sig, j, s), sig)
        elif b1[0] == "O" and b2[0] == "A":
            sig, j, s = b1[1], b1[2], b1[3]
            add(0, get_gb(sig, j, s), -sig)
        elif b1[0] == "B" and b2[0] == "O":
            # gamma(B, O) = - gb_{sig, k, s1} b_l^s2 b_j^s - gb_{sig, l, s2} b_k^s1 b_j^s
            _, k, s1, l, s2 = b1
            sig, j, s = b2[1], b2[2], b2[3]
            add(b_idx[get_B(l, s2, j, s)], get_gb(sig, k, s1), -1)
            add(b_idx[get_B(k, s1, j, s)], get_gb(sig, l, s2), -1)
        elif b1[0] == "O" and b2[0] == "B":
            _, k, s1, l, s2 = b2
            sig, j, s = b1[1], b1[2], b1[3]
            add(b_idx[get_B(l, s2, j, s)], get_gb(sig, k, s1), 1)
            add(b_idx[get_B(k, s1, j, s)], get_gb(sig, l, s2), 1)
        elif b1[0] == "O" and b2[0] == "O":
            # gamma(O1, O2) = - gb_{sig2, k, s1} O^{sig1, s2}_l - gb_{sig1, l, s2} O^{sig2, s1}_k
            sig1, k, s1 = b1[1], b1[2], b1[3]
            sig2, l, s2 = b2[1], b2[2], b2[3]
            add(b_idx[("O", sig1, l, s2)], get_gb(sig2, k, s1), -1)
            add(b_idx[("O", sig2, k, s1)], get_gb(sig1, l, s2), -1)
            
        return res

    # Construct the linear system
    # Unknowns: 
    # gb_vars (4n)
    # f_matrix (dim x dim, but f is odd, so only even->odd and odd->even are non-zero)
    # Total unknowns = 4n + dim_even * dim_odd * 2
    
    gb_vars = []
    for sig in [1, -1]:
        for j in range(1, n+1):
            for s in [1, -1]:
                gb_vars.append(get_gb(sig, j, s))
                
    f_vars = []
    for i in range(dim_even):
        for j in range(dim_even, dim):
            f_vars.append(f"f_{i}_{j}") # f(even) = odd
    for i in range(dim_even, dim):
        for j in range(dim_even):
            f_vars.append(f"f_{i}_{j}") # f(odd) = even

    all_vars = gb_vars + f_vars
    var_idx = {v: i for i, v in enumerate(all_vars)}
    
    # delta f(X, Y) = (-1)^p(X) [X, f(Y)] - (-1)^{(pX+1)pY} [Y, f(X)] - f([X, Y])
    # For each pair (i1, i2) with i1 <= i2, we equate delta f(X, Y) and gamma(X, Y)
    
    equations = []
    
    # We will build a matrix eq_matrix where each row is an equation
    for i1 in range(dim):
        for i2 in range(i1, dim):
            # We want: delta f(i1, i2) - gamma(i1, i2) == 0
            
            p1 = 0 if i1 < dim_even else 1
            p2 = 0 if i2 < dim_even else 1
            
            # Since gamma maps (even, even) -> even, (odd, odd) -> odd, (even, odd) -> even
            # Wait, gamma(even, odd) is purely bosonic (even).
            # So gamma always has parity p1 + p2.
            # delta f also has parity p1 + p2.
            
            for k in range(dim):
                eq = [0] * len(all_vars)
                
                # add -gamma
                g = gamma(i1, i2)
                if k in g:
                    for var_name, coeff in g[k]:
                        eq[var_idx[var_name]] -= coeff
                        
                # add delta f
                # 1. (-1)^p1 [X, f(Y)]
                # f(Y) = sum_m f_{i2}_{m} basis_m
                sign1 = 1 if p1 == 0 else -1
                for m in range(dim):
                    if (i2 < dim_even and m >= dim_even) or (i2 >= dim_even and m < dim_even):
                        f_var = f"f_{i2}_{m}"
                        br = bracket(i1, m)
                        if k in br:
                            eq[var_idx[f_var]] += sign1 * br[k]
                            
                # 2. - (-1)^{(p1+1)p2} [Y, f(X)]
                sign2 = -1 if ((p1+1)*p2)%2 == 0 else 1
                for m in range(dim):
                    if (i1 < dim_even and m >= dim_even) or (i1 >= dim_even and m < dim_even):
                        f_var = f"f_{i1}_{m}"
                        br = bracket(i2, m)
                        if k in br:
                            eq[var_idx[f_var]] += sign2 * br[k]
                            
                # 3. - f([X, Y])
                br_xy = bracket(i1, i2)
                for m, coeff in br_xy.items():
                    # - coeff * f(basis_m)
                    # f(basis_m) has component in basis_k if (m, k) is a valid f mapping
                    if (m < dim_even and k >= dim_even) or (m >= dim_even and k < dim_even):
                        f_var = f"f_{m}_{k}"
                        eq[var_idx[f_var]] -= coeff
                        
                if any(v != 0 for v in eq):
                    equations.append(eq)

    print(f"n={n}: Variables = {len(all_vars)}, Equations = {len(equations)}")
    
    # We want to know if there is a solution where some gb variables are NON-ZERO.
    # To do this, we compute the nullspace of the equations matrix.
    # We will use sympy to do rref or find nullspace.
    mat = sp.Matrix(equations)
    nullspace = mat.nullspace()
    
    print(f"Nullspace dimension: {len(nullspace)}")
    gb_solutions = []
    
    for vec in nullspace:
        # Check if any gb part is non-zero
        gb_part = vec[:4*n]
        if any(v != 0 for v in gb_part):
            gb_solutions.append(vec)
            
    if len(gb_solutions) > 0:
        print("FOUND NON-TRIVIAL DEFORMATION!")
        for vec in gb_solutions:
            print(vec[:4*n])
    else:
        print("ALL DEFORMATIONS ARE TRIVIAL (gb must be 0) OR NO SOLUTION EXISTS.")

if __name__ == "__main__":
    solve_for_n(1)
    solve_for_n(2)
    solve_for_n(3)
