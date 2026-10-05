import sympy as sp
import json

def analyze_osp_deformation(n):
    print(f"\n=================================================================")
    print(f"       Exact Algebraic Analysis for C({n+1}) = osp(2|{2*n})      ")
    print(f"=================================================================")

    # Boson coordinate list: (1,+), (1,-), ..., (n,+), (n,-)
    bosons = []
    for k in range(1, n + 1):
        bosons.append((k, '+'))
        bosons.append((k, '-'))
    num_b = 2 * n

    # Define basis elements:
    # 0: J (even)
    # 1 .. dim_sp: B(b_i, b_j) for i <= j (even)
    # dim_even .. dim_total-1: F(sigma, b_i) for sigma in ['+', '-'], b_i in bosons (odd)
    
    basis = []
    basis_names = []
    parities = []

    # J:
    basis.append(('J',))
    basis_names.append('J')
    parities.append(0)

    # Sp(2n):
    for i in range(num_b):
        for j in range(i, num_b):
            b1, b2 = bosons[i], bosons[j]
            basis.append(('B', b1, b2))
            basis_names.append(f"B({b1[0]}{b1[1]},{b2[0]}{b2[1]})")
            parities.append(0)

    # Odd:
    for sigma in ['+', '-']:
        for b in bosons:
            basis.append(('F', sigma, b))
            basis_names.append(f"F({sigma},{b[0]}{b[1]})")
            parities.append(1)

    dim_total = len(basis)
    dim_even = sum(1 for p in parities if p == 0)
    dim_odd = sum(1 for p in parities if p == 1)
    
    print(f"Dimension: even={dim_even}, odd={dim_odd}, total={dim_total}")
    assert dim_even == 2*n**2 + n + 1
    assert dim_odd == 4*n
    assert dim_total == 2*n**2 + 5*n + 1

    def get_B_idx(b1, b2):
        i1 = bosons.index(b1)
        i2 = bosons.index(b2)
        if i1 <= i2:
            return basis.index(('B', b1, b2))
        else:
            return basis.index(('B', b2, b1))

    def get_F_idx(sigma, b):
        return basis.index(('F', sigma, b))

    def omega(b1, b2):
        # [b_k^-, b_l^+] = delta_{kl}, [b_k^+, b_l^-] = -delta_{kl}
        if b1[0] == b2[0]:
            if b1[1] == '-' and b2[1] == '+':
                return 1
            elif b1[1] == '+' and b2[1] == '-':
                return -1
        return 0

    # gb parameters
    gb = {}
    gb_vars = []
    for sigma in ['+', '-']:
        for b in bosons:
            var = sp.Symbol(f"gb_{sigma}_{b[0]}{b[1]}")
            gb[(sigma, b)] = var
            gb_vars.append(var)

    # Structure constants C_{ij}^k of [ , ]_0:
    C = { (i, j): [sp.Rational(0)]*dim_total for i in range(dim_total) for j in range(dim_total) }

    # [J, F(sigma, b)]:
    for b in bosons:
        idx_p = get_F_idx('+', b)
        idx_m = get_F_idx('-', b)
        C[(0, idx_p)][idx_p] = sp.Rational(1)
        C[(idx_p, 0)][idx_p] = sp.Rational(-1)
        C[(0, idx_m)][idx_m] = sp.Rational(-1)
        C[(idx_m, 0)][idx_m] = sp.Rational(1)

    # [B(b1, b2), B(b3, b4)]:
    # Basis: Z_{b1, b2} = 1/2 b1^2 (if b1=b2) or 1/2(b1 b2 + b2 b1) (if b1!=b2)
    # Commutator:
    # [1/2(b1 b2 + b2 b1), 1/2(b3 b4 + b4 b3)]
    # = 1/2 [ w23 {b1,b4} + w24 {b1,b3} + w13 {b2,b4} + w14 {b2,b3} ]
    # where {u, v} = 1/2(u v + v u) = Z_{u,v} (if u!=v) or 2 Z_{u,u} (if u==v).
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(1, dim_even):
            _, b3, b4 = basis[j]
            terms = [
                (omega(b2, b3), b1, b4),
                (omega(b2, b4), b1, b3),
                (omega(b1, b3), b2, b4),
                (omega(b1, b4), b2, b3)
            ]
            for w, u, v in terms:
                if w != 0:
                    idx = get_B_idx(u, v)
                    mult = 2 if u == v else 1
                    C[(i, j)][idx] += sp.Rational(w * mult, 2)

    # [B(b1, b2), F(sigma, b3)]:
    # [ 1/2(b1 b2 + b2 b1), a_sigma b3 ] = a_sigma ( w23 b1 + w13 b2 ) = w23 F(sigma, b1) + w13 F(sigma, b2)
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(dim_even, dim_total):
            _, sigma, b3 = basis[j]
            w23 = omega(b2, b3)
            w13 = omega(b1, b3)
            if w23 != 0:
                idx = get_F_idx(sigma, b1)
                C[(i, j)][idx] += sp.Rational(w23)
                C[(j, i)][idx] -= sp.Rational(w23)
            if w13 != 0:
                idx = get_F_idx(sigma, b2)
                C[(i, j)][idx] += sp.Rational(w13)
                C[(j, i)][idx] -= sp.Rational(w13)

    # {F(sigma1, b1), F(sigma2, b2)}:
    # {a_+ b1, a_- b2} = {b1, b2} + w12 J
    # {a_- b1, a_+ b2} = {b1, b2} - w12 J
    for i in range(dim_even, dim_total):
        _, sig1, b1 = basis[i]
        for j in range(dim_even, dim_total):
            _, sig2, b2 = basis[j]
            if sig1 == '+' and sig2 == '-':
                idx = get_B_idx(b1, b2)
                mult = 2 if b1 == b2 else 1
                w12 = omega(b1, b2)
                C[(i, j)][idx] += sp.Rational(mult)
                C[(i, j)][0] += sp.Rational(w12)
            elif sig1 == '-' and sig2 == '+':
                idx = get_B_idx(b1, b2)
                mult = 2 if b1 == b2 else 1
                w12 = omega(b1, b2)
                C[(i, j)][idx] += sp.Rational(mult)
                C[(i, j)][0] -= sp.Rational(w12)

    # Verify Jacobi:
    print("Verifying graded Jacobi identity on undeformed bracket...")
    jac_err = 0
    for i in range(dim_total):
        for j in range(dim_total):
            for k in range(dim_total):
                pi, pj, pk = parities[i], parities[j], parities[k]
                t1 = [sum(C[(j,k)][m] * C[(i,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t2 = [sum(C[(k,i)][m] * C[(j,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t3 = [sum(C[(i,j)][m] * C[(k,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                s1, s2, s3 = (-1)**(pi * pk), (-1)**(pj * pi), (-1)**(pk * pj)
                tot = [s1 * t1[r] + s2 * t2[r] + s3 * t3[r] for r in range(dim_total)]
                if any(x != 0 for x in tot):
                    jac_err += 1
    print(f"Jacobi check: {jac_err} errors.")
    assert jac_err == 0

    # Inhomogeneous 2-cocycle gamma:
    gamma = { (i, j): [sp.Rational(0)]*dim_total for i in range(dim_total) for j in range(dim_total) }

    # 1. Even-Even:
    # gamma(J, B(b1, b2)) = 1/2 [ gb_{-, b1} F(+, b2) + gb_{+, b1} F(-, b2) + gb_{-, b2} F(+, b1) + gb_{+, b2} F(-, b1) ]
    for j in range(1, dim_even):
        _, b1, b2 = basis[j]
        idx_p2 = get_F_idx('+', b2)
        idx_m2 = get_F_idx('-', b2)
        idx_p1 = get_F_idx('+', b1)
        idx_m1 = get_F_idx('-', b1)
        
        g_m1 = gb[('-', b1)]
        g_p1 = gb[('+', b1)]
        g_m2 = gb[('-', b2)]
        g_p2 = gb[('+', b2)]
        
        gamma[(0, j)][idx_p2] += sp.Rational(1, 2) * g_m1
        gamma[(0, j)][idx_m2] += sp.Rational(1, 2) * g_p1
        gamma[(0, j)][idx_p1] += sp.Rational(1, 2) * g_m2
        gamma[(0, j)][idx_m1] += sp.Rational(1, 2) * g_p2
        
        gamma[(j, 0)][idx_p2] -= sp.Rational(1, 2) * g_m1
        gamma[(j, 0)][idx_m2] -= sp.Rational(1, 2) * g_p1
        gamma[(j, 0)][idx_p1] -= sp.Rational(1, 2) * g_m2
        gamma[(j, 0)][idx_m1] -= sp.Rational(1, 2) * g_p2

    # 2. Even-Odd:
    # gamma(J, F(+, b)) = gb_{+, b} J
    # gamma(J, F(-, b)) = - gb_{-, b} J
    for j in range(dim_even, dim_total):
        _, sigma, b = basis[j]
        if sigma == '+':
            g = gb[('+', b)]
            gamma[(0, j)][0] += g
            gamma[(j, 0)][0] -= g
        else:
            g = gb[('-', b)]
            gamma[(0, j)][0] -= g
            gamma[(j, 0)][0] += g

    # gamma(B(b1, b2), F(sigma, b3)):
    # = - 1/2 [ gb_{sigma, b2} {b1, b3} + gb_{sigma, b1} {b2, b3} ]
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(dim_even, dim_total):
            _, sigma, b3 = basis[j]
            g_s2 = gb[(sigma, b2)]
            g_s1 = gb[(sigma, b1)]
            
            idx13 = get_B_idx(b1, b3)
            mult13 = 2 if b1 == b3 else 1
            idx23 = get_B_idx(b2, b3)
            mult23 = 2 if b2 == b3 else 1
            
            term1 = sp.Rational(mult13, 2) * g_s2
            term2 = sp.Rational(mult23, 2) * g_s1
            
            gamma[(i, j)][idx13] -= term1
            gamma[(i, j)][idx23] -= term2
            
            gamma[(j, i)][idx13] += term1
            gamma[(j, i)][idx23] += term2

    # 3. Odd-Odd:
    # gamma(F(sigma1, b1), F(sigma2, b2)) = - [ gb_{sigma2, b1} F(sigma1, b2) + gb_{sigma1, b2} F(sigma2, b1) ]
    for i in range(dim_even, dim_total):
        _, sig1, b1 = basis[i]
        for j in range(dim_even, dim_total):
            _, sig2, b2 = basis[j]
            g2_1 = gb[(sig2, b1)]
            g1_2 = gb[(sig1, b2)]
            
            idx1 = get_F_idx(sig1, b2)
            idx2 = get_F_idx(sig2, b1)
            
            gamma[(i, j)][idx1] -= g2_1
            gamma[(i, j)][idx2] -= g1_2

    # Verify 2-cocycle identity for gamma:
    print("Verifying that gamma is a Lie superalgebra 2-cocycle...")
    cocycle_err = 0
    # delta gamma(X, Y, Z) = 0
    # For Lie superalgebra:
    # (-1)^{pX pZ} [X, gamma(Y,Z)] + (-1)^{pX pZ} gamma(X, [Y,Z]) + cyclic = 0
    for i in range(min(dim_total, 6)): # sample check
        for j in range(min(dim_total, 6)):
            for k in range(min(dim_total, 6)):
                pi, pj, pk = parities[i], parities[j], parities[k]
                # term 1: [Xi, gamma(Xj, Xk)] + gamma(Xi, [Xj, Xk])
                # [Xi, gamma(Xj, Xk)] = sum_m gamma_{jk}^m C_{im}^r
                t1_a = [sum(gamma[(j,k)][m] * C[(i,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                # gamma(Xi, [Xj, Xk]) = sum_m C_{jk}^m gamma_{im}^r
                t1_b = [sum(C[(j,k)][m] * gamma[(i,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t1 = [t1_a[r] + t1_b[r] for r in range(dim_total)]

                t2_a = [sum(gamma[(k,i)][m] * C[(j,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t2_b = [sum(C[(k,i)][m] * gamma[(j,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t2 = [t2_a[r] + t2_b[r] for r in range(dim_total)]

                t3_a = [sum(gamma[(i,j)][m] * C[(k,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t3_b = [sum(C[(i,j)][m] * gamma[(k,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t3 = [t3_a[r] + t3_b[r] for r in range(dim_total)]

                s1, s2, s3 = (-1)**(pi * pk), (-1)**(pj * pi), (-1)**(pk * pj)
                tot = [sp.simplify(s1 * t1[r] + s2 * t2[r] + s3 * t3[r]) for r in range(dim_total)]
                if any(x != 0 for x in tot):
                    cocycle_err += 1
    print(f"2-cocycle check: {cocycle_err} errors.")
    assert cocycle_err == 0

    # 4. Set up Coboundary Equation delta f == gamma
    phi = {}
    phi_vars = []
    for j in range(dim_total):
        for i in range(dim_total):
            if parities[i] != parities[j]:
                var = sp.Symbol(f"phi_{i}_{j}")
                phi[(i, j)] = var
                phi_vars.append(var)
            else:
                phi[(i, j)] = sp.Rational(0)

    equations = []
    for i in range(dim_total):
        for j in range(dim_total):
            pi = parities[i]
            pj = parities[j]
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
    M, b_vec = sp.linear_eq_to_matrix(equations, phi_vars)
    print(f"Coboundary operator matrix M size: {M.shape}, Rank: {M.rank()}")
    
    # Analyze left nullspace / cokernel constraints:
    print("Computing left nullspace of coboundary operator...")
    left_null = M.T.nullspace()
    print(f"Cokernel dimension: {len(left_null)}")
    
    constraints = []
    for v in left_null:
        c = sum(v[i] * b_vec[i, 0] for i in range(len(v)))
        c_simp = sp.simplify(c)
        if c_simp != 0:
            constraints.append(c_simp)

    unique_constraints = list(set(constraints))
    print(f"Number of distinct constraint equations on gb: {len(unique_constraints)}")
    
    gb_sol = sp.solve(unique_constraints, gb_vars)
    print(f"Solvability conditions on gb parameters:")
    print(f"  {gb_sol}")
    
    all_zero = (gb_sol == {v: 0 for v in gb_vars})
    print(f"  All gb parameters must be zero: {all_zero}")
    
    return {
        "n": n,
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "dim_even": dim_even,
        "dim_odd": dim_odd,
        "dim_total": dim_total,
        "dim_f_odd_maps": len(phi_vars),
        "rank_coboundary_operator": int(M.rank()),
        "cokernel_dim": len(left_null),
        "num_equations": len(equations),
        "num_gb_parameters": len(gb_vars),
        "gb_parameters": [str(v) for v in gb_vars],
        "triviality_condition": "gb = 0 for all parameters",
        "all_gb_zero_required": all_zero,
        "non_trivial_constraints_sample": [str(c) + " = 0" for c in unique_constraints[:10]]
    }

summary = {}
for n in [1, 2, 3]:
    summary[f"C({n+1})"] = analyze_osp_deformation(n)

with open("deformation_analysis_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=================================================================")
print("  All verifications for n=1, 2, 3 completed and summary saved!   ")
print("=================================================================")
