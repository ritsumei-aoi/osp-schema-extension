import sympy as sp
import json

def check_gb_forced_zero(n):
    print(f"Checking gb zero condition for n={n}...")
    
    even_basis = [('Na',)]
    for k in range(1, n+1):
        for l in range(k, n+1): even_basis.append(('B++', k, l))
    for k in range(1, n+1):
        for l in range(k, n+1): even_basis.append(('B--', k, l))
    for k in range(1, n+1):
        for l in range(1, n+1): even_basis.append(('B+-', k, l))

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

    def get_parity(idx): return 0 if idx < dim_even else 1

    gb_syms = {}
    for sigma in [1, -1]:
        for j in range(1, n+1):
            for s in [1, -1]:
                sig_str = '+' if sigma == 1 else '-'
                s_str = '+' if s == 1 else '-'
                gb_syms[(sigma, j, s)] = sp.Symbol(f"gb_{sig_str}_{j}_{s_str}", real=False)

    C_0 = [[[sp.S.Zero for _ in range(dim_total)] for _ in range(dim_total)] for _ in range(dim_total)]
    Gamma_gb = [[[sp.S.Zero for _ in range(dim_total)] for _ in range(dim_total)] for _ in range(dim_total)]

    def single_op_comm(o1, o2):
        t1, *a1 = o1
        t2, *a2 = o2
        if t1 == 'a' and t2 == 'a':
            return (1 if a1[0] != a2[0] else 0, 0)
        elif t1 == 'b' and t2 == 'b':
            k1, s1 = a1
            k2, s2 = a2
            if k1 == k2 and s1 != s2:
                return (1 if s1 == -1 and s2 == 1 else -1, 0)
            return (0, 0)
        elif t1 == 'a' and t2 == 'b':
            return (0, gb_syms[(a1[0], a2[0], a2[1])])
        elif t1 == 'b' and t2 == 'a':
            return (0, -gb_syms[(a2[0], a1[0], a1[1])])

    def express_bilinear(o1, o2):
        t1, *a1 = o1
        t2, *a2 = o2
        if t1 == 'a' and t2 == 'a':
            s1, s2 = a1[0], a2[0]
            if s1 == 1 and s2 == -1: return basis_to_idx[('Na',)], 1
            elif s1 == -1 and s2 == 1: return basis_to_idx[('Na',)], -1
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
            elif s1 == 1 and s2 == -1: return basis_to_idx[('B+-', k1, k2)], 1
            elif s1 == -1 and s2 == 1: return basis_to_idx[('B+-', k2, k1)], 1
        elif t1 == 'a' and t2 == 'b': return basis_to_idx[('F', a1[0], a2[0], a2[1])], 1
        elif t1 == 'b' and t2 == 'a': return basis_to_idx[('F', a2[0], a1[0], a1[1])], 1
        return None, 0

    def get_terms(basis_elem):
        tag = basis_elem[0]
        if tag == 'Na': return [(1, ('a', 1), ('a', -1))]
        elif tag == 'B++':
            k, l = basis_elem[1], basis_elem[2]
            return [(sp.Rational(1, 2) if k == l else 1, ('b', k, 1), ('b', l, 1))]
        elif tag == 'B--':
            k, l = basis_elem[1], basis_elem[2]
            return [(sp.Rational(1, 2) if k == l else 1, ('b', k, -1), ('b', l, -1))]
        elif tag == 'B+-': return [(1, ('b', basis_elem[1], 1), ('b', basis_elem[2], -1))]
        elif tag == 'F': return [(1, ('a', basis_elem[1]), ('b', basis_elem[2], basis_elem[3]))]

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

    phi = {}
    for j in range(dim_total):
        pj = get_parity(j)
        for k in range(dim_total):
            pk = get_parity(k)
            if pk != pj: phi[(k, j)] = sp.Symbol(f"phi_{k}_{j}", real=False)

    def f_map(j):
        pj = get_parity(j)
        return [(phi[(k, j)], k) for k in range(dim_total) if get_parity(k) != pj]

    eqs = []
    for i in range(dim_total):
        pi = get_parity(i)
        for j in range(dim_total):
            pj = get_parity(j)
            
            delta_f_vec = [sp.S.Zero] * dim_total
            sign1 = (-1)**pi
            for phi_kj, k in f_map(j):
                for m in range(dim_total):
                    if C_0[i][k][m] != 0: delta_f_vec[m] += sign1 * phi_kj * C_0[i][k][m]

            sign2 = - ((-1)**((pi + 1) * pj))
            for phi_ki, k in f_map(i):
                for m in range(dim_total):
                    if C_0[j][k][m] != 0: delta_f_vec[m] += sign2 * phi_ki * C_0[j][k][m]

            for k in range(dim_total):
                c_ijk = C_0[i][j][k]
                if c_ijk != 0:
                    for phi_mk, m in f_map(k): delta_f_vec[m] -= c_ijk * phi_mk

            for m in range(dim_total):
                diff = delta_f_vec[m] - Gamma_gb[i][j][m]
                if diff != 0: eqs.append(diff)

    # Solve linear system for ALL unknowns: phi parameters AND gb parameters
    all_vars = list(phi.values()) + list(gb_syms.values())
    solution = sp.solve(eqs, all_vars, dict=True)

    print(f"Full solution for n={n}:")
    gb_vals = {}
    if solution:
        sol = solution[0]
        for g_sym in gb_syms.values():
            gb_vals[str(g_sym)] = str(sol.get(g_sym, "free"))
        print(f"  gb parameters forced values: {gb_vals}")
    else:
        print("  No solution found.")
        
    return gb_vals

if __name__ == "__main__":
    for n in [1, 2]:
        check_gb_forced_zero(n)
