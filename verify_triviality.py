import sympy as sp
from itertools import product
import json

def solve_for_n(n):
    print(f"==================== Solving for n = {n} ====================")
    
    # Deformation parameters gb[sigma, k, s]
    # sigma in {+, -}, k in {1..n}, s in {+, -}
    gb = {}
    for sigma in ['+', '-']:
        for k in range(1, n + 1):
            for s in ['+', '-']:
                name = f"gb_{sigma}_{k}_{s}"
                gb[(sigma, k, s)] = sp.Symbol(name)
                
    # Define Lie superalgebra generators
    basis = []
    basis_names = []
    basis_parity = []
    
    # 0: J (even)
    basis.append(('J',))
    basis_names.append('J')
    basis_parity.append(0)
    
    # Sp(2n) basis:
    boson_list = []
    for k in range(1, n + 1):
        boson_list.append((k, '+'))
        boson_list.append((k, '-'))
        
    for i in range(len(boson_list)):
        for j in range(i, len(boson_list)):
            b1 = boson_list[i]
            b2 = boson_list[j]
            basis.append(('B', b1, b2))
            basis_names.append(f"B({b1[0]}{b1[1]},{b2[0]}{b2[1]})")
            basis_parity.append(0)
            
    # Odd basis:
    for sigma in ['+', '-']:
        for (k, s) in boson_list:
            basis.append(('F', sigma, (k, s)))
            basis_names.append(f"F({sigma},{k}{s})")
            basis_parity.append(1)
            
    dim_even = 1 + len(boson_list)*(len(boson_list)+1)//2
    dim_odd = 2 * len(boson_list)
    dim_total = dim_even + dim_odd
    print(f"Dimension: even={dim_even}, odd={dim_odd}, total={dim_total}")
    
    def osc_bracket_0(u, v):
        if u[0] == 'a' and v[0] == 'a':
            if (u[1], v[1]) == ('-', '+') or (u[1], v[1]) == ('+', '-'):
                return sp.Rational(1)
            return sp.Rational(0)
        elif u[0] == 'b' and v[0] == 'b':
            if u[1] == v[1]: # same k
                if u[2] == '-' and v[2] == '+':
                    return sp.Rational(1)
                elif u[2] == '+' and v[2] == '-':
                    return sp.Rational(-1)
            return sp.Rational(0)
        else:
            return sp.Rational(0)
            
    def osc_bracket_kappa(u, v):
        if u[0] == 'b' and v[0] == 'a':
            k, s = u[1], u[2]
            sigma = v[1]
            return -gb[(sigma, k, s)]
        elif u[0] == 'a' and v[0] == 'b':
            sigma = u[1]
            k, s = v[1], v[2]
            return gb[(sigma, k, s)]
        return sp.Rational(0)
        
    def osc_parity(u):
        return 1 if u[0] == 'a' else 0

    def project_to_basis(quad_dict):
        res = [sp.Rational(0)] * dim_total
        for (u, v), c in quad_dict.items():
            if c == 0:
                continue
            if u[0] == 'a' and v[0] == 'a':
                if u[1] == '+' and v[1] == '-':
                    res[0] += c
                elif u[1] == '-' and v[1] == '+':
                    res[0] -= c
            elif u[0] == 'b' and v[0] == 'b':
                b1 = (u[1], u[2])
                b2 = (v[1], v[2])
                if boson_list.index(b1) <= boson_list.index(b2):
                    idx = basis.index(('B', b1, b2))
                else:
                    idx = basis.index(('B', b2, b1))
                if b1 == b2:
                    res[idx] += c
                else:
                    res[idx] += c * sp.Rational(1, 2)
            elif u[0] == 'a' and v[0] == 'b':
                sigma = u[1]
                b = (v[1], v[2])
                idx = basis.index(('F', sigma, b))
                res[idx] += c
            elif u[0] == 'b' and v[0] == 'a':
                sigma = v[1]
                b = (u[1], u[2])
                idx = basis.index(('F', sigma, b))
                res[idx] += c
        return res

    def get_basis_quad(b_elem):
        if b_elem[0] == 'J':
            return {(('a', '+'), ('a', '-')): sp.Rational(1, 2), (('a', '-'), ('a', '+')): -sp.Rational(1, 2)}
        elif b_elem[0] == 'B':
            b1 = ('b', b_elem[1][0], b_elem[1][1])
            b2 = ('b', b_elem[2][0], b_elem[2][1])
            if b1 == b2:
                return {(b1, b2): sp.Rational(1)}
            else:
                return {(b1, b2): sp.Rational(1, 2), (b2, b1): sp.Rational(1, 2)}
        elif b_elem[0] == 'F':
            a = ('a', b_elem[1])
            b = ('b', b_elem[2][0], b_elem[2][1])
            return {(a, b): sp.Rational(1)}

    def bracket_quad(q1, q2, order='0'):
        res = {}
        for (u1, u2), c1 in q1.items():
            p_u1 = osc_parity(u1)
            p_u2 = osc_parity(u2)
            for (v1, v2), c2 in q2.items():
                p_v1 = osc_parity(v1)
                p_v2 = osc_parity(v2)
                
                if order == '0':
                    b_u2_v1 = osc_bracket_0(u2, v1)
                    if b_u2_v1 != 0:
                        term = (u1, v2)
                        res[term] = res.get(term, 0) + c1 * c2 * b_u2_v1
                        
                    b_u2_v2 = osc_bracket_0(u2, v2)
                    if b_u2_v2 != 0:
                        sign = (-1)**(p_u2 * p_v1)
                        term = (u1, v1)
                        res[term] = res.get(term, 0) + c1 * c2 * sign * b_u2_v2
                        
                    b_u1_v1 = osc_bracket_0(u1, v1)
                    if b_u1_v1 != 0:
                        sign = (-1)**(p_u2 * (p_v1 + p_v2))
                        term = (v2, u2)
                        res[term] = res.get(term, 0) + c1 * c2 * sign * b_u1_v1
                        
                    b_u1_v2 = osc_bracket_0(u1, v2)
                    if b_u1_v2 != 0:
                        sign = (-1)**(p_u2 * (p_v1 + p_v2) + p_u1 * p_v1)
                        term = (v1, u2)
                        res[term] = res.get(term, 0) + c1 * c2 * sign * b_u1_v2

                elif order == 'kappa':
                    b_u2_v1 = osc_bracket_kappa(u2, v1)
                    if b_u2_v1 != 0:
                        term = (u1, v2)
                        res[term] = res.get(term, 0) + c1 * c2 * b_u2_v1
                        
                    b_u2_v2 = osc_bracket_kappa(u2, v2)
                    if b_u2_v2 != 0:
                        sign = (-1)**(p_u2 * p_v1)
                        term = (u1, v1)
                        res[term] = res.get(term, 0) + c1 * c2 * sign * b_u2_v2
                        
                    b_u1_v1 = osc_bracket_kappa(u1, v1)
                    if b_u1_v1 != 0:
                        sign = (-1)**(p_u2 * (p_v1 + p_v2))
                        term = (v2, u2)
                        res[term] = res.get(term, 0) + c1 * c2 * sign * b_u1_v1
                        
                    b_u1_v2 = osc_bracket_kappa(u1, v2)
                    if b_u1_v2 != 0:
                        sign = (-1)**(p_u2 * (p_v1 + p_v2) + p_u1 * p_v1)
                        term = (v1, u2)
                        res[term] = res.get(term, 0) + c1 * c2 * sign * b_u1_v2
        return res

    basis_quads = [get_basis_quad(b) for b in basis]
    
    C = {}
    gamma = {}
    for i in range(dim_total):
        for j in range(dim_total):
            q_comm_0 = bracket_quad(basis_quads[i], basis_quads[j], order='0')
            C[(i, j)] = project_to_basis(q_comm_0)
            
            q_comm_k = bracket_quad(basis_quads[i], basis_quads[j], order='kappa')
            gamma[(i, j)] = project_to_basis(q_comm_k)

    print("Structure constants and gamma computed successfully.")
    
    # Verify Lie superalgebra Jacobi identity for [ , ]_0:
    jacobi_failed = False
    for i in range(dim_total):
        for j in range(dim_total):
            for k in range(dim_total):
                pi = basis_parity[i]
                pj = basis_parity[j]
                pk = basis_parity[k]
                
                t1 = [sum(C[(j,k)][m] * C[(i,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t2 = [sum(C[(k,i)][m] * C[(j,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                t3 = [sum(C[(i,j)][m] * C[(k,m)][r] for m in range(dim_total)) for r in range(dim_total)]
                
                s1 = (-1)**(pi * pk)
                s2 = (-1)**(pj * pi)
                s3 = (-1)**(pk * pj)
                
                tot = [s1 * t1[r] + s2 * t2[r] + s3 * t3[r] for r in range(dim_total)]
                if any(sp.simplify(x) != 0 for x in tot):
                    print(f"Jacobi failed for {basis_names[i]}, {basis_names[j]}, {basis_names[k]}")
                    jacobi_failed = True
                    break
            if jacobi_failed: break
        if jacobi_failed: break
    if not jacobi_failed:
        print("Jacobi identity verified successfully for [ , ]_0!")

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
                
    print(f"Number of parameters in f: {len(phi_vars)}")

    # Coboundary formula:
    # (\delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    # Note: (\delta f)_{ij}^k = (-1)^{p(i)} sum_m phi_{m, j} C_{im}^k - (-1)^{(p(i)+1)p(j)} sum_m phi_{m, i} C_{jm}^k - sum_m C_{ij}^m phi_{k, m}
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
                    
    print(f"Total non-trivial equations: {len(equations)}")
    
    gb_vars = list(gb.values())
    sol = sp.solve(equations, phi_vars)
    print(f"Solver result: found solution with {len(sol)} parameters determined.")
    
    residuals = []
    for eq in equations:
        res = sp.simplify(eq.subs(sol))
        if res != 0:
            residuals.append(res)
    print(f"Residual equations depending on gb: {len(residuals)}")
    if residuals:
        print("Residuals sample:", residuals[:5])
        gb_sol = sp.solve(residuals, gb_vars)
        print("Constraints on gb:", gb_sol)
    else:
        print(">>> RESULT: Solved for ALL gb parameters WITHOUT any constraints! <<<")
        print(">>> Every inhomogeneous deformation gamma_gb is a coboundary delta f (TRIVIAL)! <<<")

    return {
        "n": n,
        "dim_even": dim_even,
        "dim_odd": dim_odd,
        "dim_total": dim_total,
        "num_gb": len(gb_vars),
        "num_phi": len(phi_vars),
        "num_equations": len(equations),
        "residuals_count": len(residuals),
        "trivial_for_all_gb": len(residuals) == 0,
        "sample_phi_solution": {str(k): str(v) for k, v in list(sol.items())[:10]}
    }

results = {}
for n in [1, 2, 3]:
    results[f"n={n}"] = solve_for_n(n)

with open("verification_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved verification_results.json successfully.")
