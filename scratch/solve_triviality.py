import sympy as sp
from collections import defaultdict
import time

def analyze_triviality(n, modulo_scalars=True):
    t0 = time.time()
    print(f"\n==========================================")
    print(f"       TRIVIALITY ANALYSIS FOR n = {n}    ")
    print(f"       Modulo scalars = {modulo_scalars}   ")
    print(f"==========================================")

    # 1. Parameters gb
    gb_syms = {}
    gb_list = []
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                sym = sp.Symbol(f"gb_{sigma}_{j}_{s}")
                gb_syms[(sigma, j, s)] = sym
                gb_list.append(sym)

    # 2. Basis
    even_basis = ["Z"]
    for j in range(1, n + 1):
        even_basis.append(f"E_2d_{j}")
        even_basis.append(f"E_-2d_{j}")
        even_basis.append(f"H_{j}")
    for j in range(1, n + 1):
        for k in range(j + 1, n + 1):
            even_basis.append(f"E_d_{j}+d_{k}")
            even_basis.append(f"E_-d_{j}-d_{k}")
    for j in range(1, n + 1):
        for k in range(1, n + 1):
            if j != k:
                even_basis.append(f"E_d_{j}-d_{k}")

    odd_basis = []
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                odd_basis.append(f"F_{sigma}_{j}_{s}")

    basis = even_basis + odd_basis
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    dim_total = len(basis)

    parity = {b: (0 if b in even_basis else 1) for b in basis}

    # 3. Parameters of odd linear map f: g -> g
    phi_syms = {}
    phi_list = []
    for E in even_basis:
        for F in odd_basis:
            sym1 = sp.Symbol(f"phi_{E}_{F}")
            phi_syms[(E, F)] = sym1
            phi_list.append(sym1)
            
            sym2 = sp.Symbol(f"phi_{F}_{E}")
            phi_syms[(F, E)] = sym2
            phi_list.append(sym2)

    def apply_f(X):
        res = defaultdict(lambda: sp.S.Zero)
        if parity[X] == 0:
            for F in odd_basis:
                res[F] += phi_syms[(X, F)]
        else:
            for E in even_basis:
                res[E] += phi_syms[(X, E)]
        return res

    def b_comm(j, s, k, t):
        if j != k: return 0
        if s == '-' and t == '+': return 1
        if s == '+' and t == '-': return -1
        return 0

    def parse_F(F_name):
        parts = F_name.split('_')
        return parts[1], int(parts[2]), parts[3]

    def get_b_pairs(sp_name):
        if sp_name.startswith("E_2d_"):
            j = int(sp_name.split('_')[2])
            return [((j, '+'), (j, '+'), sp.Rational(1, 2))]
        elif sp_name.startswith("E_-2d_"):
            j = int(sp_name.split('_')[2])
            return [((j, '-'), (j, '-'), sp.Rational(1, 2))]
        elif sp_name.startswith("H_"):
            j = int(sp_name.split('_')[1])
            return [((j, '+'), (j, '-'), 1)]
        elif "+d_" in sp_name or ("E_d_" in sp_name and "+" in sp_name):
            parts = sp_name.replace("E_d_", "").split("+d_")
            j, k = int(parts[0]), int(parts[1])
            return [((j, '+'), (k, '+'), 1)]
        elif "-d_" in sp_name and "E_-d_" in sp_name:
            parts = sp_name.replace("E_-d_", "").split("-d_")
            j, k = int(parts[0]), int(parts[1])
            return [((j, '-'), (k, '-'), 1)]
        elif "E_d_" in sp_name and "-d_" in sp_name:
            parts = sp_name.replace("E_d_", "").split("-d_")
            j, k = int(parts[0]), int(parts[1])
            return [((j, '+'), (k, '-'), 1)]
        else:
            raise ValueError(f"Unknown sp generator {sp_name}")

    def add_b_pair_to_dict(d, j, s, k, t, coeff):
        if coeff == 0: return
        if j == k:
            if s == '+' and t == '+':
                d[f"E_2d_{j}"] += 2 * coeff
            elif s == '-' and t == '-':
                d[f"E_-2d_{j}"] += 2 * coeff
            elif s == '+' and t == '-':
                d[f"H_{j}"] += coeff
                d["scalar"] -= sp.Rational(1, 2) * coeff
            elif s == '-' and t == '+':
                d[f"H_{j}"] += coeff
                d["scalar"] += sp.Rational(1, 2) * coeff
        else:
            if s == '+' and t == '+':
                j_min, k_max = min(j, k), max(j, k)
                d[f"E_d_{j_min}+d_{k_max}"] += coeff
            elif s == '-' and t == '-':
                j_min, k_max = min(j, k), max(j, k)
                d[f"E_-d_{j_min}-d_{k_max}"] += coeff
            elif s == '+' and t == '-':
                d[f"E_d_{j}-d_{k}"] += coeff
            elif s == '-' and t == '+':
                d[f"E_d_{k}-d_{j}"] += coeff

    def compute_sp_comm(X, Y):
        d = defaultdict(lambda: sp.S.Zero)
        pairs_X = get_b_pairs(X)
        pairs_Y = get_b_pairs(Y)
        for (j, s), (k, t), cX in pairs_X:
            for (m, u), (l, v), cY in pairs_Y:
                c_kt_mu = b_comm(k, t, m, u)
                if c_kt_mu != 0:
                    add_b_pair_to_dict(d, j, s, l, v, cX * cY * c_kt_mu)
                c_kt_lv = b_comm(k, t, l, v)
                if c_kt_lv != 0:
                    add_b_pair_to_dict(d, j, s, m, u, cX * cY * c_kt_lv)
                c_js_mu = b_comm(j, s, m, u)
                if c_js_mu != 0:
                    add_b_pair_to_dict(d, l, v, k, t, cX * cY * c_js_mu)
                c_js_lv = b_comm(j, s, l, v)
                if c_js_lv != 0:
                    add_b_pair_to_dict(d, m, u, k, t, cX * cY * c_js_lv)
        return d

    def bracket_0_and_gamma(X, Y):
        res_0 = defaultdict(lambda: sp.S.Zero)
        res_g = defaultdict(lambda: sp.S.Zero)

        if parity[X] == 0 and parity[Y] == 0:
            if X == "Z" or Y == "Z":
                if X == "Z" and Y == "Z":
                    pass
                elif X == "Z":
                    pairs = get_b_pairs(Y)
                    for (j, s), (k, t), coeff in pairs:
                        res_g[f"F_-_{k}_{t}"] += coeff * gb_syms[('+', j, s)]
                        res_g[f"F_+_{k}_{t}"] += coeff * gb_syms[('-', j, s)]
                        res_g[f"F_-_{j}_{s}"] += coeff * gb_syms[('+', k, t)]
                        res_g[f"F_+_{j}_{s}"] += coeff * gb_syms[('-', k, t)]
                else:
                    b0, bg = bracket_0_and_gamma("Z", X)
                    for k_b, v_b in b0.items(): res_0[k_b] -= v_b
                    for k_g, v_g in bg.items(): res_g[k_g] -= v_g
            else:
                sp_comm = compute_sp_comm(X, Y)
                for k_b, v_b in sp_comm.items(): res_0[k_b] += v_b

        elif parity[X] == 0 and parity[Y] == 1:
            sigma_Y, m, u = parse_F(Y)
            if X == "Z":
                if sigma_Y == '+': res_0[f"F_+_{m}_{u}"] += 1
                else: res_0[f"F_-_{m}_{u}"] -= 1
                
                if sigma_Y == '+':
                    res_g["Z"] += gb_syms[('+', m, u)]
                    res_g["scalar"] += sp.Rational(1, 2) * gb_syms[('+', m, u)]
                else:
                    res_g["Z"] -= gb_syms[('-', m, u)]
                    res_g["scalar"] += sp.Rational(1, 2) * gb_syms[('-', m, u)]
            else:
                pairs = get_b_pairs(X)
                for (j, s), (k, t), coeff in pairs:
                    c_jm = b_comm(j, s, m, u)
                    if c_jm != 0: res_0[f"F_{sigma_Y}_{k}_{t}"] += coeff * c_jm
                    c_km = b_comm(k, t, m, u)
                    if c_km != 0: res_0[f"F_{sigma_Y}_{j}_{s}"] += coeff * c_km

                    add_b_pair_to_dict(res_g, k, t, m, u, -coeff * gb_syms[(sigma_Y, j, s)])
                    add_b_pair_to_dict(res_g, j, s, m, u, -coeff * gb_syms[(sigma_Y, k, t)])

        elif parity[X] == 1 and parity[Y] == 0:
            b0, bg = bracket_0_and_gamma(Y, X)
            for k_b, v_b in b0.items(): res_0[k_b] -= v_b
            for k_g, v_g in bg.items(): res_g[k_g] -= v_g

        else:
            sigma_X, j, s = parse_F(X)
            sigma_Y, k, t = parse_F(Y)
            if sigma_X != sigma_Y:
                add_b_pair_to_dict(res_0, j, s, k, t, 1)

            res_g[f"F_{sigma_X}_{k}_{t}"] -= gb_syms[(sigma_Y, j, s)]
            res_g[f"F_{sigma_Y}_{j}_{s}"] -= gb_syms[(sigma_X, k, t)]

        return res_0, res_g

    b0_table = {}
    gamma_table = {}
    for X in basis:
        for Y in basis:
            b0, bg = bracket_0_and_gamma(X, Y)
            b0_table[(X, Y)] = b0
            gamma_table[(X, Y)] = bg

    def bracket_0_lin(dict_A, dict_B):
        res = defaultdict(lambda: sp.S.Zero)
        for eA, cA in dict_A.items():
            if cA == 0 or eA == "scalar": continue
            for eB, cB in dict_B.items():
                if cB == 0 or eB == "scalar": continue
                b0 = b0_table[(eA, eB)]
                for eC, cC in b0.items():
                    res[eC] += cA * cB * cC
        return res

    equations = []

    for i_x, X in enumerate(basis):
        pX = parity[X]
        fX = apply_f(X)
        for i_y, Y in enumerate(basis):
            if i_y <= i_x: continue
            pY = parity[Y]
            fY = apply_f(Y)

            term1 = bracket_0_lin({X: 1}, fY)
            sign1 = 1 if pX == 0 else -1

            term2 = bracket_0_lin({Y: 1}, fX)
            sign2 = - (1 if ((pX + 1) * pY) % 2 == 0 else -1)

            b0_XY = b0_table[(X, Y)]
            term3 = defaultdict(lambda: sp.S.Zero)
            for eC, cC in b0_XY.items():
                if cC == 0 or eC == "scalar": continue
                fC = apply_f(eC)
                for eD, cD in fC.items():
                    term3[eD] -= cC * cD

            delta_f_XY = defaultdict(lambda: sp.S.Zero)
            for k, v in term1.items(): delta_f_XY[k] += sign1 * v
            for k, v in term2.items(): delta_f_XY[k] += sign2 * v
            for k, v in term3.items(): delta_f_XY[k] += v

            gamma_XY = gamma_table[(X, Y)]

            all_keys = set(delta_f_XY.keys()) | set(gamma_XY.keys())
            for k in all_keys:
                if modulo_scalars and k == "scalar":
                    continue
                eq = delta_f_XY[k] - gamma_XY[k]
                if eq != 0:
                    equations.append(eq)

    A_phi, _ = sp.linear_eq_to_matrix(equations, phi_list)
    B_gb, _  = sp.linear_eq_to_matrix(equations, gb_list)

    rank_A_phi = A_phi.rank()
    null_A_phi_T = A_phi.T.nullspace()

    gb_constraints = []
    gb_vec = sp.Matrix(gb_list)
    for v in null_A_phi_T:
        eq = (v.T * B_gb * gb_vec)[0, 0]
        if eq != 0:
            gb_constraints.append(eq)

    if gb_constraints:
        gb_matrix, _ = sp.linear_eq_to_matrix(gb_constraints, gb_list)
        rank_gb_matrix = gb_matrix.rank()
        sol_gb = sp.solve(gb_constraints, gb_list)
    else:
        rank_gb_matrix = 0
        sol_gb = "No constraints"

    t1 = time.time()
    print(f"Summary for n = {n}:")
    print(f"  Equations: {len(equations)}, Phi vars: {len(phi_list)}, gb vars: {len(gb_list)}")
    print(f"  Rank(A_phi): {rank_A_phi} / {len(phi_list)}")
    print(f"  Left nullspace dim: {len(null_A_phi_T)}")
    print(f"  gb constraint matrix rank: {rank_gb_matrix} / {len(gb_list)}")
    print(f"  Triviality solution for gb: {sol_gb}")
    print(f"  Computation time: {t1 - t0:.2f}s")
    
    return {
        "n": n,
        "dim_even": dim_even,
        "dim_odd": dim_odd,
        "num_equations": len(equations),
        "num_phi_vars": len(phi_list),
        "num_gb_vars": len(gb_list),
        "rank_A_phi": rank_A_phi,
        "left_nullspace_dim": len(null_A_phi_T),
        "gb_rank": rank_gb_matrix,
        "sol_gb": str(sol_gb)
    }

if __name__ == "__main__":
    results = []
    for n in [1, 2, 3]:
        res = analyze_triviality(n, modulo_scalars=True)
        results.append(res)
    
    import json
    with open("scratch/verification_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved verification_results.json")
