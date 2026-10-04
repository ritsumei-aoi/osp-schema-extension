from algebra_solver import DeformedLieSuperalgebra
import sympy as sp
import time

def run_n_analysis(n_val):
    print(f"\n==========================================")
    print(f"=== Running analysis for n = {n_val} ===")
    print(f"==========================================")
    start_t = time.time()
    alg = DeformedLieSuperalgebra(n_val)
    print(f"Dimension of g: {alg.dim} (even: {alg.dim_even}, odd: {alg.dim_odd})")
    print(f"Number of gb parameters: {len(alg.gb)}")
    
    C = {}
    gamma = {}
    scalars_0 = {}
    scalars_1 = {}
    
    print("Computing brackets...")
    t0 = time.time()
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
    print(f"Brackets computed in {time.time() - t0:.2f}s")
    print(f"Non-zero C count: {len(C)}, Non-zero gamma count: {len(gamma)}")
    
    # Check Jacobi on C
    t0 = time.time()
    jacobi_errors = 0
    # Sample check or full check
    for i in range(alg.dim):
        pi = alg.basis[i][1]
        for j in range(alg.dim):
            pj = alg.basis[j][1]
            for k in range(alg.dim):
                pk = alg.basis[k][1]
                for r in range(alg.dim):
                    t1 = sum(C.get((i, j, m), 0) * C.get((m, k, r), 0) for m in range(alg.dim)) * (-1)**(pk * pi)
                    t2 = sum(C.get((j, k, m), 0) * C.get((m, i, r), 0) for m in range(alg.dim)) * (-1)**(pi * pj)
                    t3 = sum(C.get((k, i, m), 0) * C.get((m, j, r), 0) for m in range(alg.dim)) * (-1)**(pj * pk)
                    if sp.simplify(t1 + t2 + t3) != 0:
                        jacobi_errors += 1
    print(f"Jacobi identity check: {jacobi_errors} errors ({time.time() - t0:.2f}s)")
    
    # Setup coboundary delta f
    phi = {}
    for j in range(alg.dim):
        pj = alg.basis[j][1]
        for k in range(alg.dim):
            pk = alg.basis[k][1]
            if pk == 1 - pj:
                phi[(k, j)] = sp.Symbol(f"phi_{k}_{j}")
                
    print(f"Total phi parameters: {len(phi)}")
    
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
                    
    equations = []
    all_triplets = set(gamma.keys()).union(set(delta_f.keys()))
    for triplet in all_triplets:
        g_val = gamma.get(triplet, sp.Integer(0))
        df_val = delta_f.get(triplet, sp.Integer(0))
        equations.append(g_val - df_val)
        
    print(f"Total coboundary equations: {len(equations)}")
    
    t0 = time.time()
    sol = sp.solve(equations, list(phi.values()))
    print(f"Solver completed in {time.time() - t0:.2f}s")
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
            print(f">>> THEOREM FOR n={n_val}: For ALL values of gb parameters, gamma_gb = delta f IS IDENTICALLY SATISFIED! <<<")
            print(f">>> The deformation is UNCONDITIONALLY TRIVIAL for ANY gb parameters! <<<")
            
    print(f"Total time for n={n_val}: {time.time() - start_t:.2f}s")

if __name__ == "__main__":
    run_n_analysis(2)
