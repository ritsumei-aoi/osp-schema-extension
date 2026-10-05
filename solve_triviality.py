import sympy as sp
import json

def analyze_cn_triviality(n):
    print(f"==================================================")
    print(f" Computational Verification for C({n}+1) = osp(2|{2*n})")
    print(f"==================================================")

    # Basis construction
    # Even basis generators
    even_basis = [('Na',)]
    for k in range(1, n+1):
        for l in range(k, n+1):
            even_basis.append(('B++', k, l))
    for k in range(1, n+1):
        for l in range(k, n+1):
            even_basis.append(('B--', k, l))
    for k in range(1, n+1):
        for l in range(1, n+1):
            even_basis.append(('B+-', k, l))

    # Odd basis generators
    odd_basis = []
    for sigma in [1, -1]:
        for k in range(1, n+1):
            for s in [1, -1]:
                odd_basis.append(('F', sigma, k, s))

    all_basis = even_basis + odd_basis
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    dim_total = len(all_basis)

    basis_to_idx = {b: i for i, b in enumerate(all_basis)}

    def get_parity(idx):
        return 0 if idx < dim_even else 1

    # Define gb parameters: gb_{sigma, j, s}
    gb_syms = {}
    for sigma in [1, -1]:
        for j in range(1, n+1):
            for s in [1, -1]:
                sig_str = '+' if sigma == 1 else '-'
                s_str = '+' if s == 1 else '-'
                gb_syms[(sigma, j, s)] = sp.Symbol(f"gb_{sig_str}_{j}_{s_str}", real=False)

    # 1. Structure constants C_0[i][j][k] for undeformed Lie superalgebra bracket [Z_i, Z_j]_0
    # 2. Deformation tensor Gamma_gb[i][j][k] for gamma_{gb}(Z_i, Z_j)
    C_0 = [[[sp.S.Zero for _ in range(dim_total)] for _ in range(dim_total)] for _ in range(dim_total)]
    Gamma_gb = [[[sp.S.Zero for _ in range(dim_total)] for _ in range(dim_total)] for _ in range(dim_total)]

    # Helper function for single operator commutator/exchange relation:
    # returns (const_0, gb_coeff) for [o1, o2]
    def single_op_comm(o1, o2):
        t1, *a1 = o1
        t2, *a2 = o2
        if t1 == 'a' and t2 == 'a':
            s1, s2 = a1[0], a2[0]
            if s1 != s2: # {a+, a-} = 1
                return (1, 0)
            return (0, 0)
        elif t1 == 'b' and t2 == 'b':
            k1, s1 = a1
            k2, s2 = a2
            if k1 == k2 and s1 != s2:
                return (1 if s1 == -1 and s2 == 1 else -1, 0)
            return (0, 0)
        elif t1 == 'a' and t2 == 'b':
            sigma = a1[0]
            j, s = a2
            return (0, gb_syms[(sigma, j, s)])
        elif t1 == 'b' and t2 == 'a':
            j, s = a1
            sigma = a2[0]
            return (0, -gb_syms[(sigma, j, s)])

    def express_bilinear(o1, o2):
        t1, *a1 = o1
        t2, *a2 = o2
        if t1 == 'a' and t2 == 'a':
            s1, s2 = a1[0], a2[0]
            if s1 == 1 and s2 == -1:
                return basis_to_idx[('Na',)], 1
            elif s1 == -1 and s2 == 1:
                return basis_to_idx[('Na',)], -1
            return None, 0
        elif t1 == 'b' and t2 == 'b':
            k1, s1 = a1
            k2, s2 = a2
            if s1 == 1 and s2 == 1:
                k, l = min(k1, k2), max(k1, k2)
                return basis_to_idx[('B++', k, l)], (2 if k == l else 1)
            elif s1 == -1 and s2 == -1:
                k, l = min(k1, k2), max(k1, k2)
                return basis_to_idx[('B--', k, l)], (2 if k == l else 1)
            elif s1 == 1 and s2 == -1:
                return basis_to_idx[('B+-', k1, k2)], 1
            elif s1 == -1 and s2 == 1:
                return basis_to_idx[('B+-', k2, k1)], 1
        elif t1 == 'a' and t2 == 'b':
            return basis_to_idx[('F', a1[0], a2[0], a2[1])], 1
        elif t1 == 'b' and t2 == 'a':
            return basis_to_idx[('F', a2[0], a1[0], a1[1])], 1
        return None, 0

    def get_terms(basis_elem):
        tag = basis_elem[0]
        if tag == 'Na':
            return [(1, ('a', 1), ('a', -1))]
        elif tag == 'B++':
            k, l = basis_elem[1], basis_elem[2]
            return [(sp.Rational(1, 2) if k == l else 1, ('b', k, 1), ('b', l, 1))]
        elif tag == 'B--':
            k, l = basis_elem[1], basis_elem[2]
            return [(sp.Rational(1, 2) if k == l else 1, ('b', k, -1), ('b', l, -1))]
        elif tag == 'B+-':
            return [(1, ('b', basis_elem[1], 1), ('b', basis_elem[2], -1))]
        elif tag == 'F':
            return [(1, ('a', basis_elem[1]), ('b', basis_elem[2], basis_elem[3]))]

    # Compute bracket [X, Y] for all pairs
    for i in range(dim_total):
        for j in range(dim_total):
            X_elem, Y_elem = all_basis[i], all_basis[j]
            pX, pY = get_parity(i), get_parity(j)

            for cX, u, v in get_terms(X_elem):
                pu, pv = (1 if u[0]=='a' else 0), (1 if v[0]=='a' else 0)
                for cY, w, z in get_terms(Y_elem):
                    pw, pz = (1 if w[0]=='a' else 0), (1 if z[0]=='a' else 0)
                    coeff = cX * cY

                    c_vw_0, c_vw_gb = single_op_comm(v, w)
                    c_vz_0, c_vz_gb = single_op_comm(v, z)
                    c_uw_0, c_uw_gb = single_op_comm(u, w)
                    c_uz_0, c_uz_gb = single_op_comm(u, z)

                    # Term 1: u [v, w z]
                    if c_vw_0 != 0:
                        idx, c = express_bilinear(u, z)
                        if idx is not None: C_0[i][j][idx] += coeff * c_vw_0 * c
                    if c_vw_gb != 0:
                        idx, c = express_bilinear(u, z)
                        if idx is not None: Gamma_gb[i][j][idx] += coeff * c_vw_gb * c

                    sign_1b = (-1)**(pv * pw)
                    if c_vz_0 != 0:
                        idx, c = express_bilinear(u, w)
                        if idx is not None: C_0[i][j][idx] += coeff * sign_1b * c_vz_0 * c
                    if c_vz_gb != 0:
                        idx, c = express_bilinear(u, w)
                        if idx is not None: Gamma_gb[i][j][idx] += coeff * sign_1b * c_vz_gb * c

                    # Term 2: (-1)^{pv pY} [u, w z] v
                    sign_2 = (-1)**(pv * pY)
                    sign_zv = (-1)**(pz * pv)
                    if c_uw_0 != 0:
                        idx, c = express_bilinear(v, z)
                        if idx is not None: C_0[i][j][idx] += coeff * sign_2 * sign_zv * c_uw_0 * c
                    if c_uw_gb != 0:
                        idx, c = express_bilinear(v, z)
                        if idx is not None: Gamma_gb[i][j][idx] += coeff * sign_2 * sign_zv * c_uw_gb * c

                    sign_2b = sign_2 * ((-1)**(pu * pw))
                    sign_wv = (-1)**(pw * pv)
                    if c_uz_0 != 0:
                        idx, c = express_bilinear(v, w)
                        if idx is not None: C_0[i][j][idx] += coeff * sign_2b * sign_wv * c_uz_0 * c
                    if c_uz_gb != 0:
                        idx, c = express_bilinear(v, w)
                        if idx is not None: Gamma_gb[i][j][idx] += coeff * sign_2b * sign_wv * c_uz_gb * c

    # Parametrize odd linear map f: g -> g
    phi = {}
    for j in range(dim_total):
        pj = get_parity(j)
        for k in range(dim_total):
            pk = get_parity(k)
            if pk != pj:
                phi[(k, j)] = sp.Symbol(f"phi_{k}_{j}", real=False)

    def f_map(j):
        pj = get_parity(j)
        return [(phi[(k, j)], k) for k in range(dim_total) if get_parity(k) != pj]

    # Set up coboundary equations (delta f)(Z_i, Z_j) = Gamma_gb(Z_i, Z_j)
    eqs = []
    for i in range(dim_total):
        pi = get_parity(i)
        for j in range(dim_total):
            pj = get_parity(j)
            
            delta_f_vec = [sp.S.Zero] * dim_total
            
            # (-1)^{pi} [Z_i, f(Z_j)]
            sign1 = (-1)**pi
            for phi_kj, k in f_map(j):
                for m in range(dim_total):
                    if C_0[i][k][m] != 0:
                        delta_f_vec[m] += sign1 * phi_kj * C_0[i][k][m]

            # - (-1)^{(pi+1)pj} [Z_j, f(Z_i)]
            sign2 = - ((-1)**((pi + 1) * pj))
            for phi_ki, k in f_map(i):
                for m in range(dim_total):
                    if C_0[j][k][m] != 0:
                        delta_f_vec[m] += sign2 * phi_ki * C_0[j][k][m]

            # - f([Z_i, Z_j])
            for k in range(dim_total):
                c_ijk = C_0[i][j][k]
                if c_ijk != 0:
                    for phi_mk, m in f_map(k):
                        delta_f_vec[m] -= c_ijk * phi_mk

            for m in range(dim_total):
                diff = delta_f_vec[m] - Gamma_gb[i][j][m]
                if diff != 0:
                    eqs.append(diff)

    phi_vars = list(phi.values())
    solution = sp.solve(eqs, phi_vars, dict=True)

    is_trivial = len(solution) > 0
    
    sol_dict_str = {}
    if is_trivial:
        for k, v in solution[0].items():
            sol_dict_str[str(k)] = str(v)

    res_summary = {
        "n": n,
        "algebra": f"C({n}+1) = osp(2|{2*n})",
        "even_dim": dim_even,
        "odd_dim": dim_odd,
        "total_dim": dim_total,
        "num_gb_params": 4*n,
        "num_equations": len(eqs),
        "num_phi_vars": len(phi_vars),
        "is_trivial": is_trivial,
        "phi_solutions_count": len(sol_dict_str),
        "phi_sample_solutions": {k: sol_dict_str[k] for k in list(sol_dict_str.keys())[:10]}
    }
    
    return res_summary, sol_dict_str

if __name__ == "__main__":
    all_results = {}
    full_solutions = {}
    for n in [1, 2, 3]:
        res, sol = analyze_cn_triviality(n)
        all_results[f"n={n}"] = res
        full_solutions[f"n={n}"] = sol
        print(f"n={n}: is_trivial = {res['is_trivial']}, num_equations = {res['num_equations']}, num_phi_vars = {res['num_phi_vars']}")

    with open("verification_artifacts.json", "w") as f:
        json.dump(all_results, f, indent=2)

    with open("full_map_solutions.json", "w") as f:
        json.dump(full_solutions, f, indent=2)

    print("\nSaved verification_artifacts.json and full_map_solutions.json")
