import numpy as np
import sympy as sp

def solve_triviality(n):
    print(f"\n================ SOLVING FOR n = {n} ================")
    
    # Define basis elements for g = C(n+1)
    # Even basis:
    # 0: Na = a1+ a1-
    # sp(2n) basis:
    # b_i^+ b_j^+ (1 <= i <= j <= n)
    # b_i^- b_j^- (1 <= i <= j <= n)
    # b_i^+ b_j^- (1 <= i, j <= n)
    
    even_basis = [('Na',)]
    # b+ b+
    for i in range(1, n+1):
        for j in range(i, n+1):
            even_basis.append(('b+b+', i, j))
    # b- b-
    for i in range(1, n+1):
        for j in range(i, n+1):
            even_basis.append(('b-b-', i, j))
    # b+ b-
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
    dim_total = dim_even + dim_odd
    
    print(f"Dimension: Even={dim_even}, Odd={dim_odd}, Total={dim_total}")
    
    # Map basis elements to indices
    even_idx = {elem: i for i, elem in enumerate(even_basis)}
    odd_idx = {elem: i for i, elem in enumerate(odd_basis)}
    
    # Parity array: 0 for even, 1 for odd
    # Total basis: even_basis + odd_basis
    full_basis = even_basis + odd_basis
    parity = [0]*dim_even + [1]*dim_odd
    
    # Define gb parameters symbolically
    gb_vars = {}
    for sigma in ['+', '-']:
        for j in range(1, n+1):
            for s in ['+', '-']:
                var_name = f"gb_{sigma}_{j}_{s}"
                gb_vars[(sigma, j, s)] = sp.Symbol(var_name)
                
    all_gb_symbols = list(gb_vars.values())
    
    # Function to get canonical representation of quadratic b terms
    def canonical_b_quadratic(i, s, j, r):
        # returns dict {basis_even_index: coeff, 'scalar': scalar_coeff}
        if s == '+' and r == '+':
            if i <= j:
                return {even_idx[('b+b+', i, j)]: 1}
            else:
                return {even_idx[('b+b+', j, i)]: 1}
        elif s == '-' and r == '-':
            if i <= j:
                return {even_idx[('b-b-', i, j)]: 1}
            else:
                return {even_idx[('b-b-', j, i)]: 1}
        elif s == '+' and r == '-':
            return {even_idx[('b+b-', i, j)]: 1}
        elif s == '-' and r == '+':
            # b_i^- b_j^+ = b_j^+ b_i^- + delta_ij
            res = {even_idx[('b+b-', j, i)]: 1}
            if i == j:
                res['scalar'] = 1
            return res
            
    # Compute bracket [X, Y]_0 for all basis elements X, Y
    # Bracket returns a dict {full_basis_index: coeff, 'scalar': coeff}
    def bracket_0(idx1, idx2):
        elem1 = full_basis[idx1]
        elem2 = full_basis[idx2]
        p1 = parity[idx1]
        p2 = parity[idx2]
        
        res = {}
        def add_res(target, val):
            if val != 0:
                res[target] = res.get(target, 0) + val
                
        # Even-Even
        if p1 == 0 and p2 == 0:
            if elem1[0] == 'Na' or elem2[0] == 'Na':
                # Na commutes with all b_i^s b_j^r and Na
                return res
            # Both are sp(2n) elements
            # [b_i^s b_j^r, b_k^u b_m^v] = b_i^s [b_j^r, b_k^u b_m^v] + [b_i^s, b_k^u b_m^v] b_j^r
            # [b_j^r, b_k^u b_m^v] = [b_j^r, b_k^u] b_m^v + b_k^u [b_j^r, b_m^v]
            # [b_a^x, b_b^y] = delta_{a,b} if x='-', y='+' -> 1
            #                  -delta_{a,b} if x='+', y='-' -> -1
            #                  0 otherwise
            def ccr(a, x, b, y):
                if a == b:
                    if x == '-' and y == '+': return 1
                    if x == '+' and y == '-': return -1
                return 0
                
            # elem1: type, i, j (or s, r implied)
            def parse_sp(elem):
                t, i, j = elem
                if t == 'b+b+': return (i, '+', j, '+')
                if t == 'b-b-': return (i, '-', j, '-')
                if t == 'b+b-': return (i, '+', j, '-')
                
            i, s, j, r = parse_sp(elem1)
            k, u, m, v = parse_sp(elem2)
            
            # [b_i^s b_j^r, b_k^u b_m^v]
            # = ccr(j,r, k,u) b_i^s b_m^v + ccr(j,r, m,v) b_i^s b_k^u
            # + ccr(i,s, k,u) b_k^u b_j^r ... wait, order matters!
            # [A B, C D] = A [B, C D] + [A, C D] B = A [B, C] D + A C [B, D] + [A, C] D B + C [A, D] B
            # All commutator terms [B,C] etc. are scalars! So ordering is simple:
            # = ccr(j,r, k,u) b_i^s b_m^v + ccr(j,r, m,v) b_i^s b_k^u + ccr(i,s, k,u) b_m^v b_j^r + ccr(i,s, m,v) b_k^u b_j^r
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
            
        # Even-Odd
        if p1 == 0 and p2 == 1:
            # elem1 is even, elem2 is odd ('F', sigma, m, u)
            sigma, m, u = elem2[1], elem2[2], elem2[3]
            if elem1[0] == 'Na':
                # [Na, a1^\sigma b_m^u] = \sigma a1^\sigma b_m^u
                val = 1 if sigma == '+' else -1
                add_res(idx2, val)
                return res
            # elem1 is sp(2n): [b_i^s b_j^r, a1^\sigma b_m^u] = a1^\sigma [b_i^s b_j^r, b_m^u]
            # [b_i^s b_j^r, b_m^u] = ccr(j,r, m,u) b_i^s + ccr(i,s, m,u) b_j^r
            def parse_sp(elem):
                t, i, j = elem
                if t == 'b+b+': return (i, '+', j, '+')
                if t == 'b-b-': return (i, '-', j, '-')
                if t == 'b+b-': return (i, '+', j, '-')
            def ccr(a, x, b, y):
                if a == b:
                    if x == '-' and y == '+': return 1
                    if x == '+' and y == '-': return -1
                return 0
            i, s, j, r = parse_sp(elem1)
            c1 = ccr(j, r, m, u)
            if c1 != 0:
                target_odd = odd_idx[('F', sigma, i, s)] + dim_even
                add_res(target_odd, c1)
            c2 = ccr(i, s, m, u)
            if c2 != 0:
                target_odd = odd_idx[('F', sigma, j, r)] + dim_even
                add_res(target_odd, c2)
            return res
            
        if p1 == 1 and p2 == 0:
            # [Odd, Even] = - [Even, Odd]
            res_eo = bracket_0(idx2, idx1)
            for k_idx, v_val in res_eo.items():
                add_res(k_idx, -v_val)
            return res
            
        # Odd-Odd
        if p1 == 1 and p2 == 1:
            # [a1^\sigma b_i^s, a1^\tau b_j^r] = {a1^\sigma, a1^\tau} b_i^s b_j^r + a1^\tau a1^\sigma [b_i^s, b_j^r]
            sigma, i, s = elem1[1], elem1[2], elem1[3]
            tau, j, r = elem2[1], elem2[2], elem2[3]
            
            # {a1^\sigma, a1^\tau} = 1 if (sigma, tau) in [('+', '-'), ('-', '+')], else 0
            if sigma != tau:
                d = canonical_b_quadratic(i, s, j, r)
                for k_idx, v_val in d.items():
                    add_res(k_idx, v_val)
                    
            # a1^\tau a1^\sigma [b_i^s, b_j^r]
            # CCR commutator [b_i^s, b_j^r]:
            def ccr(a, x, b, y):
                if a == b:
                    if x == '-' and y == '+': return 1
                    if x == '+' and y == '-': return -1
                return 0
            c = ccr(i, s, j, r)
            if c != 0:
                # a1^\tau a1^\sigma:
                # if tau='+', sigma='-': a1+ a1- = Na (index 0)
                # if tau='-', sigma='-': 0
                # if tau='+', sigma='+': 0
                # if tau='-', sigma='+': a1- a1+ = 1 - Na
                if tau == '+' and sigma == '-':
                    add_res(0, c) # Na
                elif tau == '-' and sigma == '+':
                    add_res('scalar', c) # 1
                    add_res(0, -c) # -Na
            return res

    # Compute deformation \gamma_{gb}(X, Y)
    def gamma_gb(idx1, idx2):
        elem1 = full_basis[idx1]
        elem2 = full_basis[idx2]
        p1 = parity[idx1]
        p2 = parity[idx2]
        
        res = {}
        def add_res(target, val):
            if val != 0:
                res[target] = res.get(target, 0) + val
                
        # Even-Even
        if p1 == 0 and p2 == 0:
            if elem1[0] == 'Na' and elem2[0] != 'Na':
                # gamma(Na, b_j^s b_k^r) = gb_{-, j, s} F_{+, k, r} - gb_{+, j, s} F_{-, k, r} + gb_{-, k, r} F_{+, j, s} - gb_{+, k, r} F_{-, j, s}
                def parse_sp(elem):
                    t, i, j = elem
                    if t == 'b+b+': return (i, '+', j, '+')
                    if t == 'b-b-': return (i, '-', j, '-')
                    if t == 'b+b-': return (i, '+', j, '-')
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
                
        # Even-Odd
        if p1 == 0 and p2 == 1:
            sigma, m, u = elem2[1], elem2[2], elem2[3]
            if elem1[0] == 'Na':
                # gamma(Na, a1^+ b_k^s) = -gb_{+, k, s} Na
                # gamma(Na, a1^- b_k^s) = gb_{-, k, s} (1 - Na)
                if sigma == '+':
                    add_res(0, -gb_vars[('+', m, u)])
                else:
                    add_res('scalar', gb_vars[('-', m, u)])
                    add_res(0, -gb_vars[('-', m, u)])
                return res
            else:
                # elem1 is sp(2n): b_j^s b_k^r
                # gamma(b_j^s b_k^r, a1^\sigma b_m^u) = -gb_{\sigma, k, r} b_j^s b_m^u - gb_{\sigma, j, s} b_k^r b_m^u
                def parse_sp(elem):
                    t, i, j = elem
                    if t == 'b+b+': return (i, '+', j, '+')
                    if t == 'b-b-': return (i, '-', j, '-')
                    if t == 'b+b-': return (i, '+', j, '-')
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
            
        # Odd-Odd
        if p1 == 1 and p2 == 1:
            # gamma(a1^\sigma b_j^s, a1^\tau b_k^r) = -gb_{\tau, j, s} F_{\sigma, k, r} - gb_{\sigma, k, r} F_{\tau, j, s}
            sigma, j, s = elem1[1], elem1[2], elem1[3]
            tau, k, r = elem2[1], elem2[2], elem2[3]
            
            target1 = odd_idx[('F', sigma, k, r)] + dim_even
            add_res(target1, -gb_vars[(tau, j, s)])
            
            target2 = odd_idx[('F', tau, j, s)] + dim_even
            add_res(target2, -gb_vars[(sigma, k, r)])
            return res

    print("Checking structure constants and gamma calculations for n =", n)
    # Test a few bracket and gamma calls
    print("Bracket [Na, F_{+, 1, +}]_0 =", bracket_0(0, dim_even))
    print("Gamma (Na, F_{+, 1, +}) =", gamma_gb(0, dim_even))
    
    return dim_even, dim_odd, full_basis, parity, bracket_0, gamma_gb, all_gb_symbols

solve_triviality(1)
