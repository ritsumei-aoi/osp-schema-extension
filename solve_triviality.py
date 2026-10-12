import sympy as sp
import json
import sys

def build_algebra(n):
    osc = []
    osc.append(('a', 'p', 0))
    osc.append(('a', 'm', 0))
    for k in range(1, n+1):
        osc.append(('b', 'p', k))
        osc.append(('b', 'm', k))
        
    def parity(u):
        return 1 if u[0] == 'a' else 0
        
    def order(u):
        if u[0] == 'a':
            return 1 if u[1] == 'p' else 2
        else:
            base = 2 + 2 * (u[2] - 1)
            return base + 1 if u[1] == 'p' else base + 2

    gb_syms = {}
    gb_vars = []
    for sigma in ['p', 'm']:
        for k in range(1, n+1):
            for s in ['p', 'm']:
                sym = sp.Symbol(f'gb_{sigma}_{k}_{s}')
                gb_syms[(sigma, k, s)] = sym
                gb_vars.append(sym)

    def omega0(u, v):
        if u[0] == 'b' and v[0] == 'b':
            if u[2] == v[2] and u[1] != v[1]:
                return 1 if u[1] == 'm' else -1
            return 0
        if u[0] == 'a' and v[0] == 'a':
            if u[1] != v[1]:
                return 1
            return 0
        return 0

    def omega1(u, v):
        if u[0] == 'b' and v[0] == 'a':
            return -gb_syms[(v[1], u[2], u[1])]
        if u[0] == 'a' and v[0] == 'b':
            return gb_syms[(u[1], v[2], v[1])]
        return 0

    def normal_order(u, v):
        if order(u) <= order(v):
            return { (u, v): 1 }
        else:
            sign = -1 if (parity(u) == 1 and parity(v) == 1) else 1
            res = { (v, u): sign }
            w0 = omega0(u, v)
            w1 = omega1(u, v)
            if w0 != 0:
                res['scalar'] = w0
            if w1 != 0:
                res['kappa'] = w1
            return res

    def multiply_scalar(term, scalar):
        return {k: v * scalar for k, v in term.items()}

    def add_terms(t1, t2):
        res = {}
        for k, v in t1.items():
            res[k] = res.get(k, 0) + v
        for k, v in t2.items():
            res[k] = res.get(k, 0) + v
        return {k: sp.simplify(v) for k, v in res.items() if v != 0}

    def superbracket(AB, CD):
        A, B = AB
        C, D = CD
        res = {}
        
        def process_term(u, v, w0, w1, sign):
            nonlocal res
            if w0 != 0:
                ord_uv = normal_order(u, v)
                res = add_terms(res, multiply_scalar(ord_uv, w0 * sign))
            if w1 != 0:
                ord_uv = normal_order(u, v)
                for k, val in ord_uv.items():
                    if k != 'kappa' and k != 'scalar':
                        res[('kappa', k)] = res.get(('kappa', k), 0) + val * w1 * sign
                    elif k == 'scalar':
                        res['kappa_scalar'] = res.get('kappa_scalar', 0) + val * w1 * sign
                        
        pA = parity(A); pB = parity(B); pC = parity(C); pD = parity(D)
        
        w0, w1 = omega0(B, C), omega1(B, C)
        process_term(A, D, w0, w1, 1)
        
        w0, w1 = omega0(B, D), omega1(B, D)
        process_term(A, C, w0, w1, (-1)**(pB*pC))
        
        w0, w1 = omega0(A, C), omega1(A, C)
        process_term(D, B, w0, w1, (-1)**(pB*(pC+pD)))
        
        w0, w1 = omega0(A, D), omega1(A, D)
        process_term(C, B, w0, w1, (-1)**(pB*(pC+pD) + pA*pC))
        
        return {k: sp.simplify(v) for k, v in res.items() if v != 0}

    basis = []
    basis.append((('a', 'p', 0), ('a', 'm', 0)))
    for k in range(1, n+1):
        for l in range(k, n+1):
            basis.append((('b', 'p', k), ('b', 'p', l)))
            basis.append((('b', 'm', k), ('b', 'm', l)))
    for k in range(1, n+1):
        for l in range(1, n+1):
            basis.append((('b', 'p', k), ('b', 'm', l)))
    for k in range(1, n+1):
        basis.append((('a', 'p', 0), ('b', 'p', k)))
        basis.append((('a', 'p', 0), ('b', 'm', k)))
        basis.append((('a', 'm', 0), ('b', 'p', k)))
        basis.append((('a', 'm', 0), ('b', 'm', k)))

    return basis, superbracket, parity, gb_vars

def solve_for_n(n):
    basis, bracket, parity_fn, gb_vars = build_algebra(n)
    
    def element_parity(b):
        return (parity_fn(b[0]) + parity_fn(b[1])) % 2

    dim = len(basis)
    
    f_vars = []
    f_matrix = {}
    for j, bj in enumerate(basis):
        for i, bi in enumerate(basis):
            if element_parity(bi) != element_parity(bj):
                var = sp.Symbol(f'phi_{i}_{j}')
                f_vars.append(var)
                f_matrix[(i, j)] = var

    equations = []
    
    for i, X in enumerate(basis):
        for j, Y in enumerate(basis):
            if i > j: continue
            
            b_xy = bracket(X, Y)
            
            gamma_xy = [0] * dim
            for k, Z in enumerate(basis):
                if ('kappa', Z) in b_xy:
                    gamma_xy[k] = b_xy[('kappa', Z)]
                    
            pX = element_parity(X)
            pY = element_parity(Y)
            
            delta_f_xy = [0] * dim
            
            for k, Z in enumerate(basis):
                if (k, j) in f_matrix:
                    phi_k_j = f_matrix[(k, j)]
                    b_xz = bracket(X, Z)
                    for m, W in enumerate(basis):
                        if W in b_xz:
                            delta_f_xy[m] += (-1)**pX * phi_k_j * b_xz[W]
                            
            for k, Z in enumerate(basis):
                if (k, i) in f_matrix:
                    phi_k_i = f_matrix[(k, i)]
                    b_yz = bracket(Y, Z)
                    for m, W in enumerate(basis):
                        if W in b_yz:
                            delta_f_xy[m] -= (-1)**((pX+1)*pY) * phi_k_i * b_yz[W]
                            
            for k, Z in enumerate(basis):
                if Z in b_xy:
                    coeff = b_xy[Z]
                    for m, W in enumerate(basis):
                        if (m, k) in f_matrix:
                            delta_f_xy[m] -= coeff * f_matrix[(m, k)]
                            
            for k in range(dim):
                eq = gamma_xy[k] - delta_f_xy[k]
                eq = sp.simplify(eq)
                if eq != 0:
                    equations.append(eq)
                    
    A = sp.zeros(len(equations), len(f_vars))
    B = sp.zeros(len(equations), 1)
    
    for r, eq in enumerate(equations):
        for c, f_var in enumerate(f_vars):
            coeff = eq.coeff(f_var)
            A[r, c] = coeff
        
        rem = eq.subs({f: 0 for f in f_vars})
        B[r, 0] = -rem
        
    left_null = A.T.nullspace()
    
    cond_exprs = []
    conditions = []
    for v in left_null:
        cond = sp.simplify((v.T * B)[0, 0])
        if cond != 0:
            cond_exprs.append(cond)
            conditions.append(str(cond))
            
    # Check if all variables must be zero
    sol = sp.solve(cond_exprs, gb_vars)
    
    rk = A.rank()
    
    return {
        "n": n,
        "dim_g": dim,
        "equations_count": len(equations),
        "f_vars_count": len(f_vars),
        "matrix_rank": int(rk),
        "nullspace_dim": len(left_null),
        "conditions": conditions,
        "solution": {str(k): str(v) for k, v in sol.items()} if isinstance(sol, dict) else str(sol)
    }

if __name__ == '__main__':
    results = []
    for n in [1, 2, 3]:
        print(f"Processing n={n}...")
        res = solve_for_n(n)
        results.append(res)
        
    with open('verification_artifacts.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("Done")
