import sympy as sp
import json

def run_verification(n):
    print(f"\n=======================================================")
    print(f"       Running Rigorous Verification for n = {n}       ")
    print(f"=======================================================")
    
    # 1. Define basis and indexing
    boson_coords = []
    for k in range(1, n + 1):
        boson_coords.append((k, '+'))
        boson_coords.append((k, '-'))
    num_bosons = 2 * n

    # gb parameters
    gb = {}
    gb_vars = []
    for sigma in ['+', '-']:
        for (k, s) in boson_coords:
            var = sp.Symbol(f"gb_{sigma}_{k}_{s}")
            gb[(sigma, k, s)] = var
            gb_vars.append(var)

    basis = []
    basis_type = []
    basis_parity = []
    
    # Even: J
    basis.append(('J',))
    basis_type.append('J')
    basis_parity.append(0)
    
    # Even: B(b_i, b_j) for i <= j
    for i in range(num_bosons):
        for j in range(i, num_bosons):
            basis.append(('B', boson_coords[i], boson_coords[j]))
            basis_type.append('B')
            basis_parity.append(0)
            
    # Odd: F(sigma, b_i)
    for sigma in ['+', '-']:
        for b in boson_coords:
            basis.append(('F', sigma, b))
            basis_type.append('F')
            basis_parity.append(1)

    dim_total = len(basis)
    dim_even = sum(1 for p in basis_parity if p == 0)
    dim_odd = sum(1 for p in basis_parity if p == 1)
    print(f"Dim even: {dim_even}, Dim odd: {dim_odd}, Dim total: {dim_total}")

    # Helper function to get index of B(b1, b2)
    def get_B_index(b1, b2):
        i1 = boson_coords.index(b1)
        i2 = boson_coords.index(b2)
        if i1 <= i2:
            return basis.index(('B', b1, b2))
        else:
            return basis.index(('B', b2, b1))
            
    def get_F_index(sigma, b):
        return basis.index(('F', sigma, b))
        
    def omega(b1, b2):
        # [b1, b2]: [b_{k,-}, b_{k,+}] = 1, [b_{k,+}, b_{k,-}] = -1
        if b1[0] == b2[0]:
            if b1[1] == '-' and b2[1] == '+':
                return 1
            elif b1[1] == '+' and b2[1] == '-':
                return -1
        return 0

    # 2. Compute C_{ij}^k (undeformed bracket [Z_i, Z_j]_0)
    C = {}
    for i in range(dim_total):
        for j in range(dim_total):
            C[(i, j)] = [sp.Rational(0)] * dim_total

    # Fill C:
    # [J, J] = 0
    # [J, B(b1, b2)] = 0
    # [J, F(sigma, b)]: [J, F(+, b)] = + F(+, b), [J, F(-, b)] = - F(-, b)
    for b in boson_coords:
        f_plus = get_F_index('+', b)
        f_minus = get_F_index('-', b)
        # [J, F+] = F+, [F+, J] = -F+
        C[(0, f_plus)][f_plus] += 1
        C[(f_plus, 0)][f_plus] -= 1
        # [J, F-] = -F-, [F-, J] = +F-
        C[(0, f_minus)][f_minus] -= 1
        C[(f_minus, 0)][f_minus] += 1

    # [B(b1, b2), B(b3, b4)]:
    # [ 1/2(b1 b2 + b2 b1), 1/2(b3 b4 + b4 b3) ]
    # = 1/2 [ omega(b2, b3) B(b1, b4) + omega(b2, b4) B(b1, b3) + omega(b1, b3) B(b2, b4) + omega(b1, b4) B(b2, b3) ]
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(1, dim_even):
            _, b3, b4 = basis[j]
            # Bracket of B(b1, b2) with B(b3, b4)
            # using [b1 b2, b3 b4] = b1 [b2, b3 b4] + [b1, b3 b4] b2
            # = b1 omega(b2,b3) b4 + b1 b3 omega(b2,b4) + omega(b1,b3) b4 b2 + b3 omega(b1,b4) b2
            # symmetrized:
            w23 = omega(b2, b3)
            w24 = omega(b2, b4)
            w13 = omega(b1, b3)
            w14 = omega(b1, b4)
            
            vec = [sp.Rational(0)] * dim_total
            if w23 != 0:
                idx = get_B_index(b1, b4)
                vec[idx] += sp.Rational(w23, 2) * (2 if b1 == b4 else 1) # Note: B(b,b) is b^2 = 1/2(b b + b b)
            if w24 != 0:
                idx = get_B_index(b1, b3)
                vec[idx] += sp.Rational(w24, 2) * (2 if b1 == b3 else 1)
            if w13 != 0:
                idx = get_B_index(b2, b4)
                vec[idx] += sp.Rational(w13, 2) * (2 if b2 == b4 else 1)
            if w14 != 0:
                idx = get_B_index(b2, b3)
                vec[idx] += sp.Rational(w14, 2) * (2 if b2 == b3 else 1)
            # Correct normalization:
            # Let's verify [B(b1,b2), B(b3,b4)]:
            # Standard: if B(b,b) = b^2, then [1/2 b+^2, 1/2 b-^2] = - H = - B(b+, b-)
            C[(i, j)] = vec

    # Let's adjust B definition so B(b,b) has standard normalization:
    # In our basis:
    # If b1 == b2, the element is B(b1, b1) = b1^2.
    # If b1 != b2, the element is B(b1, b2) = b1 b2 (symmetrized = 1/2(b1 b2 + b2 b1)).
    # Then:
    # [b1 b2, b3 b4] = w23 b1 b4 + w24 b1 b3 + w13 b4 b2 + w14 b3 b2
    # For any product u v of bosons, its projection to basis is:
    # if u == v: B(u, u)
    # if u != v: B(u, v) (since B(u,v) = 1/2(u v + v u) and u v = B(u,v) + 1/2 omega(u,v), scalar drops out)
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        factor_i = sp.Rational(1, 2) if b1 == b2 else sp.Rational(1) # basis element Z_i is (b1^2)/2 or b1 b2?
        # Let's take basis element to be:
        # if b1 == b2: Z_i = 1/2 b1^2
        # if b1 != b2: Z_i = 1/2(b1 b2 + b2 b1) = b1 b2 (mod scalar)
        pass

    # Let's use the exact commutator [Z_i, Z_j]:
    # Let's re-derive for general basis:
    # Even elements:
    # E_{b1, b2} = 1/2 (b1 b2 + b2 b1). (Note: for b1=b2, this is b1^2, so 1/2(b1^2 + b1^2) = b1^2. If we define Z = 1/2 b1^2 for b1=b2, or Z = b1 b2 for b1!=b2)
    # Let's define basis Z:
    # For all b1, b2 (i1 <= i2):
    # If i1 == i2: Z = 1/2 (b1)^2
    # If i1 < i2: Z = 1/2 (b1 b2 + b2 b1)
    # Then:
    # [1/2(b1 b2 + b2 b1), 1/2(b3 b4 + b4 b3)]
    # = 1/4 [ b1 [b2, b3 b4] + [b1, b3 b4] b2 + (1 <-> 2) ]
    # = 1/4 [ w23 (b1 b4 + b4 b1) + w24 (b1 b3 + b3 b1) + w13 (b2 b4 + b4 b2) + w14 (b2 b3 + b3 b2) + (1 <-> 2) ]
    # = 1/2 [ w23 (b1 b4 + b4 b1) + w24 (b1 b3 + b3 b1) + w13 (b2 b4 + b4 b2) + w14 (b2 b3 + b3 b2) ]
    # Notice: 1/2 (u v + v u) = Z_{u, v} if u != v, and 2 * Z_{u, u} if u == v!
    # So each term 1/2(u v + v u) is:
    # - if u != v: 1 * Z_{u, v}
    # - if u == v: 2 * Z_{u, u} (since Z_{u,u} = 1/2 u^2, so u^2 = 2 Z_{u,u}).
    
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(1, dim_even):
            _, b3, b4 = basis[j]
            w23 = omega(b2, b3)
            w24 = omega(b2, b4)
            w13 = omega(b1, b3)
            w14 = omega(b1, b4)
            
            vec = [sp.Rational(0)] * dim_total
            pairs = [(w23, b1, b4), (w24, b1, b3), (w13, b2, b4), (w14, b2, b3)]
            for w, u, v in pairs:
                if w != 0:
                    idx = get_B_index(u, v)
                    mult = 2 if u == v else 1
                    vec[idx] += sp.Rational(w * mult, 2)
            C[(i, j)] = vec

    # [B(b1, b2), F(sigma, b3)]:
    # [ 1/2(b1 b2 + b2 b1), a_sigma b3 ]
    # = a_sigma 1/2 [ b1 b2 + b2 b1, b3 ]
    # = a_sigma 1/2 [ b1 w23 + w13 b2 + b2 w13 + w23 b1 ]
    # = a_sigma [ w23 b1 + w13 b2 ]
    # = w23 F(sigma, b1) + w13 F(sigma, b2)
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(dim_even, dim_total):
            _, sigma, b3 = basis[j]
            w23 = omega(b2, b3)
            w13 = omega(b1, b3)
            
            vec = [sp.Rational(0)] * dim_total
            if w23 != 0:
                idx = get_F_index(sigma, b1)
                vec[idx] += w23
            if w13 != 0:
                idx = get_F_index(sigma, b2)
                vec[idx] += w13
            C[(i, j)] = vec
            # [F, B] = - [B, F]
            C[(j, i)] = [-x for x in vec]

    # [F(sigma1, b1), F(sigma2, b2)] (anticommutator):
    # { a_sigma1 b1, a_sigma2 b2 }
    # For sigma1 = sigma2: 0
    # For sigma1 = +, sigma2 = -:
    # { a_+ b1, a_- b2 } = 1/2(b1 b2 + b2 b1) + w12 J
    # Note: 1/2(b1 b2 + b2 b1) is 2 * Z_{b1, b1} if b1=b2, and 1 * Z_{b1, b2} if b1!=b2.
    # And { a_- b2, a_+ b1 } = { a_+ b1, a_- b2 }.
    # For sigma1 = -, sigma2 = +:
    # { a_- b1, a_+ b2 } = 1/2(b1 b2 + b2 b1) + w21 J = 1/2(b1 b2 + b2 b1) - w12 J.
    for i in range(dim_even, dim_total):
        _, sig1, b1 = basis[i]
        for j in range(dim_even, dim_total):
            _, sig2, b2 = basis[j]
            vec = [sp.Rational(0)] * dim_total
            if sig1 == '+' and sig2 == '-':
                w12 = omega(b1, b2)
                idx = get_B_index(b1, b2)
                mult = 2 if b1 == b2 else 1
                vec[idx] += mult
                vec[0] += w12 # coeff of J
            elif sig1 == '-' and sig2 == '+':
                w12 = omega(b1, b2)
                idx = get_B_index(b1, b2)
                mult = 2 if b1 == b2 else 1
                vec[idx] += mult
                vec[0] -= w12 # coeff of J
            C[(i, j)] = vec

    # Verify Jacobi for [ , ]_0:
    jacobi_errors = 0
    for i in range(dim_total):
        for j in range(dim_total):
            for k in range(dim_total):
                pi, pj, pk = basis_parity[i], basis_parity[j], basis_parity[k]
                t1 = [sum(C[(j,k)][m] * C[(i,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t2 = [sum(C[(k,i)][m] * C[(j,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t3 = [sum(C[(i,j)][m] * C[(k,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                s1, s2, s3 = (-1)**(pi * pk), (-1)**(pj * pi), (-1)**(pk * pj)
                tot = [s1 * t1[r] + s2 * t2[r] + s3 * t3[r] for r in range(dim_total)]
                if any(x != 0 for x in tot):
                    jacobi_errors += 1
    print(f"Jacobi identity check on undeformed bracket: {jacobi_errors} errors (0 expected)")

    # 3. Compute gamma_{ij}^k (inhomogeneous deformation cocycle)
    gamma = {}
    for i in range(dim_total):
        for j in range(dim_total):
            gamma[(i, j)] = [sp.Rational(0)] * dim_total

    # Formulas for gamma:
    # 1. Even-Even:
    # gamma(J, J) = 0
    # gamma(B, B) = 0
    # gamma(J, B(b1, b2)) = 1/2 [ gb_{-, b1} F(+, b2) + gb_{+, b1} F(-, b2) + gb_{-, b2} F(+, b1) + gb_{+, b2} F(-, b1) ]
    for j in range(1, dim_even):
        _, b1, b2 = basis[j]
        vec = [sp.Rational(0)] * dim_total
        
        idx_p2 = get_F_index('+', b2)
        idx_m2 = get_F_index('-', b2)
        idx_p1 = get_F_index('+', b1)
        idx_m1 = get_F_index('-', b1)
        
        gb_m1 = gb[('-', b1[0], b1[1])]
        gb_p1 = gb[('+', b1[0], b1[1])]
        gb_m2 = gb[('-', b2[0], b2[1])]
        gb_p2 = gb[('+', b2[0], b2[1])]
        
        vec[idx_p2] += sp.Rational(1, 2) * gb_m1
        vec[idx_m2] += sp.Rational(1, 2) * gb_p1
        vec[idx_p1] += sp.Rational(1, 2) * gb_m2
        vec[idx_m1] += sp.Rational(1, 2) * gb_p2
        
        gamma[(0, j)] = vec
        gamma[(j, 0)] = [-x for x in vec] # gamma is graded skew-symmetric

    # 2. Even-Odd:
    # gamma(J, F(+, b)) = gb_{ik, +} J
    # gamma(J, F(-, b)) = - gb_{ik, -} J
    for j in range(dim_even, dim_total):
        _, sigma, b = basis[j]
        vec = [sp.Rational(0)] * dim_total
        if sigma == '+':
            vec[0] += gb[('+', b[0], b[1])]
        else:
            vec[0] -= gb[('-', b[0], b[1])]
        gamma[(0, j)] = vec
        gamma[(j, 0)] = [-x for x in vec]

    # gamma(B(b1, b2), F(sigma, b3)):
    # = - 1/2 [ gb_{sigma, b2} (b1 b3 symmetrized) + gb_{sigma, b1} (b2 b3 symmetrized) ]
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(dim_even, dim_total):
            _, sigma, b3 = basis[j]
            vec = [sp.Rational(0)] * dim_total
            
            gb_s2 = gb[(sigma, b2[0], b2[1])]
            gb_s1 = gb[(sigma, b1[0], b1[1])]
            
            idx13 = get_B_index(b1, b3)
            mult13 = 2 if b1 == b3 else 1
            idx23 = get_B_index(b2, b3)
            mult23 = 2 if b2 == b3 else 1
            
            vec[idx13] -= sp.Rational(mult13, 2) * gb_s2
            vec[idx23] -= sp.Rational(mult23, 2) * gb_s1
            
            gamma[(i, j)] = vec
            gamma[(j, i)] = [-x for x in vec]

    # 3. Odd-Odd:
    # gamma(F(sigma1, b1), F(sigma2, b2)):
    # = - [ gb_{sigma2, b1} F(sigma1, b2) + gb_{sigma1, b2} F(sigma2, b1) ]
    for i in range(dim_even, dim_total):
        _, sig1, b1 = basis[i]
        for j in range(dim_even, dim_total):
            _, sig2, b2 = basis[j]
            vec = [sp.Rational(0)] * dim_total
            
            gb2_1 = gb[(sig2, b1[0], b1[1])]
            gb1_2 = gb[(sig1, b2[0], b2[1])]
            
            idx_sig1_b2 = get_F_index(sig1, b2)
            idx_sig2_b1 = get_F_index(sig2, b1)
            
            vec[idx_sig1_b2] -= gb2_1
            vec[idx_sig2_b1] -= gb1_2
            
            gamma[(i, j)] = vec

    print("Inhomogeneous 2-cocycle gamma computed successfully.")

    # 4. Set up Coboundary System gamma == delta f
    phi = {}
    phi_vars = []
    for j in range(dim_total):
        for i in range(dim_total):
            if basis_parity[i] != basis_parity[j]:
                var = sp.Symbol(f"phi_{i}_{j}")
                phi[(i, j)] = var
                phi_vars.append(var)
            else:
                phi[(i, j)] = sp.Rational(0)

    # Coboundary formula:
    # (\delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    equations = []
    for i in range(dim_total):
        for j in range(dim_total):
            pi = basis_parity[i]
            pj = basis_parity[j]
            for k in range(dim_total):
                delta_f_ijk = (
                    (-1)**pi * sum(phi[(m, j)] * C[(i, m)][k] for m in range(dim_total))
                    - (-1)**((pi + 1) * pj) * sum(phi[(m, i)] * C[(j, m)][k] for m in range(dim_total))
                    - sum(C[(i, j)][m] * phi[(k, m)] for m in range(dim_total))
                )
                eq = delta_f_ijk - gamma[(i, j)][k]
                eq_simp = sp.simplify(eq)
                if eq_simp != 0:
                    equations.append(eq_simp)

    print(f"Total coboundary equations: {len(equations)}")
    
    # Solve linear system for phi_vars:
    sol = sp.solve(equations, phi_vars)
    print(f"Linear solver determined {len(sol)} phi variables.")
    
    # Check residuals
    residuals = []
    for eq in equations:
        res = sp.simplify(eq.subs(sol))
        if res != 0:
            residuals.append(res)
            
    print(f"Residual equations depending on gb: {len(residuals)}")
    
    if len(residuals) == 0:
        print(">>> SUCCESS: System is solved for ALL gb parameters without any constraints!")
        print(">>> CONCLUSION: Inhomogeneous deformation gamma_gb is ALWAYS a coboundary (TRIVIAL).")
        trivial = True
    else:
        print("Residuals exist! Checking gb constraints:")
        gb_sol = sp.solve(residuals, gb_vars)
        print("gb constraints:", gb_sol)
        trivial = False

    return {
        "n": n,
        "dim_even": dim_even,
        "dim_odd": dim_odd,
        "dim_total": dim_total,
        "num_gb": len(gb_vars),
        "num_phi": len(phi_vars),
        "num_equations": len(equations),
        "residuals_count": len(residuals),
        "trivial_for_all_gb": trivial,
        "phi_solution": {str(k): str(v) for k, v in sol.items()}
    }

all_res = {}
for n in [1, 2, 3]:
    all_res[f"n={n}"] = run_verification(n)

with open("verification_results.json", "w") as f:
    json.dump(all_res, f, indent=2)

print("\nSaved all verification results to verification_results.json")
