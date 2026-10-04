import itertools
import json
import os
import sympy as sp

def get_algebra(n):
    """
    Constructs the Lie superalgebra C(n+1) = osp(2|2n)
    """
    basis_elements = [] # list of (name, parity, [(u, v, c)])
    
    # 1. H_0 = a+ a-
    basis_elements.append(('H_0', 0, [('a+', 'a-', sp.Integer(1))]))
    
    # 2. sp(2n) Cartan: h_k = b+_k b-_k for k = 1..n
    for k in range(1, n + 1):
        basis_elements.append((f'h_{k}', 0, [(f'b+{k}', f'b-{k}', sp.Integer(1))]))
        
    # 3. sp(2n) long roots: E_+2d_k = 1/2 (b+_k)^2, E_-2d_k = 1/2 (b-_k)^2
    for k in range(1, n + 1):
        basis_elements.append((f'E_+2d{k}', 0, [(f'b+{k}', f'b+{k}', sp.Rational(1, 2))]))
        basis_elements.append((f'E_-2d{k}', 0, [(f'b-{k}', f'b-{k}', sp.Rational(1, 2))]))
        
    # 4. sp(2n) short roots:
    for k in range(1, n + 1):
        for l in range(k + 1, n + 1):
            basis_elements.append((f'E_+d{k}+d{l}', 0, [(f'b+{k}', f'b+{l}', sp.Integer(1))]))
            basis_elements.append((f'E_-d{k}-d{l}', 0, [(f'b-{k}', f'b-{l}', sp.Integer(1))]))
            basis_elements.append((f'E_+d{k}-d{l}', 0, [(f'b+{k}', f'b-{l}', sp.Integer(1))]))
            basis_elements.append((f'E_-d{k}+d{l}', 0, [(f'b+{l}', f'b-{k}', sp.Integer(1))]))

    # Odd elements:
    for k in range(1, n + 1):
        basis_elements.append((f'E_+e+d{k}', 1, [('a+', f'b+{k}', sp.Integer(1))]))
        basis_elements.append((f'E_+e-d{k}', 1, [('a+', f'b-{k}', sp.Integer(1))]))
        basis_elements.append((f'E_-e+d{k}', 1, [('a-', f'b+{k}', sp.Integer(1))]))
        basis_elements.append((f'E_-e-d{k}', 1, [('a-', f'b-{k}', sp.Integer(1))]))

    names = [b[0] for b in basis_elements]
    parities = {b[0]: b[1] for b in basis_elements}
    
    def osc_parity(osc):
        return 1 if osc.startswith('a') else 0

    gb_symbols = {}
    for sigma in ['+', '-']:
        for j in range(1, n + 1):
            for s in ['+', '-']:
                sym_name = f'gb_{sigma}_{j}_{s}'
                gb_symbols[(sigma, j, s)] = sp.Symbol(sym_name)

    def osc_bracket(x, y):
        px, py = osc_parity(x), osc_parity(y)
        c0 = sp.Integer(0)
        c1 = sp.Integer(0)
        
        # Fermion-fermion
        if px == 1 and py == 1:
            if (x == 'a-' and y == 'a+') or (x == 'a+' and y == 'a-'):
                c0 = sp.Integer(1)
        # Boson-boson
        elif px == 0 and py == 0:
            sx, jx = x[1], int(x[2:])
            sy, jy = y[1], int(y[2:])
            if jx == jy:
                if sx == '-' and sy == '+':
                    c0 = sp.Integer(1)
                elif sx == '+' and sy == '-':
                    c0 = sp.Integer(-1)
        # Boson-fermion: [b_j^s, a_1^\sigma] = - gb_{\sigma, j, s} * kappa
        elif px == 0 and py == 1:
            s, j = x[1], int(x[2:])
            sigma = y[1]
            c1 = - gb_symbols[(sigma, j, s)]
        # Fermion-boson: [a_1^\sigma, b_j^s] = + gb_{\sigma, j, s} * kappa
        elif px == 1 and py == 0:
            sigma = x[1]
            s, j = y[1], int(y[2:])
            c1 = gb_symbols[(sigma, j, s)]
            
        return c0, c1

    def reduce_pair(u, v):
        pu, pv = osc_parity(u), osc_parity(v)
        res = {name: sp.Integer(0) for name in names}
        scalar = sp.Integer(0)
        
        if pu == 1 and pv == 1:
            if u == 'a+' and v == 'a-':
                res['H_0'] += 1
            elif u == 'a-' and v == 'a+':
                res['H_0'] -= 1
                scalar += 1
        elif pu == 0 and pv == 0:
            su, ju = u[1], int(u[2:])
            sv, jv = v[1], int(v[2:])
            if ju == jv:
                if su == '+' and sv == '-':
                    res[f'h_{ju}'] += 1
                elif su == '-' and sv == '+':
                    res[f'h_{ju}'] += 1
                    scalar += 1
                elif su == '+' and sv == '+':
                    res[f'E_+2d{ju}'] += 2
                elif su == '-' and sv == '-':
                    res[f'E_-2d{ju}'] += 2
            else:
                j_min, j_max = min(ju, jv), max(ju, jv)
                if su == '+' and sv == '+':
                    res[f'E_+d{j_min}+d{j_max}'] += 1
                elif su == '-' and sv == '-':
                    res[f'E_-d{j_min}-d{j_max}'] += 1
                elif su == '+' and sv == '-':
                    res[f'E_+d{ju}-d{jv}' if ju < jv else f'E_-d{jv}+d{ju}'] += 1
                elif su == '-' and sv == '+':
                    res[f'E_+d{jv}-d{ju}' if jv < ju else f'E_-d{ju}+d{jv}'] += 1
        else:
            if pu == 1 and pv == 0:
                sigma = u[1]
                s, j = v[1], int(v[2:])
            else:
                sigma = v[1]
                s, j = u[1], int(u[2:])
            res[f'E_{sigma}e{s}d{j}'] += 1
            
        return res, scalar

    def bilinear_bracket(u, v, w, z):
        pu, pv, pw, pz = osc_parity(u), osc_parity(v), osc_parity(w), osc_parity(z)
        terms = [
            (u, z, 1, v, w),
            (u, w, (-1)**(pv * pw), v, z),
            (z, v, (-1)**(pv * (pw + pz)), u, w),
            (w, v, (-1)**(pv * (pw + pz) + pu * pw), u, z)
        ]
        
        b0_res = {name: sp.Integer(0) for name in names}
        b1_res = {name: sp.Integer(0) for name in names}
        b0_scalar = sp.Integer(0)
        b1_scalar = sp.Integer(0)
        
        for (first, second, sign, comm_x, comm_y) in terms:
            c0, c1 = osc_bracket(comm_x, comm_y)
            if c0 != 0 or c1 != 0:
                pair_res, pair_scalar = reduce_pair(first, second)
                if c0 != 0:
                    for k, val in pair_res.items():
                        b0_res[k] += sign * c0 * val
                    b0_scalar += sign * c0 * pair_scalar
                if c1 != 0:
                    for k, val in pair_res.items():
                        b1_res[k] += sign * c1 * val
                    b1_scalar += sign * c1 * pair_scalar
                    
        return b0_res, b0_scalar, b1_res, b1_scalar

    struct_consts = {}
    gamma_gb = {}
    
    for (name1, p1, expr1) in basis_elements:
        for (name2, p2, expr2) in basis_elements:
            tot_b0 = {name: sp.Integer(0) for name in names}
            tot_b1 = {name: sp.Integer(0) for name in names}
            tot_b0_sc = sp.Integer(0)
            tot_b1_sc = sp.Integer(0)
            
            for (u1, v1, coeff1) in expr1:
                for (u2, v2, coeff2) in expr2:
                    b0, b0_sc, b1, b1_sc = bilinear_bracket(u1, v1, u2, v2)
                    for k in names:
                        tot_b0[k] += coeff1 * coeff2 * b0[k]
                        tot_b1[k] += coeff1 * coeff2 * b1[k]
                    tot_b0_sc += coeff1 * coeff2 * b0_sc
                    tot_b1_sc += coeff1 * coeff2 * b1_sc
                    
            struct_consts[(name1, name2)] = {k: sp.simplify(v) for k, v in tot_b0.items() if v != 0}
            gamma_gb[(name1, name2)] = {k: sp.simplify(v) for k, v in tot_b1.items() if v != 0}
            
    return basis_elements, names, parities, gb_symbols, struct_consts, gamma_gb

def verify_and_solve(n):
    print(f"\n==================== Analyzing C({n+1}) = osp(2|{2*n}) ====================")
    basis_elements, names, parities, gb_symbols, struct_consts, gamma_gb = get_algebra(n)
    dim = len(names)
    even_names = [name for name in names if parities[name] == 0]
    odd_names = [name for name in names if parities[name] == 1]
    print(f"Dimension: {dim} (Even: {len(even_names)}, Odd: {len(odd_names)})")
    
    # 1. Verify graded skew-symmetry and Jacobi identity
    print("Verifying graded skew-symmetry of undeformed bracket...")
    for i, x in enumerate(names):
        for j, y in enumerate(names):
            px, py = parities[x], parities[y]
            sign = - ((-1)**(px * py))
            b_xy = struct_consts[(x, y)]
            b_yx = struct_consts[(y, x)]
            for k in names:
                v_xy = b_xy.get(k, sp.Integer(0))
                v_yx = b_yx.get(k, sp.Integer(0))
                assert sp.simplify(v_yx - sign * v_xy) == 0, f"Skew-symmetry failed for [{x}, {y}]"

    print("Verifying super Jacobi identity...")
    # Jacobi: [X, [Y, Z]] = [[X, Y], Z] + (-1)^{p(X) p(Y)} [Y, [X, Z]]
    # or [X, [Y, Z]] - [[X, Y], Z] - (-1)^{px py} [Y, [X, Z]] == 0
    # Let's check on all triples
    def bracket_eval(d_xy, z):
        # d_xy is dict of {k: coeff}
        # computes [d_xy, z]
        res = {k: sp.Integer(0) for k in names}
        for elem, c in d_xy.items():
            if c == 0: continue
            for out_elem, out_c in struct_consts[(elem, z)].items():
                res[out_elem] += c * out_c
        return res

    def bracket_eval_left(x, d_yz):
        res = {k: sp.Integer(0) for k in names}
        for elem, c in d_yz.items():
            if c == 0: continue
            for out_elem, out_c in struct_consts[(x, elem)].items():
                res[out_elem] += c * out_c
        return res

    jacobi_passed = True
    for x in names:
        for y in names:
            for z in names:
                px, py, pz = parities[x], parities[y], parities[z]
                # [X, [Y, Z]]
                term1 = bracket_eval_left(x, struct_consts[(y, z)])
                # [[X, Y], Z]
                term2 = bracket_eval(struct_consts[(x, y)], z)
                # (-1)^{px py} [Y, [X, Z]]
                term3 = bracket_eval_left(y, struct_consts[(x, z)])
                sign3 = (-1)**(px * py)
                
                for k in names:
                    diff = term1[k] - term2[k] - sign3 * term3[k]
                    if sp.simplify(diff) != 0:
                        print(f"Jacobi failed for ({x}, {y}, {z}) at component {k}: {diff}")
                        jacobi_passed = False
                        break
    print(f"Jacobi identity verified: {jacobi_passed}")

    # 2. Define odd linear map f: g -> g
    # f reverses parity:
    # If p(Y) == 0, f(Y) is in g_1, so f(Y) = sum_{k in odd} phi_{k, Y} Z_k
    # If p(Y) == 1, f(Y) is in g_0, so f(Y) = sum_{k in even} phi_{k, Y} Z_k
    phi_symbols = {}
    for y in names:
        py = parities[y]
        target_names = odd_names if py == 0 else even_names
        for k in target_names:
            sym = sp.Symbol(f"phi_{k}_{y}")
            phi_symbols[(k, y)] = sym

    print(f"Number of parameters in f: {len(phi_symbols)} ({len(even_names)}*{len(odd_names)}*2 = {2*len(even_names)*len(odd_names)})")

    # 3. Compute delta f(X, Y)
    # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    # Let's compute delta f for all pairs (X, Y)
    delta_f = {}
    for x in names:
        for y in names:
            px, py = parities[x], parities[y]
            res = {k: sp.Integer(0) for k in names}
            
            # Term 1: (-1)^{p(X)} [X, f(Y)]
            sign1 = (-1)**px
            # f(Y) = sum_k phi_{k, Y} Z_k
            target_y = odd_names if py == 0 else even_names
            for ky in target_y:
                phi_ky = phi_symbols[(ky, y)]
                for out_k, c in struct_consts[(x, ky)].items():
                    res[out_k] += sign1 * phi_ky * c
                    
            # Term 2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
            sign2 = - ((-1)**((px + 1) * py))
            target_x = odd_names if px == 0 else even_names
            for kx in target_x:
                phi_kx = phi_symbols[(kx, x)]
                for out_k, c in struct_consts[(y, kx)].items():
                    res[out_k] += sign2 * phi_kx * c
                    
            # Term 3: - f([X, Y])
            # [X, Y] = sum_k c_k Z_k
            # f([X, Y]) = sum_k c_k f(Z_k)
            for k_xy, c_xy in struct_consts[(x, y)].items():
                if c_xy == 0: continue
                p_kxy = parities[k_xy] # Note: p_kxy == (px + py) % 2
                target_kxy = odd_names if p_kxy == 0 else even_names
                for out_k in target_kxy:
                    phi_out = phi_symbols[(out_k, k_xy)]
                    res[out_k] -= c_xy * phi_out
                    
            delta_f[(x, y)] = {k: sp.simplify(v) for k, v in res.items() if v != 0}

    # 4. Set up triviality condition: gamma_gb(X, Y) == delta_f(X, Y)
    print("Setting up linear system gamma_gb(X, Y) = delta_f(X, Y)...")
    equations = []
    # Collect all equations for all pairs (X, Y) and all components k
    for i, x in enumerate(names):
        for j, y in enumerate(names):
            if i > j: continue # graded skew symmetry means i <= j is sufficient
            gamma_dict = gamma_gb[(x, y)]
            delta_dict = delta_f[(x, y)]
            all_out_keys = set(gamma_dict.keys()) | set(delta_dict.keys())
            for k in all_out_keys:
                g_val = gamma_dict.get(k, sp.Integer(0))
                d_val = delta_dict.get(k, sp.Integer(0))
                eq = sp.simplify(g_val - d_val)
                if eq != 0:
                    equations.append(eq)

    print(f"Total non-trivial linear equations: {len(equations)}")
    
    # Solve linear system for gb and phi
    all_gb_vars = list(gb_symbols.values())
    all_phi_vars = list(phi_symbols.values())
    all_vars = all_gb_vars + all_phi_vars
    
    # Build linear system matrix M * V = 0
    system_matrix, rhs = sp.linear_eq_to_matrix(equations, all_vars)
    print(f"Matrix shape: {system_matrix.shape}")
    
    # Compute nullspace of system_matrix
    print("Computing nullspace of the system...")
    nullspace = system_matrix.nullspace()
    print(f"Nullspace dimension (moduli of trivial deformations / coboundary symmetries): {len(nullspace)}")
    
    # Check if any vector in nullspace has non-zero gb components
    num_gb = len(all_gb_vars)
    gb_null_dim = 0
    non_zero_gb_solutions = []
    for vec in nullspace:
        gb_part = vec[:num_gb, :]
        if not gb_part.is_zero_matrix:
            gb_null_dim += 1
            non_zero_gb_solutions.append(vec)
            
    print(f"Dimension of solutions with non-zero gb: {gb_null_dim}")
    
    # Also test if eliminating phi implies gb = 0
    # Solve for gb in terms of phi:
    # Let's project system_matrix onto gb subspace
    gb_matrix = system_matrix[:, :num_gb]
    phi_matrix = system_matrix[:, num_gb:]
    
    print(f"gb_matrix rank: {gb_matrix.rank()}, phi_matrix rank: {phi_matrix.rank()}")
    
    # Check if there is any solution when gb != 0
    sol = sp.solve(equations, all_vars, dict=True)
    print(f"General solution sample: {sol}")
    
    # Specifically check what conditions on gb are required:
    gb_constraints = []
    for g in all_gb_vars:
        val = sol[0].get(g, None)
        print(f"Constraint on {g}: {val}")
        if val == 0 or val is None:
            pass
        gb_constraints.append((str(g), str(val)))

    result_data = {
        'n': n,
        'algebra': f'C({n+1}) = osp(2|{2*n})',
        'even_dim': len(even_names),
        'odd_dim': len(odd_names),
        'total_dim': dim,
        'num_gb_params': len(all_gb_vars),
        'num_phi_params': len(all_phi_vars),
        'num_equations': len(equations),
        'system_matrix_rows': system_matrix.shape[0],
        'system_matrix_cols': system_matrix.shape[1],
        'nullspace_dim': len(nullspace),
        'non_zero_gb_sol_dim': gb_null_dim,
        'gb_must_be_zero': all(sol[0].get(g, 1) == 0 for g in all_gb_vars),
        'structure_constants': {f"{k[0]},{k[1]}": {str(out): str(v) for out, v in val.items()} for k, val in struct_consts.items() if val},
        'gamma_gb': {f"{k[0]},{k[1]}": {str(out): str(v) for out, v in val.items()} for k, val in gamma_gb.items() if val},
    }
    
    return result_data

def run_all():
    all_results = {}
    for n in [1, 2, 3]:
        res = verify_and_solve(n)
        all_results[f'C_{n+1}'] = res
        
    out_file = 'verification/verification_results.json'
    with open(out_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nAll results saved to {out_file}")

if __name__ == '__main__':
    run_all()
