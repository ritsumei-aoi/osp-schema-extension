import sympy as sp

def analyze_triviality_for_n(n, allow_scalar_in_f=False):
    print(f"\n========================================================")
    print(f"       ANALYZING TRIVIALITY FOR n = {n}")
    print(f"       Allow scalar in f: {allow_scalar_in_f}")
    print(f"========================================================")
    
    even_basis = [('Na',)]
    for i in range(1, n+1):
        for j in range(i, n+1):
            even_basis.append(('b+b+', i, j))
    for i in range(1, n+1):
        for j in range(i, n+1):
            even_basis.append(('b-b-', i, j))
    for i in range(1, n+1):
        for j in range(1, n+1):
            even_basis.append(('b+b-', i, j))
            
    odd_basis = []
    for sigma in ['+', '-']:
        for i in range(1, n+1):
            for s in ['+', '-']:
                odd_basis.append(('F', sigma, i, s))
                
    dim_even = len(even_basis)
    dim_odd = len(odd_basis)
    full_basis = even_basis + odd_basis
    dim_total = len(full_basis)
    parity = [0]*dim_even + [1]*dim_odd
    
    even_idx = {elem: i for i, elem in enumerate(even_basis)}
    odd_idx = {elem: i for i, elem in enumerate(odd_basis)}
    
    gb_vars = {}
    for sigma in ['+', '-']:
        for j in range(1, n+1):
            for s in ['+', '-']:
                var_name = f"gb_{sigma}_{j}_{s}"
                gb_vars[(sigma, j, s)] = sp.Symbol(var_name)
    gb_symbols = list(gb_vars.values())
    
    def canonical_b_quadratic(i, s, j, r):
        if s == '+' and r == '+':
            return {even_idx[('b+b+', min(i,j), max(i,j))]: 1}
        elif s == '-' and r == '-':
            return {even_idx[('b-b-', min(i,j), max(i,j))]: 1}
        elif s == '+' and r == '-':
            return {even_idx[('b+b-', i, j)]: 1}
        elif s == '-' and r == '+':
            res = {even_idx[('b+b-', j, i)]: 1}
            if i == j:
                res['scalar'] = 1
            return res
            
    def bracket_0(idx1, idx2):
        elem1 = full_basis[idx1]
        elem2 = full_basis[idx2]
        p1 = parity[idx1]
        p2 = parity[idx2]
        
        res = {}
        def add_res(target, val):
            if val != 0:
                res[target] = res.get(target, 0) + val
                
        def ccr(a, x, b, y):
            if a == b:
                if x == '-' and y == '+': return 1
                if x == '+' and y == '-': return -1
            return 0
            
        def parse_sp(elem):
            t, i, j = elem
            if t == 'b+b+': return (i, '+', j, '+')
            if t == 'b-b-': return (i, '-', j, '-')
            if t == 'b+b-': return (i, '+', j, '-')
            
        if p1 == 0 and p2 == 0:
            if elem1[0] == 'Na' or elem2[0] == 'Na':
                return res
            i, s, j, r = parse_sp(elem1)
            k, u, m, v = parse_sp(elem2)
            terms = [
                (ccr(j,r, k,u), i, s, m, v),
                (ccr(j,r, m,v), i, s, k, u),
                (ccr(i,s, k,u), m, v, j, r),
                (ccr(i,s, m,v), k, u, j, r)
            ]
            for coeff, a, x, b, y in terms:
                if coeff != 0:
                    d = canonical_b_quadratic(a, x, b, y)
                    for k_idx, v_val in d.items():
                        add_res(k_idx, coeff * v_val)
            return res
            
        if p1 == 0 and p2 == 1:
            sigma, m, u = elem2[1], elem2[2], elem2[3]
            if elem1[0] == 'Na':
                val = 1 if sigma == '+' else -1
                add_res(idx2, val)
                return res
            i, s, j, r = parse_sp(elem1)
            c1 = ccr(j, r, m, u)
            if c1 != 0:
                add_res(odd_idx[('F', sigma, i, s)] + dim_even, c1)
            c2 = ccr(i, s, m, u)
            if c2 != 0:
                add_res(odd_idx[('F', sigma, j, r)] + dim_even, c2)
            return res
            
        if p1 == 1 and p2 == 0:
            res_eo = bracket_0(idx2, idx1)
            for k_idx, v_val in res_eo.items():
                add_res(k_idx, -v_val)
            return res
            
        if p1 == 1 and p2 == 1:
            sigma, i, s = elem1[1], elem1[2], elem1[3]
            tau, j, r = elem2[1], elem2[2], elem2[3]
            if sigma != tau:
                d = canonical_b_quadratic(i, s, j, r)
                for k_idx, v_val in d.items():
                    add_res(k_idx, v_val)
            c = ccr(i, s, j, r)
            if c != 0:
                if tau == '+' and sigma == '-':
                    add_res(0, c)
                elif tau == '-' and sigma == '+':
                    add_res('scalar', c)
                    add_res(0, -c)
            return res

    def gamma_gb(idx1, idx2):
        elem1 = full_basis[idx1]
        elem2 = full_basis[idx2]
        p1 = parity[idx1]
        p2 = parity[idx2]
        
        res = {}
        def add_res(target, val):
            if val != 0:
                res[target] = res.get(target, 0) + val
                
        def parse_sp(elem):
            t, i, j = elem
            if t == 'b+b+': return (i, '+', j, '+')
            if t == 'b-b-': return (i, '-', j, '-')
            if t == 'b+b-': return (i, '+', j, '-')
            
        if p1 == 0 and p2 == 0:
            if elem1[0] == 'Na' and elem2[0] != 'Na':
                j, s, k, r = parse_sp(elem2)
                add_res(odd_idx[('F', '+', k, r)] + dim_even, gb_vars[('-', j, s)])
                add_res(odd_idx[('F', '-', k, r)] + dim_even, -gb_vars[('+', j, s)])
                add_res(odd_idx[('F', '+', j, s)] + dim_even, gb_vars[('-', k, r)])
                add_res(odd_idx[('F', '-', j, s)] + dim_even, -gb_vars[('+', k, r)])
                return res
            elif elem1[0] != 'Na' and elem2[0] == 'Na':
                res_g = gamma_gb(idx2, idx1)
                for k_idx, v_val in res_g.items():
                    add_res(k_idx, -v_val)
                return res
            else:
                return res
                
        if p1 == 0 and p2 == 1:
            sigma, m, u = elem2[1], elem2[2], elem2[3]
            if elem1[0] == 'Na':
                if sigma == '+':
                    add_res(0, -gb_vars[('+', m, u)])
                else:
                    add_res('scalar', gb_vars[('-', m, u)])
                    add_res(0, -gb_vars[('-', m, u)])
                return res
            else:
                j, s, k, r = parse_sp(elem1)
                d1 = canonical_b_quadratic(j, s, m, u)
                for k_idx, v_val in d1.items():
                    add_res(k_idx, -gb_vars[(sigma, k, r)] * v_val)
                d2 = canonical_b_quadratic(k, r, m, u)
                for k_idx, v_val in d2.items():
                    add_res(k_idx, -gb_vars[(sigma, j, s)] * v_val)
                return res
                
        if p1 == 1 and p2 == 0:
            res_eo = gamma_gb(idx2, idx1)
            for k_idx, v_val in res_eo.items():
                add_res(k_idx, -v_val)
            return res
            
        if p1 == 1 and p2 == 1:
            sigma, j, s = elem1[1], elem1[2], elem1[3]
            tau, k, r = elem2[1], elem2[2], elem2[3]
            target1 = odd_idx[('F', sigma, k, r)] + dim_even
            add_res(target1, -gb_vars[(tau, j, s)])
            target2 = odd_idx[('F', tau, j, s)] + dim_even
            add_res(target2, -gb_vars[(sigma, k, r)])
            return res

    f_vars = {}
    f_symbols = []
    
    for i in range(dim_even):
        for a in range(dim_odd):
            var = sp.Symbol(f"phi_E{i}_O{a}")
            f_vars[('E', i, 'O', a)] = var
            f_symbols.append(var)
            
    for a in range(dim_odd):
        for i in range(dim_even):
            var = sp.Symbol(f"phi_O{a}_E{i}")
            f_vars[('O', a, 'E', i)] = var
            f_symbols.append(var)
        if allow_scalar_in_f:
            var = sp.Symbol(f"phi_O{a}_scalar")
            f_vars[('O', a, 'scalar')] = var
            f_symbols.append(var)

    def eval_f(idx):
        res = {}
        p = parity[idx]
        if p == 0:
            i = idx
            for a in range(dim_odd):
                o_idx = dim_even + a
                res[o_idx] = f_vars[('E', i, 'O', a)]
        else:
            a = idx - dim_even
            for i in range(dim_even):
                res[i] = f_vars[('O', a, 'E', i)]
            if allow_scalar_in_f:
                res['scalar'] = f_vars[('O', a, 'scalar')]
        return res

    def coboundary_f(idx1, idx2):
        p1 = parity[idx1]
        p2 = parity[idx2]
        
        res = {}
        def add_res(target, val):
            if val != 0:
                res[target] = res.get(target, 0) + val
                
        sign1 = -1 if p1 == 1 else 1
        fY = eval_f(idx2)
        for target_y, coeff_y in fY.items():
            if target_y == 'scalar':
                pass
            else:
                br = bracket_0(idx1, target_y)
                for target_br, coeff_br in br.items():
                    add_res(target_br, sign1 * coeff_y * coeff_br)
                    
        sign2 = - (-1)**((p1 + 1) * p2)
        fX = eval_f(idx1)
        for target_x, coeff_x in fX.items():
            if target_x == 'scalar':
                pass
            else:
                br = bracket_0(idx2, target_x)
                for target_br, coeff_br in br.items():
                    add_res(target_br, sign2 * coeff_x * coeff_br)
                    
        br_XY = bracket_0(idx1, idx2)
        for target_xy, coeff_xy in br_XY.items():
            if target_xy == 'scalar':
                pass
            else:
                f_br = eval_f(target_xy)
                for target_f, coeff_f in f_br.items():
                    add_res(target_f, - coeff_xy * coeff_f)
                    
        return res

    eqs = []
    all_targets = list(range(dim_total)) + ['scalar']
    
    for idx1 in range(dim_total):
        for idx2 in range(idx1, dim_total):
            df = coboundary_f(idx1, idx2)
            gg = gamma_gb(idx1, idx2)
            
            for t in all_targets:
                val_df = df.get(t, 0)
                val_gg = gg.get(t, 0)
                if val_df != 0 or val_gg != 0:
                    eqs.append(val_df - val_gg)
                    
    A, b_vec = sp.linear_eq_to_matrix(eqs, f_symbols)
    B, _ = sp.linear_eq_to_matrix(list(b_vec), gb_symbols)
    aug = A.row_join(B)
    aug_rref, pivots = aug.rref()
    
    gb_conditions = []
    for r in range(aug_rref.rows):
        is_A_zero = True
        for c in range(A.cols):
            if aug_rref[r, c] != 0:
                is_A_zero = False
                break
        if is_A_zero:
            b_row_expr = 0
            for c_gb in range(gb_symbols.__len__()):
                coeff = aug_rref[r, A.cols + c_gb]
                if coeff != 0:
                    b_row_expr += coeff * gb_symbols[c_gb]
            if b_row_expr != 0:
                gb_conditions.append(b_row_expr)
                
    gb_sol = sp.solve(gb_conditions, gb_symbols) if gb_conditions else {}
    print(f"n={n}, allow_scalar={allow_scalar_in_f}: {len(gb_conditions)} gb conditions.")
    print("Solution for gb:", gb_sol)

if __name__ == '__main__':
    for n in [1, 2, 3]:
        analyze_triviality_for_n(n, allow_scalar_in_f=True)
