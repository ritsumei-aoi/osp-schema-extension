from algebra_solver import DeformedLieSuperalgebra
import sympy as sp
import json

def run_n1_analysis():
    alg = DeformedLieSuperalgebra(1)
    print(f"Dimension of g: {alg.dim} (even: {alg.dim_even}, odd: {alg.dim_odd})")
    
    C = {}
    gamma = {}
    scalars_0 = {}
    scalars_1 = {}
    
    print("\nComputing brackets...")
    for i in range(alg.dim):
        b1, p1 = alg.basis[i]
        for j in range(alg.dim):
            b2, p2 = alg.basis[j]
            bracket_dict = alg.superbracket(b1, p1, b2, p2)
            (c_k0, s_k0), (c_k1, s_k1) = alg.decompose_modulo_scalars(bracket_dict)
            if s_k0 != 0:
                scalars_0[(i, j)] = s_k0
            if s_k1 != 0:
                scalars_1[(i, j)] = s_k1
            for k in range(alg.dim):
                if c_k0[k] != 0:
                    C[(i, j, k)] = c_k0[k]
                if c_k1[k] != 0:
                    gamma[(i, j, k)] = c_k1[k]
                    
    print(f"Non-zero structure constants count: {len(C)}")
    print(f"Non-zero gamma coefficients count: {len(gamma)}")
    print(f"Non-zero scalar_0 count: {len(scalars_0)}")
    print(f"Non-zero scalar_1 count: {len(scalars_1)}")
    
    # Check Jacobi identity on C (undeformed)
    jacobi_errors = 0
    for i in range(alg.dim):
        pi = alg.basis[i][1]
        for j in range(alg.dim):
            pj = alg.basis[j][1]
            for k in range(alg.dim):
                pk = alg.basis[k][1]
                # [[X_i, X_j], X_k] * (-1)^{pk pi} + cyclic = 0
                # Term 1: (-1)^{pk pi} [ [Xi, Xj], Xk ]
                # [Xi, Xj] = sum_m C_{ij}^m Xm
                # [ [Xi, Xj], Xk ] = sum_m C_{ij}^m sum_r C_{mk}^r Xr
                for r in range(alg.dim):
                    t1 = sum(C.get((i, j, m), 0) * C.get((m, k, r), 0) for m in range(alg.dim)) * (-1)**(pk * pi)
                    t2 = sum(C.get((j, k, m), 0) * C.get((m, i, r), 0) for m in range(alg.dim)) * (-1)**(pi * pj)
                    t3 = sum(C.get((k, i, m), 0) * C.get((m, j, r), 0) for m in range(alg.dim)) * (-1)**(pj * pk)
                    if sp.simplify(t1 + t2 + t3) != 0:
                        jacobi_errors += 1
    print(f"Jacobi identity check on undeformed C(2): {jacobi_errors} errors")
    
    # Setup coboundary delta f
    # f: g -> g is odd, parameterized by phi_{k, j} where p(k) = 1 - p(j)
    phi = {}
    for j in range(alg.dim):
        pj = alg.basis[j][1]
        for k in range(alg.dim):
            pk = alg.basis[k][1]
            if pk == 1 - pj:
                phi[(k, j)] = sp.Symbol(f"phi_{k}_{j}")
                
    # delta f formula:
    # (delta f)(X, Y) = (-1)^{p(X)} [X, f(Y)] - (-1)^{(p(X)+1)p(Y)} [Y, f(X)] - f([X, Y])
    delta_f = {}
    for i in range(alg.dim):
        pi = alg.basis[i][1]
        for j in range(alg.dim):
            pj = alg.basis[j][1]
            for m in range(alg.dim):
                val = sp.Integer(0)
                sgn1 = -1 if pi == 1 else 1
                sgn2 = -1 if ((pi + 1) * pj % 2 == 1) else 1
                
                # Term 1: (-1)^{p(X)} [X, f(Y)]
                for k in range(alg.dim):
                    if (k, j) in phi and (i, k, m) in C:
                        val += sgn1 * phi[(k, j)] * C[(i, k, m)]
                        
                # Term 2: - (-1)^{(p(X)+1)p(Y)} [Y, f(X)]
                for k in range(alg.dim):
                    if (k, i) in phi and (j, k, m) in C:
                        val -= sgn2 * phi[(k, i)] * C[(j, k, m)]
                        
                # Term 3: - f([X, Y])
                for k in range(alg.dim):
                    if (i, j, k) in C and (m, k) in phi:
                        val -= C[(i, j, k)] * phi[(m, k)]
                        
                val = sp.simplify(val)
                if val != 0:
                    delta_f[(i, j, m)] = val
                    
    # System: gamma_{ij}^m = (delta f)_{ij}^m
    equations = []
    all_triplets = set(gamma.keys()).union(set(delta_f.keys()))
    for triplet in all_triplets:
        g_val = gamma.get(triplet, sp.Integer(0))
        df_val = delta_f.get(triplet, sp.Integer(0))
        equations.append(g_val - df_val)
        
    print(f"Total coboundary equations: {len(equations)}")
    
    # Solve for phi in terms of gb
    sol = sp.solve(equations, list(phi.values()))
    print(f"Solution exists? {bool(sol)}")
    if sol:
        print(f"Number of solved variables: {len(sol)} / {len(phi)}")
        remaining = [sp.simplify(eq.subs(sol)) for eq in equations if sp.simplify(eq.subs(sol)) != 0]
        print(f"Number of unsatisfied equations on gb: {len(remaining)}")
        if remaining:
            print("Unsatisfied equations:", remaining)
            gb_sol = sp.solve(remaining, list(alg.gb.values()))
            print("Constraint on gb:", gb_sol)
        else:
            print(">>> THEOREM: For ALL values of gb parameters, gamma_gb = delta f IS IDENTICALLY SATISFIED! <<<")
            print(">>> The deformation is UNCONDITIONALLY TRIVIAL for ANY gb parameters! <<<")
            print("\nExplicit solution for f in terms of gb:")
            for k, v in sol.items():
                if v != 0:
                    print(f"  {k} = {v}")
    else:
        # Check combined linear system
        all_vars = list(phi.values()) + list(alg.gb.values())
        sol_all = sp.solve(equations, all_vars)
        print("Combined solution:", sol_all)

if __name__ == "__main__":
    run_n1_analysis()
