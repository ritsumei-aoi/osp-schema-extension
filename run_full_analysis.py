import sympy as sp
import json
import time

def run_full_analysis(n):
    print(f"\n=================================================================")
    print(f"       Running Full Triviality Analysis for C({n+1}) = osp(2|{2*n})")
    print(f"=================================================================")
    t0 = time.time()

    bosons = []
    for k in range(1, n + 1):
        bosons.append((k, '+'))
        bosons.append((k, '-'))
    num_b = 2 * n

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
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(1, dim_even):
            _, b3, b4 = basis[j]
            if b1 == b2 and b3 == b4:
                terms = [(omega(b1, b3), b1, b3)]
            elif b1 == b2 and b3 != b4:
                terms = [(omega(b1, b3), b1, b4), (omega(b1, b4), b1, b3)]
            elif b1 != b2 and b3 == b4:
                terms = [(omega(b2, b3), b1, b3), (omega(b1, b3), b2, b3)]
            else:
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
                    C[(i, j)][idx] += sp.Rational(w * mult)

    # [B(b1, b2), F(sigma, b3)]:
    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(dim_even, dim_total):
            _, sigma, b3 = basis[j]
            if b1 == b2:
                terms = [(omega(b1, b3), b1)]
            else:
                terms = [(omega(b2, b3), b1), (omega(b1, b3), b2)]
            for w, u in terms:
                if w != 0:
                    idx = get_F_idx(sigma, u)
                    C[(i, j)][idx] += sp.Rational(w)
                    C[(j, i)][idx] -= sp.Rational(w)

    # {F(sigma1, b1), F(sigma2, b2)}:
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

    # Inhomogeneous 2-cocycle gamma:
    gamma = { (i, j): [sp.Rational(0)]*dim_total for i in range(dim_total) for j in range(dim_total) }

    # 1. Even-Even:
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
        
        if b1 == b2:
            gamma[(0, j)][idx_p1] += g_m1
            gamma[(0, j)][idx_m1] += g_p1
            gamma[(j, 0)][idx_p1] -= g_m1
            gamma[(j, 0)][idx_m1] -= g_p1
        else:
            gamma[(0, j)][idx_p2] += sp.Rational(1, 2) * g_m1
            gamma[(0, j)][idx_m2] += sp.Rational(1, 2) * g_p1
            gamma[(0, j)][idx_p1] += sp.Rational(1, 2) * g_m2
            gamma[(0, j)][idx_m1] += sp.Rational(1, 2) * g_p2

            gamma[(j, 0)][idx_p2] -= sp.Rational(1, 2) * g_m1
            gamma[(j, 0)][idx_m2] -= sp.Rational(1, 2) * g_p1
            gamma[(j, 0)][idx_p1] -= sp.Rational(1, 2) * g_m2
            gamma[(j, 0)][idx_m1] -= sp.Rational(1, 2) * g_p2

    # 2. Even-Odd:
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

    for i in range(1, dim_even):
        _, b1, b2 = basis[i]
        for j in range(dim_even, dim_total):
            _, sigma, b3 = basis[j]
            if b1 == b2:
                g = gb[(sigma, b1)]
                idx = get_B_idx(b1, b3)
                mult = 2 if b1 == b3 else 1
                val = mult * g
                gamma[(i, j)][idx] -= val
                gamma[(j, i)][idx] += val
            else:
                g_s1 = gb[(sigma, b1)]
                g_s2 = gb[(sigma, b2)]
                
                idx23 = get_B_idx(b2, b3)
                mult23 = 2 if b2 == b3 else 1
                idx13 = get_B_idx(b1, b3)
                mult13 = 2 if b1 == b3 else 1
                
                val1 = sp.Rational(mult23, 2) * g_s1
                val2 = sp.Rational(mult13, 2) * g_s2
                
                gamma[(i, j)][idx23] -= val1
                gamma[(i, j)][idx13] -= val2
                gamma[(j, i)][idx23] += val1
                gamma[(j, i)][idx13] += val2

    # 3. Odd-Odd:
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

    # 4. Set up Coboundary System gamma == delta f
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
    rank_M = M.rank()
    print(f"Coboundary matrix M shape: {M.shape}, Rank: {rank_M}")

    # Compute cokernel
    left_null = M.T.nullspace()
    dim_cokernel = len(left_null)
    print(f"Cokernel dimension: {dim_cokernel}")

    constraints = []
    for v in left_null:
        c = sum(v[i] * b_vec[i, 0] for i in range(len(v)))
        c_simp = sp.simplify(c)
        if c_simp != 0:
            constraints.append(c_simp)

    unique_constraints = list(set(constraints))
    print(f"Number of non-trivial constraints on gb: {len(unique_constraints)}")

    gb_sol = sp.solve(unique_constraints, gb_vars)
    print(f"Solvability conditions on gb parameters: {gb_sol}")
    all_zero = (gb_sol == {v: 0 for v in gb_vars})
    print(f"All gb must be zero: {all_zero}")

    elapsed = time.time() - t0
    print(f"Analysis for n={n} completed in {elapsed:.2f}s")

    # Structure constants summary sample:
    non_zero_C_count = sum(1 for k, v in C.items() if any(x != 0 for x in v))
    non_zero_gamma_count = sum(1 for k, v in gamma.items() if any(x != 0 for x in v))

    return {
        "n": n,
        "algebra": f"C({n+1}) = osp(2|{2*n})",
        "dim_even": dim_even,
        "dim_odd": dim_odd,
        "dim_total": dim_total,
        "dim_f_odd_maps": len(phi_vars),
        "rank_coboundary_operator": int(rank_M),
        "cokernel_dim": int(dim_cokernel),
        "total_equations": len(equations),
        "non_zero_structure_constants_pairs": non_zero_C_count,
        "non_zero_gamma_pairs": non_zero_gamma_count,
        "num_gb_parameters": len(gb_vars),
        "gb_parameters": [str(v) for v in gb_vars],
        "triviality_condition": "gb = 0 for all parameters",
        "all_gb_zero_required": all_zero,
        "unique_constraints_sample": [str(c) + " = 0" for c in unique_constraints[:10]],
        "computation_time_seconds": round(elapsed, 2)
    }

final_results = {}
for n in [1, 2, 3]:
    final_results[f"C({n+1})"] = run_full_analysis(n)

with open("verification_artifacts.json", "w") as f:
    json.dump(final_results, f, indent=2)

print("\nSaved full structured data to verification_artifacts.json successfully.")
