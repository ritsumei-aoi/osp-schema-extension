import sympy as sp
import json
import time

def analyze_cn1(n):
    t0 = time.time()
    print(f"\n=======================================================")
    print(f"       COMPUTATIONAL TRIVIALITY SOLVER FOR C({n}+1)")
    print(f"=======================================================")

    V_basis = []
    for i in range(1, n + 1):
        V_basis.append((i, '+'))
        V_basis.append((i, '-'))
    dim_V = 2 * n  # 2n
    
    even_basis = ["Z0"]
    bosonic_pairs = []
    for a in range(dim_V):
        for b in range(a, dim_V):
            bosonic_pairs.append((a, b))
            even_basis.append(f"B_{V_basis[a][0]}{V_basis[a][1]}_{V_basis[b][0]}{V_basis[b][1]}")
            
    odd_basis = []
    odd_tuples = []
    for sigma in ['+', '-']:
        for a in range(dim_V):
            odd_tuples.append((sigma, a))
            odd_basis.append(f"F_{sigma}_{V_basis[a][0]}{V_basis[a][1]}")
            
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    dim_total = dim_even + dim_odd
    
    print(f"Superdimension: ({dim_even} | {dim_odd}), total = {dim_total}")
    
    total_basis = even_basis + odd_basis
    parity = [0]*dim_even + [1]*dim_odd
    
    # Structure constants
    bracket_0 = {}
    
    def add_b0(i, j, k, coeff):
        if coeff != 0:
            bracket_0[(i, j, k)] = bracket_0.get((i, j, k), 0) + coeff

    def omega(a, b):
        (i, s1) = V_basis[a]
        (j, s2) = V_basis[b]
        if i == j and s1 == '-' and s2 == '+':
            return 1
        if i == j and s1 == '+' and s2 == '-':
            return -1
        return 0

    def action_sp(a, b, c):
        res = {}
        w_bc = omega(b, c)
        w_ac = omega(a, c)
        if w_bc != 0:
            res[a] = res.get(a, 0) + w_bc
        if w_ac != 0:
            res[b] = res.get(b, 0) + w_ac
        return res

    def v_prod_to_even(c, d):
        idx_c, idx_d = min(c, d), max(c, d)
        b_idx = bosonic_pairs.index((idx_c, idx_d)) + 1
        return b_idx, 1/2 * omega(c, d)

    # Brackets
    for c in range(dim_V):
        idx_Fplus = dim_even + odd_tuples.index(('+', c))
        idx_Fminus = dim_even + odd_tuples.index(('-', c))
        add_b0(0, idx_Fplus, idx_Fplus, 1)
        add_b0(idx_Fplus, 0, idx_Fplus, -1)
        add_b0(0, idx_Fminus, idx_Fminus, -1)
        add_b0(idx_Fminus, 0, idx_Fminus, 1)

    for p_idx, (a, b) in enumerate(bosonic_pairs):
        b_idx = p_idx + 1
        for sigma in ['+', '-']:
            for c in range(dim_V):
                f_in = dim_even + odd_tuples.index((sigma, c))
                act = action_sp(a, b, c)
                for d, coeff in act.items():
                    f_out = dim_even + odd_tuples.index((sigma, d))
                    add_b0(b_idx, f_in, f_out, coeff)
                    add_b0(f_in, b_idx, f_out, -coeff)

    for p1_idx, (a, b) in enumerate(bosonic_pairs):
        b1_idx = p1_idx + 1
        for p2_idx, (c, d) in enumerate(bosonic_pairs):
            b2_idx = p2_idx + 1
            if b1_idx >= b2_idx:
                continue
            terms = [
                (omega(b, c), a, d),
                (omega(b, d), a, c),
                (omega(a, c), b, d),
                (omega(a, d), b, c)
            ]
            for w, x, y in terms:
                if w != 0:
                    out_b_idx, _ = v_prod_to_even(x, y)
                    add_b0(b1_idx, b2_idx, out_b_idx, w)
                    add_b0(b2_idx, b1_idx, out_b_idx, -w)

    for c in range(dim_V):
        for d in range(dim_V):
            f1_idx = dim_even + odd_tuples.index(('+', c))
            f2_idx = dim_even + odd_tuples.index(('-', d))
            
            w = omega(c, d)
            if w != 0:
                add_b0(f1_idx, f2_idx, 0, w)
                add_b0(f2_idx, f1_idx, 0, w)
                
            out_b_idx, _ = v_prod_to_even(c, d)
            add_b0(f1_idx, f2_idx, out_b_idx, 1)
            add_b0(f2_idx, f1_idx, out_b_idx, 1)

    print(f"Undeformed bracket computed in {time.time()-t0:.2f}s: {len(bracket_0)} entries.")
    t1 = time.time()

    # Deformed 2-cocycle
    gb_symbols = {}
    gb_list = []
    for sigma in ['+', '-']:
        for c in range(dim_V):
            v_info = V_basis[c]
            sym = sp.Symbol(f"gb_{sigma}_{v_info[0]}_{v_info[1]}")
            gb_symbols[(sigma, c)] = sym
            gb_list.append(sym)

    gamma_gb = {}

    def add_gamma(i, j, k, expr):
        if expr != 0:
            gamma_gb[(i, j, k)] = gamma_gb.get((i, j, k), 0) + expr

    for p_idx, (a, b) in enumerate(bosonic_pairs):
        b_idx = p_idx + 1
        f_minus_b = dim_even + odd_tuples.index(('-', b))
        f_minus_a = dim_even + odd_tuples.index(('-', a))
        f_plus_b  = dim_even + odd_tuples.index(('+', b))
        f_plus_a  = dim_even + odd_tuples.index(('+', a))
        
        expr_f_minus_b = gb_symbols[('+', a)]
        expr_f_minus_a = gb_symbols[('+', b)]
        expr_f_plus_b  = gb_symbols[('-', a)]
        expr_f_plus_a  = gb_symbols[('-', b)]
        
        add_gamma(0, b_idx, f_minus_b, expr_f_minus_b)
        add_gamma(b_idx, 0, f_minus_b, -expr_f_minus_b)
        
        add_gamma(0, b_idx, f_minus_a, expr_f_minus_a)
        add_gamma(b_idx, 0, f_minus_a, -expr_f_minus_a)
        
        add_gamma(0, b_idx, f_plus_b, expr_f_plus_b)
        add_gamma(b_idx, 0, f_plus_b, -expr_f_plus_b)
        
        add_gamma(0, b_idx, f_plus_a, expr_f_plus_a)
        add_gamma(b_idx, 0, f_plus_a, -expr_f_plus_a)

    for p_idx, (a, b) in enumerate(bosonic_pairs):
        b_idx = p_idx + 1
        for sigma in ['+', '-']:
            for c in range(dim_V):
                f_idx = dim_even + odd_tuples.index((sigma, c))
                
                out_bc_idx, _ = v_prod_to_even(b, c)
                expr1 = -gb_symbols[(sigma, a)]
                add_gamma(b_idx, f_idx, out_bc_idx, expr1)
                add_gamma(f_idx, b_idx, out_bc_idx, -expr1)
                
                out_ac_idx, _ = v_prod_to_even(a, c)
                expr2 = -gb_symbols[(sigma, b)]
                add_gamma(b_idx, f_idx, out_ac_idx, expr2)
                add_gamma(f_idx, b_idx, out_ac_idx, -expr2)

    for c in range(dim_V):
        f_plus_idx  = dim_even + odd_tuples.index(('+', c))
        f_minus_idx = dim_even + odd_tuples.index(('-', c))
        
        expr_plus = gb_symbols[('+', c)]
        add_gamma(0, f_plus_idx, 0, expr_plus)
        add_gamma(f_plus_idx, 0, 0, -expr_plus)
        
        expr_minus = -gb_symbols[('-', c)]
        add_gamma(0, f_minus_idx, 0, expr_minus)
        add_gamma(f_minus_idx, 0, 0, -expr_minus)

    for sigma1 in ['+', '-']:
        for a in range(dim_V):
            f1_idx = dim_even + odd_tuples.index((sigma1, a))
            for sigma2 in ['+', '-']:
                for b in range(dim_V):
                    f2_idx = dim_even + odd_tuples.index((sigma2, b))
                    
                    f_out1 = dim_even + odd_tuples.index((sigma1, b))
                    f_out2 = dim_even + odd_tuples.index((sigma2, a))
                    
                    expr1 = -gb_symbols[(sigma2, a)]
                    expr2 = -gb_symbols[(sigma1, b)]
                    
                    add_gamma(f1_idx, f2_idx, f_out1, expr1)
                    add_gamma(f1_idx, f2_idx, f_out2, expr2)

    print(f"Deformed 2-cocycle computed in {time.time()-t1:.2f}s: {len(gamma_gb)} entries.")
    t2 = time.time()

    f_EO_symbols = {}
    f_OE_symbols = {}
    f_list = []
    
    for k in range(dim_odd):
        for j in range(dim_even):
            sym = sp.Symbol(f"f_EO_{k}_{j}")
            f_EO_symbols[(k, j)] = sym
            f_list.append(sym)
            
    for k in range(dim_even):
        for j in range(dim_odd):
            sym = sp.Symbol(f"f_OE_{k}_{j}")
            f_OE_symbols[(k, j)] = sym
            f_list.append(sym)

    def get_f(in_idx, out_idx):
        p_in = parity[in_idx]
        p_out = parity[out_idx]
        if p_in == 0 and p_out == 1:
            j = in_idx
            k = out_idx - dim_even
            return f_EO_symbols[(k, j)]
        elif p_in == 1 and p_out == 0:
            j = in_idx - dim_even
            k = out_idx
            return f_OE_symbols[(k, j)]
        else:
            return 0

    def compute_delta_f(i, j, k):
        px = parity[i]
        py = parity[j]
        
        t1 = 0
        sign1 = 1 if px == 0 else -1
        for m in range(dim_total):
            f_jm = get_f(j, m)
            if f_jm != 0:
                c_im_k = bracket_0.get((i, m, k), 0)
                if c_im_k != 0:
                    t1 += sign1 * f_jm * c_im_k
                    
        t2 = 0
        sign2_pow = (px + 1) * py
        sign2 = -1 if sign2_pow % 2 == 0 else 1
        for m in range(dim_total):
            f_im = get_f(i, m)
            if f_im != 0:
                c_jm_k = bracket_0.get((j, m, k), 0)
                if c_jm_k != 0:
                    t2 += sign2 * f_im * c_jm_k
                    
        t3 = 0
        for m in range(dim_total):
            c_ij_m = bracket_0.get((i, j, m), 0)
            if c_ij_m != 0:
                f_mk = get_f(m, k)
                if f_mk != 0:
                    t3 -= c_ij_m * f_mk
                    
        return t1 + t2 + t3

    equations = []
    
    for i in range(dim_total):
        for j in range(i, dim_total):
            expected_parity = (parity[i] + parity[j] + 1) % 2
            for k in range(dim_total):
                if parity[k] != expected_parity:
                    continue
                gamma_val = gamma_gb.get((i, j, k), 0)
                delta_f_val = compute_delta_f(i, j, k)
                eq = gamma_val - delta_f_val
                if eq != 0:
                    equations.append(eq)

    print(f"Equations generated in {time.time()-t2:.2f}s: {len(equations)} equations.")
    t3 = time.time()

    num_f = len(f_list)
    num_gb = len(gb_list)

    M_f, M_gb = sp.linear_eq_to_matrix(equations, f_list + gb_list)
    M_f_mat = M_f[:, :num_f]
    M_gb_mat = -M_f[:, num_f:]
    
    print(f"Matrix shapes: M_f {M_f_mat.shape}, M_gb {M_gb_mat.shape}")
    
    rank_M_f = M_f_mat.rank()
    aug_mat = M_f_mat.hstack(M_gb_mat)
    rank_aug = aug_mat.rank()
    
    print(f"Rank(M_f) = {rank_M_f}")
    print(f"Rank([M_f | M_gb]) = {rank_aug}")
    
    left_null = M_f_mat.T.nullspace()
    print(f"Left nullspace dim: {len(left_null)}")
    
    if len(left_null) == 0:
        dim_trivial_gb = num_gb
    else:
        left_null_mat = sp.Matrix([v.T for v in left_null])
        gb_constraints = left_null_mat * M_gb_mat
        gb_constraints_rank = gb_constraints.rank()
        gb_nullspace = gb_constraints.nullspace()
        dim_trivial_gb = len(gb_nullspace)
        print(f"GB Constraint Matrix Rank: {gb_constraints_rank}")
        print(f"Dimension of trivial gb parameter space: {dim_trivial_gb} / {num_gb}")
        
    print(f"Total time for n={n}: {time.time()-t0:.2f}s")
    
    return {
        "n": n,
        "superdim": f"({dim_even}|{dim_odd})",
        "num_gb": num_gb,
        "num_f": num_f,
        "num_eqs": len(equations),
        "rank_M_f": int(rank_M_f),
        "rank_aug": int(rank_aug),
        "dim_trivial_gb": int(dim_trivial_gb)
    }

if __name__ == '__main__':
    results = []
    for n in [1, 2, 3]:
        res = analyze_cn1(n)
        results.append(res)
        
    with open("verification_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved all verification results to verification_results.json")
